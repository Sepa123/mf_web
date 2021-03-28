import base64
import os
import time
import traceback
from io import BytesIO
import pydicom
from datetime import datetime

import imageio
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Agg')
from matplotlib.backends.backend_agg import FigureCanvasAgg
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

from random import sample

from mf_web import settings

#Iniciando UploadImage
apc = AppController()
upl = UploadImage(apc)
resu = ResultScreen(apc)
now = datetime.now()
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
                    

                    print("Imagen leida Stress: ",dcpimg)
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
        #print(dir)
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
           # print(str (position))
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
                    print("Full RUTA; ",full_path_file)
                    dcpimg = imageio.imread(full_path_file)
                    for keys in dcpimg.meta:

                        medinfo[keys] = str(dcpimg.meta[keys])

                    if len(dcpimg.shape) ==4:
                        dcpimg = dcpimg[0,0]
                    elif len(dcpimg.shape) ==3:
                        dcpimg = dcpimg[0]

                    print("Imagen leida REST: ",dcpimg)

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
        #print(dir)
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
            #print(str (position))
    upl.subir_img_rest(position)
    return JsonResponse(d)

def zonaImagen1(request):

    figGraf, tabla = resu.curve_print(1)
    #print rest

    figrest, posRest = resu.imprimir_imagenesRest(tipo=0)
    # Como enviaremos la imagen en bytes la guardaremos en un buffer
    bufRest = BytesIO()
    canvasRest = FigureCanvasAgg(figrest)
    canvasRest.print_png(bufRest)

    #print stress

    figstress, posStress = resu.imprimir_imagenesStress(tipo=0)

    bufStress = BytesIO()
    canvasStress = FigureCanvasAgg(figstress)
    canvasStress.print_png(bufStress)

    #nuevo diccionario

    posImages = {**posRest, **posStress}

    posImages['urlRest'] = {'base64': 'data:image/png;base64,' + base64.b64encode(bufRest.getvalue()).decode()}

    posImages['urlStress'] = {'base64': 'data:image/png;base64,' + base64.b64encode(bufStress.getvalue()).decode()}

    return JsonResponse(posImages)

def zonaImagen2(request):

    figGraf, tabla = resu.curve_print(2)
    #print rest

    figrest, posRest = resu.imprimir_imagenesRest(tipo=0)
    # Como enviaremos la imagen en bytes la guardaremos en un buffer
    bufRest = BytesIO()
    canvasRest = FigureCanvasAgg(figrest)
    canvasRest.print_png(bufRest)

    #print stress

    figstress, posStress = resu.imprimir_imagenesStress(tipo=0)

    bufStress = BytesIO()
    canvasStress = FigureCanvasAgg(figstress)
    canvasStress.print_png(bufStress)

    #nuevo diccionario

    posImages = {**posRest, **posStress}

    posImages['urlRest'] = {'base64': 'data:image/png;base64,' + base64.b64encode(bufRest.getvalue()).decode()}

    posImages['urlStress'] = {'base64': 'data:image/png;base64,' + base64.b64encode(bufStress.getvalue()).decode()}

    return JsonResponse(posImages)

def recargaImagen(request):

    #figGraf, tabla = resu.curve_print(2)
    #print rest

    if request.method == 'POST':
        ww = request.POST['ww_obt']
        wl = request.POST['wl_obt']
        resu.recarga_img(str(ww), str(wl))

    figrest, posRest = resu.imprimir_imagenesRest(tipo=0)
    # Como enviaremos la imagen en bytes la guardaremos en un buffer
    bufRest = BytesIO()
    canvasRest = FigureCanvasAgg(figrest)
    canvasRest.print_png(bufRest)

    #print stress

    figstress, posStress = resu.imprimir_imagenesStress(tipo=0)

    bufStress = BytesIO()
    canvasStress = FigureCanvasAgg(figstress)
    canvasStress.print_png(bufStress)

    #nuevo diccionario

    posImages = {**posRest, **posStress}

    posImages['urlRest'] = {'base64': 'data:image/png;base64,' + base64.b64encode(bufRest.getvalue()).decode()}

    posImages['urlStress'] = {'base64': 'data:image/png;base64,' + base64.b64encode(bufStress.getvalue()).decode()}

    return JsonResponse(posImages)

