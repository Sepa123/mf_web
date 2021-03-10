#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unet with batchnormalization layers as in https://github.com/ankurhanda/tf-unet/blob/master/UNet.py
Anddata uagmentation that performs flips, rotations ans shifts
@author Esteban Reyes
"""

# python 2 and 3 compatibility
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

# basic libraries
import os
import sys
import tensorflow as tf
import numpy as np
import time
import datetime

PATH_TO_PROJECT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(PATH_TO_PROJECT)
from .u_net_model import U_net
from ..modules.augmentation import online_data_aug_by_sample as online_data_aug
from ..modules.iterators import train_iterator, validation_iterator


# TODO: refactor train test and validate
class U_net_online_aug(U_net):
    """
    Constructor
    """

    def __init__(self, params={}, model_name="U-net_online_aug"):
        super().__init__(params, model_name)

    def _iterator_init(self, params):
        with tf.name_scope("iterators"):
            train_it_builder = train_iterator.TrainIteratorBuilder(
                params,
                pre_batch_processing=self._augmentator_wrapper,
                post_batch_processing=None)
            iterator_train, train_sample_ph, train_lbl_ph = train_it_builder.get_iterator_and_ph()
            val_it_builder = validation_iterator.ValidationIteratorBuilder(
                params)
            iterator_val, val_sample_ph, val_lbl_ph = val_it_builder.get_iterator_and_ph()
            handle_ph, global_iterator = train_it_builder.get_global_iterator()
        return global_iterator, handle_ph, train_sample_ph, train_lbl_ph, iterator_train, val_sample_ph, val_lbl_ph, \
               iterator_val

    def _augmentator_wrapper(self, imgs, annot):
        return online_data_aug.online_data_augmentation(imgs, annot, self.params)

if __name__ == "__main__":
    params = {}

    model = U_net_online_aug(params)
    model._create_paths()
    train_writer = tf.summary.FileWriter(
        model.tb_path + 'train', model.sess.graph)
