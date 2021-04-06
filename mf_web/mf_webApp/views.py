import base64
import os
import time
import traceback
from io import BytesIO
import pydicom
from datetime import datetime
import shutil

import imageio
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Agg')
from matplotlib.backends.backend_agg import FigureCanvasAgg
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages

from mf_webApp.models import Patient as pat, Curve as cur, CurveDivide as curd

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

        #print('FILE--->',str(request.FILES['imgInpStress']))

        if request.method == 'POST' and ('imgInpStress' in request.FILES) and request.FILES['imgInpStress'] and  str(request.FILES['imgInpStress'])[-3:].upper() =='DCM':
            #print("Soy ajax server Stress")            
            file = request.FILES['imgInpStress']
            #print('###################################')
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
                    plt.figure(figsize=(1,1))
                    plt.axis('off')
                
                   # print("Imagen leida Stress: ",dcpimg)
                    plt.imshow(dcpimg, cmap='gray')
                    #plt.colorbar()
                    figure = BytesIO()
                    plt.savefig(figure, format='jpg', dpi=300, facecolor="#222")

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
    # shutil.rmtree(position, ignore_errors=True) # Si funciona para borrar la carpeta
    return JsonResponse(d)

def upImgRest(request):
    start = time.time()
    d = dict()
    generic = dict()
    medinfo = dict()

    try:

       # print('FILE--->',str(request.FILES['imgInp'])[-3:])

        if request.method == 'POST' and ('imgInp' in request.FILES) and request.FILES['imgInp'] and  str(request.FILES['imgInp'])[-3:].upper() =='DCM':
            #print("Soy Ajax server 2 ")            
            file = request.FILES['imgInp']
            fs = FileSystemStorage()
            filename = fs.save(file.name, file)
            full_path_file = os.path.join(settings.MEDIA_ROOT, filename)
            

            generic['name'] = filename
            generic['size'] = os.path.getsize(full_path_file)
            try:
                if full_path_file[-3:].upper() == 'DCM':
                    #print("Full RUTA; ",full_path_file)
                    dcpimg = imageio.imread(full_path_file)
                    for keys in dcpimg.meta:

                        medinfo[keys] = str(dcpimg.meta[keys])

                    if len(dcpimg.shape) ==4:
                        dcpimg = dcpimg[0,0]
                    elif len(dcpimg.shape) ==3:
                        dcpimg = dcpimg[0]

                    #print("Imagen leida REST: ",dcpimg)

                    fig = plt.gcf()
                    plt.figure(figsize=(1,1))
                    plt.axis('off')
                    
                    plt.imshow(dcpimg, cmap='gray')
                    #plt.colorbar()
                    figure = BytesIO()
                    plt.savefig(figure, format='jpg', dpi=300, facecolor="#222")

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

def particion(request):

    if request.method == 'POST':
        pxRest = request.POST['xRest']
        pyRest = request.POST['yRest']
        pxStress= request.POST['xStress']
        pyStress = request.POST['yStress']
        resu.pressed_rest(int(pxRest),int(pyRest))
        resu.pressed_stress(int(pxStress),int(pyStress))
        print("partition")

        resu.punto_tocado()

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

def cambiar_particion(request):
    if request.method == 'POST':
        part = request.POST['particion']
        zona = request.POST['zona']
        print ("zona",zona)
        resu.cambio_particion(int(part),int(zona))

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

    #print("pos actual Rest", posImages['pos_actualRest'])
    #print("pos actual Stress", posImages['pos_actualStress'])

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

    #print("pos actual Rest", posRest['pos_actualRest'])

    posRest['urlRest'] = {'base64': 'data:image/png;base64,' + base64.b64encode(bufRest.getvalue()).decode()}

    return JsonResponse(posRest)

