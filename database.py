
import dotenv
import psycopg
import asyncio

from config import get_config
from models import UserCreate,UserRead,UserDatabase,Question,QuestionImageFragment,\
    QuestionOption
from security import get_hashed_text
import sys
import numpy as np

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
    
#endregion



#region Question

async def create_question(user_id:int,number_of_question_image_fragments:int,number_of_options:int,
                          number_of_option_image_fragments:int):
    conn,cur = await get_connection()

    question_result = await(await cur.execute('INSERT INTO SUBMITTED_QUESTION(SUBMITTED_BY,IS_CONFIRMED) \
        VALUES(%s,%s) returning QUESTION_ID',(user_id,False))).fetchone()
    if question_result is None:
        return None
    
    question = Question(question_id=question_result[0],submitted_by=user_id,is_confirmed=False)
    question_image_fragments_params =\
    [(i,question.question_id) for i in range(1,number_of_question_image_fragments+1,1)]
    await cur.executemany(
        'INSERT INTO QUESTION_IMAGE_FRAGMENT(IMAGE_ORDER,QUESTION_ID) VALUES\
        (%s,%s) RETURNING IMAGE_ID,IMAGE_ORDER,QUESTION_ID',question_image_fragments_params
    )
    question_image_fragments_result = await (await cur.execute('\
        SELECT IMAGE_ID,IMAGE_ORDER,QUESTION_ID,TRANSCRIPTED_BY,TRANSCRIPT\
        FROM QUESTION_IMAGE_FRAGMENT WHERE QUESTION_ID=%s',\
            (question.question_id,))).fetchall()
    question_image_fragments = [QuestionImageFragment(image_id=r[0],image_order=r[1],\
        question_id=r[2],transcripted_by=r[3],transcript=r[4]) for r in question_image_fragments_result]
    
    option_params = [(i,True if i==1 else False,
        question.question_id) for i in range(1,number_of_options+1,1)]
    await cur.executemany('INSERT INTO QUESTION_OPTION (OPTION_ID,IS_CORRECT,\
    QUESTION_ID) VALUES(%s,%s,%s)',option_params)
    
    option_result = await (await cur.execute('SELECT OPTION_ID,IS_CORRECT,QUESTION_ID FROM\
        QUESTION_OPTION WHERE QUESTION_ID=%s',(question.question_id,))).fetchall()
    question_options = [QuestionOption(option_id=r[0],is_correct=r[1],\
        question_id=r[2]) for r in option_result]
    question_option_image_fragments_params = []
    for o in question_options:
        for i in range(1,number_of_option_image_fragments+1,1):
            question_option_image_fragments_params.append((i,question.question_id,o.option_id))
    await cur.executemany('INSERT INTO QUESTION_OPTION_IMAGE_FRAGMENT(IMAGE_ORDER,QUESTION_ID,\
        OPTION_ID) VALUES(%s,%s,%s)',question_option_image_fragments_params)
    await close_connection(conn,cur)
    
    return question,question_image_fragments,question_options


async def get_all_questions_from_setter(user_id:int):
    conn,cur = await get_connection()
    questions = await (await cur.execute('''
    SELECT json_build_object(
    'submitted', COALESCE(
        (
        SELECT json_agg(row_to_json(sq))
        FROM submitted_question sq
        WHERE sq.submitted_by = %(user_id)s AND
        (
        exists (select 1 from question_image_fragment qif where qif.question_id = sq.question_id and transcript is null) or 
        exists (select 1 from question_option_image_fragment qoif where qoif.question_id = sq.question_id and transcript is null)
        )
        ),
        '[]'::json
    ),
    'transcribed', COALESCE(
        (
        SELECT json_agg(json_build_object('question_id',sq.question_id,'question_transcription',
            (select string_agg(transcript,' ') from question_image_fragment qif where qif.question_id=sq.question_id),
            'options',(select json_agg(json_build_object('option_id',option_id,'is_correct',is_correct,
            'option_transcription',(select string_agg(qoif.transcript,' ') from question_option_image_fragment qoif where qoif.question_id=sq.question_id
            )) order by qo.option_id) from question_option qo where qo.question_id = sq.question_id
            )
            )
        
        )
        FROM submitted_question sq
        WHERE sq.submitted_by = %(user_id)s 
        AND
        (
        not exists (select 1 from question_image_fragment qif where qif.question_id = sq.question_id and transcript is null) and
        not exists (select 1 from question_option_image_fragment qoif where qoif.question_id = sq.question_id and transcript is null)
        )
        ),
        '[]'::json
    ),
    'confirmed', COALESCE(
        (
        SELECT json_agg(json_build_object('question_id',sq.question_id,'question_transcription',
            (select string_agg(transcript,' ') from question_image_fragment qif where qif.question_id=sq.question_id),
            'options',(select json_agg(json_build_object('option_id',option_id,'is_correct',is_correct,
            'option_transcription',(select string_agg(qoif.transcript,' ') from question_option_image_fragment qoif where qoif.question_id=sq.question_id
            )) order by qo.option_id) from question_option qo where qo.question_id = sq.question_id
            )
            )
        
        )
        FROM submitted_question sq
        WHERE sq.submitted_by = %(user_id)s 
        and sq.is_confirmed=true
        ),
        '[]'::json
    )
    ) AS user_questions;              
    ''',{'user_id':user_id})).fetchone()
    await close_connection(conn,cur)
    return questions[0]
    pass


async def get_question(question_id:int)->Question:
    conn,cur = await get_connection()
    result = await(await cur.execute('''SELECT 
        QUESTION_ID,IS_CONFIRMED,SUBMITTED_BY FROM SUBMITTED_QUESTION 
        WHERE QUESTION_ID=%s''',(question_id,))).fetchone()
    await close_connection(conn,cur)
    if result is None:
        return None
    return Question(question_id=question_id,submitted_by=result[2],is_confirmed=result[1])

#endregion