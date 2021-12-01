import numpy as np
import skimage.morphology
import matplotlib.pyplot as plt
import matplotlib.animation as animation


def combine_image_and_maps(label, pos_click_map, neg_click_map, dilation=3):
    assert(2 <= len(label.shape) == len(pos_click_map.shape) == len(neg_click_map.shape) <= 3)
    if len(label.shape) == 2:
        se = skimage.morphology.disk
    else:
        se = skimage.morphology.ball

    for _ in range(dilation):
        pos_click_map = skimage.morphology.binary_dilation(pos_click_map, se(3))
    for _ in range(dilation):
        neg_click_map = skimage.morphology.binary_dilation(neg_click_map, se(3))

    label = np.divide(label, (1+pos_click_map))
    label = np.divide(label, (1+neg_click_map))

    result = np.stack([(neg_click_map > 0)*1.0,
                       (pos_click_map > 0)*1.0,
                       label*1.0], axis=-1)

    return result


def show_stack(stack, interval=50, axis=0, vmin=None, vmax=None, cmap=None, save_filename=None):
    assert(3 <= len(stack.shape) <= 4)

    if axis is not 0:
        stack = np.moveaxis(stack, axis, 0)

    fig = plt.figure()
    slices = []

    for z in range(stack.shape[0]):
        s = plt.imshow(stack[z], vmin=vmin, vmax=vmax, cmap=cmap)
        slices.append([s])

    anim = animation.ArtistAnimation(fig, slices, interval=interval, repeat_delay=1000, blit=True)

    if save_filename is not None:
        anim.save(save_filename)

    plt.show()


def get_exterior_neighborhood(label, size, margin, se_radius=3):
    assert 2 <= len(label.shape) <= 3
    assert size >= 1
    assert margin >= 0
    assert size > margin

    if len(label.shape) == 2:
        se = skimage.morphology.disk(se_radius)
    else:
        se = skimage.morphology.ball(se_radius)

    label_dil_1 = label
    for _ in range(size):
        label_dil_1 = skimage.morphology.dilation(label_dil_1, se)

    label_dil_2 = label
    for _ in range(margin):
        label_dil_2 = skimage.morphology.dilation(label_dil_2, se)

    return np.where(label_dil_2, 0, label_dil_1)