def zonaImagen3(request):

    figGraf, tabla = resu.curve_print(3)
    #print rest

    figrest, posRest = resu.imprimir_imagenesRest(tipo=0)
    # Como enviaremos la imagen en bytes la guardaremos en un buffer
    bufRest = BytesIO()
    canvasRest = FigureCanvasAgg(figrest)
    canvasRest.print_png(bufRest)

    #print stress

    figstress, posStress = resu.imprimir_imagenesStress(tipo=0)

    bufStress = BytesIO()
    canvasStress = FigureCanvasAgg(figstress)
    canvasStress.print_png(bufStress)

    #nuevo diccionario

    posImages = {**posRest, **posStress}

    print("pos actual Rest", posImages['pos_actualRest'])
    print("pos actual Stress", posImages['pos_actualStress'])

    posImages['urlRest'] = {'base64': 'data:image/png;base64,' + base64.b64encode(bufRest.getvalue()).decode()}

    posImages['urlStress'] = {'base64': 'data:image/png;base64,' + base64.b64encode(bufStress.getvalue()).decode()}

    return JsonResponse(posImages)

def zona1(request):
    #graficos Zona de la Sangre

    figGraf, tabla = resu.curve_print(1)

    buf = BytesIO()
    canvas = FigureCanvasAgg(figGraf)
    canvas.print_png(buf)
    tabla['url'] = {'base64': 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode()}

    return JsonResponse(tabla)

def zona2(request):
    #graficos Zona del Epicardio 

    figGraf, tabla = resu.curve_print(2)

    buf = BytesIO()
    canvas = FigureCanvasAgg(figGraf)
    canvas.print_png(buf)

    tabla['url'] = {'base64': 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode()}

    return JsonResponse(tabla)

def zona3(request):
    #graficos Zona del Endocardio 

    figGraf, tabla = resu.curve_print(3)
    buf = BytesIO()
    canvas = FigureCanvasAgg(figGraf)
    canvas.print_png(buf)
    tabla['url'] = {'base64': 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode()}

    return JsonResponse(tabla)

def curve_table(request):
    #template de los graficos con su tabla

    figGraf, tabla = resu.curve_print(1)
    return render(request, "mf_webApp/curve_table.html", tabla )

def plot(request):
    figGraf, tabla = resu.curve_print(1)

    # Como enviaremos la imagen en bytes la guardaremos en un buffer
    buf = BytesIO()
    canvas = FigureCanvasAgg(figGraf)
    canvas.print_png(buf)
    # Llamamos a curve_print() que retorna un response

    # Creamos la respuesta enviando los bytes en tipo imagen png
    response = HttpResponse(buf.getvalue(), content_type='image/png')

    # Añadimos la cabecera de longitud de fichero para más estabilidad
    response['Content-Length'] = str(len(response.content))
    # Devolvemos la response
    return response

def app_render(request):
    return render(request, "mf_webApp/upl.html")

def lo(request):

    return render(request, "mf_webApp/upl.html")

def home(request):

    return render(request, "mf_webApp/home.html")

def mov_imgAtrasRest(request):

    figRest, figStress, posRest = resu.mov_img(1,1)

    bufRest = BytesIO()
    canvasRest = FigureCanvasAgg(figRest)
    canvasRest.print_png(bufRest)

    print("pos actual Rest", posRest['pos_actualRest'])

    posRest['urlRest'] = {'base64': 'data:image/png;base64,' + base64.b64encode(bufRest.getvalue()).decode()}

    return JsonResponse(posRest)

def mov_imgDelanteRest(request):

    figRest, figStress, posRest  = resu.mov_img(1, 2)

    # Como enviaremos la imagen en bytes la guardaremos en un buffer
    bufRest = BytesIO()
    canvasRest = FigureCanvasAgg(figRest)
    canvasRest.print_png(bufRest)

    print("pos actual Rest", posRest['pos_actualRest'])

    posRest['urlRest'] = {'base64': 'data:image/png;base64,' + base64.b64encode(bufRest.getvalue()).decode()}

    return JsonResponse(posRest)

def mov_imgAtrasStress(request):

    figRest, figStress, posStress = resu.mov_img(2, 1)

    bufStress = BytesIO()
    canvasRest = FigureCanvasAgg(figStress)
    canvasRest.print_png(bufStress)

    posStress['urlStress'] = {'base64': 'data:image/png;base64,' + base64.b64encode(bufStress.getvalue()).decode()}

    return JsonResponse(posStress)