def mov_imgDelanteRest(request):

    figRest, figStress, posRest  = resu.mov_img(1, 2)

    # Como enviaremos la imagen en bytes la guardaremos en un buffer
    bufRest = BytesIO()
    canvasRest = FigureCanvasAgg(figRest)
    canvasRest.print_png(bufRest)

    #print("pos actual Rest", posRest['pos_actualRest'])

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

    p = pat(patient=name_paciente, study_desc=study_patient,series_desc=series_des_patient,series_id=series_id_patient)
    p.save()

    id = p.id

    img, pos_actualRest, l_button, r_button = apc.img_rest.contenido[0].current_img(1,2)

    img, pos_actualStress, l_button, r_button = apc.img_stress.contenido[0].current_img(1,2)

    cant_rest = apc.img_rest.contenido[0].cantidad_imgs()
    cant_stress = apc.img_stress.contenido[0].cantidad_imgs()

    ww = apc.img_stress.contenido[0].ww
    wl = apc.img_stress.contenido[0].wl

    pos_rest = pos_actualRest + 1
    pos_stress = pos_actualStress + 1

    #print("nombre paciente: ",name_paciente)
    #print("cantidad imagnenes: ",cantidad_img)


    data_patient = {"name_pat":name_paciente,"id_pat":series_id_patient,"series_des_pat":series_des_patient,
                    "study_pat":study_patient,"cant_stress":cant_stress,"cant_rest":cant_rest,"pos_rest":pos_rest,
                    "pos_stress":pos_stress, "ww":ww, "wl":wl, "id_patient": id }


    #data_patient['urlRest'] = {'base64': 'data:image/png;base64,' + base64.b64encode(bufRest.getvalue()).decode()}

    #data_patient['urlStress'] = {'base64': 'data:image/png;base64,' + base64.b64encode(bufStress.getvalue()).decode()}

    #  Loading Image Values : WW-WL-SLICE

    # predict_img()

    return render(request, "mf_webApp/result.html",data_patient)


def dataList(request):

    return render(request, "mf_webApp/listData.html")

def lista(request):

    paciente = pat.objects.all()

    curva = cur.objects.all()

    ctxp = {"pacientes":paciente}
    ctxc = {"curvas":curva}

    ctx = {**ctxp, **ctxc}

    return render(request, "mf_webApp/list.html",ctx)

def listaResultado(request):

    paciente = pat.objects.all()

    curva = cur.objects.all()

    ctxp = {"pacientes":paciente}
    ctxc = {"curvas":curva}

    ctx = {**ctxp, **ctxc}

    return render(request, "mf_webApp/listResult.html",ctx)

 
def saveData(request):

    #Guardar los resultados en la base de datos

    figGraf2, tablaEp = resu.curve_print(2)
    figGraf3, tablaEn = resu.curve_print(3)
    figGraf1, tablaBl = resu.curve_print(1)

    id = request.POST['id_patient']

    obj = pat.objects.get(id=int(id))

    blood = cur(id_patient= obj, zone="Blood", area_rest= float(tablaBl['area_rest']), peak_rest=float(tablaBl['res_peak_rest']),
                slope_rest=float(tablaBl['res_pend_rest']),area_stress=float(tablaBl['area_stress']),peak_stress=float(tablaBl['res_peak_stress']),
                slope_stress= float(tablaBl['res_pend_stress']),coefficent= float(tablaBl['res_ratio_value']))
    blood.save()

    epi = cur(id_patient= obj, zone="Epicardium", area_rest= float(tablaEp['area_rest']), peak_rest=float(tablaEp['res_peak_rest']),
                slope_rest=float(tablaEp['res_pend_rest']),area_stress=float(tablaEp['area_stress']),peak_stress=float(tablaEp['res_peak_stress']),
                slope_stress= float(tablaEp['res_pend_stress']),coefficent= float(tablaEp['res_ratio_value']))
    epi.save()

    endo = cur(id_patient= obj, zone="Endocardium", area_rest= float(tablaEn['area_rest']), peak_rest=float(tablaEn['res_peak_rest']),
                slope_rest=float(tablaEn['res_pend_rest']),area_stress=float(tablaEn['area_stress']),peak_stress=float(tablaEn['res_peak_stress']),
                slope_stress= float(tablaEn['res_pend_stress']),coefficent= float(tablaEn['res_ratio_value']))
    endo.save()

    messages.success(request, "Usuario guardado correctamente")


    id_p = dict (id_patient = id)


   # id_p =  {"id_patient": str(p.id)}

    return JsonResponse(id_p)

