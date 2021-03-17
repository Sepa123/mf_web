from tkinter import *

from model.exportacion_model import ExportPDF
from res import dim, string, colors
from tkinter import ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from PIL import Image, ImageTk


import pickle

from utils.dicom_utils import refactor_dicom_file
from utils.tkinter_img import img2rgba
from utils.tooltip_utils import CreateToolTip
from utils.valores_curvas import *


class ResultScreen:

    def __init__(self, frame_lateral, frame_opciones, frame_principal, parent):
        self.frame_lateral = frame_lateral
        self.frame_opciones = frame_opciones
        self.frame_princial = frame_principal
        self.parent = parent
        # e aqui en adelante se borra todo

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
        
    def start(self):
        self.iniciar_opciones()
        self.iniciar_lateral()
        self.iniciar_principal()

        self.iniciar_data()

    

    def iniciar_data(self):

        #  Patient data upload
        name_paciente = self.parent.patient.s_name
        series_id_patient = self.parent.patient.s_series_id
        series_des_patient = self.parent.patient.s_series_desc
        study_patient = self.parent.patient.s_study_desc

        print("Nombre paciente: ",name_paciente)
        print("Series id paciente: ",series_id_patient)
        print("series des paciente:",series_des_patient)
        print("estudio paciente:",study_patient)
        self.paciente.config(text=(self.paciente.cget("text")+name_paciente))
        self.serie_id.config(text=(self.serie_id.cget("text") + series_id_patient))
        self.serie_desc.config(text=(self.serie_desc.cget("text") + series_des_patient))
        self.study_desc.config(text=(self.study_desc.cget("text") + study_patient))

        #  Loading of old data
        file1 = open('paq_rest.obj', 'rb')
        self.parent.img_rest = pickle.load(file1)
        file2 = open('paq_stress.obj', 'rb')
        self.parent.img_stress = pickle.load(file2)

        #  Loading Image Values : WW-WL-SLICE
        valores_slice = self.parent.img_stress.get_array_slice()
        self.valor_slice['values'] = valores_slice
        self.valor_slice.bind("<<ComboboxSelected>>", self.sle_cbox)
        self.valor_slice.current(0)
        self.valor_wl.insert(0, str(self.parent.img_stress.contenido[self.slice_select_stress].wl))
        self.valor_ww.insert(0, str(self.parent.img_stress.contenido[self.slice_select_stress].ww))

        #  Loading Display Images
        self.imprimir_imagenes(tipo=0)
        self.print_img_prediccion(tipo=0)

        #  Loading of Canvas touch functions - Images
        self.img_res.bind("<Button-1>", self.pressed_rest)
        self.img_stress.bind("<Button-1>", self.pressed_stress)

        #  Loading curve data
        self.curva_print(1)
        pass

    def pressed_rest(self, event):
        if self.habilitar_punto_rest == 1:
            if self.punto_rest_canvas == "":
                self.punto_rest_canvas = self.img_res.create_oval(event.x-3,
                                                                  event.y-3,
                                                                  event.x+3,
                                                                  event.y+3,
                                                                  fill=colors.punto)
            else:
                self.img_res.delete(self.punto_rest_canvas)
                self.punto_rest_canvas = self.img_res.create_oval(event.x-3,
                                                                  event.y-3,
                                                                  event.x+3,
                                                                  event.y+3,
                                                                  fill=colors.punto)
            self.punto_rest = [int(event.x/2), int(event.y/2)]
            if self.punto_rest is not None and self.punto_stress is not None:
                self.boton_export.config(state=NORMAL)
        else:
            pass

    def pressed_stress(self, event):
        if self.habilitar_punto_stress == 1:
            print(self.punto_stress_canvas)
            if self.punto_stress_canvas == "":
                self.punto_stress_canvas = self.img_stress.create_oval(event.x - 3,
                                                                       event.y - 3,
                                                                       event.x + 3,
                                                                       event.y + 3,
                                                                       fill=colors.punto)
            else:
                self.img_stress.delete(self.punto_stress_canvas)
                self.punto_stress_canvas = self.img_stress.create_oval(event.x - 3,
                                                                       event.y - 3,
                                                                       event.x + 3,
                                                                       event.y + 3,
                                                                       fill=colors.punto)
            self.punto_stress = [int(event.x/2), int(event.y/2)]
            if self.punto_rest is not None and self.punto_stress is not None:
                self.boton_export.config(state=NORMAL)
        else:
            pass

    def recarga_img(self):
        ww_obt = self.valor_ww.get()
        wl_obt = self.valor_wl.get()
        self.parent.img_stress.contenido[self.slice_select_stress].wl = int(wl_obt)
        self.parent.img_rest.contenido[self.slice_select_rest].wl = int(wl_obt)
        self.parent.img_stress.contenido[self.slice_select_stress].ww = int(ww_obt)
        self.parent.img_rest.contenido[self.slice_select_rest].ww = int(ww_obt)
        self.imprimir_imagenes(tipo=0)

    def sle_cbox(self, event):
        valor_select = str(self.valor_slice.get()).split(':')[0]
        self.slice_select_rest = int(valor_select) - 1
        self.slice_select_stress = int(valor_select) - 1
        self.imprimir_imagenes(tipo=0)
        self.curva_print(1)
        pass

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
                self.parent.img_rest.contenido[int(self.slice_select_rest)].disminuir_pos()
                self.imprimir_imagenes(tipo=1)
            elif direccion == 2:
                self.parent.img_rest.contenido[int(self.slice_select_rest)].aumentar_pos()
                self.imprimir_imagenes(tipo=1)
        elif paquete == 2:
            if direccion == 1:
                self.parent.img_stress.contenido[int(self.slice_select_stress)].disminuir_pos()
                self.imprimir_imagenes(tipo=2)
            elif direccion == 2:
                self.parent.img_stress.contenido[int(self.slice_select_stress)].aumentar_pos()
                self.imprimir_imagenes(tipo=2)

    def set_init_fin(self, paquete, opcion):
        """
        Set the value of the start and end frame of an image. Helps to discard values
        param packet: packet of images to be moved
            1: rest
            2: stress
        param option: Option to modify
            1: Init
            2: End
        return:
        """
        if paquete == 1:
            if opcion == 1:
                self.parent.img_rest.contenido[int(self.slice_select_rest)].set_init_current()
            elif opcion == 2:
                self.parent.img_rest.contenido[int(self.slice_select_rest)].set_fin_current()
            self.curva_print(1)
        elif paquete == 2:
            if opcion == 1:
                self.parent.img_stress.contenido[int(self.slice_select_rest)].set_init_current()
            elif opcion == 2:
                self.parent.img_stress.contenido[int(self.slice_select_rest)].set_fin_current()
            self.curva_print(1)

    def imprimir_imagenes(self, tipo=0):
        """
        Displays the images in the corresponding area of the canvas. You can display 1 of the 2 images, or update both, depending on the
        both, depending on the parameters entered
        param type: Determines which of the images will be displayed
            0: Both images
            1: Display img Rest
            2: Display img Stress
        return: images displayed in the canvas
        """
        if tipo == 0 or tipo == 1:
            #  Rest printed
            x, y = self.parent.img_rest.contenido[self.slice_select_rest].imgs[0].pixel_array.shape
            height = int(dim.height_img_res_screen)
            width = int(height*y/x)
            img, pos_actual, l_button, r_button = self.parent.img_rest.contenido[
                int(self.slice_select_rest)].current_img(width, height)
            img = ImageTk.PhotoImage(img)
            self.imagen_rest = img
            self.img_res.create_image(dim.w_mid_img, dim.h_mid_img, image=self.imagen_rest)
            cantidad_img = self.parent.img_rest.contenido[self.slice_select_rest].cantidad_imgs()
            self.info_res_center.config(text="Image " + str(pos_actual+1) + " of " + str(cantidad_img))
            if l_button:
                self.izq_rest.config(state=NORMAL)
            else:
                self.izq_rest.config(state=DISABLED)
            if r_button:
                self.der_rest.config(state=NORMAL)
            else:
                self.der_rest.config(state=DISABLED)
        if tipo == 0 or tipo == 2:
            #  Stress printed
            x, y = self.parent.img_stress.contenido[self.slice_select_stress].imgs[0].pixel_array.shape
            height = int(dim.height_img_res_screen)
            width = int(height * y / x)
            img, pos_actual, l_button, r_button = self.parent.img_stress.contenido[
                int(self.slice_select_stress)].current_img(width, height)
            img = ImageTk.PhotoImage(img)
            self.imagen_stress = img
            self.img_stress.create_image(dim.w_mid_img, dim.h_mid_img, image=self.imagen_stress)
            cantidad_img = self.parent.img_stress.contenido[self.slice_select_stress].cantidad_imgs()
            self.info_stress_center.config(text="Image " + str(pos_actual + 1) + " of " + str(cantidad_img))
            if l_button:
                self.izq_stress.config(state=NORMAL)
            else:
                self.izq_stress.config(state=DISABLED)
            if r_button:
                self.der_stress.config(state=NORMAL)
            else:
                self.der_stress.config(state=DISABLED)
        self.print_img_prediccion(tipo=tipo)

    def exportacion_pdf(self):
        if self.habilitado_para_div == 0 or self.habilitado_para_div == 2:
            self.expotar_data_pdf()
        elif self.habilitado_para_div == 1:
            self.habilitado_para_div = 2
            self.boton_particion.config(text="Complete Section")
            self.boton_export.config(text=string.boton_export)
            self.boton_volver.config(text=string.boton_volver)
            self.b_particion_ttip.change_text(string.tt_particion)
            self.b_export_ttip.change_text(string.tt_export)
            self.b_volver_ttip.change_text(string.tt_volver)
            self.punto_tocado()

    def particionar(self):
        if self.habilitado_para_div == 0:
            print("Partition")
            self.habilitado_para_div = 1
            self.habilitar_punto_stress = 1
            self.habilitar_punto_rest = 1
            self.boton_volver.config(text="Cancel")
            self.boton_export.config(text="Confirm",
                                     state=DISABLED)
            self.boton_particion.config(text="Delete Points")
            self.b_particion_ttip.change_text(string.tt_borrar_puntos)
            self.b_export_ttip.change_text(string.tt_confirmar)
            self.b_volver_ttip.change_text(string.tt_cancelar)
        elif self.habilitado_para_div == 1:
            self.img_stress.delete(self.punto_stress_canvas)
            self.img_res.delete(self.punto_rest_canvas)
            self.punto_stress = None
            self.punto_rest = None
        elif self.habilitado_para_div == 2:
            self.habilitado_para_div = 0
            self.boton_particion.config(text=string.boton_particion)


    def volver_upload(self):
        if self.habilitado_para_div == 0 or self.habilitado_para_div ==  2:
            print("Back UpLoad")
            self.parent.nuevo_paciente()
        elif self.habilitado_para_div == 1:
            self.habilitado_para_div = 0
            self.habilitar_punto_stress = 0
            self.habilitar_punto_rest = 0
            self.img_res.delete(self.punto_rest_canvas)
            self.img_stress.delete(self.punto_stress_canvas)
            self.boton_particion.config(text=string.boton_particion)
            self.boton_export.config(text=string.boton_export,
                                     state=NORMAL)
            self.boton_volver.config(text=string.boton_volver)
            self.b_particion_ttip.change_text(string.tt_particion)
            self.b_export_ttip.change_text(string.tt_export)
            self.b_volver_ttip.change_text(string.tt_volver)

    def punto_tocado(self):
        self.parent.img_rest.calculo_division(self.punto_rest)
        self.parent.img_stress.calculo_division(self.punto_stress)

        self.f_valor_div.config(width=dim.width_valor_img,
                                height=dim.height_valor_img)
        self.f_valor_div.pack_propagate(0)
        self.f_label_div.config(width=dim.width_label_valor_img,
                                height=dim.height_label_valor_img)
        self.f_label_div.pack_propagate(0)

        self.label_div.config(text="Partition",
                              anchor=W)
        self.label_div.pack(fill=BOTH, expand=1)
        self.valor_div.pack(fill=BOTH, expand=1)
        self.valor_div.config(values=[1, 2, 3, 4])
        self.valor_div.bind("<<ComboboxSelected>>", self.cambio_particion)
        self.valor_div.current(0)
        self.f_dif_9.pack_forget()
        self.f_label_div.grid(row=8, column=13)
        self.f_valor_div.grid(row=8, column=14)
        self.cambio_particion(event=None)
        pass

    def cambio_particion(self, event):
        particion = self.valor_div.get()
        self.subdiv = 'sub' + str(particion)
        self.curva_print(1)


    def curva_print(self, zona):
        """
        Display the Stress perfusion curve. Depending on the case
        param zone: Zone to be observed
            1: Blood
            2: Epicardium
            3: Endocardium
        :return: Curve printed on the canvas
        """
        init_rest = self.parent.img_rest.contenido[self.slice_select_rest].inicio
        fin_rest = self.parent.img_rest.contenido[self.slice_select_rest].fin
        init_stress = self.parent.img_stress.contenido[self.slice_select_stress].inicio
        fin_stress = self.parent.img_stress.contenido[self.slice_select_stress].fin
        time_r = self.parent.img_rest.contenido[self.slice_select_rest].data_tiempo
        time_rest = range(len(time_r))
        time_s = self.parent.img_stress.contenido[self.slice_select_stress].data_tiempo
        time_stress = range(len(time_s))
        data_rest = []
        data_stress = []
        if zona == 1:
            self.zona_select = 1
            self.button_san.config(state=DISABLED)
            self.button_epi.config(state=NORMAL)
            self.button_end.config(state=NORMAL)
            data_rest = self.parent.img_rest.contenido[self.slice_select_rest].data_sangre[self.subdiv]
            data_stress = self.parent.img_stress.contenido[self.slice_select_stress].data_sangre[self.subdiv]
        elif zona == 2:
            self.zona_select = 2
            self.button_san.config(state=NORMAL)
            self.button_epi.config(state=DISABLED)
            self.button_end.config(state=NORMAL)
            data_rest = self.parent.img_rest.contenido[self.slice_select_rest].data_epicardio[self.subdiv]
            data_stress = self.parent.img_stress.contenido[self.slice_select_stress].data_epicardio[self.subdiv]
        elif zona == 3:
            self.zona_select = 3
            self.button_san.config(state=NORMAL)
            self.button_epi.config(state=NORMAL)
            self.button_end.config(state=DISABLED)
            data_rest = self.parent.img_rest.contenido[self.slice_select_rest].data_endocardio[self.subdiv]
            data_stress = self.parent.img_stress.contenido[self.slice_select_stress].data_endocardio[self.subdiv]
        if self.plot_rest_res is None:
            self.plot_rest_res, = self.plot_rest.plot(time_rest[init_rest:fin_rest],
                                                      data_rest[init_rest:fin_rest])
            self.plot_stress_res, = self.plot_stress.plot(time_stress[init_stress:fin_stress],
                                                          data_stress[init_stress:fin_stress])
            self.canvas_stress.figure.axes[0].xaxis.set_visible(False)
            self.canvas_rest.figure.axes[0].xaxis.set_visible(False)
        else:

            self.plot_rest_res.set_xdata(time_rest[init_rest:fin_rest])
            self.plot_rest_res.set_ydata(data_rest[init_rest:fin_rest])
            self.plot_stress_res.set_xdata(time_stress[init_stress:fin_stress])
            self.plot_stress_res.set_ydata(data_stress[init_stress:fin_stress])


            self.canvas_rest.figure.axes[0].set_ylim(min(data_rest[init_rest:fin_rest]),
                                                     max(data_rest[init_rest:fin_rest]))
            # self.canvas_rest.figure.axes[0].set_xlim(min(time_rest[init_rest:fin_rest]),
            #                                          max(time_rest[init_rest:fin_rest]))
            self.canvas_rest.draw()
            self.canvas_stress.figure.axes[0].set_ylim(min(data_stress[init_stress:fin_stress]),
                                                       max(data_stress[init_stress:fin_stress]))
            # self.canvas_stress.figure.axes[0].set_xlim(min(time_stress[init_stress:fin_stress]),
            #                                            max(time_stress[init_stress:fin_stress]))
            self.canvas_stress.draw()
        self.print_img_prediccion(tipo=0)
        self.rellenar_tabla(time_rest[init_rest:fin_rest],
                            data_rest[init_rest:fin_rest],
                            time_stress[init_stress:fin_stress],
                            data_stress[init_stress:fin_stress])


    def print_img_prediccion(self, tipo):
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
            x, y = self.parent.img_rest.contenido[self.slice_select_rest].imgs[0].pixel_array.shape
            height = int(dim.height_img_res_screen)
            width = int(height * y / x)
            img_rgba = self.get_predict(tipo, zona, width, height)
            img_rgba = Image.frombytes('RGBA', (img_rgba.shape[1], img_rgba.shape[0]), img_rgba.astype('b').tostring())
            img_rgba = ImageTk.PhotoImage(img_rgba)
            self.predict_rest = img_rgba
            self.img_res.create_image(dim.w_mid_img, dim.h_mid_img, image=self.predict_rest)

            pass
        if tipo == 0 or tipo == 2:
            #  Print Stress
            x, y = self.parent.img_stress.contenido[self.slice_select_stress].imgs[0].pixel_array.shape
            height = int(dim.height_img_res_screen)
            width = int(height * y / x)
            img_rgba = self.get_predict(tipo, zona, width, height)
            img_rgba = Image.frombytes('RGBA', (img_rgba.shape[1], img_rgba.shape[0]), img_rgba.astype('b').tostring())
            img_rgba = ImageTk.PhotoImage(img_rgba)
            self.predict_stress = img_rgba
            self.img_stress.create_image(dim.w_mid_img, dim.h_mid_img, image=self.predict_stress)
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
                imgs_array = self.parent.img_rest.contenido[
                    int(self.slice_select_rest)].current_predict(0)[zona - 1]
            else:
                parte = int(self.subdiv[len(self.subdiv)-1])
                imgs_array = self.parent.img_rest.contenido[
                    int(self.slice_select_rest)].current_predict(parte)[zona - 1]
            img_rgba = img2rgba(imgs_array, zona, w, h)
        if tipo == 0 or tipo == 2:
            # Return image STRESS
            if self.subdiv == 'total':
                imgs_array = self.parent.img_stress.contenido[
                    int(self.slice_select_stress)].current_predict(0)[zona - 1]
            else:
                parte = int(self.subdiv[len(self.subdiv) - 1])
                imgs_array = self.parent.img_stress.contenido[
                    int(self.slice_select_stress)].current_predict(parte)[zona - 1]
            img_rgba = img2rgba(imgs_array, zona, w, h)
        return img_rgba

    def rellenar_tabla(self, time_rest, data_rest, time_stress, data_stress):
        self.area_rest.config(text=str(calculo_area_curva(data_rest, time_rest)))
        self.area_stress.config(text=str(calculo_area_curva(data_stress, time_stress)))
        self.res_peak_rest.config(text=str(calculo_maximo(data_rest, time_rest)[0]))
        self.res_peak_stress.config(text=str(calculo_maximo(data_stress, time_stress)[0]))
        self.res_pend_rest.config(text=str(calculo_pendiente(data_rest, time_rest)[0]))
        self.res_pend_stress.config(text=str(calculo_pendiente(data_stress, time_stress)[0]))
        self.res_ratio_value.config(text=str(np.round(calculo_pendiente(data_stress, time_stress)[0]
                                             / calculo_pendiente(data_rest, time_rest)[0], 2)))

    def expotar_data_pdf(self):
        pdf = ExportPDF(self.parent)
        print(pdf.generar_reporte())
        print("Export PDF")
