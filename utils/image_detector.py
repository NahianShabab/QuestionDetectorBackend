import cv2
import numpy as np
import random
from PIL import ImageDraw,Image
from utils.response import create_message
import base64

DPI = 300
INCH_TO_MM = 25.4 # 1 inch = what mm 

def mm_to_pixel(mm:float)->int:
    return int(mm * DPI / INCH_TO_MM)

A4_WIDTH_MM = 210
A4_HEIGHT_MM = 297




A4_WIDTH_PX = mm_to_pixel  (A4_WIDTH_MM)  # ~2480 pixels
A4_HEIGHT_PX = mm_to_pixel (A4_HEIGHT_MM)  # ~3508 pixels

MARGIN_SIZE_MM= 5
MARGIN_SIZE_PX = mm_to_pixel(MARGIN_SIZE_MM)

A_MARKER_SIZE_MM = 20
A_MARKER_SIZE_PX = mm_to_pixel(A_MARKER_SIZE_MM)

ARUCO_DICT_ID = cv2.aruco.DICT_6X6_50
# print(ARUCO_DICT_ID)

ARUCO_DICT = cv2.aruco.getPredefinedDictionary(ARUCO_DICT_ID)

marker_ids = [0,1,2,3]

marker_positions = {
    0: (MARGIN_SIZE_PX,MARGIN_SIZE_PX),
    1: (MARGIN_SIZE_PX,A4_WIDTH_PX-MARGIN_SIZE_PX-A_MARKER_SIZE_PX),
    2: (A4_HEIGHT_PX-MARGIN_SIZE_PX-A_MARKER_SIZE_PX,MARGIN_SIZE_PX),
    3: (A4_HEIGHT_PX-MARGIN_SIZE_PX-A_MARKER_SIZE_PX,A4_WIDTH_PX-MARGIN_SIZE_PX-A_MARKER_SIZE_PX)
}
SHORT_DIST_WIDTH_MM = 5
SHORT_DIST_HEIGHT_MM = 5

SHORT_DIST_WIDTH_PX = mm_to_pixel(SHORT_DIST_WIDTH_MM)
SHORT_DIST_HEIGHT_PX = mm_to_pixel(SHORT_DIST_HEIGHT_MM)

MED_DIST_HEIGHT_MM = 10
MED_DIST_HEIGHT_PX = mm_to_pixel(MED_DIST_HEIGHT_MM)

LONG_DIST_WIDTH_MM = 50
LONG_DIST_HEIGHT_MM = 50

LONG_DIST_WIDTH_PX = mm_to_pixel(LONG_DIST_WIDTH_MM)
LONG_DIST_HEIGHT_PX = mm_to_pixel(LONG_DIST_HEIGHT_MM)

TEXT_BOX_WIDTH_MM = 200
TEXT_BOX_WIDTH_PX = mm_to_pixel(TEXT_BOX_WIDTH_MM)

TEXT_BOX_HEIGHT_MM = 10
TEXT_BOX_HEIGHT_PX = mm_to_pixel(TEXT_BOX_HEIGHT_MM)

question_1_textbox_start_y = MARGIN_SIZE_PX + A_MARKER_SIZE_PX + SHORT_DIST_HEIGHT_PX
question_1_textbox_start_x = MARGIN_SIZE_PX

QUESTION_1_TEXTBOX_END_X = question_1_textbox_start_x + TEXT_BOX_WIDTH_PX
QUESTION_1_TEXTBOX_END_Y = question_1_textbox_start_y + TEXT_BOX_HEIGHT_PX

BLANK_BOX_WIDTH_MM = 45
BLANK_BOX_HEIGHT_MM = 15
NUMBER_OF_BLANK_BOXES_PER_LINE = 4
NUMBER_OF_LINES_FOR_A_QUESTION = 5

BLANK_BOX_WIDTH_PX = mm_to_pixel(BLANK_BOX_WIDTH_MM)
BLANK_BOX_HEIGHT_PX = mm_to_pixel(BLANK_BOX_HEIGHT_MM)

