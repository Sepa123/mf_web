"""Class definition to manipulate datasets."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import pickle

import numpy as np

from .utils import PATH_TO_PROJECT

TEST_FRACTION = 0.2
VAL_FROM_TRAIN_FRACTION = 0.1
SEED = 1234

KEY_ID = 'subject_id'
KEY_IMAGES = 'images'
KEY_MARKS = 'marks'


class BaseDataset(object):
    """This is a base class for heart MRI datasets.

    It provides the option to load and create checkpoints of the processed
    data, and provides methods to query data from specific ids or entire
    subsets.
    Data is stored as arrays of shape ZTXY.

    You have to overwrite the method '_load_from_files'.
    """

    def __init__(self, dataset_dir, load_checkpoint, name):
        """Constructor.

        Args:
            dataset_dir: (String) Path to the folder containing the dataset.
                This path can be absolute, or relative to the project root.
            load_checkpoint: (Boolean). Whether to load from a checkpoint or to
                load from scratch using the original files of the dataset.
            name: (String) Name of the dataset. This name will be used for
                checkpoints.
        """

        if os.path.isabs(dataset_dir):
            self.dataset_dir = dataset_dir
        else:
            self.dataset_dir = os.path.join(PATH_TO_PROJECT, dataset_dir)
        self._check_dataset_dir()  # We verify that the directory exists

        self.load_checkpoint = load_checkpoint
        self.name = name
        self.ckpt_dir = os.path.abspath(os.path.join(
            self.dataset_dir, '..', 'ckpt_%s' % self.name))
        self.data, self.all_ids = self._load_data()
        print('Dataset %s with %d patients.' % (self.name, len(self.all_ids)))
        train_ids, self.test_ids = self._train_test_split(
            self.all_ids, TEST_FRACTION)
        self.train_ids, self.val_ids = self._train_test_split(
            train_ids, VAL_FROM_TRAIN_FRACTION)
        print('Train size: %d. Val size %d. Test size: %d'
              % (len(self.train_ids), len(self.val_ids), len(self.test_ids)))

    def get_data(self):
        return self.data

    def save_checkpoint(self):
        """Saves a pickle file containing the loaded data."""
        os.makedirs(self.ckpt_dir, exist_ok=True)
        for subject_data in self.data:
            filename = os.path.join(
                self.ckpt_dir, '%s.pickle' % subject_data[KEY_ID])
            with open(filename, 'wb') as handle:
                pickle.dump(
                    subject_data, handle, protocol=pickle.HIGHEST_PROTOCOL)
        print('Checkpoint saved at %s' % self.ckpt_dir)

    def get_subject(self, subject_id, verbose=False):
        """Returns the images and marks of a single subject."""
        if subject_id not in self.all_ids:
            raise ValueError(
                'Invalid subject id %s' % subject_id)
        subject_index = self.all_ids.index(subject_id)
        subject_data = self.data[subject_index]
        images = subject_data[KEY_IMAGES]
        marks = subject_data[KEY_MARKS]
        if verbose:
            print('Getting ID %s' % subject_data[KEY_ID])
            if marks is None:
                print('Marks for this subject is None.')
        return images, marks

    def get_subset(self, subject_id_list, drop_none_marks=False,
                   verbose=False):
        """Returns the list of images and marks of a list of subjects.
        If drop_none_marks is True, subjects without any marks are ignored
        """
        subset_images = []
        subset_marks = []
        subset_ids = []
        for subject_id in subject_id_list:
            images, marks = self.get_subject(subject_id, verbose=verbose)
            if marks is None and drop_none_marks:
                if verbose:
                    print('Dropping subject (None mark)')
            else:
                subset_images.append(images)
                subset_marks.append(marks)
                subset_ids.append(subject_id)
        print('Returning:')
        print(subset_ids)
        return subset_images, subset_marks

    def get_all(self, drop_none_marks=False, verbose=False):
        """Returns all subjects
        If drop_none_marks is True, subjects without any marks are ignored.
        """
        all_images, all_marks = self.get_subset(
            self.all_ids, drop_none_marks=drop_none_marks,
            verbose=verbose)
        return all_images, all_marks

    def _train_test_split(self, ids_list, test_fraction):
        """Random but reproducible split."""
        ids_permuted = np.random.RandomState(seed=SEED).permutation(
            ids_list)
        split_point = int(test_fraction * len(ids_list))
        test_ids = ids_permuted[:split_point]
        train_ids = ids_permuted[split_point:]
        return train_ids, test_ids

    def _load_data(self):
        """Loads and returns data either from a checkpoint or from scratch."""
        if self.load_checkpoint:
            print('Loading %s from checkpoint.' % self.name)
            data, all_ids = self._load_from_checkpoint()
        else:
            print('Loading %s from files.' % self.name)
            data, all_ids = self._load_from_files()
        print('Loaded')
        return data, all_ids

    def _load_from_checkpoint(self):
        """Loads the pickle file containing the loaded data and returns it."""
        data = []
        all_ids = self._get_ids()
        for i, subject_id in enumerate(all_ids):
            print('Loading %03d/%03d. ID: %s'
                  % (i + 1, len(all_ids), subject_id))
            filename = os.path.join(
                self.ckpt_dir, '%s.pickle' % subject_id)
            with open(filename, 'rb') as handle:
                subject_data = pickle.load(handle)
            data.append(subject_data)
        return data, all_ids

    def _check_dataset_dir(self):
        """Checks if the directory containing the data exists"""
        if not os.path.isdir(self.dataset_dir):
            raise FileNotFoundError(
                'Directory not found: %s' % self.dataset_dir)

    def _get_ids(self):
        """Returns the ids from the checkpoint folder."""
        all_ids = os.listdir(self.ckpt_dir)
        all_ids = [sub_id for sub_id in all_ids if '.pickle' in sub_id]
        for i, sub_id in enumerate(all_ids):
            filename, file_extension = os.path.splitext(sub_id)
            all_ids[i] = filename
        all_ids.sort()
        return all_ids

    def _load_from_files(self):
        """Loads and return the data from files and transforms it appropriately.
        This is just a template for the specific implementation of the dataset.
        """
        # List of dictionaries containing the data
        data = []
        all_ids = [1, 2, 3]
        for pat_id in all_ids:
            pat_dict = {KEY_ID: pat_id, KEY_IMAGES: None, KEY_MARKS: None}
            data.append(pat_dict)
        return data, all_ids
