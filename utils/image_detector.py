import cv2
import numpy as np
import random
from PIL import ImageDraw,Image
from utils.response import create_message
import base64
from pathlib import Path


# Directories
QUESTION_IMAGES_DIR = Path('question_images')
QUESTION_IMAGE_FRAGMENTS_DIR = Path('question_fragmented_images')
OPTION_FRAGMENTS_DIR = Path('question_option_fragmented_images')

QUESTION_IMAGES_DIR.mkdir(exist_ok=True)
QUESTION_IMAGE_FRAGMENTS_DIR.mkdir(exist_ok=True)
OPTION_FRAGMENTS_DIR.mkdir(exist_ok=True)

def save_question_image(question_id:int,img:np.ndarray):
    img_path = QUESTION_IMAGES_DIR / f'{question_id}.png'
    cv2.imwrite(str(img_path),img)
    
def load_question_image(question_id:int):
    img_path = QUESTION_IMAGES_DIR / f'{question_id}.png'
    img = cv2.imread(str(img_path))
    if img is None:
        return None
    return convert_image_to_base64(img)

def delete_question_image(question_id:int):
    img_path = QUESTION_IMAGES_DIR / f'{question_id}.png'
    img_path.unlink(missing_ok=True)

def save_question_image_fragment(question_id:int,image_order,img:np.ndarray):
    img_path = QUESTION_IMAGE_FRAGMENTS_DIR / f'question_{question_id}_{image_order}.png'
    cv2.imwrite(str(img_path),img)

def load_question_image_fragment(question_id:int,image_order):
    img_path = QUESTION_IMAGE_FRAGMENTS_DIR / f'question_{question_id}_{image_order}.png'
    img = cv2.imread(str(img_path))
    if img is None:
        return None
    return convert_image_to_base64(img)

def save_option_image_fragment(question_id:int,option_id:int,image_order:int,img:np.ndarray):
    img_path = OPTION_FRAGMENTS_DIR / f'question_{question_id}_option_{option_id}_{image_order}.png'
    cv2.imwrite(str(img_path),img)

def load_option_image_fragment(question_id:int,option_id:int,image_order):
    img_path = OPTION_FRAGMENTS_DIR / f'question_{question_id}_option_{option_id}_{image_order}.png'
    img = cv2.imread(str(img_path))
    if img is None:
        return None
    return convert_image_to_base64(img)

# Question Paper Processing
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

def create_question_form(file_path: str):
    img = np.ones((A4_HEIGHT_PX, A4_WIDTH_PX, 3), dtype=np.uint8) * 255

    # ---------- Draw ArUco markers ----------
    for marker_id, (y, x) in marker_positions.items():
        marker = cv2.aruco.generateImageMarker(
            ARUCO_DICT, marker_id, A_MARKER_SIZE_PX
        )
        img[y:y+A_MARKER_SIZE_PX, x:x+A_MARKER_SIZE_PX] = cv2.cvtColor(
            marker, cv2.COLOR_GRAY2BGR
        )

    font = cv2.FONT_HERSHEY_SIMPLEX
    thickness = 3

    # ---------- Question label ----------
    # cv2.putText(
    #     img,
    #     f"Write the content of the question in the following {NUMBER_OF_LINES_FOR_A_QUESTION} Lines. Only put 1-3 words in each box",
    #     (MARGIN_SIZE_PX+20, question_1_textbox_start_y+40),
    #     font,
    #     1.2,
    #     (0, 0, 0),
    #     thickness
    # )

    # ---------- Question text box ----------
    cv2.rectangle(
        img,
        (question_1_textbox_start_x, question_1_textbox_start_y),
        (QUESTION_1_TEXTBOX_END_X, QUESTION_1_TEXTBOX_END_Y),
        (0, 0, 0),
        2
    )

    # ---------- Question blank boxes ----------
    for bb in question_1_blank_boxes:
        cv2.rectangle(img, bb[0], bb[1], (0, 0, 0), 2)

    # ---------- Options header ----------
    # cv2.putText(
    #     img,
    #     "OPTIONS (fill text in boxes)",
    #     (MARGIN_SIZE_PX, option_text_box_start_y + 12),
    #     font,
    #     0.9,
    #     (0, 0, 0),
    #     thickness
    # )

    cv2.rectangle(
        img,
        (option_text_box_start_x, option_text_box_start_y),
        (option_text_box_end_x, option_text_box_end_y),
        (0, 0, 0),
        2
    )

    # ---------- Option rows ----------
    for i in range(NUMBER_OF_OPTIONS):
        option_label = 'OPTION: '+ chr(ord("1") + i)

        row_y = option_blank_box_start_y + i * (BLANK_BOX_HEIGHT_PX + MED_DIST_HEIGHT_PX)

        # Option label (A, B, C, D)
        cv2.putText(
            img,
            f"{option_label}",
            (MARGIN_SIZE_PX, row_y -20),
            font,
            1.0,
            (0, 0, 0),
            thickness
        )

        # Mark FIRST option as correct (LEFT SIDE, CLEAR)
        # if i == 0:
        #     cv2.putText(
        #         img,
        #         "CORRECT →",
        #         (MARGIN_SIZE_PX + 40, row_y + BLANK_BOX_HEIGHT_PX - 5),
        #         font,
        #         0.9,
        #         (0, 120, 0),
        #         thickness
        #     )

        # Draw option blank boxes
        for j in range(NUMBER_OF_BLANK_BOXES_PER_LINE):
            idx = i * NUMBER_OF_BLANK_BOXES_PER_LINE + j
            bb = option_blank_boxes[idx]
            cv2.rectangle(img, bb[0], bb[1], (0, 0, 0), 2)

    cv2.imwrite(file_path, img)




def detect_question_image(original_img:np.ndarray,convert_to_base64:bool=True):

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
        question_images.append(convert_image_to_base64(cropped_box) if convert_to_base64 else cropped_box)
    option_images = [[] for i in range(NUMBER_OF_OPTIONS)]
    
    for i,bb in enumerate(option_blank_boxes):
        cropped_box = extracted[bb[0][1]:bb[1][1],bb[0][0]:bb[1][0]]
        # cv2.imwrite(f'question_part_{i+1}.png',cropped_box)
        option_images[i//NUMBER_OF_BLANK_BOXES_PER_LINE].append(convert_image_to_base64(cropped_box) if convert_to_base64 else cropped_box)
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
    # cv2.imwrite('extracted.png', extracted)
    extracted = convert_image_to_base64(extracted) if convert_to_base64 else extracted
    # print(extracted.shape)
    # Save the extracted document
    
    print('Saved the Image')
    return True,{'question_images':question_images,'extracted_image':extracted,'option_images_list':option_images}
    # for i in [8,9,10]:
    #     bb = question_1_blank_boxes[i]
    #     sliced_image = extracted[bb[0][1]:bb[1][1],bb[0][0]:bb[1][0]]
    #     cv2.imwrite(f'sliced_{i}.png',sliced_image)


def convert_image_to_base64(img:np.ndarray)->str:
    success,buffer = cv2.imencode('.png',img)
    img_str = base64.b64encode(buffer.tobytes()).decode('ascii')
    return img_str
    
if __name__=="__main__":
    pass
    # create_question_form('question_form.png')