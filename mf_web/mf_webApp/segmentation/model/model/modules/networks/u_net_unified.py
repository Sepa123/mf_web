from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import tensorflow as tf

from ...modules import layers
from ...parameters import param_keys


# TODO: (Z) Add dropout in bottleneck (use DROP_RATE parameter)
# TODO: (Z) Test if parameters are used correctly
# parameters used here: INITIAL_CONV_FILTERS, BATCHNORM_CONV, NUMBER_OF_CLASSES
class Network(object):
    def __init__(self, inputs, params, training_flag):
        self.logits = self._build_network(inputs, params, training_flag)

    def _build_network(self, inputs, params, training_flag):
        init_filters = params[param_keys.INITIAL_CONV_FILTERS]
        batchnorm_conv = params[param_keys.BATCHNORM_CONV]

        # encoding path
        e_1_1 = layers.conv_2d_bn(
            inputs=inputs, filters=init_filters, training=training_flag,
            batchnorm=batchnorm_conv, name="enc_conv_1_1")
        e_1_2 = layers.conv_2d_bn(
            inputs=e_1_1, filters=init_filters,  training=training_flag,
            batchnorm=batchnorm_conv, name="enc_conv_1_2")

        down_1 = layers.pooling_layer(e_1_2, name="enc_down_1_3")
        e_2_1 = layers.conv_2d_bn(
            inputs=down_1, filters=2*init_filters, training=training_flag,
            batchnorm=batchnorm_conv, name="enc_conv_2_1")
        e_2_2 = layers.conv_2d_bn(
            inputs=e_2_1, filters=2*init_filters, training=training_flag,
            batchnorm=batchnorm_conv, name="enc_conv_2_2")

        down_2 = layers.pooling_layer(e_2_2, name="enc_down_2_3")
        e_3_1 = layers.conv_2d_bn(
            inputs=down_2, filters=4*init_filters, training=training_flag,
            batchnorm=batchnorm_conv, name="enc_conv_3_1")
        e_3_2 = layers.conv_2d_bn(
            inputs=e_3_1, filters=4*init_filters, training=training_flag,
            batchnorm=batchnorm_conv, name="enc_conv_3_2")

        down_3 = layers.pooling_layer(e_3_2, name="enc_down_3_3")
        e_4_1 = layers.conv_2d_bn(
            inputs=down_3, filters=8*init_filters, training=training_flag,
            batchnorm=batchnorm_conv, name="enc_conv_4_1")
        e_4_2 = layers.conv_2d_bn(
            inputs=e_4_1, filters=8*init_filters, training=training_flag,
            batchnorm=batchnorm_conv, name="enc_conv_4_2")

        down_4 = layers.pooling_layer(e_4_2, name="enc_down_4_3")
        e_5_1 = layers.conv_2d_bn(
            inputs=down_4, filters=16*init_filters, training=training_flag,
            batchnorm=batchnorm_conv, name="enc_conv_5_1")
        e_5_2 = layers.conv_2d_bn(
            inputs=e_5_1, filters=16*init_filters, training=training_flag,
            batchnorm=batchnorm_conv, name="enc_conv_5_2")

        # decoding path
        up_4 = layers.upsampling_layer(
            inputs=e_5_2, filters=8*init_filters, name="dec_up_4_1")
        concat_4 = tf.concat([e_4_2, up_4], axis=3)
        d_4_1 = layers.conv_2d_bn(
            inputs=concat_4, filters=8*init_filters, training=training_flag,
            batchnorm=batchnorm_conv, name="dec_conv_4_2")
        d_4_2 = layers.conv_2d_bn(
            inputs=d_4_1, filters=8*init_filters, training=training_flag,
            batchnorm=batchnorm_conv, name="dec_conv_4_3")

        up_3 = layers.upsampling_layer(
            inputs=d_4_2, filters=4*init_filters, name="dec_up_3_1")
        concat_3 = tf.concat([e_3_2, up_3], axis=3)
        d_3_1 = layers.conv_2d_bn(
            inputs=concat_3, filters=4*init_filters, training=training_flag,
            batchnorm=batchnorm_conv, name="dec_conv_3_2")
        d_3_2 = layers.conv_2d_bn(
            inputs=d_3_1, filters=4*init_filters, training=training_flag,
            batchnorm=batchnorm_conv, name="dec_conv_3_3")

        up_2 = layers.upsampling_layer(
            inputs=d_3_2, filters=2 * init_filters, name="dec_up_2_1")
        concat_2 = tf.concat([e_2_2, up_2], axis=3)
        d_2_1 = layers.conv_2d_bn(
            inputs=concat_2, filters=2 * init_filters, training=training_flag,
            batchnorm=batchnorm_conv, name="dec_conv_2_2")
        d_2_2 = layers.conv_2d_bn(
            inputs=d_2_1, filters=2 * init_filters, training=training_flag,
            batchnorm=batchnorm_conv, name="dec_conv_2_3")

        up_1 = layers.upsampling_layer(
            inputs=d_2_2, filters=init_filters, name="dec_up_1_1")
        concat_1 = tf.concat([e_1_2, up_1], axis=3)
        d_1_1 = layers.conv_2d_bn(
            inputs=concat_1, filters=init_filters, training=training_flag,
            batchnorm=batchnorm_conv, name="dec_conv_1_2")
        d_1_2 = layers.conv_2d_bn(
            inputs=d_1_1, filters=init_filters, training=training_flag,
            batchnorm=batchnorm_conv, name="dec_conv_1_3")

        output = tf.layers.conv2d(
            inputs=d_1_2, filters=params[param_keys.NUMBER_OF_CLASSES],
            kernel_size=1, strides=1, activation=None, name="output_seg_map")

        return output

    def get_output(self):
        return self.logits