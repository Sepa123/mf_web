from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from . import train_iterator


class ValidationIteratorBuilder(train_iterator.TrainIteratorBuilder):

    def __init__(self, params, post_batch_processing=None, pre_batch_processing=None):
        super().__init__(params, post_batch_processing, pre_batch_processing)

    def _shuffle_and_repeat(self, dataset, shuffle_buffer):
        return dataset
