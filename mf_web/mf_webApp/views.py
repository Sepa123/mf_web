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
from .segmentation.model.model.models.u_net_fine_tuning import U_net_fine_tune as U_net
from .segmentation.model.input_data.input_app import InputDataApp

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

    #print(colored(d, 'red'))
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


#def predict_ztxy(model, img_array):
   #n_timesteps = img_array.shape[1]
    #img_length = img_array.shape[2]
    #img_flatten = img_array.reshape(-1, img_length, img_length)
    #img_flatten = img_flatten[..., np.newaxis]
    #results_flatten = model.predict(img_flatten)
    #results_array = results_flatten.reshape(
     #   -1, n_timesteps, img_length, img_length)
    #return results_array

#def predict_img():
        
        #print(os.getcwd() + '\\mf_webApp\\segmentation\\checkpoint\\model')
        #checkpoint_path = os.getcwd() + '\\mf_webApp\\segmentation\\checkpoint\\model'

        #model = U_net()
        #model.saver.restore(model.sess, checkpoint_path)

        #dataset_stress = InputDataApp('C:\\Users\\Seba\\Desktop\\Test Images\\5342 Stress')
        #data_extract_stress, frames_drop_stress = dataset_stress.get_data()
        #pred_stress = predict_ztxy(model, data_extract_stress)
        #if frames_drop_stress == 0:
         #   delete = False
        #else:
         #   delete = True
        #img_stress = PaqImgModel("Stress")
        #img_stress.agregar_predict(pred_stress, delete)
        #pass
        #dataset_rest = InputDataApp('C:\\Users\\Seba\\Desktop\\Test Images\\5342 Stress')
        #data_extract_rest, frames_drop_rest = dataset_rest.get_data()
        #pred_rest = predict_ztxy(model, data_extract_rest)
        #if frames_drop_rest == 0:
         #   delete = False
        #else:
         #   delete = True
        #self.img_rest.agregar_predict(pred_rest, delete)
        #print("Esto segmentaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")

def result(request):

    print("Pantalla Resultados de imagen")
    apc = AppController()

    upl = UploadImage(apc)

    upl.subir_img_rest()
    upl.subir_img_stress()

    #ruta = 'C:\\Users\\Seba\\Desktop\\Test Images\\5342 Rest\\series'
    #ruta = 'C:\\Users\\Seba\\Desktop\\Test Images\\5342 Stress\\series'
    # C:\\Users\\Seba\\Desktop\\Test Images\\imgTest1

    #apc.process_rest_img(ruta)
    #apc.process_stress_img(ruta)

    apc.process_img()

    print("Tamos daos pal exito")

    name_paciente = apc.patient.s_name
    series_id_patient = apc.patient.s_series_id
    series_des_patient = apc.patient.s_series_desc
    study_patient = apc.patient.s_study_desc

    data_patient = {"name_pat":name_paciente,"id_pat":series_id_patient,"series_des_pat":series_des_patient,
                    "study_pat":study_patient,}

    print("Nombre paciente: ",name_paciente)
    print("Series id paciente: ",series_id_patient)
    print("series des paciente: ",series_des_patient)
    print("estudio paciente: ",study_patient) 


#  Loading Image Values : WW-WL-SLICE
    #valores_slice = apc.parent.img_stress.get_array_slice()
    #self.valor_slice['values'] = valores_slice
    #self.valor_slice.bind("<<ComboboxSelected>>", self.sle_cbox)
    #self.valor_slice.current(0)
    #self.valor_wl.insert(0, str(self.parent.img_stress.contenido[self.slice_select_stress].wl))
    #self.valor_ww.insert(0, str(self.parent.img_stress.contenido[self.slice_select_stress].ww))

    #  Loading Display Images
    #self.imprimir_imagenes(tipo=0)
    #self.print_img_prediccion(tipo=0)

   # predict_img()

    return render(request, "mf_webApp/result.html",data_patient)

def lista(request):

    return render(request, "mf_webApp/list.html")

