from pydantic import BaseModel


#region Users

_USER_VALID_ROLES = ('admin','setter','composer')
def is_valid_user_role(user_role:str):
    return user_role in _USER_VALID_ROLES

class UserBase(BaseModel):
    username:str
    user_role:str
    first_name:str
    last_name:str
    email:str|None

class ExistingUser(UserBase):
    user_id:int

class UserDatabase(ExistingUser):
    hashed_password:str

class UserUpdate(ExistingUser):
    password:str

class UserCreate(UserBase):
    password:str

class UserRead(ExistingUser):
    pass
#endregion