# each entry is a rect coord
question_1_blank_box_start_y = QUESTION_1_TEXTBOX_END_Y + SHORT_DIST_HEIGHT_PX
question_1_blank_box_start_x = 2*  MARGIN_SIZE_PX
question_1_blank_boxes = []

for i in range(NUMBER_OF_LINES_FOR_A_QUESTION):
    for j in range(NUMBER_OF_BLANK_BOXES_PER_LINE):
        blank_box_start_x = question_1_blank_box_start_x+ j * (BLANK_BOX_WIDTH_PX+SHORT_DIST_WIDTH_PX)
        blank_box_start_y = question_1_blank_box_start_y+ i * (BLANK_BOX_HEIGHT_PX+SHORT_DIST_HEIGHT_PX)

        blank_box_end_x = blank_box_start_x+ BLANK_BOX_WIDTH_PX
        blank_box_end_y = blank_box_start_y+ BLANK_BOX_HEIGHT_PX
        question_1_blank_boxes.append(
            [
                (blank_box_start_x,blank_box_start_y),
                (blank_box_end_x,blank_box_end_y)
            ]
        )

option_text_box_start_x = MARGIN_SIZE_PX
option_text_box_start_y = question_1_blank_box_start_y + NUMBER_OF_LINES_FOR_A_QUESTION * BLANK_BOX_HEIGHT_PX+\
                        (NUMBER_OF_LINES_FOR_A_QUESTION-1) * SHORT_DIST_HEIGHT_PX + SHORT_DIST_HEIGHT_PX
option_text_box_end_x = option_text_box_start_x + TEXT_BOX_WIDTH_PX
option_text_box_end_y = option_text_box_start_y + TEXT_BOX_HEIGHT_PX

option_blank_box_start_x = 2* MARGIN_SIZE_PX
option_blank_box_start_y = option_text_box_end_y + MED_DIST_HEIGHT_PX

option_blank_boxes = []
# option_label_texts = []
NUMBER_OF_OPTIONS = 4
for i in range(NUMBER_OF_OPTIONS):
    for j in range(NUMBER_OF_BLANK_BOXES_PER_LINE):
        blank_box_start_x = option_blank_box_start_x+ j * (BLANK_BOX_WIDTH_PX+SHORT_DIST_WIDTH_PX)
        blank_box_start_y = option_blank_box_start_y+ i * (BLANK_BOX_HEIGHT_PX+MED_DIST_HEIGHT_PX)

        blank_box_end_x = blank_box_start_x+ BLANK_BOX_WIDTH_PX
        blank_box_end_y = blank_box_start_y+ BLANK_BOX_HEIGHT_PX
        option_blank_boxes.append(
            [
                (blank_box_start_x,blank_box_start_y),
                (blank_box_end_x,blank_box_end_y)
            ]
        )
    # option_label_text_x = MARGIN_SIZE_PX
    # option_label_text_y = option_blank_box_start_y+ i * (BLANK_BOX_HEIGHT_PX+MED_DIST_HEIGHT_PX)
    # option_label_texts.append(
    #     (chr(ord('A')+i),[option_label_text_x,option_label_text_y])
    # )


