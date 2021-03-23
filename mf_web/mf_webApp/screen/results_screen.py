import io
import matplotlib.pyplot as plt

from django.http import HttpResponse
from django.shortcuts import render
from matplotlib.backends.backend_agg import FigureCanvasAgg
from random import sample

from mf_webApp.app_controller import * 

import pickle

from mf_webApp.screen.upload_image import UploadImage



from PIL import Image, ImageTk

import pickle

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

        # Creamos los datos para representar en el gráfico
        restx = range(1,11)
        resty = sample(range(20), len(restx))

        stressx = range(1,11)
        stressy = sample(range(20), len(stressx))

        # Creamos una figura y le dibujamos el gráfico
        f = plt.figure()
        # Creamos los ejes
        axes = f.add_axes([0.15, 0.15, 0.75, 0.75]) # [left, bottom, width, height]
        #axes.plot(stressx, stressx, label="Curva Rest")
        axes.plot(time_rest[init_rest:fin_rest], data_rest[init_rest:fin_rest], label="Curva Rest")
        axes.plot(time_stress[init_stress:fin_stress], data_stress[init_stress:fin_stress], label="Curva stress")
        #axes.plot(restx,resty, label="Curva Stress")
        axes.set_xlabel("Eje X")
        axes.set_ylabel("Eje Y")
        axes.set_title("Graphics")
        plt.legend(('Curva Rest', 'Curva Stress'), loc = 'upper right')

        print("wl", self.apc.img_stress.contenido[self.slice_select_stress].wl )
        print("ww", self.apc.img_stress.contenido[self.slice_select_stress].ww )

        # Como enviaremos la imagen en bytes la guardaremos en un buffer
        buf = io.BytesIO()
        canvas = FigureCanvasAgg(f)
        canvas.print_png(buf)

        self.rellenar_tabla(time_rest[init_rest:fin_rest], data_rest[init_rest:fin_rest],
                       time_stress[init_stress:fin_stress], data_stress[init_stress:fin_stress])

        # Creamos la respuesta enviando los bytes en tipo imagen png
        response = HttpResponse(buf.getvalue(), content_type='image/png')

        # Limpiamos la figura para liberar memoria
        f.clear()

        # Añadimos la cabecera de longitud de fichero para más estabilidad
        response['Content-Length'] = str(len(response.content))

        # Devolvemos la response
        return response

    def rellenar_tabla(self, time_rest, data_rest, time_stress, data_stress):
        self.area_rest = calculo_area_curva(data_rest,time_rest)
        self.area_stress = calculo_area_curva(data_stress,time_stress)
        self.res_peak_rest = calculo_maximo(data_rest,time_rest)[0]
        self.res_peak_stress = calculo_maximo(data_stress, time_stress)[0]
        self.res_pend_rest = calculo_pendiente(data_rest, time_rest)[0]
        self.res_pend_stress = calculo_pendiente(data_stress, time_stress)[0]
        self.res_ratio_value = np.round(calculo_pendiente(data_stress, time_stress)[0]
                                      / calculo_pendiente(data_rest, time_rest)[0], 2)
        
        print("area rest :", self.area_rest)
        print("area stress :", self.area_stress)
        print("peak rest :", self.res_peak_rest)
        print("peak stress :", self.res_peak_stress)
        print("pediente rest :", self.res_pend_rest)
        print("pendiente stress :", self.res_pend_stress)
        print("coefficiente :", self.res_ratio_value)
        

    

    



