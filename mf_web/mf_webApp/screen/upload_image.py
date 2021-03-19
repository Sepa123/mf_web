from os import listdir, path as pt
#from tkinter import *
#from tkinter import filedialog
#import tkinter.font as font
import PIL.Image
import PIL.ImageTk
import pydicom

from mf_webApp.model.imagen_model import Imagen
#from mmodel.imagen_model import Imagen
#from res import dim, string, colors
from mf_webApp.utils.dicom_utils import refactor_dicom_file
#from utils.dicom_utils import refactor_dicom_file
#from utils.tooltip_utils import CreateToolTip


class UploadImage:

    def __init__(self, parent):
        self.parent = parent

    def subir_img_rest(self):
        print("START UPLOAD IMG REST")
        #path_imgs = filedialog.askdirectory(initialdir="/", title=string.FileDialog_Rest)
        ruta_img_rest= 'C:/Users/Seba/Desktop/Test Images/5342 Rest/series'
        path_imgs = ruta_img_rest
        self.parent.dir_img_rest = path_imgs
        print("", self.parent.dir_img_rest )
        self.parent.img_rest.reiniciar_paq()
        self.process_path_img(path_imgs, self.parent.img_rest)
        cantidad_img = self.parent.img_rest.cantidad_imagenes()
        #self.titulo_rest.config(text="Images in rest: " + str(cantidad_img) + " total")
        #self.print_img(1)

    def subir_img_stress(self):
        print("START UPLOAD IMG STRESS")
        #path_imgs = filedialog.askdirectory(initialdir="/", title=string.FileDialog_Stress)
        ruta_img_stress = 'C:/Users/Seba/Desktop/Test Images/5342 Stress/series'
        path_imgs = ruta_img_stress
        self.parent.dir_img_stress = path_imgs
        print(self.parent.dir_img_stress)
        self.parent.img_stress.reiniciar_paq()
        self.process_path_img(path_imgs, self.parent.img_stress)
        cantidad_img = self.parent.img_stress.cantidad_imagenes()
        #self.titulo_stress.config(text="Images in stress: " + str(cantidad_img) + " total")
        #self.print_img(2)


    def process_path_img(self, path, paq):
        lista_file = listdir(path)
        lista_file.sort()
        primero = True
        for file in lista_file:
            filename, file_extension = pt.splitext(file)
            if file_extension == ".dcm":
                archivo = pydicom.dcmread(path+"/"+file)
                if primero:
                    self.agregar_paciente(archivo, paq)
                    primero = False
                imagen = Imagen(
                    image_size=str(archivo.Rows) + 'x' + str(archivo.Columns),
                    view_size="",
                    wl=archivo.WindowCenter,
                    ww=archivo.WindowWidth,
                    mouse_mm="",
                    mouse_px="",
                    zoom="",
                    angle="",
                    image_position=archivo.ImagePositionPatient,
                    compression="",
                    thickness=archivo.SliceThickness,
                    location=archivo.SliceLocation,
                    mri="",
                    field_strenght=archivo.MagneticFieldStrength,
                    image_acq_time=archivo.AcquisitionTime,
                    pixel_array=archivo.pixel_array
                )
                paq.agregar_img(imagen)
        paq.get_array_slice()

    #def print_img(self, posc):
        #if posc == 1:
            #img = self.parent.img_rest.contenido[0].imgs[0].pixel_array

            #img = refactor_dicom_file(img,
                                      #self.parent.img_rest.contenido[0].imgs[0].ww,
                                      #self.parent.img_rest.contenido[0].imgs[0].wl)
            #img = PIL.Image.frombytes('L', (img.shape[1], img.shape[0]),
                                            #img.astype('b').tostring())
            #img = PIL.ImageTk.PhotoImage(img)
            #self.canvas_rest.create_image(256, 256, image=img)
            #self.canvas_rest.photo_reference = img

        #elif posc == 2:
            #img = self.parent.img_stress.contenido[0].imgs[0].pixel_array
            #mg = refactor_dicom_file(img,
                                      #self.parent.img_stress.contenido[0].imgs[0].ww,
                                      #self.parent.img_stress.contenido[0].imgs[0].wl)
            #img = PIL.Image.frombytes('L', (img.shape[1], img.shape[0]),
                                      #img.astype('b').tostring())
            #img = PIL.ImageTk.PhotoImage(img)
            #self.canvas_stress.create_image(256, 256, image=img)
            #self.canvas_stress.photo_reference = img
        #pass

    #def imagen_sobre_canvas(self, parent, arr, x, y):
        #image = Label(parent)
        #img_creada = PIL.Image.frombytes('L', (arr.shape[1], arr.shape[0]), arr.astype('b').tostring())
        #img_creada = PIL.ImageTk.PhotoImage(img_creada)
        #image.place(x=x,
                    #y=y,
                    #width=dim.WIDTH_UI_RES_IMG_REST,
                    #height=int((256 * dim.WIDTH_IMG_UL / 208)))
        #image.config(image=img_creada)
        #image.photo_reference = img_creada

    def agregar_paciente(self, archivo, paq):
        if paq.tipo == "Rest":
            self.parent.patient.r_name = str(archivo.PatientID)
            self.parent.patient.r_series_desc = str(archivo.SeriesDescription)
            self.parent.patient.r_series_id = str(archivo.SeriesNumber)
            self.parent.patient.r_study_desc = str(archivo.StudyDescription)
        elif paq.tipo == "Stress":
            self.parent.patient.s_name = str(archivo.PatientID)
            self.parent.patient.s_series_desc = str(archivo.SeriesDescription)
            self.parent.patient.s_series_id = str(archivo.SeriesNumber)
            self.parent.patient.s_study_desc = str(archivo.StudyDescription)
