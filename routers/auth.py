from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from db.database import get_db
from db.models import User, TokenBlackList, Cart
from db.shemas import UserCreate, UserResponse, UserForgotPassword
from core.config import settings

router = APIRouter(tags=["Auth"])

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")



def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def create_token(data: dict, expires_delta: timedelta, token_type: str):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire, "type": token_type})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
):

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    check_token = db.query(TokenBlackList).filter(TokenBlackList.token == token).first()
    if check_token:
        raise credentials_exception

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        sub: str = payload.get("sub")
        token_type: str = payload.get("type")

        if sub is None or token_type != "access":
            raise credentials_exception

        user = db.query(User).filter(User.login == sub).first()
        if user is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    return user


@router.post('/register', response_model=UserResponse)
def register(user_data: UserCreate, db: Session = Depends(get_db)):

    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    if db.query(User).filter(User.login == user_data.login).first():
        raise HTTPException(status_code=400, detail="Login already taken")

    hashed = hash_password(user_data.password)

    new_user = User(
        email=user_data.email,
        password=hashed,
        login=user_data.login,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        phone_number=user_data.phone_number
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    cart = Cart(
        user_id=new_user.id,
    )

    db.add(cart)
    db.commit()

    return new_user


@router.post('/login')
def login(user_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.login == user_data.username).first()

    # 2. Перевірка пароля
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
    #
    # db.add(refresh_token)
    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post('/logout')
def logout( token: str = Depends(oauth2_scheme),
            db: Session = Depends(get_db),
            current_user: User = Depends(get_current_user)
):

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        db.refresh(current_user)

        current_user.last_logout_at = datetime.now(timezone.utc)

        check_token = db.query(TokenBlackList).filter(TokenBlackList.token == token).first()

        if check_token:
            raise credentials_exception

        new_blacklisted_token = TokenBlackList(
            token = token
        )
        db.add(new_blacklisted_token)
        db.commit()

        return f"Logout successfully"

    except Exception as e:
        return f"Error {e}"


@router.post("/refresh")
def refresh_token_endpoint(refresh_token: str, db: Session = Depends(get_db)):
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

    user = db.query(User).filter(User.login == sub).first()
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
def change_password(
        new_password: str,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    current_user.password = hash_password(new_password)
    db.add(current_user)
    db.commit()
    return {"message": "Password updated successfully"}


@router.post('/forgot-password')
def forgot_password(user_email: UserForgotPassword, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user_email.email).first()

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    return {"message": f"message for reset password was sent successfully on {user_email.email} email"}
