import base64
import io
from io import BytesIO
import imageio
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Agg')

from django.http import HttpResponse
from django.shortcuts import render
from matplotlib.backends.backend_agg import FigureCanvasAgg
from random import sample

from mf_webApp.app_controller import * 

import pickle

from mf_webApp.screen.upload_image import UploadImage



from PIL import Image, ImageTk

from mf_webApp.utils.dicom_utils import refactor_dicom_file
from mf_webApp.utils.tkinter_img import img2rgba
from mf_webApp.utils.tooltip_utils import CreateToolTip
from mf_webApp.utils.valores_curvas import *

class ResultScreen:

    def __init__(self, apc):

        self.apc = apc

        #  FRAME OPTIONS

        #  FRAME LATERAL

        self.plot_stress_res = None
        self.plot_stress_axis = None

        self.plot_rest_res = None
        self.plot_rest_axis = None

        #  FRAME IMAGES

        self.figRest = None
        self.figStress = None
        self.figGraf = None



        self.zona_select = 1

        #  Results Table Labels
        self.resultados_stress = None
        self.resultados_rest = None
        self.res_area = None
        self.area_stress = None
        self.area_rest = None
        self.res_peak = None
        self.res_peak_rest = None
        self.res_peak_stress = None
        self.res_pend = None
        self.res_pend_rest = None
        self.res_pend_stress = None
        self.res_ratio = None
        self.res_ratio_value = None

        self.slice_select_rest = 0
        self.slice_select_stress = 0
        self.pos_actual_img = 0
        self.photo_reference_rest = None
        self.photo_reference_stress = None

        self.habilitar_punto_rest = 0
        self.habilitar_punto_stress = 0
        self.habilitado_para_div = 0

        #  Images displayed in Canvas
        self.predict_rest = None
        self.predict_stress = None
        self.imagen_rest = None
        self.imagen_stress = None

        self.punto_stress = None
        self.punto_stress_canvas = ""
        self.punto_rest_canvas = ""
        self.punto_rest = None
        self.subdiv = 'total'

    def pressed_rest(self, x, y):
        
        self.punto_rest = None
        self.punto_rest = [int(x/2), int(y/2)]

    def pressed_stress(self, x, y):
        self.punto_stress = None
        self.punto_stress = [int(x/2), int(y/2)]
    
    def punto_tocado(self):
        #self.punto_rest = punto_rest
        #self,punto_stress = punto_stress
        self.apc.img_rest.calculo_division(self.punto_rest)
        self.apc.img_stress.calculo_division(self.punto_stress)
        self.cambio_particion(1,1)
        pass

    def cambio_particion(self, particion, zona):
       # particion = self.valor_div.get()
        self.subdiv = 'sub' + str(particion)
        figGraf, tablaP = self.curve_print(zona)

        return tablaP

        

    def recarga_img(self, ww_obt, wl_obt):
        self.apc.img_stress.contenido[self.slice_select_stress].wl = int(wl_obt)
        self.apc.img_rest.contenido[self.slice_select_rest].wl = int(wl_obt)
        self.apc.img_stress.contenido[self.slice_select_stress].ww = int(ww_obt)
        self.apc.img_rest.contenido[self.slice_select_rest].ww = int(ww_obt)
        self.imprimir_imagenesRest(tipo=0)
        self.imprimir_imagenesStress(tipo=0)


    def mov_img(self, paquete, direccion):
        """
        Moves the display images. Method called by the move buttons
        param packet: packet of images to move
            1: rest
            2: stress
        param direction: direction of movement
            1: Left
            2: Right
        return: call to print_image, as appropriate
        """
        if paquete == 1:
            if direccion == 1:
                self.apc.img_rest.contenido[int(self.slice_select_rest)].disminuir_pos()
                self.figRest , posA = self.imprimir_imagenesRest(tipo=1)
            elif direccion == 2:
                self.apc.img_rest.contenido[int(self.slice_select_rest)].aumentar_pos()
                self.figRest , posA = self.imprimir_imagenesRest(tipo=1)
        elif paquete == 2:
            if direccion == 1:
                self.apc.img_stress.contenido[int(self.slice_select_stress)].disminuir_pos()
                self.figStress, posA = self.imprimir_imagenesStress(tipo=2)
            elif direccion == 2:
                self.apc.img_stress.contenido[int(self.slice_select_stress)].aumentar_pos()
                self.figStress, posA = self.imprimir_imagenesStress(tipo=2)

        return self.figRest, self.figStress, posA



    def imprimir_imagenesStress(self, tipo=0):

        if tipo == 0 or tipo == 2:
            #  Stress printed
            x, y = self.apc.img_stress.contenido[self.slice_select_stress].imgs[0].pixel_array.shape
            height = int(306)
            width = int(height * y / x)
            img, pos_actual, l_button, r_button = self.apc.img_stress.contenido[
                int(self.slice_select_stress)].current_img(width, height)
            cantidad_img = self.apc.img_stress.contenido[self.slice_select_rest].cantidad_imgs()

            posStress = {"cantidad_imgStress": cantidad_img, "pos_actualStress": pos_actual+1}
            self.figStress = plt.gcf()
            plt.figure(facecolor="#222")
            plt.axis('off')
            plt.imshow(img, cmap='gray')
        
        self.print_img_prediccionStress(tipo=tipo)

        return self.figStress, posStress


    def imprimir_imagenesRest(self, tipo=0):
        
        if tipo == 0 or tipo == 1:
            #  Rest printed
            d = dict()
            x, y = self.apc.img_rest.contenido[self.slice_select_rest].imgs[0].pixel_array.shape
            height = int(306)
            width = int(height*y/x)
            img, pos_actual, l_button, r_button = self.apc.img_rest.contenido[
                int(self.slice_select_rest)].current_img(width, height)

            cantidad_img = self.apc.img_rest.contenido[self.slice_select_rest].cantidad_imgs()

            posRest = {"cantidad_imgRest": cantidad_img, "pos_actualRest": pos_actual+1}
            self.figRest = plt.gcf()
            plt.figure(facecolor="#222")
            plt.axis('off')
            plt.imshow(img, cmap='gray')

        self.print_img_prediccionRest(tipo=tipo)

        return self.figRest, posRest

    def print_img_prediccionStress(self, tipo):

        zona = self.zona_select
        if tipo == 0 or tipo == 2:
            #  Print Stress
            x, y = self.apc.img_stress.contenido[self.slice_select_stress].imgs[0].pixel_array.shape
            height = int(306)
            width = int(height * y / x)
            img_rgba = self.get_predict(tipo, zona, width, height)
            img_rgba = Image.frombytes('RGBA', (img_rgba.shape[1], img_rgba.shape[0]), img_rgba.astype('b').tostring())

            self.predict_stress = img_rgba

            self.figStress = plt.gcf()
            plt.axis('off')
            plt.imshow(self.predict_stress, cmap='gray')
            plt.close()

            pass


    def print_img_prediccionRest(self, tipo):
        """
        Prints the preductions, according to the area of interest.
        param type: What type of image to display
            0: Both images
            1: Show Rest image
            2: Display image Stress
        return: Image on canvas
        """
        zona = self.zona_select
        if tipo == 0 or tipo == 1:
            #  Print Rest
            x, y = self.apc.img_rest.contenido[self.slice_select_rest].imgs[0].pixel_array.shape
            height = int(306)
            width = int(height * y / x)
            img_rgba = self.get_predict(tipo, zona, width, height)
            img_rgba = Image.frombytes('RGBA', (img_rgba.shape[1], img_rgba.shape[0]), img_rgba.astype('b').tostring())

            self.predict_rest = img_rgba

            self.figRest = plt.gcf()
            plt.axis('off')
            plt.imshow(self.predict_rest, cmap='gray')
            plt.close()

            pass
        

    def get_predict(self, tipo, zona, w, h):
        """
        Delivers the array of the RGBA image of the area to be displayed.
        param type: What type of image to display
            0: Both Images
            1: Show Rest image
            2: Show Stress image
        param zone: Zone to be displayed
            1: Blood
            2: Epicardium
            3: Endocardium
        param w: Width that you want the image to show
        :param h: Height you want the image to show
        return: RGBA Array
        """
        img_rgba = None
        if tipo == 0 or tipo == 1:
            # Return image REST
            if self.subdiv == 'total':
                imgs_array = self.apc.img_rest.contenido[
                    int(self.slice_select_rest)].current_predict(0)[zona - 1]
            else:
                parte = int(self.subdiv[len(self.subdiv)-1])
                imgs_array = self.apc.img_rest.contenido[
                    int(self.slice_select_rest)].current_predict(parte)[zona - 1]
            img_rgba = img2rgba(imgs_array, zona, w, h)
        if tipo == 0 or tipo == 2:
            # Return image STRESS
            if self.subdiv == 'total':
                imgs_array = self.apc.img_stress.contenido[
                    int(self.slice_select_stress)].current_predict(0)[zona - 1]
            else:
                parte = int(self.subdiv[len(self.subdiv) - 1])
                imgs_array = self.apc.img_stress.contenido[
                    int(self.slice_select_stress)].current_predict(parte)[zona - 1]
            img_rgba = img2rgba(imgs_array, zona, w, h)
        return img_rgba

    

    def curve_print(self, zona):

        init_rest = self.apc.img_rest.contenido[self.slice_select_rest].inicio
        fin_rest =  self.apc.img_rest.contenido[self.slice_select_rest].fin
        init_stress = self.apc.img_stress.contenido[self.slice_select_stress].inicio
        fin_stress = self.apc.img_stress.contenido[self.slice_select_stress].fin

        time_r = self.apc.img_rest.contenido[self.slice_select_rest].data_tiempo
        time_rest = range(len(time_r))
        time_s = self.apc.img_stress.contenido[self.slice_select_stress].data_tiempo
        time_stress = range(len(time_s))
        data_rest = []
        data_stress = []
        if zona == 1:
            self.zona_select = 1
            data_rest = self.apc.img_rest.contenido[self.slice_select_rest].data_sangre[self.subdiv]
            data_stress = self.apc.img_stress.contenido[self.slice_select_stress].data_sangre[self.subdiv]
        elif zona == 2:
            self.zona_select = 2
            data_rest = self.apc.img_rest.contenido[self.slice_select_rest].data_epicardio[self.subdiv]
            data_stress = self.apc.img_stress.contenido[self.slice_select_stress].data_epicardio[self.subdiv]
        elif zona == 3:
            self.zona_select = 3
            data_rest = self.apc.img_rest.contenido[self.slice_select_rest].data_endocardio[self.subdiv]
            data_stress = self.apc.img_stress.contenido[self.slice_select_stress].data_endocardio[self.subdiv]
        ##

        # Creamos una figura y le dibujamos el gráfico
        self.figGraf = plt.figure()
        # Creamos los ejes
        axes = self.figGraf.add_axes([0.15, 0.15, 0.75, 0.75]) # [left, bottom, width, height]
        #axes.plot(stressx, stressx, label="Curva Rest")
        axes.plot(time_rest[init_rest:fin_rest], data_rest[init_rest:fin_rest], label="Curva Rest")
        axes.plot(time_stress[init_stress:fin_stress], data_stress[init_stress:fin_stress], label="Curva stress")
        #axes.plot(restx,resty, label="Curva Stress")
        axes.set_xlabel("Time")
        axes.set_ylabel("Signal")
        axes.set_title("Graphics")
        plt.legend(('Curva Rest', 'Curva Stress'), loc = 'upper right')

        #print("wl", self.apc.img_stress.contenido[self.slice_select_stress].wl )
        #print("ww", self.apc.img_stress.contenido[self.slice_select_stress].ww )
        plt.close()

        tabla = self.rellenar_tabla(time_rest[init_rest:fin_rest], data_rest[init_rest:fin_rest],
                       time_stress[init_stress:fin_stress], data_stress[init_stress:fin_stress])

        self.print_img_prediccionRest(tipo=0)
        self.print_img_prediccionStress(tipo=0)



        return self.figGraf, tabla

        # Devolvemos la response
       # return time_rest[init_rest:fin_rest], data_rest[init_rest:fin_rest], time_stress[init_stress:fin_stress], data_stress[init_stress:fin_stress]

    def rellenar_tabla(self, time_rest, data_rest, time_stress, data_stress):
        self.area_rest = calculo_area_curva(data_rest,time_rest)
        self.area_stress = calculo_area_curva(data_stress,time_stress)
        self.res_peak_rest = calculo_maximo(data_rest,time_rest)[0]
        self.res_peak_stress = calculo_maximo(data_stress, time_stress)[0]
        self.res_pend_rest = calculo_pendiente(data_rest, time_rest)[0]
        self.res_pend_stress = calculo_pendiente(data_stress, time_stress)[0]
        self.res_ratio_value = np.round(calculo_pendiente(data_stress, time_stress)[0]
                                      / calculo_pendiente(data_rest, time_rest)[0], 2)

        tabla = {'area_rest': self.area_rest,'area_stress': self.area_stress,'res_peak_rest': self.res_peak_rest,
                 'res_peak_stress': self.res_peak_stress,'res_pend_rest': self.res_pend_rest,'res_pend_stress': self.res_pend_stress,
                 'res_ratio_value': self.res_ratio_value}

        
        return tabla

    

    



