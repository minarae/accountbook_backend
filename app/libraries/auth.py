from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from fastapi import HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm


# 암호화를 위한 객체 생성
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 임의로 사용할 비밀키(secret key)
SECRET_KEY = "7395e755307a3276d60f253cc58ecd3b80ab82d95fdaeb30a424c8f52b9faa5c"
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# 패스워드를 암호화하는 함수
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# 암호화된 패스워드와 입력된 패스워드를 비교하는 함수
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# JWT 생성 함수
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# JWT 검증 함수
def decode_access_token(token: str = Header("token")):
    encode = token.split(" ")
    if len(encode) != 2 or encode[0] != 'Bearer':
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = jwt.decode(encode[1], SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
