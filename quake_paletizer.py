import cv2
import numpy as np

import os

palette = cv2.imread(r'quake1\quake-1x.png').squeeze()



def find_nearest(palette,color):
    min_dist = np.inf
    nearest_color = None
    for c in palette:
        dist = np.linalg.norm(color-c)
        if dist<min_dist:
            nearest_color=c
            min_dist = dist
    return nearest_color
count = 0
filedir = r'quake1'
for file in os.listdir(filedir):
    img = cv2.imread(os.path.join(filedir,file))
    converted_image = img.copy()  
    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            nearest_color = find_nearest(palette,img[i,j,:])
            converted_image[i,j,:] = nearest_color

    cv2.imwrite(os.path.join(filedir,f'{count}.png'),converted_image)
    count+=1