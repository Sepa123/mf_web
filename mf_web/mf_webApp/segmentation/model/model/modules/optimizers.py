from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import tensorflow as tf


def generic_minimizer(optimizer, loss):
    update_ops = tf.get_collection(tf.GraphKeys.UPDATE_OPS)  # For BN
    with tf.control_dependencies(update_ops):
        train_step = optimizer.minimize(loss)
    reset_optimizer_op = tf.variables_initializer(optimizer.variables())
    return train_step, reset_optimizer_op


def create_non_trainable(initial_value, name):
    return tf.Variable(initial_value, trainable=False, name=name)


def adam(loss, learning_rate_value):
    # TODO: Learning rate from params, caution with learning rate exponential decay that is currently implemented)
    # learning rate that can be actualized through training
    learning_rate = create_non_trainable(learning_rate_value, 'learning_rate')
    # Adam
    optimizer = tf.train.AdamOptimizer(0.0001)
    # train operation to be run for performing a learning iteration
    train_step, _ = generic_minimizer(optimizer, loss)
    return train_step, learning_rate


def sgd(loss, learning_rate_value):
    # learning rate that can be actualized through training
    learning_rate = create_non_trainable(learning_rate_value, 'learning_rate')
    # SDG optimizer
    optimizer = tf.train.GradientDescentOptimizer(learning_rate)
    # train operation to be run for performing a learning iteration
    train_step, _ = generic_minimizer(optimizer, loss)
    return train_step, learning_rate


def momentum_sgd(loss, learning_rate_value, momentum_value=0.5):
    # learning and momentum rate that can be actualized through training
    learning_rate = create_non_trainable(learning_rate_value, 'learning_rate')
    momentum = create_non_trainable(momentum_value)
    # MomentumSDG optimizer
    optimizer = tf.train.MomentumOptimizer(
        learning_rate=learning_rate, momentum=momentum)
    # train operation to be run for performing a learning iteration
    train_step, _ = generic_minimizer(optimizer, loss)
    return train_step, learning_rate, momentum
