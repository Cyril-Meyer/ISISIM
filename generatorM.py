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

                if len(label_coord_) == 0:
                    print('error empty label_coord_', i, len(label_coord_))
                    continue

                coord = tuple(label_coord_[random.randint(0, len(label_coord_)-1)])
                click_map[coord] = 1
                click_pos.append(coord)

                if d_step is not None:
                    # remove label_coord_ closer than d_step
                    distances = np.sqrt(np.sum(np.square(np.array(coord) - label_coord_), axis=1))
                    label_coord_ = label_coord_[np.where(distances > d_step)]

        yield click_map, click_pos


# generate click around the border
# after the first click, the next maximize distance between clicks
# inspired by Xu et al. strategy 3
# max_boundary_distance : maximum distance to the border
# min_border_distance : minimum distance to the border
# max_boundary_distance and min_border_distance select the area where the clicks are sampled
def gen_click_around_border(label, label_dt=None, click=5, max_border_distance=10, min_border_distance=0):
    if label_dt is None:
        label_dt = edt.edt(label)

    if max_border_distance is not None:
        label_dt = np.logical_and(label_dt < max_border_distance, label_dt > min_border_distance)

    labels_n = np.max(label)
    label_coord = []
    for i in range(1, labels_n + 1):
        label_coord.append(np.argwhere(np.logical_and(label == i, label_dt > 0)))

    while True:
        click_map = np.zeros(label.shape, dtype=label.dtype)
        click_pos = []

        for i in range(labels_n):
            click_pos_i = []
            label_coord_ = np.copy(label_coord[i])

            # sample first random click
            coord = tuple(label_coord_[random.randint(0, len(label_coord_) - 1)])
            click_map[coord] = 1
            click_pos.append(coord)
            click_pos_i.append(coord)
            for _ in range(click-1):
                # compute sum distance to the existing click
                distances = np.zeros(len(label_coord_))
                for p in click_pos_i:
                    distances = distances + np.sqrt(np.sum(np.square(np.array(p) - label_coord_), axis=1))
                # keep the click which maximize the distance
                coord = tuple(label_coord_[np.argmax(distances)])
                click_map[coord] = 1
                click_pos.append(coord)
                click_pos_i.append(coord)

        yield click_map, click_pos


# generate 4(2D)/6(3D) extreme points click
def get_click_extreme_points(label):
    labels_n = np.max(label)

    click_map = np.zeros(label.shape, dtype=label.dtype)
    click_pos = []

    def add_click(coord):
        click_pos.append(coord)
        click_map[coord] = 1

    def get_3d_coord(view):
        label_coord = np.argwhere(view > 0)
        xmin = np.min(label_coord[:, 0])
        ymin = np.random.choice(np.argwhere(view[xmin])[:, 0])
        zmin = np.random.choice(np.argwhere(view[xmin])[:, 1])
        xmax = np.max(label_coord[:, 0])
        ymax = np.random.choice(np.argwhere(view[xmax])[:, 0])
        zmax = np.random.choice(np.argwhere(view[xmax])[:, 1])
        return xmin, ymin, zmin, xmax, ymax, zmax

    if len(label.shape) == 2:
        for i in range(labels_n):
            view_ = label == i+1
            view = np.expand_dims(view_, -1)
            xmin, ymin, zmin, xmax, ymax, zmax = get_3d_coord(view)
            add_click(tuple([xmin, ymin]))
            add_click(tuple([xmax, ymax]))

            view = np.expand_dims(np.swapaxes(view_, 0, 1), -1)
            xmin, ymin, zmin, xmax, ymax, zmax = get_3d_coord(view)
            add_click(tuple([ymin, xmin]))
            add_click(tuple([ymax, xmax]))

    elif len(label.shape) == 3:
        for i in range(labels_n):
            view_ = label == i+1
            xmin, ymin, zmin, xmax, ymax, zmax = get_3d_coord(view_)
            add_click(tuple([xmin, ymin, zmin]))
            add_click(tuple([xmax, ymax, zmax]))

            view = np.swapaxes(view_, 1, 0)
            xmin, ymin, zmin, xmax, ymax, zmax = get_3d_coord(view)
            add_click(tuple([ymin, xmin, zmin]))
            add_click(tuple([ymax, xmax, zmax]))

            view = np.swapaxes(view_, 2, 0)
            xmin, ymin, zmin, xmax, ymax, zmax = get_3d_coord(view)
            add_click(tuple([zmin, ymin, xmin]))
            add_click(tuple([zmax, ymax, xmax]))

    return click_map, click_pos


# generate random click to fill the label.
# d_step   : minimum distance between different clicks
# d_margin : minimum distance to the border
def gen_click_fill(label, label_dt=None, d_step=50, d_margin=20):
    assert d_step > 0

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

            while True:
                if len(label_coord_) == 0:
                    break

                coord = tuple(label_coord_[random.randint(0, len(label_coord_)-1)])
                click_map[coord] = 1
                click_pos.append(coord)

                if d_step is not None:
                    # remove label_coord_ closer than d_step
                    distances = np.sqrt(np.sum(np.square(np.array(coord) - label_coord_), axis=1))
                    label_coord_ = label_coord_[np.where(distances > d_step)]

        yield click_map, click_pos
