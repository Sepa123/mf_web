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

def rellenar_tabla(time_rest, data_rest, time_stress, data_stress):
        area_rest = calculo_area_curva(data_rest,time_rest)
        area_stress = calculo_area_curva(data_stress,time_stress)
        res_peak_rest = calculo_maximo(data_rest,time_rest)[0]
        res_peak_stress = calculo_maximo(data_stress, time_stress)[0]
        res_pend_rest = calculo_pendiente(data_rest, time_rest)[0]
        res_pend_stress = calculo_pendiente(data_stress, time_stress)[0]
        res_ratio_value = np.round(calculo_pendiente(data_stress, time_stress)[0]
                                      / calculo_pendiente(data_rest, time_rest)[0], 2)
        print("area rest :", area_rest)
        print("area stress :", area_stress)
        print("peak rest :", res_peak_rest)
        print("peak stress :", res_peak_stress)
        print("pediente rest :", res_pend_rest)
        print("pendiente stress :", res_pend_stress)
        print("coefficiente :", res_ratio_value)

class ResultScreen:

    def plot(request):
        apc = AppController()
        upl = UploadImage(apc)
        #resu = ResultScreen(apc)
         #Funciones para subir los datos de res y stress
        upl.subir_img_rest()
        upl.subir_img_stress()
        subdiv = 'total'

        apc.process_img()
        slice_select_rest = 0
        slice_select_stress = 0
        zona = 1

        init_rest = apc.img_rest.contenido[slice_select_rest].inicio
        fin_rest =  apc.img_rest.contenido[slice_select_rest].fin
        init_stress = apc.img_stress.contenido[slice_select_stress].inicio
        fin_stress = apc.img_stress.contenido[slice_select_stress].fin

        time_r = apc.img_rest.contenido[slice_select_rest].data_tiempo
        time_rest = range(len(time_r))
        time_s = apc.img_stress.contenido[slice_select_stress].data_tiempo
        time_stress = range(len(time_s))
        data_rest = []
        data_stress = []
        if zona == 1:
            zona_select = 1
            data_rest = apc.img_rest.contenido[slice_select_rest].data_sangre[subdiv]
            data_stress = apc.img_stress.contenido[slice_select_stress].data_sangre[subdiv]
        elif zona == 2:
            zona_select = 2
            data_rest = apc.img_rest.contenido[slice_select_rest].data_epicardio[subdiv]
            data_stress = apc.img_stress.contenido[slice_select_stress].data_epicardio[subdiv]
        elif zona == 3:
            zona_select = 3
            data_rest = apc.img_rest.contenido[slice_select_rest].data_endocardio[subdiv]
            data_stress = apc.img_stress.contenido[slice_select_stress].data_endocardio[subdiv]
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
        axes.set_title("Graficos")
        plt.legend(('Curva Rest', 'Curva Stress'), loc = 'upper right')

        # Como enviaremos la imagen en bytes la guardaremos en un buffer
        buf = io.BytesIO()
        canvas = FigureCanvasAgg(f)
        canvas.print_png(buf)

        rellenar_tabla(time_rest[init_rest:fin_rest], data_rest[init_rest:fin_rest],
                       time_stress[init_stress:fin_stress], data_stress[init_stress:fin_stress])

        # Creamos la respuesta enviando los bytes en tipo imagen png
        response = HttpResponse(buf.getvalue(), content_type='image/png')

        # Limpiamos la figura para liberar memoria
        f.clear()

        # Añadimos la cabecera de longitud de fichero para más estabilidad
        response['Content-Length'] = str(len(response.content))

        # Devolvemos la response
        return response

    



