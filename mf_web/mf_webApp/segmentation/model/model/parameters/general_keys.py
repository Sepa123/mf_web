"""Module that defines miscellaneous keys to manipulate the model"""

# For fitting (keep best models in validation)
ITERATION_KEY = 'iteration'
LOSS_KEY = 'loss'

# Names of metrics
IOU_ENDO_KEY = 'iou_endo'
IOU_EPI_KEY = 'iou_epi'
IOU_MYO_KEY = 'iou_myo'
DICE_ENDO_KEY = 'dice_endo'
DICE_EPI_KEY = 'dice_epi'
DICE_MYO_KEY = 'dice_myo'

# To evaluate the metrics
BATCH_MEAN_KEY = 'batch_mean'
VALUES_PER_BATCH_KEY = 'values_per_batch'
