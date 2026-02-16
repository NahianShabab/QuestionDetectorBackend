from fastapi import APIRouter, Depends
from fastapi import UploadFile
from fastapi import responses
import database
import base64
import numpy as np
import cv2
from security import text_and_hash_match,get_jwt
from models import UserRead
from authentication import get_current_user,check_current_user_role
from utils import image_detector
from config import get_config
from utils.response import create_message
import random
router = APIRouter(prefix='/composer',tags=['Question Composer'])

@router.get('/next-image')
async def get_next_image(cu:UserRead=Depends(check_current_user_role(['composer']))):
    qimg_id = await database.get_next_question_image_fragment_for_composer(cu.user_id)
    qoimg_id = await database.get_next_question_option_image_fragment_for_composer(cu.user_id)
    image_type=''
    img = None
    image_id=None
    if qimg_id is None and qoimg_id is None:
        return None
    elif qoimg_id is None and qimg_id is not None:
        image_type='question'
        qif = await database.get_question_image_fragment(qimg_id)
        img = image_detector.load_question_image_fragment(qif.question_id,qif.image_order)
        image_id=qimg_id
    else:
        image_type='option'
        qoif = await database.get_question_option_image_fragment(qoimg_id)
        img = image_detector.load_option_image_fragment(qoif.question_id,qoif.option_id,qoif.image_order)
        image_id=qoimg_id
    return {'image_type':image_type,'image':img,'image_id':image_id}

@router.put('/transcribe-image')
async def transcribe_image(image_id:int,image_type:str,transcript:str,
    cu:UserRead=Depends(check_current_user_role(['composer']))):
    print('Transcript is',transcript,' Length is ',len(transcript))
    if image_type=='question':
        qif = await database.get_question_image_fragment(image_id)
        question = await database.get_question(qif.question_id)
        if question.is_confirmed:
            return create_message(False,'Cannot modify confirmed question')
        if qif is None:
            return create_message(False,'Cannot find the image')
        if qif.transcripted_by is None or qif.transcript is not None or qif.transcripted_by!=cu.user_id:
            return create_message(False,'unauthorized')
        await database.add_transcript_to_question_image(image_id,transcript.strip())
        return create_message(True,'Done!')
    elif image_type=='option':
        qoif = await database.get_question_option_image_fragment(image_id)
        question = await database.get_question(qoif.question_id)
        if question.is_confirmed:
            return create_message(False,'Cannot modify confirmed question')
        if qoif is None:
            return create_message(False,'Cannot find the image')
        if qoif.transcripted_by is None or qoif.transcript is not None or qoif.transcripted_by!=cu.user_id:
            return create_message(False,'unauthorized')
        await database.add_transcript_to_question_option_image(image_id,transcript.strip())
        return create_message(True,'Done!')
    
    return create_message(False,'invalid type!')
        

