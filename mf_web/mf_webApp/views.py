import base64
import os
import time
import traceback
from io import BytesIO
import pydicom

import imageio
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Agg')
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse

from django.shortcuts import render, HttpResponse

#Segmentation

from .model.paq_img_model import PaqImgModel
from .model.patient_data import Patient
import numpy as np

from .app_controller import * 

import pickle

from mf_webApp.screen.upload_image import UploadImage
from mf_webApp.screen.results_screen import ResultScreen

from mf_webApp.utils.dicom_utils import refactor_dicom_file
from mf_webApp.utils.tkinter_img import img2rgba
from mf_webApp.utils.tooltip_utils import CreateToolTip
from mf_webApp.utils.valores_curvas import *

from mf_web import settings

#Codigo de segmentacion 

#codigo para subir las imagenes


#django-dicom-viewer proyecto
   
def ajax_server(request):
    start = time.time()
    d = dict()
    generic = dict()
    medinfo = dict()

    try:

        print('FILE--->',str(request.FILES['imgInpStress'])[-3:])

        if request.method == 'POST' and ('imgInpStress' in request.FILES) and request.FILES['imgInpStress'] and  str(request.FILES['imgInpStress'])[-3:].upper() =='DCM':
            print("Soy ajax server")            
            file = request.FILES['imgInpStress']
            content = file.read()
            print('###################################')
            print(content)

            fs = FileSystemStorage()
            filename = fs.save(file.name, file)
            print()
            full_path_file = os.path.join(settings.MEDIA_ROOT, filename)
            #print(colored('path->', 'red'), full_path_file)

            generic['name'] = filename
            generic['size'] = os.path.getsize(full_path_file)
            try:
                if full_path_file[-3:].upper() == 'DCM':
                    dcpimg = imageio.imread(full_path_file)
                    for keys in dcpimg.meta:

                        medinfo[keys] = str(dcpimg.meta[keys])

                    if len(dcpimg.shape) ==4:
                        dcpimg = dcpimg[0,0]
                    elif len(dcpimg.shape) ==3:
                        dcpimg = dcpimg[0]

                    fig = plt.gcf()
                    plt.axis('off')
                    plt.imshow(dcpimg, cmap='gray')
                    #plt.colorbar()
                    figure = BytesIO()
                    plt.savefig(figure, format='jpg', dpi=300, facecolor="#7C7878")

                    plt.close()
                    d['url'] = {'base64': 'data:image/png;base64,' + base64.b64encode(figure.getvalue()).decode()}

                # medinfo.update(dcpimg.meta)

            except Exception as e:

                traceback.print_tb(e)

            fs.delete(filename)
    except Exception as e:
        traceback.print_tb(e)

    generic['process time'] = time.time() - start
    d['generic'] = generic

    d['med'] = medinfo

    #print(colored(d, 'red'))
    #apc = AppController()

    #upl = UploadImage(apc)

    #upl.subir_img_stress(full_path_file)

    return JsonResponse(d)

def ajax_server2(request):
    start = time.time()
    d = dict()
    generic = dict()
    medinfo = dict()

    try:

        print('FILE--->',str(request.FILES['imgInp'])[-3:])

        if request.method == 'POST' and ('imgInp' in request.FILES) and request.FILES['imgInp'] and  str(request.FILES['imgInp'])[-3:].upper() =='DCM':
            print("Soy Ajax server 2 ")            
            file = request.FILES['imgInp']
            fs = FileSystemStorage()
            filename = fs.save(file.name, file)
            full_path_file = os.path.join(settings.MEDIA_ROOT, filename)
            

            generic['name'] = filename
            generic['size'] = os.path.getsize(full_path_file)
            try:
                if full_path_file[-3:].upper() == 'DCM':
                    dcpimg = imageio.imread(full_path_file)
                    for keys in dcpimg.meta:

                        medinfo[keys] = str(dcpimg.meta[keys])

                    if len(dcpimg.shape) ==4:
                        dcpimg = dcpimg[0,0]
                    elif len(dcpimg.shape) ==3:
                        dcpimg = dcpimg[0]

                    fig = plt.gcf()
                    plt.axis('off')
                    plt.imshow(dcpimg, cmap='gray')
                    #plt.colorbar()
                    figure = BytesIO()
                    plt.savefig(figure, format='jpg', dpi=300, facecolor="#7C7878")

                    plt.close()
                    d['url'] = {'base64': 'data:image/png;base64,' + base64.b64encode(figure.getvalue()).decode()}

                # medinfo.update(dcpimg.meta)

            except Exception as e:

                traceback.print_tb(e)

            fs.delete(filename)
    except Exception as e:
        traceback.print_tb(e)

    generic['process time'] = time.time() - start
    d['generic'] = generic

    d['med'] = medinfo

    #print(colored(d, 'red'))
    #apc = AppController()

    #upl = UploadImage(apc)

    #upl.subir_img_rest(full_path_file)

    return JsonResponse(d)

def app_render(request):
    #print(settings.BASE_DIR)
    #d = {'title': 'DICOM viewer','info':'DICOM SERVER SIDE RENDER'}
    return render(request, "mf_webApp/upl.html")

def lo(request):

    return render(request, "mf_webApp/upl.html")

# Lo mio
def home(request):

    return render(request, "mf_webApp/home.html")

def upload_image(request):
    print("Pantalla upload imagen")
    
    return render(request, "mf_webApp/upload.html")

def result(request):

    print("Pantalla Resultados de imagen")
    apc = AppController()
    upl = UploadImage(apc)
    #resu = ResultScreen(apc)

#Funciones para subir los datos de res y stress
    upl.subir_img_rest()
    upl.subir_img_stress()

    apc.process_img()
# Carga de datos del paciente
    print("Tamos daos pal exito")

    #name_paciente = apc.patient.s_name
    #series_id_patient = apc.patient.s_series_id
    #series_des_patient = apc.patient.s_series_desc
    #study_patient = apc.patient.s_study_desc

    #data_patient = {"name_pat":name_paciente,"id_pat":series_id_patient,"series_des_pat":series_des_patient,
    #                "study_pat":study_patient,}

#  Loading Image Values : WW-WL-SLICE

    #  Loading Display Images
    #self.imprimir_imagenes(tipo=0)
    #self.print_img_prediccion(tipo=0)

   # predict_img()

    return render(request, "mf_webApp/result.html")

def lista(request):

    return render(request, "mf_webApp/list.html")

