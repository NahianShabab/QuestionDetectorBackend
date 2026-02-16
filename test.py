
import base64
import cv2
import numpy as np

text = 'Ma'

encoded_bytes = text.encode()

encoded_bytes_b64 = base64.b64encode(encoded_bytes)

print(encoded_bytes_b64.decode('ascii'))

img = cv2.imread('')
success,buffer = cv2.imencode('.png',img)
img_bytes = base64.b64encode(buffer.to_bytes()).decode('ascii')