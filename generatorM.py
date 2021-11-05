# ---------------------------------------------------------------------------- #
#           ISISIM - Interactive Segmentation Interaction SIMulation           #
# generatorM.py (generatorMultiple)
# generator for label with multiple object
# ---------------------------------------------------------------------------- #
# common arguments
# label    : a 2D/3D numpy array, if label is binary, use skimage.measure.label
# label_dt : label distance transform
# click    : number of click
# ---------------------------------------------------------------------------- #
import random
import time
import numpy as np
import edt


# generate random (uniform) click
def gen_click_random_uniform(label, click=5):
    labels_n = np.max(label)
    label_coord = []
    for i in range(1, labels_n+1):
        print(i)
        label_coord.append(np.argwhere(label == i))

    while True:
        click_map = np.zeros(label.shape, dtype=label.dtype)
        click_pos = []

        for i in range(labels_n):
            label_coord_ = np.copy(label_coord[i])

            for _ in range(click):
                coord = tuple(label_coord_[random.randint(0, len(label_coord_)-1)])
                click_map[coord] = 1
                click_pos.append(coord)

        yield click_map, click_pos


# generate random (uniform) click with step and margin options
# d_step   : minimum distance between different clicks
# d_margin : minimum distance to the border
# d_margin allow not to sample click near border
def gen_click_random_uniform_advanced(label, label_dt=None, click=5, d_step=10, d_margin=10):
    if label_dt is None:
        label_dt = edt.edt(label > 0)

    if d_margin is not None:
        label_dt = label_dt > d_margin

    labels_n = np.max(label)
    label_coord = []
    for i in range(1, labels_n + 1):
        label_coord.append(np.argwhere(np.logical_and(label == i, label_dt > 0)))

    while True:
        click_map = np.zeros(label.shape, dtype=label.dtype)
        click_pos = []

        for i in range(labels_n):
            label_coord_ = np.copy(label_coord[i])

            for _ in range(click):
                if len(label_coord_) == 0:
                    label_coord_ = np.copy(label_coord[i])

                coord = tuple(label_coord_[random.randint(0, len(label_coord_)-1)])
                click_map[coord] = 1
                click_pos.append(coord)

                if d_step is not None:
                    # remove label_coord_ closer than d_step
                    distances = np.sqrt(np.sum(np.square(np.array(coord) - label_coord_), axis=1))
                    label_coord_ = label_coord_[np.where(distances > d_step)]

        yield click_map, click_pos
