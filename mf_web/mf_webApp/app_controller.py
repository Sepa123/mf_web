from tkinter import *

from mf_webApp.model.paq_img_model import PaqImgModel
from mf_webApp.model.patient_data import Patient
from mf_webApp.res import colors, dim, string
import numpy as np
import os

import pickle

#from screen.results_screen import ResultScreen
from mf_webApp.screen.upload_image import UploadImage
#from screen.upload_image import UploadImage
from mf_webApp.segmentation.model.input_data.input_app import InputDataApp
from mf_webApp.segmentation.model.model.models.u_net_fine_tuning import U_net_fine_tune as U_net


def predict_ztxy(model, img_array):
    n_timesteps = img_array.shape[1]
    img_length = img_array.shape[2]
    img_flatten = img_array.reshape(-1, img_length, img_length)
    img_flatten = img_flatten[..., np.newaxis]
    results_flatten = model.predict(img_flatten)
    results_array = results_flatten.reshape(
        -1, n_timesteps, img_length, img_length)
    return results_array


class AppController:

    def __init__(self):

        self.img_rest = PaqImgModel("Rest")
        self.img_stress = PaqImgModel("Stress")

        self.dir_img_rest = ""
        self.dir_img_stress = ""

        self.patient = Patient()

    def process_rest_img(self, path_img):
        """
        This function saves the dcm images uploaded to the corresponding list.

        Returns boolean, if it can display the button of the next process, which is responsible for
        doing the image processing

        Parameters:
        img -- list of image paths
        """
        self.dir_img_rest = path_img
        print(path_img)
        # self.predict_img()
        return True

    def process_stress_img(self, path_img):
        """
        This function saves the dcm images uploaded to the corresponding list.

        Returns boolean, if it can display the button of the next process, which is in charge of doing the
        processing of the image

        Parameters:
        img -- list of image paths
        """
        self.dir_img_stress = path_img
        print(path_img)
        return True

    def all_img(self):
        if self.img_rest.esta_vacio() or self.img_stress.esta_vacio():
            return False
        else:
            return True

    def predict_img(self):
        
        print(os.getcwd() + '\\mf_webApp\\segmentation\\checkpoint\\model')
        
        #C:\Users\Seba\Desktop\Myocardial Perfusion and segmentation\Interface\segmentation\checkpoint\model

        checkpoint_path = 'C:\\Users\\Seba\\Desktop\\Myocardial Perfusion and segmentation\\Interface\\segmentation\\checkpoint\\model'
        #checkpoint_path = os.getcwd() + '\\mf_webApp\\segmentation\\checkpoint\\model'

        print("RUTA CARGADA CORRECTAMENTE....................................")

        model = U_net()
        model.saver.restore(model.sess, checkpoint_path)

        print("modelo CARGADO CORRECTAMENTE..................................")
        dataset_stress = InputDataApp(self.dir_img_stress)
        data_extract_stress, frames_drop_stress = dataset_stress.get_data()
        print("DATA CARGADA..................................")

        pred_stress = predict_ztxy(model, data_extract_stress)

        print("PREDICT_ZTXY STRESS..................................")
        print("length de data_extract_stress",data_extract_stress.shape)
        print("length de pred_stress",pred_stress.shape)
        print("length de pred_stress",frames_drop_stress)

        if frames_drop_stress == 0:
            print("NO EXISTEN frame drops EN STRESS..................................")
            delete = False
        else:
            print("SI EXISTEN frame drops EN STRESS..................................")
            delete = True

        print("AGREGANDO PREDICT DE STRESS..................................")
        self.img_stress.agregar_predict(pred_stress, delete)
        print("AGREGADO CORRECTAMENTE PREDICT DE STRESS..................................")

        pass

        dataset_rest = InputDataApp(self.dir_img_rest)
        data_extract_rest, frames_drop_rest = dataset_rest.get_data()
        pred_rest = predict_ztxy(model, data_extract_rest)
        print("PREDICT_ZTXY REST...................................................")
        if frames_drop_rest == 0:
            print("NO EXISTEN Frame drops EN Rest..................................")
            delete = False
        else:
            print("SI EXISTEN frame drops EN Rest..................................")
            delete = True
        self.img_rest.agregar_predict(pred_rest, delete)


    def process_img(self):
        
        print("processing")
        self.predict_img()
        print("PROCESSION LISTA")
        file_pk = open('paq_stress.obj', 'wb')
        pickle.dump(self.img_stress, file_pk)
        file_pk.close()
        file_pk2 = open('paq_rest.obj', 'wb')
        pickle.dump(self.img_rest, file_pk2)
        file_pk2.close()

        pass

   # def to_result_screen(self):
    #    self.clean_screen()
     #   res_screen = ResultScreen(self.frame_data, self.frame_opt, self.frame_img, self)
      #  res_screen.start()

 #   def new_patient(self):
  #      self.clean_screen_pack()
   #     frame_ul = UploadImage(frame_lateral=self.frame_data, frame_opciones=self.frame_opt,
    #                           frame_principal=self.frame_img, parent=self)
     #   frame_ul.start()

#        self.img_rest = PaqImgModel("Rest")
 #       self.img_stress = PaqImgModel("Stress")
#
 #       self.dir_img_rest = ""
  #      self.dir_img_stress = ""

   #     self.patient = Patient()