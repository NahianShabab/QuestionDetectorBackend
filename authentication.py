
from fastapi import Depends
from models import UserRead
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordBearer
from security import verify_and_decode_jwt
import database as db
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/users/login')

async def get_current_user(token:str=Depends(oauth2_scheme))->UserRead:
    payload= verify_and_decode_jwt(token)
    if payload is None:
        raise HTTPException(401)
    current_user = await db.get_user_from_username(payload['username'])
    if current_user is None:
        raise HTTPException(401)
    return current_user

def check_current_user_role(allowed_roles:list[str]):
    async def _check_current_user_role(current_user:UserRead= Depends(get_current_user)):
        if current_user.user_role in allowed_roles:
            return current_user
        raise HTTPException(401)
    return _check_current_user_role