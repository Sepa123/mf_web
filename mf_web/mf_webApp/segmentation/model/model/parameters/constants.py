"""Modules that defines useful constants for the project."""

# Database split
TRAIN_SUBSET = 'train'
VAL_SUBSET = 'val'
TEST_SUBSET = 'test'

# Type of padding
PAD_SAME = 'same'
PAD_VALID = 'valid'

# Type of batch normalization
BN = 'bn'
BN_RENORM = 'bn_renorm'

# Type of pooling
MAXPOOL = 'maxpool'
AVGPOOL = 'avgpool'

# Types of loss
CROSS_ENTROPY_LOSS = 'cross_entropy_loss'
DICE_LOSS = 'dice_loss'

# Types of optimizer
ADAM_OPTIMIZER = 'adam_optimizer'
SGD_OPTIMIZER = 'sgd_optimizer'
MOMENTUM_SGD_OPTIMIZER = 'momentum_sgd_optimizer'

# Error message, parameter not in valid list
ERROR_INVALID = 'Expected %s for %s, but %s was provided.'
