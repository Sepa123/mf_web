#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 18 18:05:40 2018

Dataset Object

CHECK MAX DISBALANCE OPN REPLICATION FOR MULTICLASS

@author: ereyes
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np


class Dataset(object):
    
    """
    Constructor
    """
    def __init__(self, data_array, data_labels, batch_size):
        self.batch_counter = 0
        self.batch_counter_eval = 0
        self.batch_size = batch_size
        self.data_array = data_array
        self.data_label = data_labels
        
    def _merge_with_dataset(self, array, labels):
        self.data_label = np.concatenate((self.data_label, labels))
        self.data_array = np.concatenate((self.data_array, array))

    def get_batch_images(self):
        batch, _ = self.get_batch()
        
        return batch
    
    def get_batch(self):
        if self.batch_counter+self.batch_size < self.data_array.shape[0]:
            batch_image = self.data_array[self.batch_counter:self.batch_counter + self.batch_size, ...]
            batch_label = self.data_label[self.batch_counter:self.batch_counter + self.batch_size, ...]
            self.batch_counter += self.batch_size
            # print(get_batch.batch_counter)
        else:
            self.batch_counter = 0
            self.shuffle_data()
            batch_image = self.data_array[self.batch_counter:self.batch_counter + self.batch_size, ...]
            batch_label = self.data_label[self.batch_counter:self.batch_counter + self.batch_size, ...]
            self.batch_counter += self.batch_size
        
        return batch_image, batch_label
    
    def get_batch_eval(self):
        print(self.batch_counter_eval)
        if self.batch_counter_eval+self.batch_size < self.data_array.shape[0]:
            batch_image = self.data_array[self.batch_counter_eval:self.batch_counter_eval + self.batch_size, ...]
            batch_label = self.data_label[self.batch_counter_eval:self.batch_counter_eval + self.batch_size, ...]
            self.batch_counter_eval += self.batch_size
            # print(get_batch.batch_counter)
        else:
            left_samples = self.data_array.shape[0]-self.batch_counter_eval
            batch_image = self.data_array[self.batch_counter_eval:self.batch_counter_eval + left_samples, ...]
            batch_label = self.data_label[self.batch_counter_eval:self.batch_counter_eval + left_samples, ...]
            self.batch_counter_eval = 0
        
        return batch_image, batch_label
    
    def shuffle_data(self):
        idx = np.arange(self.data_array.shape[0])
        np.random.shuffle(idx)        
        self.data_array = self.data_array[idx, ...]
        self.data_label = self.data_label[idx, ...]
        
    # TODO: change both values for uique functions (AVOID CODE REPLICATION)
    # TODO: recursively? replicate_data should be?
    # TODO: min_lbl_count changes on very iteration, it should stay the same or shuffle
    # of replicate_data cannot be
    def balance_data_by_replication(self):
        max_disbalance = self.get_max_disbalance()
        max_lbl_count, min_lbl_count  = self.get_max_min_label_count()
        max_lbl, min_lbl = self.get_max_min_label()
        
        if max_disbalance == 0:
            return     
        while max_disbalance != 0:
            if min_lbl_count > max_disbalance:
                self.replicate_data(min_lbl, max_disbalance)
                # max_disbalance = 0
            else:
                self.replicate_data(min_lbl, min_lbl_count)
                # max_disbalance -= min_lbl_count
            max_disbalance = self.get_max_disbalance()#
        self.balance_data_by_replication()
        return    

    def get_max_disbalance(self):
        max_label_count, min_label_count = self.get_max_min_label_count()
        return max_label_count-min_label_count

    def get_max_min_label_count(self):
        max_label, min_label = self.get_max_min_label()
        
        max_label_count = np.where(self.data_label == max_label)[0].shape[0]
        min_label_count = np.where(self.data_label == min_label)[0].shape[0]
        
        return max_label_count, min_label_count

    def get_max_min_label(self):
        labels = np.unique(self.data_label)
        labels_count = []
        
        for j in range(labels.shape[0]):
            label_j_count = np.where(self.data_label==labels[j])[0].shape[0]
            labels_count.append(label_j_count)
        
        labels_count = np.array(labels_count)
        
        max_label = labels[np.where(labels_count == np.max(labels_count))[0][0]]
        min_label = labels[np.where(labels_count == np.min(labels_count))[0][0]]
        return max_label, min_label

    def replicate_data(self, label, samples_number):
        # print("%i samples replicated of class %i" %(samples_number,label))
        label_idx = np.where(self.data_label == label)[0]
        # np.random.shuffle(label_idx)
        label_idx = label_idx[0:samples_number]
        replicated_data_array = self.data_array[label_idx, ...]
        self._merge_with_dataset(replicated_data_array, label)
        
    def get_array_from_label(self, label):
        label_idx = np.where(self.data_label == label)[0]
        return self.data_array[label_idx]
