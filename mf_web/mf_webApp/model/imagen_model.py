import cv2
import numpy as np

import matplotlib.pyplot as plt


class Imagen:

    def __init__(self, image_size, view_size, wl, ww, mouse_px, mouse_mm,
                 zoom, angle, image_position, compression, thickness, location,
                 mri, field_strenght, image_acq_time,
                 pixel_array):

        self.image_size = image_size
        self.view_size = view_size
        self.wl = wl
        self.ww = ww
        self.mouse_px = mouse_px
        self.mouse_mm = mouse_mm

        self.zoom = zoom
        self.angle = angle
        self.image_position = image_position
        self.compression = compression
        self.thickness = thickness
        self.location = location

        self.mri = mri
        self.field_strenght = field_strenght
        self.image_acq_time = image_acq_time

        self.pixel_array = pixel_array
        self.predict = []

        self.border = []

        self.radio = []
        self.endocardio = []
        self.epicardio = []
        self.sangre = []

        self.m = {'I': 0.0, 'II': 0.0, 'III': 0.0, 'IV': 0.0, 'init': ''}
        self.end_part = {"1": [], "2": [], "3": [], "4": []}
        self.epi_part = {"1": [], "2": [], "3": [], "4": []}
        self.san_part = {"1": [], "2": [], "3": [], "4": []}

    def arreglar_pad(self):
        imagen = self.pixel_array
        predict = self.predict
        epicardio = self.epicardio
        endocardio = self.endocardio
        sangre = self.sangre
        (x, y) = imagen.shape
        (xp, yp) = predict.shape
        qx = int((xp - x) / 2)
        qy = int((yp - y) / 2)
        self.predict = predict[qx:xp - qx, qy:yp - qy]
        self.epicardio = np.array(epicardio)[qx:xp - qx, qy:yp - qy]
        self.endocardio = np.array(endocardio)[qx:xp - qx, qy:yp - qy]
        self.sangre = np.array(sangre)[qx:xp - qx, qy:yp - qy]
        self.detectar_centro()

    def separacion_miocardio(self):
        """
        Detects predict edge, its center and separates the myocardium between epicardium and endocardium.
        :return:
        """
        self.deteccion_bordes()
        self.detectar_separacion()
        pass

    def deteccion_bordes(self):
        """
        Detects the edges of the found segmentation using Canny.
        return: saves the results in self.border
        """
        img_augmented = self.predict * 5
        border = cv2.Canny(img_augmented, 3, 7)
        self.border = border

    def detectar_centro(self):
        """
        Detect the center of the myocardium. For this, the average of the positions of the blood pool is calculated.
        return: store the center in self.radius
        """
        sum_x = 0
        sum_y = 0
        cant_px = 0
        for i in range(len(self.predict)):
            for j in range(len(self.predict[i])):
                if self.predict[i][j] == 2:
                    sum_x += i
                    sum_y += j
                    cant_px += 1
        try:
            x = np.rint(sum_x / cant_px)
        except ZeroDivisionError:
            x = 0
        try:
            y = np.rint(sum_y / cant_px)
        except ZeroDivisionError:
            y = 0
        self.radio = [x, y]

    def detectar_separacion(self):
        """
        Detect which part of the myocardium is part of the endocardium and which part is part of the epicardium
        Search for value 1 of self.predict
        - If closest is 0: ENDOCARDIUM
        - If closest is 2: EPICARDIUM
        - If both close: EPICARDIUM
        return: store results in self.epicardium and self.endocardium
        """
        for i in range(len(self.predict)):
            x_end = []
            x_epi = []
            x_san = []
            for j in range(len(self.predict[i])):
                is0 = False
                is2 = False
                if self.predict[i][j] == 1:
                    dif = 1
                    while not is0 and not is2:
                        is0, is2 = self.mas_cercano(i, j, dif)
                        if is2 and not is0:
                            x_end.append(1)
                            x_epi.append(0)
                            x_san.append(0)
                        elif is0:
                            x_end.append(0)
                            x_epi.append(1)
                            x_san.append(0)
                        dif += 1
                elif self.predict[i][j] == 2:
                    x_san.append(1)
                    x_end.append(0)
                    x_epi.append(0)
                else:
                    x_epi.append(0)
                    x_end.append(0)
                    x_san.append(0)
            self.endocardio.append(np.array(x_end))
            self.epicardio.append(np.array(x_epi))
            self.sangre.append(np.array(x_san))

    def mas_cercano(self, pos_x, pos_y, dist):
        """
        Find the closest point of interest to the point of analysis. It must be found outside of the myocardium (0) or
        blood (2). It is searched in squares, with center in the point
        param pos_x: x position of the point
        param pos_y: y-position of the point
        param dist: distance from the point to the point where to analyze
        return: is0 True if myocardium is detected, False otherwise. is2 True if blood is detected, False otherwise.
        """
        is0 = False
        is2 = False
        # Set pos_y-dist
        if pos_y - dist >= 0:
            for i in range(dist):
                if pos_x - i >= 0:
                    if self.predict[pos_x - i][pos_y - dist] == 0:
                        is0 = True
                    elif self.predict[pos_x - i][pos_y - dist] == 2:
                        is2 = True
                if pos_x + i < len(self.predict):
                    if self.predict[pos_x + i][pos_y - dist] == 0:
                        is0 = True
                    elif self.predict[pos_x + i][pos_y - dist] == 2:
                        is2 = True
        # Set pos_y + dist
        if pos_y + dist < len(self.predict[0]):
            for i in range(dist):
                if pos_x - i >= 0:
                    if self.predict[pos_x - i][pos_y + dist] == 0:
                        is0 = True
                    elif self.predict[pos_x - i][pos_y + dist] == 2:
                        is2 = True
                if pos_x + i < len(self.predict):
                    if self.predict[pos_x + i][pos_y + dist] == 0:
                        is0 = True
                    elif self.predict[pos_x + i][pos_y + dist] == 2:
                        is2 = True
        # Set pos_x-dist
        if pos_x - dist >= 0:
            for i in range(dist):
                if pos_y - i >= 0:
                    if self.predict[pos_x - dist][pos_y - i] == 0:
                        is0 = True
                    elif self.predict[pos_x - dist][pos_y - i] == 2:
                        is2 = True
                if pos_y + i < len(self.predict[i]):
                    if self.predict[pos_x - dist][pos_y + i] == 0:
                        is0 = True
                    elif self.predict[pos_x - dist][pos_y + i] == 2:
                        is2 = True
        # Set pos_x + dist
        if pos_x + dist >= len(self.predict):
            for i in range(dist):
                if pos_y - i >= 0:
                    if self.predict[pos_x + dist][pos_y - i] == 0:
                        is0 = True
                    elif self.predict[pos_x + dist][pos_y - i] == 2:
                        is2 = True
                if pos_y + i < len(self.predict[i]):
                    if self.predict[pos_x + dist][pos_y + i] == 0:
                        is0 = True
                    elif self.predict[pos_x + dist][pos_y + i] == 2:
                        is2 = True
        return is0, is2

    def get_prom_epi(self, parte):
        """
        Calculates the average pixel intensity of the Epicardium in the image area.
        param part: what amount of data you are referring to
            0: whole epicardium area
            1: subdiv1
            2: subdiv2
            3: subdiv3
            4: subdiv4
        return: float value of the average intensity
        """
        sum_in = 0
        total = 0
        if parte == 0:
            for i in range(len(self.epicardio)):
                for j in range(len(self.epicardio[i])):
                    if self.epicardio[i][j] == 1:
                        sum_in += self.pixel_array[i][j]
                        total += 1
        else:
            data = self.epi_part[str(parte)]
            for i in range(len(data)):
                for j in range(len(data[i])):
                    if data[i][j] == 1:
                        sum_in += self.pixel_array[i][j]
                        total += 1
        try:
            prom = sum_in / total
        except ZeroDivisionError:
            prom = 0
        return prom

    def get_prom_end(self, parte):
        """
        Calculates the average pixel intensity of the Endocardium in the image area.
        param part: what amount of data you are referring to
            0: whole epicardium area
            1: subdiv1
            2: subdiv2
            3: subdiv3
            4: subdiv4
        return: float value of the average intensity
        """
        sum_in = 0
        total = 0
        if parte == 0:
            for i in range(len(self.endocardio)):
                for j in range(len(self.endocardio[i])):
                    if self.endocardio[i][j] == 1:
                        sum_in += self.pixel_array[i][j]
                        total += 1
        else:
            data = self.end_part[str(parte)]
            for i in range(len(data)):
                for j in range(len(data[i])):
                    if data[i][j] == 1:
                        sum_in += self.pixel_array[i][j]
                        total += 1
        try:
            prom = sum_in/total
        except ZeroDivisionError:
            prom = 0
        return prom

    def get_prom_blood(self, parte):
        """
        Calculates the average intensity of blood zone pixels in the image.
        param part: what amount of data you are referring to
            0: whole epicardium area
            1: subdiv1
            2: subdiv2
            3: subdiv3
            4: subdiv4
        return: float value of the average intensity
        """
        sum_in = 0
        total = 0
        if parte == 0:
            for i in range(len(self.pixel_array)):
                for j in range(len(self.pixel_array[i])):
                    if self.sangre[i][j] == 1:
                        sum_in += self.pixel_array[i][j]
                        total += 1
        else:
            data = self.san_part[str(parte)]
            for i in range(len(data)):
                for j in range(len(data[i])):
                    if data[i][j] == 1:
                        sum_in += self.pixel_array[i][j]
                        total += 1
        try:
            prom = sum_in / total
        except ZeroDivisionError:
            prom = 0
        return prom

    def dividir_miocardio(self, punto):
        """
        Receiving the point entered by the user, it divides the myocardium into the 4 necessary sections, using the quadrant system.
        quadrant system, which complements the functions named
        param point: point entered by the user.
        return: void, the sections are saved as a parameter of the image.
        """
        x_p = int(punto[0])
        y_p = int(punto[1])
        p = self.calculo_m(x_p, y_p)
        if p != 0 and np.isfinite(p):
            cuadrante = self.detectar_cuadrante(punto)  #  Give the quadrant in which I, II, III, IV is located.
            self.m[cuadrante] = p
            self.m["init"] = cuadrante
            self.completar_pendientes()
            self.partir_puntos()
        else:
            cuadrante = self.detectar_cuadrante(punto)  # Gives the axis on which I-II, II-III, III-IV, I-IV is located.
            self.m["init"] = cuadrante
            self.partir_puntos()


    def detectar_cuadrante(self, p):
        """
        Given a point p, calculate the quadrant to which it belongs, taking into account that the (0,0) of the created system is the radius point of the blood pool.
        created is the radius point of the blood pool. In case it touches an axis, a pair with the quadrants it touches is returned.
        quadrants it touches.
        param p: point entered to analyze (x, y)
        return: String with the value of the quadrant where it is located.
        """
        x = p[0]
        y = p[1]
        if x > self.radio[0]:
            if y > self.radio[1]:
                return 'IV'
            elif y < self.radio[1]:
                return 'I'
            else:
                return 'I-IV'
        elif x < self.radio[0]:
            if y > self.radio[1]:
                return 'III'
            elif y < self.radio[1]:
                return 'II'
            else:
                return 'II-III'
        else:
            if y > self.radio[1]:
                return 'III-IV'
            elif y <= self.radio[1]:
                return 'I-II'

    def completar_pendientes(self):
        """
        This function is called only if the entered point has a slope other than 0 and finite.
        Taking the slope value of the init, it proceeds to calculate the rest of the slopes using m1*m2=-1, since
        must be perpendicular slopes.
        :return:
        """
        init = self.m["init"]
        p = self.m[init]
        p_cont = -1 / p
        if init == "I" or init == "III":
            self.m["I"] = p
            self.m["II"] = p_cont
            self.m["III"] = p
            self.m["IV"] = p_cont
        elif init == "II" or init == "IV":
            self.m["I"] = p_cont
            self.m["II"] = p
            self.m["III"] = p_cont
            self.m["IV"] = p

    def calculo_m(self, x, y):
        """
        Calculate slope with respect to the center of the blood pool. If it is divided by zero, it returns the
        numpy infinity.
        param x: X-axis value
        param y: value on the y-axis
        return: calculated slope value
        """
        try:
            if x < int(self.radio[0]):
                p = (y - int(self.radio[1])) / (int(self.radio[0]) - x)
            else:
                p = (int(self.radio[1] - y)) / (x - int(self.radio[0]))
        except ZeroDivisionError:
            p = np.inf
        return p

    def partir_puntos(self):
        """
        The predict, endocardium and epicardium points are traversed, the points of interest are found and then 
        the corresponding zone is entered. The functions enter_point are used if the entered touch point is in
        the quadrant zone, or enter_by_axis, if it is on one of the axes.they are identified according to whether
        the slope is still 0.
        return: void, fills the dictionary with the 4 divided zones
        """
        for i in range(len(self.predict)):
            end1 = []
            end2 = []
            end3 = []
            end4 = []
            epi1 = []
            epi2 = []
            epi3 = []
            epi4 = []
            san1 = []
            san2 = []
            san3 = []
            san4 = []
            for j in range(len(self.predict[i])):
                #  Buscar puntos de sangre
                if self.sangre[i][j] == 1:
                    pos_c = self.detectar_cuadrante((i, j))
                    pend = self.calculo_m(i, j)
                    if self.m["I"] == 0.0:
                        self.ingresar_por_eje(pos_c, san1, san2, san3, san4)
                    else:
                        self.ingresar_punto(pos_c, pend, san1, san2, san3, san4)
                else:
                    self.ingresar_punto('0', 0, san1, san2, san3, san4)

                #  Buscar punto de Epicardio
                if self.epicardio[i][j] == 1:
                    pos_c = self.detectar_cuadrante((i, j))
                    pend = self.calculo_m(i, j)
                    if self.m["I"] == 0.0:
                        self.ingresar_por_eje(pos_c, epi1, epi2, epi3, epi4)
                    else:
                        self.ingresar_punto(pos_c, pend, epi1, epi2, epi3, epi4)
                else:
                    self.ingresar_punto('0', 0, epi1, epi2, epi3, epi4)

                #  Buscar punto de Endocardio
                if self.endocardio[i][j] == 1:
                    pos_c = self.detectar_cuadrante((i, j))
                    pend = self.calculo_m(i, j)
                    if self.m["I"] == 0.0:
                        self.ingresar_por_eje(pos_c, end1, end2, end3, end4)
                    else:
                        self.ingresar_punto(pos_c, pend, end1, end2, end3, end4)
                else:
                    self.ingresar_punto('0', 0, end1, end2, end3, end4)
            self.san_part["1"].append(san1)
            self.san_part["2"].append(san2)
            self.san_part["3"].append(san3)
            self.san_part["4"].append(san4)
            self.epi_part["1"].append(epi1)
            self.epi_part["2"].append(epi2)
            self.epi_part["3"].append(epi3)
            self.epi_part["4"].append(epi4)
            self.end_part["1"].append(end1)
            self.end_part["2"].append(end2)
            self.end_part["3"].append(end3)
            self.end_part["4"].append(end4)

    def ingresar_punto(self, pos, pend, a1, a2, a3, a4):
        """
        Given the point, the point is entered into the corresponding array as a 1, while the others are entered as a 0, 
        in order to keep the shape of the image and then be able to enter it.
         param pos: position with respect to the quadrant
         param pend: slope of the point, used to compare and see which segment it goes to.
         param a1: first shape array
         param a2: second shape array
         param a3: third shape array
         param a4: fourth shape array
        return: void, ends with the point added where it corresponds, and the rest with 0
        """
        if pos == '0':
            a1.append(0); a2.append(0); a3.append(0); a4.append(0)
        else:
            if self.m["init"] == 'I':
                if pos == 'I':
                    if pend < self.m["I"]:
                        a1.append(1); a2.append(0); a3.append(0); a4.append(0)
                    else:
                        a1.append(0); a2.append(0); a3.append(0); a4.append(1)
                elif pos == 'II':
                    if pend < self.m["II"]:
                        a1.append(0); a2.append(0); a3.append(0); a4.append(1)
                    else:
                        a1.append(0); a2.append(0); a3.append(1); a4.append(0)
                elif pos == 'III':
                    if pend < self.m["III"]:
                        a1.append(0); a2.append(0); a3.append(1); a4.append(0)
                    else:
                        a1.append(0); a2.append(1); a3.append(0); a4.append(0)
                elif pos == 'IV':
                    if pend < self.m["IV"]:
                        a1.append(0); a2.append(1); a3.append(0); a4.append(0)
                    else:
                        a1.append(1); a2.append(0); a3.append(0); a4.append(0)
                elif pos == 'I-II':
                    a1.append(0); a2.append(0); a3.append(0); a4.append(1)
                elif pos == 'II-III':
                    a1.append(0); a2.append(0); a3.append(1); a4.append(0)
                elif pos == 'III-IV':
                    a1.append(0); a2.append(1); a3.append(0); a4.append(0)
                elif pos == 'I-IV':
                    a1.append(1); a2.append(0); a3.append(0); a4.append(0)
            elif self.m["init"] == 'II':
                if pos == 'I':
                    if pend < self.m["I"]:
                        a1.append(0); a2.append(1); a3.append(0); a4.append(0)
                    else:
                        a1.append(1); a2.append(0); a3.append(0); a4.append(0)
                elif pos == 'II':
                    if pend < self.m["II"]:
                        a1.append(1); a2.append(0); a3.append(0); a4.append(0)
                    else:
                        a1.append(0); a2.append(0); a3.append(0); a4.append(1)
                elif pos == 'III':
                    if pend < self.m["III"]:
                        a1.append(0); a2.append(0); a3.append(0); a4.append(1)
                    else:
                        a1.append(0); a2.append(0); a3.append(1); a4.append(0)
                elif pos == 'IV':
                    if pend < self.m["IV"]:
                        a1.append(0); a2.append(0); a3.append(1); a4.append(0)
                    else:
                        a1.append(0); a2.append(1); a3.append(0); a4.append(0)
                elif pos == 'I-II':
                    a1.append(1); a2.append(0); a3.append(0); a4.append(0)
                elif pos == 'II-III':
                    a1.append(0); a2.append(0); a3.append(0); a4.append(1)
                elif pos == 'III-IV':
                    a1.append(0); a2.append(0); a3.append(1); a4.append(0)
                elif pos == 'I-IV':
                    a1.append(0); a2.append(1); a3.append(0); a4.append(0)
            elif self.m["init"] == 'III':
                if pos == 'I':
                    if pend < self.m["I"]:
                        a1.append(0); a2.append(0); a3.append(1); a4.append(0)
                    else:
                        a1.append(0); a2.append(1); a3.append(0); a4.append(0)
                elif pos == 'II':
                    if pend < self.m["II"]:
                        a1.append(0); a2.append(1); a3.append(0); a4.append(0)
                    else:
                        a1.append(1); a2.append(0); a3.append(0); a4.append(0)
                elif pos == 'III':
                    if pend < self.m["III"]:
                        a1.append(1); a2.append(0); a3.append(0); a4.append(0)
                    else:
                        a1.append(0); a2.append(0); a3.append(0); a4.append(1)
                elif pos == 'IV':
                    if pend < self.m["IV"]:
                        a1.append(0); a2.append(0); a3.append(0); a4.append(1)
                    else:
                        a1.append(0); a2.append(0); a3.append(1); a4.append(0)
                elif pos == 'I-II':
                    a1.append(0); a2.append(1); a3.append(0); a4.append(0)
                elif pos == 'II-III':
                    a1.append(1); a2.append(0); a3.append(0); a4.append(0)
                elif pos == 'III-IV':
                    a1.append(0); a2.append(0); a3.append(0); a4.append(1)
                elif pos == 'I-IV':
                    a1.append(0); a2.append(0); a3.append(1); a4.append(0)
            elif self.m["init"] == 'IV':
                if pos == 'I':
                    if pend < self.m["I"]:
                        a1.append(0); a2.append(0); a3.append(0); a4.append(1)
                    else:
                        a1.append(0); a2.append(0); a3.append(1); a4.append(0)
                elif pos == 'II':
                    if pend < self.m["II"]:
                        a1.append(0); a2.append(0); a3.append(1); a4.append(0)
                    else:
                        a1.append(0); a2.append(1); a3.append(0); a4.append(0)
                elif pos == 'III':
                    if pend < self.m["III"]:
                        a1.append(0); a2.append(1); a3.append(0); a4.append(0)
                    else:
                        a1.append(1); a2.append(0); a3.append(0); a4.append(0)
                elif pos == 'IV':
                    if pend < self.m["IV"]:
                        a1.append(1); a2.append(0); a3.append(0); a4.append(0)
                    else:
                        a1.append(0); a2.append(0); a3.append(0); a4.append(1)
                elif pos == 'I-II':
                    a1.append(0); a2.append(0); a3.append(1); a4.append(0)
                elif pos == 'II-III':
                    a1.append(0); a2.append(1); a3.append(0); a4.append(0)
                elif pos == 'III-IV':
                    a1.append(1); a2.append(0); a3.append(0); a4.append(0)
                elif pos == 'I-IV':
                    a1.append(0); a2.append(0); a3.append(0); a4.append(1)

    def ingresar_por_eje(self, pos, a1, a2, a3, a4):
        """
        Case in which the touched point is part of an axis. In this case, the point to be entered will be part of a quadrant directly, since the sections are
        quadrant directly, since the sections are quadrants.
         param pos: pos of the point to be entered
         param a1: first posc of array
         param a2: second posc of array
         param a3: third posc of array
         param a4: fourth posc of array
        return: void, fills the arrays with their corresponding
        """
        if pos == '0':
            a1.append(0); a2.append(0); a3.append(0); a4.append(0)
        else:
            if self.m["init"] == 'I-II':
                if pos == 'I':
                    a1.append(1); a2.append(0); a3.append(0); a4.append(0)
                elif pos == 'II':
                    a1.append(0); a2.append(0); a3.append(0); a4.append(1)
                elif pos == 'III':
                    a1.append(0); a2.append(0); a3.append(1); a4.append(0)
                elif pos == 'IV':
                    a1.append(0); a2.append(1); a3.append(0); a4.append(0)
                elif pos == 'I-II':
                    a1.append(0); a2.append(0); a3.append(0); a4.append(1)
                elif pos == 'II-III':
                    a1.append(0); a2.append(0); a3.append(1); a4.append(0)
                elif pos == 'III-IV':
                    a1.append(0); a2.append(1); a3.append(0); a4.append(0)
                elif pos == 'I-IV':
                    a1.append(1); a2.append(0); a3.append(0); a4.append(0)
            elif self.m["init"] == 'II-III':
                if pos == 'I':
                    a1.append(0); a2.append(1); a3.append(0); a4.append(0)
                elif pos == 'II':
                    a1.append(1); a2.append(0); a3.append(0); a4.append(0)
                elif pos == 'III':
                    a1.append(0); a2.append(0); a3.append(0); a4.append(1)
                elif pos == 'IV':
                    a1.append(0); a2.append(0); a3.append(1); a4.append(0)
                elif pos == 'I-II':
                    a1.append(1); a2.append(0); a3.append(0); a4.append(0)
                elif pos == 'II-III':
                    a1.append(0); a2.append(0); a3.append(0); a4.append(1)
                elif pos == 'III-IV':
                    a1.append(0); a2.append(0); a3.append(1); a4.append(0)
                elif pos == 'I-IV':
                    a1.append(0); a2.append(1); a3.append(0); a4.append(0)
            elif self.m["init"] == 'III-IV':
                if pos == 'I':
                    a1.append(0); a2.append(0); a3.append(1); a4.append(0)
                elif pos == 'II':
                    a1.append(0); a2.append(1); a3.append(0); a4.append(0)
                elif pos == 'III':
                    a1.append(1); a2.append(0); a3.append(0); a4.append(0)
                elif pos == 'IV':
                    a1.append(0); a2.append(0); a3.append(0); a4.append(1)
                elif pos == 'I-II':
                    a1.append(0); a2.append(1); a3.append(0); a4.append(0)
                elif pos == 'II-III':
                    a1.append(1); a2.append(0); a3.append(0); a4.append(0)
                elif pos == 'III-IV':
                    a1.append(0); a2.append(0); a3.append(0); a4.append(1)
                elif pos == 'I-IV':
                    a1.append(0); a2.append(0); a3.append(1); a4.append(0)
            elif self.m["init"] == 'I-IV':
                if pos == 'I':
                    a1.append(0); a2.append(0); a3.append(0); a4.append(1)
                elif pos == 'II':
                    a1.append(0); a2.append(0); a3.append(1); a4.append(0)
                elif pos == 'III':
                    a1.append(0); a2.append(1); a3.append(0); a4.append(0)
                elif pos == 'IV':
                    a1.append(1); a2.append(0); a3.append(0); a4.append(0)
                elif pos == 'I-II':
                    a1.append(0); a2.append(0); a3.append(1); a4.append(0)
                elif pos == 'II-III':
                    a1.append(0); a2.append(1); a3.append(0); a4.append(0)
                elif pos == 'III-IV':
                    a1.append(1); a2.append(0); a3.append(0); a4.append(0)
                elif pos == 'I-IV':
                    a1.append(0); a2.append(0); a3.append(0); a4.append(1)
