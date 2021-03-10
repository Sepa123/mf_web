from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import tensorflow as tf


def xentropy(logits, input_labels, number_of_classes):
    flat_logits = tf.reshape(tensor=logits, shape=(-1, number_of_classes))
    flat_labels = tf.to_float(tf.reshape(
        tensor=input_labels, shape=(-1, number_of_classes)))
    diff = tf.nn.softmax_cross_entropy_with_logits_v2(
        logits=flat_logits, labels=flat_labels)
    loss = tf.reduce_mean(diff)
    return loss
