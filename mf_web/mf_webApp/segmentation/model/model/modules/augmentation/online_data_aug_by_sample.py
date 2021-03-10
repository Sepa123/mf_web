"""Augmentation online, currently in use, by sample and with probability p."""

import tensorflow as tf
import numpy as np
from itertools import product

from ...parameters import param_keys


def check_shape(array):
    """Adds a dummy channel when necessary, to have 3D tensors"""
    shape = array.get_shape().as_list()
    if len(shape) != 3:
        return tf.expand_dims(array, axis=-1)
    else:
        return array


def _random_flip_both_axis(data, threshold=0.5):
    uniform_random = tf.random_uniform([], 0, 1.0)
    mirror_cond = tf.less(uniform_random, threshold)
    modified_data = tf.cond(
        mirror_cond,
        lambda: tf.image.flip_up_down(tf.image.flip_left_right(data)),
        lambda: data
    )
    return modified_data


def _random_flip_up_down(data, threshold=0.5):
    uniform_random = tf.random_uniform([], 0, 1.0)
    mirror_cond = tf.less(uniform_random, threshold)
    modified_data = tf.cond(
        mirror_cond,
        lambda: tf.image.flip_up_down(data),
        lambda: data
    )
    return modified_data


def _random_flip_left_right(data, threshold=0.5):
    uniform_random = tf.random_uniform([], 0, 1.0)
    mirror_cond = tf.less(uniform_random, threshold)
    modified_data = tf.cond(
        mirror_cond,
        lambda: tf.image.flip_left_right(data),
        lambda: data
    )
    return modified_data


def _random_rotate(data, angle, threshold=0.5):
    uniform_random = tf.random_uniform([], 0, 1.0)
    mirror_cond = tf.less(uniform_random, threshold)
    modified_data = tf.cond(
        mirror_cond,
        lambda: tf.contrib.image.rotate(images=data, angles=tf.multiply(
            tf.to_float(angle), np.pi) / 180,
                            interpolation='NEAREST'),
        lambda: data
    )
    return modified_data


def _random_shift(data, shift, threshold=0.5):
    shift = (tf.to_int32(shift[0] * tf.to_float(tf.shape(data)[-3])),
             tf.to_int32(shift[1] * tf.to_float(tf.shape(data)[-2])))
    uniform_random = tf.random_uniform([], 0, 1.0)
    mirror_cond = tf.less(uniform_random, threshold)
    modified_data = tf.cond(
        mirror_cond,
        lambda: tf.contrib.image.translate(
            images=data, translations=shift, interpolation='NEAREST'),
        lambda: data
    )
    return modified_data


def apply_augmentations(data, angle, shift):
    """Transform the data via regular random data transformations."""
    data = _random_flip_both_axis(data)
    data = _random_flip_left_right(data)
    data = _random_flip_up_down(data)
    data = _random_rotate(data, angle)
    data = _random_shift(data, shift)
    return data


def online_data_augmentation(imgs, annot, params):
    """Preprocessing function to perform online data augmentation."""
    # Settings of online data augmentation
    shift_max = params[param_keys.SHIFT_MAX]
    shift_number = params[param_keys.SHIFT_NUMBER]
    angle_step = params[param_keys.ANGLE_STEP]
    # Generate posible values
    shift_array = np.arange(shift_number+1) * (shift_max/shift_number)
    shifts_list = list(product(shift_array, shift_array))[1:]
    angles_list = np.arange(angle_step, 180, angle_step)
    # Random value for angle and shift
    angles_list = tf.random_shuffle(tf.convert_to_tensor(angles_list))
    shifts_list = tf.random_shuffle(tf.convert_to_tensor(shifts_list))
    # Prepare data
    imgs = check_shape(imgs)
    annot = check_shape(annot)
    n_channels_img = tf.shape(imgs)[-1]
    imgs_dtype = imgs.dtype
    annot_dtype = annot.dtype
    data_to_augment = tf.concat([tf.to_float(imgs), tf.to_float(annot)], axis=-1)

    # Perform random augmentation
    uniform_random = tf.random_uniform([], 0, 1.0)
    # this controls when data augmentation is performed
    mirror_cond = tf.less(
            uniform_random, params[param_keys.PERCENTAGE_OF_AUGMENTED_DATA])
    augmented_data = tf.cond(
        mirror_cond,
        lambda: apply_augmentations(
            data_to_augment, angles_list[0], shifts_list[0]),
        lambda: data_to_augment
    )
    augmented_imgs = tf.cast(
        augmented_data[..., :n_channels_img], dtype=imgs_dtype)
    augmented_annot = tf.cast(
        augmented_data[..., n_channels_img:], dtype=annot_dtype)
    annot_shape = augmented_annot.get_shape().as_list()
    if annot_shape[2] == 1:
        # Remove channel dimension, so one_hot can do its job
        augmented_annot = augmented_annot[:, :, 0]

    return augmented_imgs, augmented_annot
