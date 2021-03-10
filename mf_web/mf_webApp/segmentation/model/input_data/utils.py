import os

import matplotlib.pyplot as plt
import numpy as np
import pydicom
from skimage import exposure

PATH_TO_PROJECT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', '..'))
IMAGE_SIZE = 256


def parse_cfg(filename, delimiter=':'):
    """ Returns dict with key=value of cfg file without header
    """
    cfg_dict = {}
    with open(filename, 'r') as file:
        for line in file:
            key, value = line.partition(delimiter)[::2]
            key = key.strip()
            value = value.strip().rstrip('\n')
            cfg_dict[key] = value
    return cfg_dict


def fix_size(data):
    """Transforms data to IMAGE_SIZExIMAGE_SIZE image. Data can be XY, XYZ,
    or XYZT.
    """
    max_side = max(data.shape[0], data.shape[1])
    if max_side == 2*IMAGE_SIZE:  # First, control specific case of a single example in ACDC
        data = data[::2, ::2]
    if max_side > IMAGE_SIZE:  # Now crop
        data = data[:IMAGE_SIZE, :IMAGE_SIZE]
    padded_data = zero_pad(data, IMAGE_SIZE)  # Fill with zeros
    return padded_data


def zero_pad(data, size):
    """ Zero pads the X and Y dimensions to sizexsize.
    Data can be XY, XYZ, or XYZT.
    """
    if max(data.shape[0], data.shape[1]) > size:
        raise ValueError("Data can't be padded to a smaller shape.")
    x_pad = size - data.shape[0]
    y_pad = size - data.shape[1]
    x_before = x_pad // 2
    x_after = x_pad - x_before
    y_before = y_pad // 2
    y_after = y_pad - y_before
    if data.ndim == 2:
        padding = ((x_before, x_after), (y_before, y_after))
    elif data.ndim == 3:
        padding = ((x_before, x_after), (y_before, y_after), (0, 0))
    elif data.ndim == 4:
        padding = ((x_before, x_after), (y_before, y_after), (0, 0), (0, 0))
    else:
        raise ValueError("Data should be 2D, 3D or 4D.")
    padded_data = np.pad(data, padding, 'constant')
    return padded_data


def clip_norm(data, lower_percentile=0, upper_percentile=99):
    """Clips pixel values to percentile bounds, and then reescales to [0, 255] range.
    Data can be XY, XYZ, or XYZT.
    """
    if data.ndim == 2:  # XY, base case
        lower_clip, upper_clip = np.percentile(
            data, (lower_percentile, upper_percentile))
        clipped_data = np.clip(data, lower_clip, upper_clip)
        clipped_data = exposure.rescale_intensity(
            clipped_data, out_range=(0, 255))
    elif data.ndim == 3 or data.ndim == 4:  #XYZ or XYZT, one slice at a time
        tmp_list = []
        for z in range(data.shape[2]):
            lower_clip, upper_clip = np.percentile(
                data[:, :, z], (lower_percentile, upper_percentile))
            tmp_data = np.clip(data[:, :, z], lower_clip, upper_clip)
            tmp_data = exposure.rescale_intensity(tmp_data, out_range=(0, 255))
            tmp_list.append(tmp_data)
        clipped_data = np.stack(tmp_list, axis=2)
    else:
        raise ValueError('Data should be XY, XYZ, or XYZT')
    clipped_data = clipped_data.astype(np.uint8)  # Fixes the dtype
    return clipped_data


def drop_slice_without_all_annot(data, annot, i=None):
    """ Removes slices with no annotations associated in 'annot' in some
    timestep. Assumes shape XYZT, and annotations as masks with integer labels,
    0 for background.
    """
    tmp_data = []
    tmp_annot = []
    for z in range(data.shape[2]):
        cond = [np.any(annot[:, :, z, t] > 0) for t in range(data.shape[3])]
        if np.all(cond):
            tmp_data.append(data[:, :, z, :])
            tmp_annot.append(annot[:, :, z, :])
        else:
            if i is not None:
                print('Drop slice %d of patient %d' % (z, i))
    new_data = np.stack(tmp_data, axis=2)
    new_annot = np.stack(tmp_annot, axis=2)
    return new_data, new_annot


