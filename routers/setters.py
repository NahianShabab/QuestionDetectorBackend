from fastapi import APIRouter, Depends
from fastapi import UploadFile
from fastapi import responses
import database
import base64
import numpy as np
import cv2
from security import text_and_hash_match,get_jwt
from authentication import get_current_user,check_current_user_role
from utils import image_detector
from config import get_config
from utils.response import create_message
router = APIRouter(prefix='/setter',tags=['Question Setter'])

@router.post('/verify_image')
async def upload_image(img:UploadFile,config:dict=Depends(get_config)):
    print(img.size)
    max_image_size_mb = int(config['MAX_IMAGE_UPLOAD_SIZE_MB'])
    max_image_size_bytes = max_image_size_mb * 1024 * 1024
    if img.size is None:
        return create_message(False,'File size could not be verified')
    if img.size>max_image_size_bytes:
        return create_message(False,f'Maximum Size of Image is: {max_image_size_mb} megabytes')
    file_bytes = await img.read()
    np_arr = np.frombuffer(file_bytes,dtype=np.uint8)
    print('NPARR is',np_arr)
    print(np_arr.shape)
    img_arr = cv2.imdecode(np_arr,cv2.IMREAD_COLOR)
    if img_arr is None:
        return create_message(False,f'Invalid image: {img.filename}')
    # cv2.imwrite('image.jpg',nparr)
    success,data = image_detector.detect_and_save_image(img_arr)
    if success:
        response = create_message(True,'')
        response['data'] = data
        return response
    else:
        return create_message(False,data)
    

@router.get('/image')
async def get_image():
    img = cv2.imread('extracted.png')
    success,buffer = cv2.imencode('.png',img)
    img_str = base64.b64encode(buffer.tobytes()).decode('ascii')
    
    return {'img':img_str} 