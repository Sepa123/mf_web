"""Class definition to manipulate Perfusion UCH dataset."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os

import nibabel as nib
import numpy as np

from . import utils
from .utils import IMAGE_SIZE
from .base_dataset import BaseDataset
from .base_dataset import KEY_ID, KEY_IMAGES, KEY_MARKS

FOLDER_IMAGES = ''
FOLDER_MARKS = 'marks'


class PerfusionUCH(BaseDataset):
    """This class manipulates Perfusion UCH dataset.

    It provides the option to load and create checkpoints of the processed
    data, and provides methods to query data from specific ids or entire
    subsets. Perfusion UCH corresponds to the data provided by
    the Hospital Clinico Universidad de Chile.
    Data is stored as arrays of shape ZTXY.

    Expected directory tree inside dataset_folder:

    dataset_folder
    |__ FOLDER_IMAGES
        |__ 100
            |__ ...
        |__ 101
            |__ ...
        |__ 102
            |__ ...
        |__ ...
    |__ FOLDER_MARKS
        |__ 100.nii.gz
        |__ 101.nii.gz
        |__ ...
    """

    def __init__(self, dataset_dir, load_checkpoint=False):
        """Constructor.

        Args:
            dataset_dir: Path to the folder containing the dataset (see
                the expected directory tree in the class docstring). This path
                can be either absolute, or relative to the project root.
            load_checkpoint: (Optional, boolean, defaults to False). Whether
                to load from a checkpoint or to load from scratch using the
                original files of the dataset.
        """
        super().__init__(dataset_dir, load_checkpoint, 'perfusion_uch')

    def _load_from_files(self):
        """Loads and return the data from files and transforms it appropriately.

        Data is normalized, zero padded to 256x256, and then transposed to
        ZTXY format.
        """
        # ids of patients
        all_ids = os.listdir(os.path.join(self.dataset_dir, FOLDER_IMAGES))
        # consider only folders
        all_ids = [pat_id for pat_id in all_ids
                   if os.path.isdir(os.path.join(self.dataset_dir, FOLDER_IMAGES, pat_id))]
        # all_ids = [int(pat_id) for pat_id in all_ids]
        all_ids.sort()
        # List of dictionaries containing the data
        data = []
        n_ids = len(all_ids)
        for i, pat_id in enumerate(all_ids):
            print('Loading %03d/%03d. ID: %s' % (i+1, n_ids, pat_id))

            # Get images in ZTXY format
            pat_path = os.path.join(
                self.dataset_dir, FOLDER_IMAGES, '%s' % pat_id)
            exam_folder = os.listdir(pat_path)[0]
            exam_path = os.path.join(pat_path, exam_folder)
            # XYZT format data
            imgs, n_slices = utils.get_dicom_in_folder_and_slices(exam_path)
            imgs = utils.split_slices(imgs, n_slices)  # XYZT
            imgs = utils.clip_norm(imgs)  # XYZT
            imgs = utils.zero_pad(imgs, IMAGE_SIZE)  # XYZT
            imgs = np.transpose(
                imgs, (2, 3, 0, 1))  # XYZT -> ZTXY

            # Get marks in ZTXY format
            filename = os.path.join(
                self.dataset_dir, FOLDER_MARKS, '%s.nii.gz' % pat_id)
            if os.path.isfile(filename):
                marks = self._get_nifti_labels(filename)  # XYZT
                marks = utils.split_slices(marks, n_slices)
                marks = utils.swap_labels(marks)
                marks = utils.zero_pad(marks, IMAGE_SIZE)  # XYZT
                marks = np.transpose(
                    marks, (2, 3, 0, 1))  # XYZT -> ZTXY
            else:
                print('No marks found.')
                marks = None
            # Save
            pat_dict = {KEY_ID: pat_id, KEY_IMAGES: imgs, KEY_MARKS: marks}
            data.append(pat_dict)
        return data, all_ids

    def _get_nifti_labels(self, filename):
        """Returns the labels contained in the nifti file, in XYZT format.
        Z is dummy dimension"""
        data = nib.load(filename)
        labels = data.get_fdata()  # YXT
        labels = np.swapaxes(labels, 0, 1)  # XYT
        labels = labels[:, :, np.newaxis, :]  # XYZT, Z is dummy.
        labels = labels.astype(np.uint8)
        return labels
