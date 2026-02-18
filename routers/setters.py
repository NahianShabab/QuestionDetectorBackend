from fastapi import APIRouter, Depends
from fastapi import UploadFile
from fastapi.responses import FileResponse
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
router = APIRouter(prefix='/setter',tags=['Question Setter'])

@router.post('/verify_question_image')
async def verify_question_image(img:UploadFile,config:dict=Depends(get_config),
                       cu:UserRead=Depends(check_current_user_role(['setter']))):
    print(img.size)
    max_image_size_mb = int(config['MAX_IMAGE_UPLOAD_SIZE_MB'])
    max_image_size_bytes = max_image_size_mb * 1024 * 1024
    if img.size is None:
        return create_message(False,'File size could not be verified')
    if img.size>max_image_size_bytes:
        return create_message(False,f'Maximum Size of Image is: {max_image_size_mb} megabytes')
    file_bytes = await img.read()
    np_arr = np.frombuffer(file_bytes,dtype=np.uint8)
    # print('NPARR is',np_arr)
    print(np_arr.shape)
    img_arr = cv2.imdecode(np_arr,cv2.IMREAD_COLOR)
    if img_arr is None:
        return create_message(False,f'Invalid image: {img.filename}')
    # cv2.imwrite('image.jpg',nparr)
    success,data = image_detector.detect_question_image(img_arr)
    if success:
        response = create_message(True,'')
        response['data'] = data
        return response
    else:
        return create_message(False,data)


@router.post('/upload_question_images')
async def upload_question_images(images:list[UploadFile],config:dict=Depends(get_config),
    cu:UserRead=Depends(check_current_user_role(['setter']))):
    # print(img.size)
    # print('Images Received')
    max_image_size_mb = int(config['MAX_IMAGE_UPLOAD_SIZE_MB'])
    max_image_size_bytes = max_image_size_mb * 1024 * 1024
    summary_dicts = []
    for img in images:
        summary_dict = {'filename':img.filename\
            ,'image':None,'success':True,'message':'Success','data':None}
        # print(img.filename)
        summary_dicts.append(summary_dict)
        if img.size is None:
            summary_dict.update(create_message(False,'File size could not be verified'))
            continue
        if img.size>max_image_size_bytes:
            summary_dict.update(create_message(False,f'Maximum Size of Image is: {max_image_size_mb} megabytes'))
            continue
        file_bytes = await img.read()
        np_arr = np.frombuffer(file_bytes,dtype=np.uint8)
        # print('NPARR is',np_arr)
        print(np_arr.shape)
        img_arr = cv2.imdecode(np_arr,cv2.IMREAD_COLOR)
        if img_arr is None:
            summary_dict.update(create_message(False,f'Invalid image: {img.filename}'))
            continue
        # summary_dict.update({'image':image_detector.convert_image_to_base64(img_arr)})
        # cv2.imwrite('image.jpg',nparr)
        success,data = image_detector.detect_question_image(img_arr,False)
        if success:
            summary_dict.update({'success':True})
            question,question_image_fragments,question_options = \
                await database.create_question(cu.user_id,len(data['question_images']),\
                    image_detector.NUMBER_OF_OPTIONS,image_detector.NUMBER_OF_BLANK_BOXES_PER_LINE)
            image_detector.save_question_image(question.question_id,data['extracted_image'])
            for question_image_fragment,question_image in zip(question_image_fragments,data['question_images']):
                image_detector.save_question_image_fragment\
                    (question.question_id,question_image_fragment.image_order,question_image)
            for question_option,option_images in zip(question_options,data['option_images_list']):
                for i in range(1,len(option_images)+1,1):
                    image_detector.save_option_image_fragment\
                    (question.question_id,question_option.option_id,i,option_images[i-1])
                    
        else:
            summary_dict.update(create_message(False,data))
    return summary_dicts
    

@router.get('/image')
async def get_image():
    img = cv2.imread('extracted.png')
    success,buffer = cv2.imencode('.png',img)
    img_str = base64.b64encode(buffer.tobytes()).decode('ascii')
    
    return {'img':img_str}


@router.get('/questions')
async def get_setter_questions(cu:UserRead=Depends(check_current_user_role(['setter']))):
    questions = await database.get_all_questions_from_setter(cu.user_id)
    return questions
    pass


@router.get('/question-form')
async def get_question_form(cu:UserRead=Depends(check_current_user_role(['setter']))):
    return FileResponse('question_form.png')


@router.get('/question-image')
async def get_question_image(question_id:int,cu:UserRead=Depends(check_current_user_role(['setter']))):
    question = await database.get_question(question_id)
    if question is None:
        return None
    if question.submitted_by!=cu.user_id:
        return None
    return image_detector.load_question_image(question_id)

@router.delete('/delete-questions')
async def delete_questions(question_ids:list[int],cu:UserRead=Depends(check_current_user_role(['setter']))):
    print('These are the question ids you want deleted: ',question_ids)
    for qid in question_ids:
        question = await database.get_question(qid)
        if question is None or question.submitted_by!=cu.user_id or question.is_confirmed:
            continue
        await database.delete_question(qid)
        image_detector.delete_question_image(qid)
    return 'Questions Deleted!'

@router.patch('/confirm-questions')
async def confirm_questions(question_ids:list[int],cu:UserRead=Depends(check_current_user_role(['setter']))):
    candidate_ids:list[int]= []
    for qid in question_ids:
        question = await database.get_question(qid)
        if question is None or question.submitted_by!=cu.user_id or question.is_confirmed:
            continue
        is_completely_transcribed = await database.question_has_all_images_transcribed(qid)
        if is_completely_transcribed:
            candidate_ids.append(qid)
    await database.confirm_questions(candidate_ids)
    return f'Confirmed {len(candidate_ids)} Questions!'

