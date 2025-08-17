
import dotenv
import psycopg
import asyncio

from config import get_config
from models import UserCreate,UserRead,UserDatabase
from security import get_hashed_text
import sys

if sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

async def get_connection():
    config = get_config()
    conn = await psycopg.AsyncConnection.connect(config['DATABASE_URL'])
    cur = conn.cursor()
    return (conn,cur)


async def close_connection(conn:psycopg.AsyncConnection,cur:psycopg.AsyncCursor):
    await conn.commit()
    
    await cur.close()
    await conn.close()


#region Users

async def create_user(user:UserCreate)->None:
    conn,cur = await get_connection()
    hashed_password = get_hashed_text(user.password)
    await cur.execute('INSERT INTO USERS(USERNAME,FIRST_NAME,LAST_NAME,USER_ROLE,EMAIL,\
                HASHED_PASSWORD) VALUES(%s,%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING',\
                (user.username,user.first_name,user.last_name,user.user_role,user.email,\
                hashed_password))

    await close_connection(conn,cur)

async def user_email_exists(email:str)->bool:
    conn,cur = await get_connection()
    result = await(await cur.execute('SELECT 1 FROM USERS WHERE EMAIL=%s',(email,))).fetchone()
    await close_connection(conn,cur)
    return result is not None

async def username_exists(username:str)->bool:
    conn,cur = await get_connection()
    result = await(await cur.execute('SELECT 1 FROM USERS WHERE USERNAME=%s',(username,))).fetchone()
    await close_connection(conn,cur)
    return result is not None

async def get_user_hashed_password(username:str)->str:
    conn,cur = await get_connection()
    result = await(await cur.execute('SELECT HASHED_PASSWORD FROM USERS WHERE USERNAME=%s',(username,))).fetchone()
    await close_connection(conn,cur)
    if result is None:
        return None
    return result[0]

async def get_user_from_username(username:str)->UserRead:
    conn,cur = await get_connection()
    r = await(await cur.execute('SELECT USER_ID,USERNAME,FIRST_NAME,LAST_NAME,USER_ROLE,EMAIL \
            FROM USERS WHERE USERNAME=%s',(username,))).fetchone()
    await close_connection(conn,cur)
    if r is None:
        return None
    return UserRead(username=r[1],first_name=r[2],last_name=r[3],user_role=r[4],email=r[5],\
                    user_id=r[0])