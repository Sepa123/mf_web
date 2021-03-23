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

from django.shortcuts import render, HttpResponse, redirect

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

#Iniciando UploadImage
apc = AppController()
upl = UploadImage(apc)
resu = ResultScreen(apc)

#codigo para subir las imagenes


#django-dicom-viewer proyecto
   
def upImgStress(request):
    start = time.time()
    d = dict()
    generic = dict()
    medinfo = dict()

    try:

        print('FILE--->',str(request.FILES['imgInpStress']))

        if request.method == 'POST' and ('imgInpStress' in request.FILES) and request.FILES['imgInpStress'] and  str(request.FILES['imgInpStress'])[-3:].upper() =='DCM':
            print("Soy ajax server Stress")            
            file = request.FILES['imgInpStress']
            print('###################################')
            fs = FileSystemStorage()
            filename = fs.save(file.name, file)
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

    if request.method == 'POST' :
        dir=request.FILES
        dirlist=dir.getlist('files')
        pathlist=request.POST.getlist('paths')
        print(dir)
        if not dirlist:
            return HttpResponse( 'files not found')
        else:
            for file in dirlist:
                position = os.path.join(os.path.abspath(os.path.join(os.getcwd(),'Dataset')),'/'.join(pathlist[dirlist.index(file)].split('/')[:-1]))
                if not os.path.exists(position):
                    os.makedirs(position )
                storage = open(position+'/'+file.name, 'wb+')   
                for chunk in file.chunks():          
                    storage.write(chunk)
                storage.close() 
            print(str (position))
    upl.subir_img_stress(position)
    return JsonResponse(d)

def upImgRest(request):
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

    if request.method == 'POST' :
        dir=request.FILES
        dirlist=dir.getlist('files')
        pathlist=request.POST.getlist('paths')
        print(dir)
        if not dirlist:
            return HttpResponse( 'files not found')
        else:
            for file in dirlist:
                position = os.path.join(os.path.abspath(os.path.join(os.getcwd(),'Dataset')),'/'.join(pathlist[dirlist.index(file)].split('/')[:-1]))
                if not os.path.exists(position):
                    os.makedirs(position )
                storage = open(position+'/'+file.name, 'wb+')   
                for chunk in file.chunks():          
                    storage.write(chunk)
                storage.close() 
            print(str (position))
    upl.subir_img_rest(position)
    return JsonResponse(d)

def send_data(request):
     if request.method == 'POST' :
        dir=request.FILES
        dirlist=dir.getlist('files')
        pathlist=request.POST.getlist('paths')
        print(dir)
        if not dirlist:
            return HttpResponse( 'files not found')
        else:
            for file in dirlist:
                position = os.path.join(os.path.abspath(os.path.join(os.getcwd(),'Dataset')),'/'.join(pathlist[dirlist.index(file)].split('/')[:-1]))
                if not os.path.exists(position):
                    os.makedirs(position )
                storage = open(position+'/'+file.name, 'wb+')   
                for chunk in file.chunks():          
                    storage.write(chunk)
                storage.close() 
            print(str (position))
            return HttpResponse('1hsdasdlskdads')

def plot(request):
    # Llamamos a curve_print() que retorna un response
    response = resu.curve_print(1)
    # Devolvemos la response
    return response
def app_render(request):
    return render(request, "mf_webApp/upl.html")

def lo(request):

    return render(request, "mf_webApp/upl.html")

# Lo mio
def home(request):

    return render(request, "mf_webApp/home.html")

def upload_image(request):
    print("Pantalla upload imagen")
    
    return render(request, "mf_webApp/upload.html")

def processing(request):

    # Ejecuta la funcion para procesar los datos de las imagenes
    apc.process_img()
    # carga los resultados de las imagenes
    resu.curve_print(1)

    return redirect("result")

def result(request):

    print("Pantalla Resultados de imagen")

    #Funciones para subir los datos de res y stress
    # Carga de datos del paciente

    print("Tamos daos pal exito")



    name_paciente = apc.patient.s_name
    series_id_patient = apc.patient.s_series_id
    series_des_patient = apc.patient.s_series_desc
    study_patient = apc.patient.s_study_desc

    areaR = resu.area_rest

    print("nombre paciente: ",name_paciente)
    print("El area rest del paciente es: ",areaR)

    data_patient = {"name_pat":name_paciente,"id_pat":series_id_patient,"series_des_pat":series_des_patient,
                    "study_pat":study_patient}

    #  Loading Image Values : WW-WL-SLICE

    #  Loading Display Images
    #self.imprimir_imagenes(tipo=0)
    #self.print_img_prediccion(tipo=0)

    # predict_img()

    return render(request, "mf_webApp/result.html",data_patient)

def lista(request):

    return render(request, "mf_webApp/list.html")

