# ---------------------------------------------------------------------------- #
#           ISISIM - Interactive Segmentation Interaction SIMulation           #
# generatorS.py (generatorSingle)
# generator for label with a single object
# ---------------------------------------------------------------------------- #
# common arguments
# label    : a 2D/3D numpy array
# label_dt : label distance transform
# click    : number of click
# ---------------------------------------------------------------------------- #
import random
import time
import numpy as np
import edt


# generate random (uniform) click
def gen_click_random_uniform(label, click=5):
    label_coord = np.argwhere(label)

    while True:
        click_map = np.zeros(label.shape, dtype=label.dtype)
        click_pos = []

        for _ in range(click):
            coord = tuple(label_coord[random.randint(0, len(label_coord)-1)])
            click_map[coord] = 1
            click_pos.append(coord)

        yield click_map, click_pos


# generate random (uniform) click with step and margin options
# d_step   : minimum distance between different clicks
# d_margin : minimum distance to the border
# d_margin allow not to sample click near border
def gen_click_random_uniform_advanced(label, label_dt=None, click=5, d_step=10, d_margin=10):
    if label_dt is None:
        label_dt = edt.edt(label)

    if d_margin is not None:
        label_dt = label_dt > d_margin

    label_coord = np.argwhere(label_dt)

    while True:
        label_dt_ = np.copy(label_dt)
        label_coord_ = np.copy(label_coord)

        click_map = np.zeros(label.shape, dtype=label.dtype)
        click_pos = []

        for _ in range(click):
            coord = tuple(label_coord_[random.randint(0, len(label_coord_)-1)])
            click_map[coord] = 1
            click_pos.append(coord)

            if d_step is not None:
                # remove label_coord_ closer than d_step
                # distances = np.sqrt(np.sum(np.square(np.array(coord) - label_coord_), axis=1))
                # label_coord_ = label_coord_[np.where(distances > d_step)]

                if len(label.shape) == 2:
                    label_dt_[coord[0]-d_step:coord[0]+d_step,
                              coord[1]-d_step:coord[1]+d_step] = False
                else:
                    label_dt_[coord[0]-d_step:coord[0]+d_step,
                              coord[1]-d_step:coord[1]+d_step,
                              coord[2]-d_step:coord[2]+d_step] = False
                label_coord_ = np.argwhere(label_dt_)

        yield click_map, click_pos


# generate click around the border
# after the first click, the next maximize distance between clicks
# inspired by Xu et al. strategy 3
# max_boundary_distance : maximum distance to the border
# max_boundary_distance select the area where the clicks are sampled
def gen_click_around_border(label, label_dt=None, click=5, max_border_distance=10):
    if label_dt is None:
        label_dt = edt.edt(label)

    if max_border_distance is not None:
        label_dt = np.logical_and(label_dt < max_border_distance, label_dt > 0)

    label_coord = np.argwhere(label_dt)

    while True:
        label_dt_ = np.copy(label_dt)
        label_coord_ = np.copy(label_coord)

        click_map = np.zeros(label.shape, dtype=label.dtype)
        click_pos = []

        # sample first random click
        coord = tuple(label_coord_[random.randint(0, len(label_coord_) - 1)])
        click_map[coord] = 1
        click_pos.append(coord)
        for _ in range(click-1):
            # compute sum distance to the existing click
            distances = np.zeros(len(label_coord_))
            for p in click_pos:
                distances = distances + np.sqrt(np.sum(np.square(np.array(p) - label_coord_), axis=1))
            # keep the click which maximize the distance
            coord = tuple(label_coord_[np.argmax(distances)])
            click_map[coord] = 1
            click_pos.append(coord)

        yield click_map, click_pos


# generate 4(2D)/6(3D) extreme points click
def get_click_extreme_points(label):
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
        view = np.expand_dims(label, -1)
        xmin, ymin, zmin, xmax, ymax, zmax = get_3d_coord(view)
        add_click(tuple([xmin, ymin]))
        add_click(tuple([xmax, ymax]))

        view = np.expand_dims(np.swapaxes(label, 0, 1), -1)
        xmin, ymin, zmin, xmax, ymax, zmax = get_3d_coord(view)
        add_click(tuple([ymin, xmin]))
        add_click(tuple([ymax, xmax]))

    elif len(label.shape) == 3:
        xmin, ymin, zmin, xmax, ymax, zmax = get_3d_coord(label)
        add_click(tuple([xmin, ymin, zmin]))
        add_click(tuple([xmax, ymax, zmax]))

        view = np.swapaxes(label, 1, 0)
        xmin, ymin, zmin, xmax, ymax, zmax = get_3d_coord(view)
        add_click(tuple([ymin, xmin, zmin]))
        add_click(tuple([ymax, xmax, zmax]))

        view = np.swapaxes(label, 2, 0)
        xmin, ymin, zmin, xmax, ymax, zmax = get_3d_coord(view)
        add_click(tuple([zmin, ymin, xmin]))
        add_click(tuple([zmax, ymax, xmax]))

    return click_map, click_pos
