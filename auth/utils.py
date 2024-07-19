import os
import jwt
import secrets
from datetime import datetime, timedelta
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends, HTTPException
from dotenv import load_dotenv


load_dotenv()
SECRET = os.environ.get('SECRETS')
algorithm = 'HS256'
security = HTTPBearer()


def generate_token(user_id: int):
    jti_access = secrets.token_urlsafe(32)
    jti_refresh = secrets.token_urlsafe(32)

    payload_access = {
        'type': 'access',
        'exp': datetime.utcnow() + timedelta(minutes=15),
        'user_id': user_id,
        'jti': jti_access
    }
    payload_refresh = {
        'type': 'refresh',
        'exp': datetime.utcnow() + timedelta(days=1),
        'user_id': user_id,
        'jti': jti_refresh
    }
    access_token = jwt.encode(payload_access, SECRET, algorithm=algorithm)
    refresh_token = jwt.encode(payload_refresh, SECRET, algorithm=algorithm)
    return {
        'access': access_token,
        'refresh': refresh_token
    }


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET, algorithms=[algorithm])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail='Token is expired!')
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail='Token invalid!')


async def get_current_user(payload: dict = Depends(verify_token)):
    user_id = payload.get("user_id")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    return user_id


def generate_access_token(user_id: int):
    jti_access = secrets.token_urlsafe(32)
    payload_access = {
        'type': 'access',
        'exp': datetime.utcnow() + timedelta(minutes=30),
        'user_id': user_id,
        'jti': jti_access
    }
    access_token = jwt.encode(payload_access, SECRET, algorithm=algorithm)
    return access_token
