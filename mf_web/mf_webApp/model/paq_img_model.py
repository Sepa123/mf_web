from model.slice_model import SliceModel


class PaqImgModel:

    def __init__(self, tipo):
        self.tipo = tipo
        self.contenido = []
        self.actual_slice = 0

    def agregar_img(self, imagen):
        loc = imagen.location
        slice_img = self.slice_especifico(loc)
        if slice_img is None:
            nuevo = SliceModel(loc)
            nuevo.agregar_img_slice(imagen)
            self.contenido.append(nuevo)
            self.sort_slice()
        else:
            slice_img.agregar_img_slice(imagen)

    def get_cantidad_slice(self):
        return len(self.contenido)

    def reiniciar_paq(self):
        self.contenido = []

    def esta_vacio(self):
        if len(self.contenido) == 0:
            return True
        return False

    def slice_especifico(self, loc):
        for slice_con in self.contenido:
            if loc == slice_con.slice_loc:
                return slice_con
        return None

    def cantidad_imagenes(self):
        cantidad = 0
        for slice_cont in self.contenido:
            cantidad = cantidad + slice_cont.cantidad_imgs()
        return cantidad

    def sort_slice(self):
        self.contenido.sort(key=lambda x: x.slice_loc)

    def agregar_predict(self, predict, borrar_frames):
        #  DELETE FRAMES THAT DO NOT MATTER
        if borrar_frames:
            self.borrar_frames()
        #  ADD PREDICT TO YOUR IMAGES, SLICE AND TIME ARE ASSUMED TO BE IN ORDER
        #  detect first slice, so you can enter images from there
        pos = self.get_primer_slice_time()
        cant = self.get_cantidad_slice()
        for i in range(len(predict)):
            self.contenido[(pos+i) % cant].agregar_predict_img(predict[i])

    def get_primer_slice_time(self):
        save_first = None
        slice_pos = 0
        for i in range(len(self.contenido)):
            if save_first is None:
                save_first = self.contenido[i].imgs[0].image_acq_time
                slice_pos = i
            else:
                if self.contenido[i].imgs[0].image_acq_time < save_first:
                    save_first = self.contenido[i].imgs[0].image_acq_time
                    slice_pos = i
        return slice_pos

    def borrar_frames(self):
        len_max = 0
        for slice_paq in self.contenido:
            if slice_paq.cantidad_imgs() > len_max:
                len_max = slice_paq.cantidad_imgs()
        for slice_paq in self.contenido:
            if slice_paq.cantidad_imgs() == len_max:
                slice_paq.quitar_primera()

    def get_array_slice(self):
        number = 1
        res = []
        for sli in self.contenido:
            valor_cbox = str(number) + ": loc= " + str(sli.slice_loc)
            res.append(valor_cbox)
            number += 1
        return res

    def calculo_division(self, punto):
        """
        It is passed through each slice, calculating the division of the myocardium, according to the point given by the user.
        param point: point given by the user
        return: void, the data is saved in each slice.
        """
        for slice_cont in self.contenido:
            slice_cont.calcular_division_miocardio(punto)
        pass
