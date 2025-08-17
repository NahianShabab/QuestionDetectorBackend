from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.exceptions import HTTPException
import database
from security import text_and_hash_match,get_jwt
from authentication import get_current_user,check_current_user_role
router = APIRouter(prefix='/users',tags=['Users'])

@router.post('/login')
async def login_user(login_form: OAuth2PasswordRequestForm=Depends()):
    hashed_password = await database.get_user_hashed_password(login_form.username)
    if hashed_password is None:
        raise HTTPException(400,'Invalid credentials')
    if not text_and_hash_match(login_form.password,hashed_password):
        raise HTTPException(400,'Invalid credentials')
    
    user_read = await database.get_user_from_username(login_form.username)
    jwt_token = get_jwt(user_read.model_dump())
    return {'success':True,'message':'Login successful!','user':user_read,\
        'access_token':jwt_token,'token_type':'bearer'}

@router.get('/setterinfo')
async def get_setter_info(_=Depends(check_current_user_role(['admin']))):
    return 'This is a super secret transmission only publishable to setters!'

@router.get('/me')
async def get_current_user(cu = Depends(get_current_user)):
    return cu