def delete(request, id_patient):

    id = id_patient

    paciente = pat.objects.get(id=int(id))

    curva = cur.objects.all()
    paciente.delete()
    ctxp = {"pacientes":paciente}
    ctxc = {"curvas":curva}

    ctx = {**ctxp, **ctxc}

    return redirect("listPatient")

def saveDataDivide(request):

    #Guardar los resultados de la division en la base de datos

    tablaBl2 = resu.cambio_particion(2,1)
    tablaEp2 = resu.cambio_particion(2,2)
    tablaEn2 = resu.cambio_particion(2,3)

    tablaBl3 = resu.cambio_particion(3,1)
    tablaEp3 = resu.cambio_particion(3,2)
    tablaEn3 = resu.cambio_particion(3,3)

    tablaBl4 = resu.cambio_particion(4,1)
    tablaEp4 = resu.cambio_particion(4,2)
    tablaEn4 = resu.cambio_particion(4,3)

    tablaEp1 = resu.cambio_particion(1,2)
    tablaEn1 = resu.cambio_particion(1,3)
    tablaBl1 = resu.cambio_particion(1,1) 
    
    id = request.POST['id_patient']

    obj = pat.objects.get(id=int(id))

    part1_1 = curd(id_patient= obj, zone="Blood", partition=1, area_rest= float(tablaBl1['area_rest']), peak_rest=float(tablaBl1['res_peak_rest']),
                   slope_rest=float(tablaBl1['res_pend_rest']),area_stress=float(tablaBl1['area_stress']),peak_stress=float(tablaBl1['res_peak_stress']),
                   slope_stress= float(tablaBl1['res_pend_stress']),coefficent= float(tablaBl1['res_ratio_value']))
    part1_1.save()

    part1_2 = curd(id_patient= obj, zone="Epicardium", partition=1, area_rest= float(tablaEp1['area_rest']), peak_rest=float(tablaEp1['res_peak_rest']),
                   slope_rest=float(tablaEp1['res_pend_rest']),area_stress=float(tablaEp1['area_stress']),peak_stress=float(tablaEp1['res_peak_stress']),
                   slope_stress= float(tablaEp1['res_pend_stress']),coefficent= float(tablaEp1['res_ratio_value']))
    part1_2.save()

    part1_3 = curd(id_patient= obj, zone="Endocardium", partition=1, area_rest= float(tablaEn1['area_rest']), peak_rest=float(tablaEn1['res_peak_rest']),
                   slope_rest=float(tablaEn1['res_pend_rest']),area_stress=float(tablaEn1['area_stress']),peak_stress=float(tablaEn1['res_peak_stress']),
                   slope_stress= float(tablaEn1['res_pend_stress']),coefficent= float(tablaEn1['res_ratio_value']))
    part1_3.save()


    part2_1 = curd(id_patient= obj, zone="Blood", partition=2, area_rest= float(tablaBl2['area_rest']), peak_rest=float(tablaBl2['res_peak_rest']),
                   slope_rest=float(tablaBl2['res_pend_rest']),area_stress=float(tablaBl2['area_stress']),peak_stress=float(tablaBl2['res_peak_stress']),
                   slope_stress= float(tablaBl2['res_pend_stress']),coefficent= float(tablaBl2['res_ratio_value']))
    part2_1.save()

    part2_2 = curd(id_patient= obj, zone="Epicardium", partition=2, area_rest= float(tablaEp2['area_rest']), peak_rest=float(tablaEp2['res_peak_rest']),
                   slope_rest=float(tablaEp2['res_pend_rest']),area_stress=float(tablaEp2['area_stress']),peak_stress=float(tablaEp2['res_peak_stress']),
                   slope_stress= float(tablaEp2['res_pend_stress']),coefficent= float(tablaEp2['res_ratio_value']))
    part2_2.save()

    part2_3 = curd(id_patient= obj, zone="Endocardium", partition=2, area_rest= float(tablaEn2['area_rest']), peak_rest=float(tablaEn2['res_peak_rest']),
                   slope_rest=float(tablaEn2['res_pend_rest']),area_stress=float(tablaEn2['area_stress']),peak_stress=float(tablaEn2['res_peak_stress']),
                   slope_stress= float(tablaEn2['res_pend_stress']),coefficent= float(tablaEn2['res_ratio_value']))
    part2_3.save()

    part3_1 = curd(id_patient= obj, zone="Blood", partition=3, area_rest= float(tablaBl3['area_rest']), peak_rest=float(tablaBl3['res_peak_rest']),
                   slope_rest=float(tablaBl3['res_pend_rest']),area_stress=float(tablaBl3['area_stress']),peak_stress=float(tablaBl3['res_peak_stress']),
                   slope_stress= float(tablaBl3['res_pend_stress']),coefficent= float(tablaBl3['res_ratio_value']))
    part3_1.save()

    part3_2 = curd(id_patient= obj, zone="Epicardium", partition=3, area_rest= float(tablaEp3['area_rest']), peak_rest=float(tablaEp3['res_peak_rest']),
                   slope_rest=float(tablaEp3['res_pend_rest']),area_stress=float(tablaEp3['area_stress']),peak_stress=float(tablaEp3['res_peak_stress']),
                   slope_stress= float(tablaEp3['res_pend_stress']),coefficent= float(tablaEp3['res_ratio_value']))
    part3_2.save()

    part3_3 = curd(id_patient= obj, zone="Endocardium", partition=3, area_rest= float(tablaEn3['area_rest']), peak_rest=float(tablaEn3['res_peak_rest']),
                   slope_rest=float(tablaEn3['res_pend_rest']),area_stress=float(tablaEn3['area_stress']),peak_stress=float(tablaEn3['res_peak_stress']),
                   slope_stress= float(tablaEn3['res_pend_stress']),coefficent= float(tablaEn3['res_ratio_value']))
    part3_3.save() 

    part4_1 = curd(id_patient= obj, zone="Blood", partition=4, area_rest= float(tablaBl4['area_rest']), peak_rest=float(tablaBl4['res_peak_rest']),
                   slope_rest=float(tablaBl4['res_pend_rest']),area_stress=float(tablaBl4['area_stress']),peak_stress=float(tablaBl4['res_peak_stress']),
                   slope_stress= float(tablaBl4['res_pend_stress']),coefficent= float(tablaBl4['res_ratio_value']))
    part4_1.save() 

    part4_2 = curd(id_patient= obj, zone="Epicardium", partition=4, area_rest= float(tablaEp4['area_rest']), peak_rest=float(tablaEp4['res_peak_rest']),
                   slope_rest=float(tablaEp4['res_pend_rest']),area_stress=float(tablaEp4['area_stress']),peak_stress=float(tablaEp4['res_peak_stress']),
                   slope_stress= float(tablaEp4['res_pend_stress']),coefficent= float(tablaEp4['res_ratio_value']))
    part4_2.save()

    part4_3 = curd(id_patient= obj, zone="Endocardium", partition=4, area_rest= float(tablaEn4['area_rest']), peak_rest=float(tablaEn4['res_peak_rest']),
                   slope_rest=float(tablaEn4['res_pend_rest']),area_stress=float(tablaEn4['area_stress']),peak_stress=float(tablaEn4['res_peak_stress']),
                   slope_stress= float(tablaEn4['res_pend_stress']),coefficent= float(tablaEn4['res_ratio_value']))
    part4_3.save()

    return JsonResponse({"respuesta": "si funciona"})

def newPatient(request):
    apc.new_patient()

    return redirect("upload")

def listaResultadoDivision(request):

    paciente = pat.objects.all()

    curvad = curd.objects.all()

    ctxp = {"pacientes":paciente}
    ctxc = {"curvasd":curvad}

    ctx = {**ctxp, **ctxc}

    return render(request, "mf_webApp/listDivide.html",ctx)




