from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_async_db
from db.models import User, Cart
from db.shemas import UserCreate, UserResponse, UserForgotPassword
from core.config import settings
from routers.repositories.dependencies import (
    get_user_repository,
    get_token_repository,
    get_cart_repository
)
from routers.repositories import UserRepository, TokenRepository, CartRepository

router = APIRouter(tags=["Auth"])

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_token(data: dict, expires_delta: timedelta, token_type: str) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire, "type": token_type})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    token_repo: TokenRepository = Depends(get_token_repository),
    user_repo: UserRepository = Depends(get_user_repository)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Перевірка чи токен в чорному списку
    if await token_repo.is_blacklisted(token):
        raise credentials_exception

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        sub: str = payload.get("sub")
        token_type: str = payload.get("type")

        if sub is None or token_type != "access":
            raise credentials_exception

        user = await user_repo.get_by_login(sub)
        if user is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    return user


@router.post('/register', response_model=UserResponse)
async def register(
    user_data: UserCreate,
    user_repo: UserRepository = Depends(get_user_repository),
    cart_repo: CartRepository = Depends(get_cart_repository)
):
    """Реєстрація нового користувача"""
    # Перевірка на існуючий email
    if await user_repo.get_by_email(user_data.email):
        raise HTTPException(status_code=400, detail="Email already registered")

    # Перевірка на існуючий login
    if await user_repo.get_by_login(user_data.login):
        raise HTTPException(status_code=400, detail="Login already taken")

    # Створення користувача
    hashed = hash_password(user_data.password)
    new_user = await user_repo.create(
        email=user_data.email,
        password=hashed,
        login=user_data.login,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        phone_number=user_data.phone_number
    )
    await user_repo.db.flush()

    # Створення кошика для користувача
    await cart_repo.create(new_user.id)
    await user_repo.db.commit()
    await user_repo.db.refresh(new_user)

    return new_user


@router.post('/login')
async def login(
    user_data: OAuth2PasswordRequestForm = Depends(),
    user_repo: UserRepository = Depends(get_user_repository)
):
    """Вхід користувача"""
    user = await user_repo.get_by_login(user_data.username)

    if not user or not verify_password(user_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect login or password"
        )

    access_token = create_token(
        data={"sub": user.login},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        token_type="access"
    )

    refresh_token = create_token(
        data={"sub": user.login},
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_TIME),
        token_type="refresh"
    )

    await user_repo.db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post('/logout')
async def logout(
    token: str = Depends(oauth2_scheme),
    current_user: User = Depends(get_current_user),
    user_repo: UserRepository = Depends(get_user_repository),
    token_repo: TokenRepository = Depends(get_token_repository)
):
    """Вихід користувача"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        await user_repo.db.refresh(current_user)
        current_user.last_logout_at = datetime.now(timezone.utc)

        # Перевірка чи токен вже в чорному списку
        if await token_repo.is_blacklisted(token):
            raise credentials_exception

        # Додаємо токен до чорного списку
        await token_repo.add_to_blacklist(token)
        await token_repo.db.commit()

        return "Logout successfully"

    except Exception as e:
        return f"Error {e}"


@router.post("/refresh")
async def refresh_token_endpoint(
    refresh_token: str,
    user_repo: UserRepository = Depends(get_user_repository)
):
    """Оновити access token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )

    try:
        payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        sub: str = payload.get("sub")
        token_type: str = payload.get("type")

        if sub is None or token_type != "refresh":
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    user = await user_repo.get_by_login(sub)
    if user is None:
        raise credentials_exception

    new_access_token = create_token(
        data={"sub": user.login},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        token_type="access"
    )
    new_refresh_token = create_token(
        data={"sub": user.login},
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_TIME),
        token_type="refresh"
    )

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }


@router.post('/change-password')
async def change_password(
    new_password: str,
    current_user: User = Depends(get_current_user),
    user_repo: UserRepository = Depends(get_user_repository)
):
    """Змінити пароль"""
    current_user.password = hash_password(new_password)
    await user_repo.update(current_user, password=current_user.password)
    await user_repo.db.commit()
    return {"message": "Password updated successfully"}


@router.post('/forgot-password')
async def forgot_password(
    user_email: UserForgotPassword,
    user_repo: UserRepository = Depends(get_user_repository)
):
    """Забули пароль"""
    db_user = await user_repo.get_by_email(user_email.email)

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    return {"message": f"message for reset password was sent successfully on {user_email.email} email"}
