import numpy as np
import cv2


def img2rgba(img_array, zona, w, h):
    alpha = 255
    if zona == 1:
        #  Sangre color rojo
        color = (255, 0, 0, alpha)
    elif zona == 2:
        #  Epicardio color verde
        color = (0, 255, 0, alpha)
    elif zona == 3:
        #  Endocardio color azul
        color = (0, 0, 255, alpha)
    else:
        color = (191, 21, 222, alpha)
    rgba = []

    # Resize img
    img_array = cv2.resize(np.array(img_array).astype(np.float), dsize=(w, h), interpolation=cv2.INTER_CUBIC)
    #  img_array es 2D
    for column in img_array:
        for item in column:
            if np.round(item) == 1:
                rgba.append(color)
            else:
                rgba.append((0, 0, 0, 0))
    rgba = np.array(rgba)
    rgba = np.array(rgba).reshape(len(img_array), len(img_array[0]), 4)
    return rgba
    pass
