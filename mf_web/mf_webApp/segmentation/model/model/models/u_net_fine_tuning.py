#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unet with batchnormalization layers as in https://github.com/ankurhanda/tf-unet/blob/master/UNet.py
Anddata uagmentation that performs flips, rotations ans shifts

Added addon to perform a fine tuning with second dataset
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
from ..models.u_net_online_aug_model import U_net_online_aug
from ..modules.data_set_generic import Dataset as data_set_class
from ..modules.data_splitter import DatasetDivider
from ..parameters import param_keys, general_keys

# TODO: refactor train test and validate
class U_net_fine_tune(U_net_online_aug):
    """
    Constructor
    """

    def __init__(self, params={}, model_name="U-net_fine_tune"):
        super().__init__(params, model_name)

    def _prepare_fine_tune_input(self, X, y):
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
                self.params[param_keys.DATA_PATH_4_TRANSFER_LEARNING])
        train_set = self._global_shuffling(train_set)
        return train_set, val_set, test_set

    def _check_if_train_from_scratch(self, params):
        if params[param_keys.CHECKPOINT_PATH_TO_STAR_FINETUNE] is None:
            self.fit()
        else:
            self.saver.restore(
                self.sess, params[param_keys.CHECKPOINT_PATH_TO_STAR_FINETUNE])

    def fine_tune(self, X=np.empty([]), y=np.empty([]), verbose=True, log_file='train_fine_tune.log'):
        self._check_if_train_from_scratch(self.params)
        self.train_set, self.val_set, self.test_set = self._prepare_fine_tune_input(
            X, y)
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
        self.train_writer = tf.summary.FileWriter(
            os.path.join(self.tb_path, 'train_fine_tune'),
            self.sess.graph)
        self.val_writer = tf.summary.FileWriter(
            os.path.join(self.tb_path, 'val_fine_tune'))
        merged = tf.summary.merge_all()

        print(self.params)

        print("\nBeginning fine tuning")
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
            self.params[param_keys.TRAIN_ITERATIONS_HORIZON] = self.validate(
                it, verbose)

            # check if learning rate must be updated
            if it % self.params[
                param_keys.ITERATIONS_TO_UPDATE_LEARNING_RATE] == 0:
                self.update_learning_rate(it)
                print(
                    "[PARAM UPDATE] Iteration %i (train): Learning rate updated: %.4f"
                    % (it, self.sess.run(self.learning_rate)), flush=True)
            # perform a trainning iteration
            if it % self.params[param_keys.PRINT_EVERY] != 0:
                self.sess.run(self.train_step,
                              feed_dict={self.handle_ph: self.train_handle,
                                         self.training_flag: True})
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

        print("\nFine Tuning Ended\n")
        # Closing writers
        self.train_writer.close()
        self.val_writer.close()
        # Total time
        time_usage = str(
            datetime.timedelta(seconds=int(round(time.time() - start_time))))
        print("Total tuning time: " + time_usage, flush=True)
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

