#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
custome layers for U-net and other models

@author Esteban Reyes
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import tensorflow as tf

from ..parameters import constants
from ..parameters import errors


def conv_2d_bn(
        inputs,
        filters,
        training,
        batchnorm=constants.BN,
        activation=tf.nn.relu,
        padding=constants.PAD_SAME,
        kernel_size=3,
        strides=1,
        kernel_initializer=None,
        name=None):
    """Buils a 2d convolutional layer with batch normalization.

    Args:
        inputs: (4d tensor) input tensor of shape
            [batch_size, height, width, n_channels]
        filters: (int) Number of filters to apply.
        training: (Optional, boolean, defaults to False) Indicates if it is the
            training phase or not.
        batchnorm: (Optional, {None, BN, BN_RENORM}, defaults to BN) Type of
            batchnorm to be used. BN is normal batchnorm, and BN_RENORM is a
            batchnorm with renorm activated. If None, batchnorm is not applied.
            The batchnorm layer is applied before activation.
        activation: (Optional, function, defaults to tf.nn.relu) Type of
            activation to be used after convolution. If None, activation is
            linear.
        padding: (Optional, {PAD_SAME, PAD_VALID}, defaults to PAD_SAME) Type
            of padding for the convolution.
        kernel_size: (Optional, int or tuple of int, defaults to 3) Size of
            the kernels.
        strides: (Optional, int or tuple of int, defaults to 1) Size of the
            strides of the convolutions.
        kernel_initializer: (Optional, function, defaults to None) An
            initializer for the convolution kernel.
        name: (Optional, string, defaults to None) A name for the operation.
        """
    errors.check_valid_value(
        padding, 'padding', [constants.PAD_SAME, constants.PAD_VALID])

    with tf.variable_scope(name):
        outputs = tf.layers.conv2d(
            inputs=inputs, filters=filters, kernel_size=kernel_size,
            strides=strides, activation=None, padding=padding,
            kernel_initializer=kernel_initializer, name="%s_conv_2d" % name)
        # Why scale is false when using ReLU as the next activation
        # https://datascience.stackexchange.com/questions/22073/why-is-scale-parameter-on-batch-normalization-not-needed-on-relu/22127

        if batchnorm:  # batchnorm parameter is not None
            # Here we add a pre-activation batch norm
            if activation == tf.nn.relu:
                outputs = batchnorm_layer(
                    outputs, name="%s_bn" % name, scale=False,
                    batchnorm=batchnorm, training=training)
            else:
                outputs = batchnorm_layer(
                    outputs, name="%s_bn" % name, scale=True,
                    batchnorm=batchnorm, training=training)
        output = activation(outputs)
    return output


def batchnorm_layer(
        inputs,
        name,
        scale=True,
        batchnorm=constants.BN,
        reuse=False,
        training=False):
    """Buils a batch normalization layer.
    By default, it uses a faster, fused implementation if possible.

    Args:
        inputs: (tensor) Input tensor of shape [batch_size, ..., channels].
        name: (string) A name for the operation.
        scale: (Optional, bool, defaults to True) Whether to add the scale
            parameter.
        batchnorm: (Optional, {BN, BN_RENORM}, defaults to BN) Type of batchnorm
            to be used. BN is normal batchnorm, and BN_RENORM is a batchnorm
            with renorm activated.
        reuse: (Optional, boolean, defaults to False) Whether to reuse the layer
            variables.
        training: (Optional, boolean, defaults to False) Indicates if it is the
            training phase or not.
    """
    errors.check_valid_value(
        batchnorm, 'batchnorm', [constants.BN, constants.BN_RENORM])

    if batchnorm == constants.BN_RENORM:
        name = '%s_renorm' % name
    if batchnorm == constants.BN:
        outputs = tf.layers.batch_normalization(
            inputs=inputs, training=training, scale=scale,
            reuse=reuse, name=name)
    else:  # BN_RENORM
        outputs = tf.layers.batch_normalization(
            inputs=inputs, training=training, scale=scale,
            reuse=reuse, renorm=True, name=name)
    return outputs


def pooling_layer(inputs, pooling=constants.MAXPOOL, name=None):
    """
    Args:

        inputs: (4d tensor) input tensor of shape
                [batch_size, height, width, n_channels]
        pooling: (Optional, {AVGPOOL, MAXPOOL}, defaults to MAXPOOL) Type of
            pooling to be used, which is always of stride 2
            and pool size 2.
        name: (Optional, defaults to None) A name for the operation.
    """
    errors.check_valid_value(
        pooling, 'pooling', [constants.AVGPOOL, constants.MAXPOOL])

    if pooling == constants.AVGPOOL:
        outputs = tf.layers.average_pooling2d(
            inputs=inputs, pool_size=2, strides=2, name=name)
    else:  # MAXPOOL
        outputs = tf.layers.max_pooling2d(
            inputs=inputs, pool_size=2, strides=2, name=name)
    return outputs


def upsampling_layer(inputs, filters, padding=constants.PAD_SAME, name=None):
    errors.check_valid_value(
        padding, 'padding', [constants.PAD_SAME, constants.PAD_VALID])

    outputs = tf.layers.conv2d_transpose(
        inputs=inputs, filters=filters, kernel_size=2,
        strides=2, activation=None, padding=padding, name=name)
    return outputs
