import bcrypt
import jwt
from datetime import datetime,timezone
from config import get_config

def get_hashed_text(text:str)->str:
    text_bytes = text.encode('utf-8')
    hash_bytes =  bcrypt.hashpw(text_bytes,bcrypt.gensalt())
    return hash_bytes.decode('utf-8')

def text_and_hash_match(text:str,hashed_text:str)->bool:
    return bcrypt.checkpw(text.encode('utf-8'),hashed_text.encode('utf-8'))

def get_jwt(payload:dict)->str:
    config = get_config()
    data = payload.copy()
    DAY_TO_SECONDS = 86400
    data['exp'] = int(datetime.now(timezone.utc).timestamp())+int(config['TOKEN_EXPIRATION_TIME_IN_DAYS']) * DAY_TO_SECONDS
    jwt_secret = config['JWT_SECRET']
    return jwt.encode(data,jwt_secret,'HS256')

def verify_and_decode_jwt(jwt_string:str)->dict|None:
    try:
        config = get_config()
        jwt_secret = config['JWT_SECRET']
        payload =  jwt.decode(jwt_string,jwt_secret,algorithms=['HS256'])
        return payload
    except:
        return None
    
def get_current_user():
    pass