def number_of_dicom_in_folder(folder_path):
    """ Returns number of dicom files inside this folder
    """
    image_list = os.listdir(folder_path)
    image_list = [image for image in image_list if '.dcm' in image]
    return len(image_list)


def get_dicom_in_folder(folder_path):
    """ Returns XYZT array of the content of the folder. Z is a dummy dimension
    """
    image_list = os.listdir(folder_path)
    image_list = [image for image in image_list if '.dcm' in image]
    image_list.sort()
    image_array = []
    for image in image_list:
        this_dicom = pydicom.dcmread(os.path.join(folder_path, image))
        this_array = this_dicom.pixel_array.astype(int)
        image_array.append(this_array)
    image_array = np.stack(image_array, axis=2)
    image_array = image_array[:, :, np.newaxis, :]
    return image_array


def get_dicom_in_folder_and_slices(folder_path):
    """ Returns XYZT array of the content of the folder.

    Z is a dummy dimension. The number of slices is also provided.
    """
    image_list = os.listdir(folder_path)
    image_list = [image for image in image_list if '.dcm' in image]
    image_list.sort()
    image_array = []
    slices_list = []
    for image in image_list:
        this_dicom = pydicom.dcmread(os.path.join(folder_path, image))
        this_array = this_dicom.pixel_array.astype(int)
        this_slice_id = this_dicom[0x020, 0x1041].value
        image_array.append(this_array)
        slices_list.append(this_slice_id)
    n_slices = np.unique(slices_list).size
    image_array = np.stack(image_array, axis=2)
    image_array = image_array[:, :, np.newaxis, :]
    return image_array, n_slices


def split_slices(data, n_slices):
    """Splits a XYZT data with mixed slices, into different slices
    along the Z dimension"""
    total_frames = data.shape[-1]
    frames_to_drop = total_frames % n_slices
    if frames_to_drop > 0:
        print('The first %d frames were dropped' % frames_to_drop)
        data = data[..., frames_to_drop:]
    splitted_data = []
    for i in range(n_slices):
        this_slice = data[..., i::n_slices]
        splitted_data.append(this_slice)
    splitted_data = np.concatenate(splitted_data, axis=2)
    return splitted_data, frames_to_drop


def swap_labels(marks):
    """Swaps labels 1 and 2 for marks with labels {0, 1, 2}"""
    swapped_marks = marks.copy()
    swapped_marks[marks == 1] = 2
    swapped_marks[marks == 2] = 1
    swapped_marks = swapped_marks.astype(np.uint8)
    return swapped_marks


#def animate(video, n_seconds):
#    """ Assumes shape TXY of a grayscale video. Returns an animation object
#    to be used with 'display' in an IPython notebook.
#
#    Example:
#        animate(video, n_seconds).ipython_display(
#            fps=int(n_frames/n_seconds), loop=True, autoplay=True)
#    """
#    print('Video of shape:', video.shape)
#    if video.ndim > 3:
#        raise ValueError('Video has to be 3D.')
#    make_frame = get_make_frame_fn(video, n_seconds)
#    animation = VideoClip(make_frame, duration=n_seconds)
#    return animation


def get_make_frame_fn(video, n_seconds):
    """Returns function for animation
    """
    video = np.asarray(video)
    video = exposure.rescale_intensity(video, out_range=(0, 255))
    video = video.astype(np.uint8)

    def make_frame(t):
        k = int(video.shape[0] * t / n_seconds)
        np_frame = video[k, :, :]
        np_frame_rgb = np.stack([np_frame, np_frame, np_frame], axis=2)
        return np_frame_rgb
    return make_frame


def plot_segmentation(image, mark, figsize=(10, 5), title=''):
    """Plots a single frame with its marks"""
    fig, ax = plt.subplots(1, 2, figsize=figsize)
    ax[0].imshow(image, cmap='gray', interpolation='none')
    ax[0].axis('off')
    ax[0].set_title('%s (Image)' % title)
    ax[1].imshow(image, cmap='gray', interpolation='none')
    ax[1].imshow(mark, cmap='jet', interpolation='none', alpha=0.5)
    ax[1].axis('off')
    ax[1].set_title('%s (Marks)' % title)
    plt.show()
