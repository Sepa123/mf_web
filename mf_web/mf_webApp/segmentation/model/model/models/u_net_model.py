#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unet with batchnormalization layers as in https://github.com/ankurhanda/tf-unet/blob/master/UNet.py
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
from ..modules.data_set_generic import Dataset as data_set_class
from ..modules.data_splitter import DatasetDivider
from ..modules.print_manager import PrintManager
from ..modules import metrics
from ..modules.iterators import train_iterator, validation_iterator
from ..modules import losses, optimizers
from ..modules.networks import u_net_unified as neural_net
from ..parameters import param_keys, general_keys


# TODO: refactor train test and validate
class U_net(object):
    """
    Constructor
    """

    def __init__(self, params=None, model_name="U-net"):

        self.model_name = model_name
        self.date = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

        self.params = param_keys.default_params
        if params is not None:
            self.params.update(params)

        self.global_iterator, self.handle_ph, self.train_img_ph, self.train_lbl_ph, self.iterator_train, \
            self.validation_img_ph, self.validation_lbl_ph, \
            self.iterator_validation = self._iterator_init(self.params)

        self.input_batch, self.input_labels, self.training_flag, self.logits, self.output_probabilities,\
            self.output_pred_cls = self._build_graph(self.params)

        self.loss = self._loss_init(self.logits, self.input_labels,
                                    self.params[param_keys.NUMBER_OF_CLASSES])
        self.train_step, self.learning_rate = self._optimizer_init(
            self.loss, self.params[param_keys.LEARNING_RATE])

        self.sess = self._session_init()
        self.saver = tf.train.Saver()
        self._variables_init()

        # Initialization of handles
        self.train_handle, self.validation_handle = self.sess.run(
            [self.iterator_train.string_handle(),
             self.iterator_validation.string_handle()])
        self.metrics_dict = self._define_evaluation_metrics(self.input_labels,
                                                            self.output_pred_cls)
        self.print_manager = PrintManager()
        # Init summaries
        self.summary_dict = self._init_summaries(self.loss, self.metrics_dict)

    def _session_init(self):
        config = tf.ConfigProto(allow_soft_placement=True)
        config.gpu_options.allow_growth = True
        return tf.Session(config=config)

    def _variables_init(self):
        init_op = tf.group(tf.global_variables_initializer(),
                           tf.local_variables_initializer())
        self.sess.run(init_op)

    def _data_init(self, data_path):
        test_imgs, test_masks = self._get_set_images_and_labels(
            data_path, 'test')
        train_imgs, train_masks = self._get_set_images_and_labels(
            data_path, 'train')
        val_imgs, val_masks = self._get_set_images_and_labels(
            data_path, 'val')

        train_set = data_set_class(
            train_imgs, train_masks, self.params[param_keys.BATCH_SIZE])
        val_set = data_set_class(
            val_imgs, val_masks, self.params[param_keys.BATCH_SIZE])
        test_set = data_set_class(
            test_imgs, test_masks,  self.params[param_keys.BATCH_SIZE])
        return train_set, val_set, test_set

    def _get_set_images_and_labels(self, data_path, set):
        set_masks = np.load(os.path.join(data_path, str(set+'_annot.npy')))
        set_imgs = np.expand_dims(
            np.load(os.path.join(data_path, str(set+'_imgs.npy'))), axis=-1)
        return set_imgs, set_masks

    def _define_evaluation_metrics(self, labels_OH, predictions):
        with tf.variable_scope('performance_measures'):
            metrics_dict = metrics.iou_and_dice_v2(
                labels_OH,
                tf.one_hot(predictions, self.params[param_keys.NUMBER_OF_CLASSES]),
                is_onehot=True,
                average=True)
        return metrics_dict

    def _init_summaries(self, loss, metrics_dict):
        loss_sum = tf.summary.scalar('loss_value', loss)
        summary_dict = {loss: loss_sum}
        for key, value in metrics_dict.items():
            summary_dict[value] = tf.summary.scalar(key, value)
        return summary_dict

    def _prepare_train_input(self, X, y):
        if X.shape != () and y.shape != ():
            aux_dataset_obj = data_set_class(
                X, y, self.params[param_keys.BATCH_SIZE])
            data_divider = DatasetDivider(
                aux_dataset_obj,
                val_random_seed=self.params[param_keys.VALIDATION_RANDOM_SEED])
            train_set, val_set = data_divider.get_train_val_data_set_objs()
            test_set = None
        else:
            train_set, val_set, test_set = self._data_init(
                self.params[param_keys.DATA_PATH])
        train_set = self._global_shuffling(train_set)
        return train_set, val_set, test_set

    def _global_shuffling(self, set, seed=1234):
        data_array = set.data_array
        data_label = set.data_label
        idx_permuted = np.random.RandomState(seed=seed).permutation(
            data_array.shape[0])
        data_array = data_array[idx_permuted, ...]
        data_label = data_label[idx_permuted, ...]
        set.data_array = data_array
        set.data_label = data_label
        return set

    def _create_paths(self):
        self.model_path = os.path.join(
            PATH_TO_PROJECT, 'results', '%s_%s' % (self.model_name, self.date))
        if not os.path.exists(self.model_path):
            os.makedirs(self.model_path)
        self.checkpoint_path = os.path.join(
            self.model_path, 'checkpoints', 'model')
        self.tb_path = os.path.join(self.model_path, 'tb_summaries')

    # TODO: maybe create model trainer class
    # TODO: add method metadata_runner_profiling
    def fit(self, X=np.empty([]), y=np.empty([]), verbose=True, log_file='train.log'):
        self.train_set, self.val_set, self.test_set = self._prepare_train_input(X, y)
        # Initialization of the train iterator, only once since it is repeated forever
        self.sess.run(self.iterator_train.initializer,
                      feed_dict={self.train_img_ph: self.train_set.data_array,
                                 self.train_lbl_ph: self.train_set.data_label})
        # create paths where training results will be saved
        self._create_paths()
        # verbose management
        print = self.print_manager.verbose_printing(verbose)
        file = open(os.path.join(self.model_path, log_file), 'w')
        self.print_manager.file_printing(file)
        # summaries
        self.train_writer = tf.summary.FileWriter(os.path.join(self.tb_path, 'train'),
                                                  self.sess.graph)
        self.val_writer = tf.summary.FileWriter(os.path.join(self.tb_path, 'val'))
        merged = tf.summary.merge_all()

        print(self.params)

        print("\nBeginning training")
        start_time = time.time()
        it = 0
        self.best_model_so_far = {
            general_keys.ITERATION_KEY: 0,
            general_keys.LOSS_KEY: 1e10
        }
        # model used to check if training iteration horizon should be increased
        self.it_horizon_increase_criterion_model = {
            general_keys.ITERATION_KEY: 0,
            general_keys.LOSS_KEY: 1e10
        }
        # train model
        while it < self.params[param_keys.TRAIN_ITERATIONS_HORIZON]:
            # check if validation must take place after every trainning iteration
            # and expand train horizon if validation criterion is met
            self.params[param_keys.TRAIN_ITERATIONS_HORIZON] = self.validate(it, verbose)

            # check if learning rate must be updated
            if it % self.params[param_keys.ITERATIONS_TO_UPDATE_LEARNING_RATE] == 0:
                self.update_learning_rate(it)
                print(
                    "[PARAM UPDATE] Iteration %i (train): Learning rate updated: %.4f"
                    % (it, self.sess.run(self.learning_rate)), flush=True)
            # perform a trainning iteration
            if it % self.params[param_keys.PRINT_EVERY] != 0:
                self.sess.run(self.train_step, feed_dict={self.handle_ph: self.train_handle, self.training_flag: True})
            else:
                # profiling ###############################
                # run_options = tf.RunOptions(trace_level=tf.RunOptions.FULL_TRACE)
                # run_metadata = tf.RunMetadata()
                results = self.sess.run(
                    [self.loss, merged, self.metrics_dict, self.train_step],
                    feed_dict={self.handle_ph: self.train_handle,
                               self.training_flag: True})  # ,
                # options=run_options, run_metadata=run_metadata)
                # Train evaluation
                loss_value, summ, results_dict = [results[0], results[1],
                                                    results[2]]
                print(self._get_message_to_print_loss_and_metrics(
                    previous_message="Iteration %i (train)" % it,
                    loss_value=loss_value, metrics_values_dict=results_dict),
                    flush=True)
                # print("Iteration %i (train): Batch Loss %f, IoU %f, DICE %f" %
                #      (it, loss, iou, dice), flush=True)
                self.train_writer.add_summary(summ, it)
                # self.train_writer.add_run_metadata(run_metadata, 'step%d' % it)
                time_usage = str(datetime.timedelta(
                    seconds=int(round(time.time() - start_time))))
                print("Time usage: " + time_usage, flush=True)
            it += 1

        print("\nTraining Ended\n")
        # Closing writers
        self.train_writer.close()
        self.val_writer.close()
        # Total time
        time_usage = str(
            datetime.timedelta(seconds=int(round(time.time() - start_time))))
        print("Total training time: " + time_usage, flush=True)
        # restore best model so far
        self.saver.restore(self.sess, self.checkpoint_path)
        # evaluate final model
        print("\nEvaluating final model...")
        print("Best model @ it %d.\nValidation loss %.5f" % (
            self.best_model_so_far[general_keys.ITERATION_KEY],
            self.best_model_so_far[general_keys.LOSS_KEY]))
        #final validation evaluation
        metrics = self.test(
            self.val_set.data_array,
            self.val_set.data_label, set='val', verbose=verbose)
        # evaluate model over test set
        if self.test_set is not None:
            metrics = self.test(
                self.test_set.data_array,
                self.test_set.data_label, set='test', verbose=verbose)
        self.test_over_multiple_data_sets(
            self.params[param_keys.DATA_PATH_TO_VALIDATE_SETS], set='val',
            verbose=verbose)
        self.test_over_multiple_data_sets(
            self.params[param_keys.DATA_PATH_TO_TEST_SETS], set='test',
            verbose=verbose)
        # closing train.log
        self.print_manager.dont_print_in_file()
        file.close()
        return metrics

    def test_over_multiple_data_sets(self, data_set_paths_list, set='test',
                                     verbose=True):
        if data_set_paths_list is None:
            return
        for data_set_path in data_set_paths_list:
            test_imgs, test_masks = self._get_set_images_and_labels(
                data_set_path, set)
            print("\n\n-------\n%s Metrics for dataset: %s" % (set, data_set_path))
            self.test(test_imgs, test_masks, set=set, verbose=verbose)

    def _get_message_to_print_loss_and_metrics(self, previous_message,
                                               loss_value, metrics_values_dict):
        message = previous_message + ': Batch loss %f' % loss_value
        for metric_name in metrics_values_dict.keys():
            message += ', %s %f' % (metric_name, metrics_values_dict[metric_name])
        return message

    def update_learning_rate(self, global_step):
        self.sess.run(tf.assign(self.learning_rate,
                                self.params[param_keys.LEARNING_RATE] / (2.0 ** (global_step //
                                                self.params[param_keys.ITERATIONS_TO_UPDATE_LEARNING_RATE]))))

    # TODO: [MUST prec and rec are not batch calculable] make metric estimation more robust to avoid Nans, by calculation over al rate counts instead of batch
    def generate_mean_of_batched_variables(self, set_images, set_labels):
        # define metrics to retrieve
        metrics = list(self.summary_dict.keys())

        metric_data = self.get_variables_from_set_by_batch(set_images,
                                                           set_labels, metrics)
        for metric in metrics:
            metric_data[metric][general_keys.BATCH_MEAN_KEY] = None
        # evaluate set.
        for metric in metrics:
            for i in range(len(metric_data[metric][general_keys.VALUES_PER_BATCH_KEY])):
                if np.isnan(metric_data[metric][general_keys.VALUES_PER_BATCH_KEY][i]):
                    metric_data[metric][general_keys.VALUES_PER_BATCH_KEY][i] = 1.0
        # get accuracy and loss for all batches and delete values per batch
        for metric in metrics:
            metric_data[metric][general_keys.BATCH_MEAN_KEY] = np.array(
                metric_data[metric][general_keys.VALUES_PER_BATCH_KEY]).mean()
            # del metric_data[metric]['values_per_batch']
        return metric_data

    # get variables_list by evaluating set on al batches
    def get_variables_from_set_by_batch(self, set_images, set_labels,
                                        variables_list):
        if not isinstance(variables_list, list): variables_list = [
            variables_list]  # BAD PRACTICE
        # Initialization of the iterator with the actual data
        self.sess.run(self.iterator_validation.initializer,
                      feed_dict={self.validation_img_ph: set_images,
                                 self.validation_lbl_ph: set_labels})
        # define variables to retrieve
        variables_data = {}
        for variable in variables_list:
            variables_data[variable] = {
                general_keys.VALUES_PER_BATCH_KEY: []
            }
        # evaluate set.
        while True:
            try:
                # get batch value
                variables_value = self.sess.run(variables_list,
                                                feed_dict={self.handle_ph: self.validation_handle, self.training_flag: False})
                # append every batch metric to metric_data
                for variable, value in zip(variables_list, variables_value):
                    variables_data[variable][general_keys.VALUES_PER_BATCH_KEY].append(value)
            except tf.errors.OutOfRangeError:
                break
        return variables_data

    def test(self, data_array, data_label, set='Test', verbose=True):
        print = self.print_manager.verbose_printing(verbose)
        metric_data = self.generate_mean_of_batched_variables(data_array,
                                                              data_label)
        results_dict = self._pair_metric_names_and_mean_values_in_dict(
            metrics_dict=self.metrics_dict, metric_mean_values_dict=metric_data)
        print(self._get_message_to_print_loss_and_metrics(
            previous_message="\n%s Metrics" % set,
            loss_value=metric_data[self.loss][general_keys.BATCH_MEAN_KEY],
            metrics_values_dict=results_dict), flush=True)
        return metric_data

    def _pair_metric_names_and_mean_values_in_dict(self, metrics_dict,
                                                   metric_mean_values_dict):
        paired_metric_name_mean_value_dict = {}
        for metric_name in metrics_dict.keys():
            paired_metric_name_mean_value_dict[metric_name] = \
                metric_mean_values_dict[metrics_dict[metric_name]][general_keys.BATCH_MEAN_KEY]
        return paired_metric_name_mean_value_dict

    # TODO: improve verbose management
    def validate(self, current_iteration, verbose=True):
        print = self.print_manager.verbose_printing(verbose)
        # check if current_iteration is multiple of VALIDATION_PERIOD
        # to perform validation every VALIDATION_PERIOD iterations
        if current_iteration % self.params[param_keys.ITERATIONS_TO_VALIDATE] != 0:
            return self.params[param_keys.TRAIN_ITERATIONS_HORIZON]
        # eval evaluation set
        metric_data = self.generate_mean_of_batched_variables(
            self.val_set.data_array, self.val_set.data_label)
        # variables to store: validation accuracy and loss
        metrics = list(self.summary_dict.keys())
        # loss for al validation batches and write them to validation writer
        # as a summary
        for metric in metrics:
            summ = self.sess.run(self.summary_dict[metric], feed_dict={
                metric: metric_data[metric][general_keys.BATCH_MEAN_KEY]})
            self.val_writer.add_summary(summ, current_iteration)
        #print results
        results_dict = self._pair_metric_names_and_mean_values_in_dict(
            metrics_dict=self.metrics_dict, metric_mean_values_dict=metric_data)
        print(self._get_message_to_print_loss_and_metrics(
            previous_message="\nIteration %i (val)" % current_iteration,
            loss_value=metric_data[self.loss][general_keys.BATCH_MEAN_KEY],
            metrics_values_dict=results_dict), flush=True)
        # mean accuracy of validation set
        criterion = metric_data[self.loss][general_keys.BATCH_MEAN_KEY]
        # print("criterion: ", criterion)
        # print("best model so far: ", self.best_model_so_far["loss"])
        # Check if accuracy is over best model so far and overwrite model checkpoint
        if criterion < self.best_model_so_far[general_keys.LOSS_KEY]:
            self.best_model_so_far[general_keys.LOSS_KEY] = criterion
            self.best_model_so_far[general_keys.ITERATION_KEY] = current_iteration
            print("New best validation model: Loss %.4f @ it %d" % (
                self.best_model_so_far[general_keys.LOSS_KEY],
                self.best_model_so_far[general_keys.ITERATION_KEY]))
            self.saver.save(self.sess, self.checkpoint_path)
        # check train horizon extention criterion, which is:
        # if current model error is under 99% of the error of
        # last model that met criterion, train horizon is extended
        # TODO: fix to fit to loss instead of accuracy
        if criterion < self.params[param_keys.CRITERION_PERCENTAGE] * \
                self.it_horizon_increase_criterion_model[general_keys.LOSS_KEY]:
            self.it_horizon_increase_criterion_model[general_keys.LOSS_KEY] = criterion
            self.it_horizon_increase_criterion_model[general_keys.ITERATION_KEY] = current_iteration
            new_train_horizon = current_iteration + self.params[param_keys.TRAIN_HORIZON_INCREMENT]
            if new_train_horizon > self.params[param_keys.TRAIN_ITERATIONS_HORIZON]:
                print(
                    "Train iterations increased to %d because of model with loss %.4f @ it %d\n" % (
                        new_train_horizon,
                        self.it_horizon_increase_criterion_model[general_keys.LOSS_KEY],
                        self.it_horizon_increase_criterion_model[general_keys.ITERATION_KEY]
                    ))
                return new_train_horizon
            else:
                print("\n")
                return self.params[param_keys.TRAIN_ITERATIONS_HORIZON]
        else:
            print("\n")
            return self.params[param_keys.TRAIN_ITERATIONS_HORIZON]

    # TODO implement builder pattern to avoid code replication and reduce 2 lines
    def _iterator_init(self, params):
        with tf.name_scope("iterators"):
            train_it_builder = train_iterator.TrainIteratorBuilder(params)
            iterator_train, train_sample_ph, train_lbl_ph = train_it_builder.get_iterator_and_ph()
            val_it_builder = validation_iterator.ValidationIteratorBuilder(
                params)
            iterator_val, val_sample_ph, val_lbl_ph = val_it_builder.get_iterator_and_ph()
            handle_ph, global_iterator = train_it_builder.get_global_iterator()
        return global_iterator, handle_ph, train_sample_ph, train_lbl_ph, iterator_train, val_sample_ph, val_lbl_ph, \
               iterator_val

    def _define_inputs(self):
        input_batch, input_labels = self.global_iterator.get_next()
        # Transform labels to onehot
        input_labels = tf.one_hot(
            input_labels, self.params[param_keys.NUMBER_OF_CLASSES])
        # Transform input batch to float32 and standardize
        input_batch = tf.cast(input_batch, dtype=tf.float32)
        input_batch = input_batch / 255.0  # To [0, 1] range
        training_flag = tf.placeholder(tf.bool, shape=None, name='training_flag')

        return input_batch, input_labels, training_flag

    def _init_network(self, X, params, training_flag):
        network = neural_net.Network(X, params, training_flag)
        return network.get_output()

    def _loss_init(self, logits, input_labels, number_of_classes):
        with tf.name_scope("loss"):
            loss = losses.xentropy(logits, input_labels, number_of_classes)
        return loss

    def _optimizer_init(self, loss, learning_rate_value):
        with tf.name_scope("optimizer"):
            train_step, learning_rate = optimizers.adam(
                loss, learning_rate_value)
        return train_step, learning_rate

    def _build_graph(self, params):
        with tf.name_scope('inputs'):
            input_batch, input_labels, training_flag = self._define_inputs()
        with tf.variable_scope('network'):
            logits = self._init_network(input_batch, params, training_flag)
        with tf.name_scope('outputs'):
            output_probabilities = tf.nn.softmax(logits)
            output_predicted_classes = tf.argmax(output_probabilities, 3)
        return input_batch, input_labels, training_flag, logits, output_probabilities, output_predicted_classes

    def predict(self, X):
        results = self.get_variables_from_set_by_batch(
            X, np.zeros_like(X)[..., 0], self.output_pred_cls)
        results = np.concatenate(
            results[self.output_pred_cls][general_keys.VALUES_PER_BATCH_KEY])
        results = results.astype(np.uint8)
        return results


if __name__ == "__main__":
    params = {}

    # path_weights = '/home/asceta/Alerce/AlerceDHtest/weights/CAP3c'
    model = U_net(params)
    model._create_paths()
    train_writer = tf.summary.FileWriter(model.tb_path + 'train',
                                         model.sess.graph)
# DH.train()