"""Module that defines the parameters to configure the model and their
default values."""

from . import constants


# Input params
"""
validation_random_seed: (int) Random seed to be used to split the validation
    data from the training data.
"""
DATA_PATH = 'data_path'
CHECKPOINT_PATH_TO_STAR_FINETUNE = 'checkpoint_path_to_star_fine_tune'
DATA_PATH_4_TRANSFER_LEARNING = 'data_path_4_transfer_learning'
DATA_PATH_TO_TEST_SETS = 'data_path_to_test_sets'
DATA_PATH_TO_VALIDATE_SETS = 'data_path_to_validate_sets'
DATA_PATH_ELASTIC = 'data_path_elastic'
BATCH_SIZE = 'batch_size'
NUMBER_OF_CLASSES = 'number_of_classes'
INPUT_CHANNELS = 'input_channels'
INPUT_IMAGE_SIZE = 'input_image_size'
SHUFFLE_BUFFER_SIZE = 'shuffle_buffer_size'
PREFETCH_BUFFER_SIZE = 'prefetch_buffer_size'
VALIDATION_RANDOM_SEED = 'validation_random_seed'

BATCH_SIZE_ORIGINAL = 'batch_size_original'
BATCH_SIZE_ELASTIC = 'batch_size_elastic'

SHIFT_MAX = 'shift_max'
SHIFT_NUMBER = 'shift_number'
ANGLE_STEP = 'angle_step'
PERCENTAGE_OF_AUGMENTED_DATA = 'percentage_of_augmented_data'

# Model params
"""
batchnorm_conv: ({None, BN, BN_RENORM}) Type of batchnorm to be used in the
    convolutions. If None, no batchnorm is applied.
drop_rate: ({None, int}) Dropout rate to be applied. If None, no dropout is
    applied.
"""
BATCHNORM_CONV = 'batchnorm_conv'
# DROP_RATE = 'drop_rate'
INITIAL_CONV_FILTERS = 'initial_conv_filters'

# Loss params
"""
type_loss: ({CROSS_ENTROPY_LOSS, DICE_LOSS}) Type of loss to be minimized.
"""
# TYPE_LOSS = 'type_loss'

# Optimizer params
"""
learning_rate: (float) initial learning rate value
type_optimizer: ({SGD_OPTIMIZER, MOMENTUM_SGD_OPTIMIZER, ADAM_OPTIMIZER}) Type
    of optimizer to be used.
momentum: (float) Momentum to be used with MOMENTUM_SGD_OPTIMIZER. 
    If other optimizer is used, then this parameter has no effect.
use_nesterov_momentum: (bool) If true, and if a momentum optimizer is used, 
    Nesterov momentum is applied.
"""
LEARNING_RATE = 'learning_rate'
# TYPE_OPTIMIZER = 'type_optimizer'
# MOMENTUM = 'momentum'
# USE_NESTEROV_MOMENTUM = 'use_nesterov_momentum'

# Training params
"""
print_every: (int) How many iterations to wait before printing stats.
train_iterations_horizon: (int) How many iterations to train.
iterations_to_update_learning_rate: (int) How many iterations to wait before
    decreasing the learning rate
iterations_to_validate: (int) How many iterations to wait before validating.
criterion_percentage: (float between 0 and 1) Percentage to meet wrt the last 
    best loss, to verify that the loss is still improving and we have to
    increment the training iterations.
train_horizon_increment: (int) How many iterations to be added if criterion
    percentage is met.
"""
PRINT_EVERY = 'print_every'
TRAIN_ITERATIONS_HORIZON = 'train_iterations_horizon'
ITERATIONS_TO_UPDATE_LEARNING_RATE = 'iterations_to_update_learning_rate'
ITERATIONS_TO_VALIDATE = 'iterations_to_validate'
TRAIN_HORIZON_INCREMENT = 'train_horizon_increment'
CRITERION_PERCENTAGE = 'criterion_percentage'

# Default parameters dictionary
"""
Usage:
    Import the default parameters dictionary as:
    
        from parameters import param_keys
        my_dict = param_keys.default_params
    
    Then, if you want to overwrite some values that are inside a dictionary
    named "my_custom_parameters", you can simply do:
    
        my_dict.update(my_custom_parameters)  # Overwrite defaults
        
"""
default_params = {
    DATA_PATH: None,
    DATA_PATH_4_TRANSFER_LEARNING: None,
    DATA_PATH_TO_TEST_SETS: None,
    DATA_PATH_TO_VALIDATE_SETS: None,
    DATA_PATH_ELASTIC: None,
    CHECKPOINT_PATH_TO_STAR_FINETUNE: None,
    BATCH_SIZE: 8,
    BATCH_SIZE_ORIGINAL: 4,
    BATCH_SIZE_ELASTIC: 4,
    SHIFT_MAX: 0.15,
    SHIFT_NUMBER: 4,
    ANGLE_STEP: 20,
    NUMBER_OF_CLASSES: 3,
    INPUT_CHANNELS: 1,
    INPUT_IMAGE_SIZE: 256,
    SHUFFLE_BUFFER_SIZE: 100,
    PREFETCH_BUFFER_SIZE: 20,
    VALIDATION_RANDOM_SEED: 1234,
    BATCHNORM_CONV: constants.BN,
    INITIAL_CONV_FILTERS: 64,
    LEARNING_RATE: 1e-4,  # This is currently ignored by Adam
    PRINT_EVERY: 100,
    TRAIN_ITERATIONS_HORIZON: 1e4,
    ITERATIONS_TO_UPDATE_LEARNING_RATE: 1e4,
    ITERATIONS_TO_VALIDATE: 1e3,
    CRITERION_PERCENTAGE: 0.995,
    PERCENTAGE_OF_AUGMENTED_DATA: 0.5
}
# Now set default values that depend on other params
default_params.update({
    TRAIN_HORIZON_INCREMENT: default_params[TRAIN_ITERATIONS_HORIZON],
    DATA_PATH_TO_VALIDATE_SETS: default_params[DATA_PATH_TO_TEST_SETS]
})
