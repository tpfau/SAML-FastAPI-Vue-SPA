from datetime import datetime, timedelta
from typing import Callable
from fastapi import HTTPException

from fastapi import HTTPException, status
from jose import JWTError, jwt
from pydantic import BaseModel


ACCESS_TOKEN_EXPIRE_MINUTES = 1
ALGORITHM = "HS256"
SECRET_KEY = "SomeSecret"


class TokenRequest(BaseModel):
    token: str


def checkUser(data):
    # Put in your user check here.
    return True


def create_access_token(data: dict, useracceptable: Callable = checkUser):
    createToken = useracceptable(dict)
    if createToken:
        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode = data.copy()
        expire = datetime.now() + expires_delta
        to_encode.update({"exp": expire.timestamp()})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not allowed to proceed",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(token: str):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        expTime = datetime.utcfromtimestamp(payload.get("exp"))
        if datetime.utcnow() > expTime:
            print("Token no longer valid")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token no longer valid",
                headers={"WWW-Authenticate": "Bearer"},
            )
        user: str = payload.get("user")
        if user is None:
            raise credentials_exception
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    if user is None:
        raise credentials_exception
    print("Returning user")
    return user
