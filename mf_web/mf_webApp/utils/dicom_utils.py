import numpy as np


def refactor_dicom_file(dicom_array, ww, wl):
    """
    Ingresada la imagen, procesa los límites según los valores de ww y wl, para escalar el dicom_array a
    valores de escala de grises de 8 BITS
    :param dicom_array: array de la imagen con los valores invariantes
    :param ww: Window Width
    :param wl: Window Level
    :return: Imagen en escala de grises
    """
    #  Intervalos de escala de grises
    min_val = 0
    max_val = 255

    #  Estandar DICOM, ww >= 1
    ww = max(1, ww)

    #  Formato float64 para manejo de imagenes
    wl, ww = np.float64(wl), np.float64(ww)
    interval = np.float(max_val) - min_val
    input_arr = dicom_array.astype(np.float64)

    minval = wl - 0.5 - (ww - 1.0) / 2.0
    maxval = wl - 0.5 + (ww - 1.0) / 2.0

    min_mask = (minval >= input_arr)
    to_scale = (input_arr > minval) & (input_arr < maxval)
    max_mask = (input_arr >= maxval)

    if min_mask.any():
        input_arr[min_mask] = min_val
    if to_scale.any():
        input_arr[to_scale] = ((input_arr[to_scale] - (wl - 0.5)) /
                               (ww - 1.0) + 0.5) * interval + min_val
    if max_mask.any():
        input_arr[max_mask] = max_val

    return np.rint(input_arr).astype(np.uint8)
