from datetime import timedelta, datetime
from typing import Annotated
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from jose import JWTError, jwt
from . import schemas
from .connection import connect_mysql
from .config import settings
from icecream import ic

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def hash(password: str):
    return pwd_context.hash(password)

def verify(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_access_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("username")
        is_auth: bool = payload.get("is_auth")
        if username is None:
            raise credentials_exception
        if is_auth is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username, is_auth=is_auth)
    except JWTError:
        raise credentials_exception
    return token_data

def get_current_user_active(token: Annotated[str, Depends(oauth2_scheme)], cursor = Depends(connect_mysql)):
    credentials_exception = HTTPException(
         status_code=status.HTTP_401_UNAUTHORIZED,
         detail="Could not validate credentials",
         headers={"WWW-Authenticate": "Bearer"},
         )
    token_data = verify_access_token(token, credentials_exception)
    cursor.execute("SELECT * FROM Users WHERE username = %s;", [token_data.username])
    user = cursor.fetchone()
    if not user:
        raise credentials_exception
    if not user["is_login"]:
        raise credentials_exception
    active_user = schemas.UserOut(**user)
    return active_user


