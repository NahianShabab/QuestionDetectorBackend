import cv2
import numpy as np
import os

palette = cv2.imread(r'quake1\quake-1x.png').squeeze()

def find_nearest(palette, color):
    distances = np.linalg.norm(palette - color, axis=1)
    return palette[np.argmin(distances)]

def floyd_steinberg_dither(img, palette):
    img = img.astype(float)
    h, w = img.shape[:2]
    
    for y in range(h):
        for x in range(w):
            old_pixel = img[y, x].copy()
            new_pixel = find_nearest(palette, old_pixel)
            img[y, x] = new_pixel
            error = old_pixel - new_pixel
            
            if x + 1 < w:
                img[y, x + 1] += error * 7/16
            if y + 1 < h:
                if x > 0:
                    img[y + 1, x - 1] += error * 3/16
                img[y + 1, x] += error * 5/16
                if x + 1 < w:
                    img[y + 1, x + 1] += error * 1/16
    
    return np.clip(img, 0, 255).astype(np.uint8)

filedir = r'quake1'
for count, file in enumerate(os.listdir(filedir)):
    if not file.endswith(('.png', '.jpg', '.jpeg')):
        continue
    img = cv2.imread(os.path.join(filedir, file))
    converted_image = floyd_steinberg_dither(img, palette)
    cv2.imwrite(os.path.join(filedir, f'{count}_converted.png'), converted_image)