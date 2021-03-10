from . import utils
import numpy as np

IMAGE_SIZE = 256


class InputDataApp:

    def __init__(self, img_dir):
        self.img_dir = img_dir

    def get_data(self):
        imgs, n_slices = utils.get_dicom_in_folder_and_slices(self.img_dir)
        imgs, frames_drop = utils.split_slices(imgs, n_slices)  # XYZT
        imgs = utils.clip_norm(imgs)               # XYZT
        imgs = utils.zero_pad(imgs, IMAGE_SIZE)
        imgs = np.transpose(imgs, (2, 3, 0, 1))    # XYZT -> ZTXY
        return imgs, frames_drop
