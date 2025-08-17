from fastapi import APIRouter, Depends
from fastapi import UploadFile
import database
import numpy as np
import cv2
from security import text_and_hash_match,get_jwt
from authentication import get_current_user,check_current_user_role
from utils import image_detector
router = APIRouter(prefix='/setter',tags=['Question Setter'])

@router.post('/image')
async def upload_image(img:UploadFile):
    file_bytes = await img.read()
    nparr = np.frombuffer(file_bytes,dtype=np.uint8)
    print(nparr.shape)
    nparr = cv2.imdecode(nparr,cv2.IMREAD_COLOR)
    print(nparr.shape)
    # cv2.imwrite('image.jpg',nparr)
    image_detector.detect_and_save_image(nparr)
