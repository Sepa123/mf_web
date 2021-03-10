import numpy as np
from scipy import signal


def calculo_maximo(data, time):
    """
    Calculates the largest value of the incoming data, and returns the time and position at which this largest value is found.
    param data: Data in which the max is searched.
    param time: Array of time, corresponds to the time of each data entry
    return: max value, time at which it occurs, and the position of the array
    """
    input_data = np.array(data)
    pos_max = signal.find_peaks_cwt(input_data, np.arange(1, 150))[0]
    time_max = np.array(time)[pos_max]
    max_element = np.round(input_data[pos_max], 2)

    return max_element, time_max, pos_max


def calculo_pendiente(data, time):
    """
    Returns the initial slope, considering the rise time of the curve as the moment where the data rises from 10% of the maximum to 90% of the maximum.
    of maximum to 90% of maximum
    param data: Input data, X-axis
    param time: Time data, Y-axis
    return: value of slope, initial time, final time, initial value, final value
    """
    max_data, time_max, pos_max = calculo_maximo(data, time)
    por10 = max_data*0.1
    por90 = max_data*0.9
    first = 0
    last = 0
    for valor in np.array(data):
        if valor > por10 and first == 0:
            first = valor
            continue
        if valor < por90:
            last = valor
            continue
        else:
            break
    pos_first = np.where(np.array(data) == first)[0][0]
    pos_last = np.where(np.array(data) == last)[0][0]
    time_first = np.array(time).astype(np.float)[pos_first]
    time_last = np.array(time).astype(np.float)[pos_last]
    try:
        p = np.round((last-first)/(time_last-time_first), 2)
    except ZeroDivisionError:
        p = 0
    return p, time_first, time_last, first, last


def calculo_area_curva(data, time):
    """
    Given the time and data, calculate the area of the curve using Numpy trampz
    param data: Array with the values of the averages of the intensities
    param time: Array with the time values of the images
    :return: calculated area, rounded to the second decimal place
    """
    input_data = np.array(data)
    input_time = np.array(time)
    input_time = input_data.astype(np.float)
    area = np.round(np.trapz(input_data, input_time), 2)
    return area
