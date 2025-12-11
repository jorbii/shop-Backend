from datetime import datetime, UTC, timedelta
from urllib import request

from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, APIRouter, requests
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext

from db.database import db
from core.config import settings

router = APIRouter()

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECURITY_KEY, algorithm=settings.ALGORITHM)


def get_current_user(
    token: str = Depends(oauth2_scheme),
):
    credentials_exception = HTTPException(
        status_code=404,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, settings.SECURITY_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = next((u for u in db.users if u['username'] == username), None)
    if user is None:
        raise credentials_exception

    return user

# @router.post('/register')
# def register(data: ):
#
#     hashed = hash_password(data['password'])
#
#     user = {
#         "first_name": data['first_name'],
#         "last_name": data['last_name'],
#         "username": data['username'],
#         "email": data['email'],
#         "password": hashed,
#         "birthday": data['birthday']
#     }