def mov_imgDelanteStress(request):

    figRest, figStress, posStress = resu.mov_img(2,2)

    bufStress = BytesIO()
    canvasRest = FigureCanvasAgg(figStress)
    canvasRest.print_png(bufStress)

    posStress['urlStress'] = {'base64': 'data:image/png;base64,' + base64.b64encode(bufStress.getvalue()).decode()}

    return JsonResponse(posStress)

def upload_image(request):
    print("Pantalla upload imagen")
    
    return render(request, "mf_webApp/upload.html")

def processing(request):

    # Ejecuta la funcion para procesar los datos de las imagenes
    apc.process_img()

    #resu.imprimir_imagenes(tipo=0)
    # carga los resultados de las imagenes
    resu.curve_print(1)

    return redirect("result")

def img_stress(request):

    figstress, pos= resu.imprimir_imagenesStress(tipo=0)

    bufStress = BytesIO()
    canvasStress = FigureCanvasAgg(figstress)
    canvasStress.print_png(bufStress)

    response = HttpResponse(bufStress.getvalue(), content_type='image/png')

    response['Content-Lenght'] = str(len(response.content))

    return response

def img_rest(request):

    fig, pos = resu.imprimir_imagenesRest(tipo=0)
    # Como enviaremos la imagen en bytes la guardaremos en un buffer
    bufRest = BytesIO()
    canvasRest = FigureCanvasAgg(fig)
    canvasRest.print_jpg(bufRest)
            
    response = HttpResponse(bufRest.getvalue(), content_type='image/jpg')

    response['Content-Lenght'] = str(len(response.content))

    return response

def restlist(request):

    return render(request, "mf_webApp/imageRest.html")

def result(request):

    figGraf, tabla = resu.curve_print(1)
    #print rest

    figrest, posRest = resu.imprimir_imagenesRest(tipo=0)
    # Como enviaremos la imagen en bytes la guardaremos en un buffer
    bufRest = BytesIO()
    canvasRest = FigureCanvasAgg(figrest)
    canvasRest.print_png(bufRest)

    #print stress

    figstress, posStress = resu.imprimir_imagenesStress(tipo=0)

    bufStress = BytesIO()
    canvasStress = FigureCanvasAgg(figstress)
    canvasStress.print_png(bufStress)

    #nuevo diccionario

    posImages = {**posRest, **posStress} 

    #Funciones para subir los datos de res y stress
    # Carga de datos del paciente

    name_paciente = apc.patient.s_name
    series_id_patient = apc.patient.s_series_id
    series_des_patient = apc.patient.s_series_desc
    study_patient = apc.patient.s_study_desc

    img, pos_actualRest, l_button, r_button = apc.img_rest.contenido[0].current_img(1,2)

    img, pos_actualStress, l_button, r_button = apc.img_stress.contenido[0].current_img(1,2)

    cant_rest = apc.img_rest.contenido[0].cantidad_imgs()
    cant_stress = apc.img_stress.contenido[0].cantidad_imgs()

    ww = apc.img_stress.contenido[0].ww
    wl = apc.img_stress.contenido[0].wl

    pos_rest = pos_actualRest + 1
    pos_stress = pos_actualStress + 1

    print("nombre paciente: ",name_paciente)
    #print("cantidad imagnenes: ",cantidad_img)

    data_patient = {"name_pat":name_paciente,"id_pat":series_id_patient,"series_des_pat":series_des_patient,
                    "study_pat":study_patient,"cant_stress":cant_stress,"cant_rest":cant_rest,"pos_rest":pos_rest,
                    "pos_stress":pos_stress, "ww":ww, "wl":wl}

    #data_patient['urlRest'] = {'base64': 'data:image/png;base64,' + base64.b64encode(bufRest.getvalue()).decode()}

    #data_patient['urlStress'] = {'base64': 'data:image/png;base64,' + base64.b64encode(bufStress.getvalue()).decode()}

    #  Loading Image Values : WW-WL-SLICE

    # predict_img()

    return render(request, "mf_webApp/result.html",data_patient)

def lista(request):

    return render(request, "mf_webApp/list.html")