def detect_and_save_image(original_img:np.ndarray):

    image = cv2.cvtColor(original_img,cv2.COLOR_BGR2GRAY)
    print('Thresholding Image...')
    _,image = cv2.threshold(image,127,255,cv2.THRESH_BINARY)
    print('Applied Threshold')
    parameters = cv2.aruco.DetectorParameters()
    detector = cv2.aruco.ArucoDetector(ARUCO_DICT,parameters)

    print('Detecting Markers')
    corners,ids,rejected = detector.detectMarkers(image)
    if(ids is None or ids.size!=4):
        print('4 markers not detected, returning...')
        return (False,'Not all 4 markers are detected')
    ids = ids.flatten()
    print(f'{ids.size} Markers detected')
    # print(ids)
    marker_positions_centered ={
        0: (MARGIN_SIZE_PX+A_MARKER_SIZE_PX//2,MARGIN_SIZE_PX+A_MARKER_SIZE_PX//2),
        1: (MARGIN_SIZE_PX+A_MARKER_SIZE_PX//2,A4_WIDTH_PX-MARGIN_SIZE_PX-A_MARKER_SIZE_PX+A_MARKER_SIZE_PX//2),
        2: (A4_HEIGHT_PX-MARGIN_SIZE_PX-A_MARKER_SIZE_PX+A_MARKER_SIZE_PX//2,MARGIN_SIZE_PX+A_MARKER_SIZE_PX//2),
        3: (A4_HEIGHT_PX-MARGIN_SIZE_PX-A_MARKER_SIZE_PX+A_MARKER_SIZE_PX//2,A4_WIDTH_PX-MARGIN_SIZE_PX-A_MARKER_SIZE_PX+A_MARKER_SIZE_PX//2)
    }
    source_points = []
    dest_points = []
    for index,id in enumerate(ids):
        marker_position = marker_positions_centered[id]
        dest_points.append(
            [marker_position[1],marker_position[0]]
        )
        corner = corners[index].squeeze()
        print(corner.shape)
        source_points.append(
            # centering to cancel the noise
            np.mean(corner,axis=0)
        )
    source_points = np.array(source_points,dtype=np.float32)
    dest_points= np.array(dest_points,dtype=np.float32)
    # print(source_points)
    # print(dest_points)
    matrix = cv2.getPerspectiveTransform(source_points, dest_points)


    # Apply perspective transformation
    extracted = cv2.warpPerspective(original_img, matrix, (A4_WIDTH_PX, A4_HEIGHT_PX))
    question_images = []
    
    for i,bb in enumerate(question_1_blank_boxes):
        cropped_box = extracted[bb[0][1]:bb[1][1],bb[0][0]:bb[1][0]]
        # cv2.imwrite(f'question_part_{i+1}.png',cropped_box)
        question_images.append(convert_image_to_base64(cropped_box))
    option_images = []
    for i,bb in enumerate(option_blank_boxes):
        cropped_box = extracted[bb[0][1]:bb[1][1],bb[0][0]:bb[1][0]]
        # cv2.imwrite(f'question_part_{i+1}.png',cropped_box)
        option_images.append(convert_image_to_base64(cropped_box))
    print('Extracted the Image')
    # output_path = 'extracted_image.png'
    extracted = cv2.cvtColor(extracted,cv2.COLOR_BGR2RGB)
    extracted = Image.fromarray(extracted)
    draw = ImageDraw.ImageDraw(extracted)

    for bb in question_1_blank_boxes:
        draw.rectangle(bb,outline=(0,255,0),width=3)
    

    for i,bb in enumerate(option_blank_boxes):
      outline_color = (0,0,255) if i<4 else (0,255,255)
      draw.rectangle(bb,outline=outline_color,width=3)  

    extracted = np.array(extracted)
    extracted = cv2.cvtColor(extracted,cv2.COLOR_RGB2BGR)
    cv2.imwrite('extracted.png', extracted)
    extracted = convert_image_to_base64(extracted)
    # print(extracted.shape)
    # Save the extracted document
    
    print('Saved the Image')
    return True,{'question_images':question_images,'extracted_image':extracted,'option_images':option_images}
    # for i in [8,9,10]:
    #     bb = question_1_blank_boxes[i]
    #     sliced_image = extracted[bb[0][1]:bb[1][1],bb[0][0]:bb[1][0]]
    #     cv2.imwrite(f'sliced_{i}.png',sliced_image)


def convert_image_to_base64(img:np.ndarray)->str:
    success,buffer = cv2.imencode('.png',img)
    img_str = base64.b64encode(buffer.tobytes()).decode('ascii')
    return img_str
    
