import time
import numpy as np
import tifffile
import edt
import skimage.measure
import skimage.morphology
import matplotlib.pyplot as plt

import utils
import generatorM


def example_2d(export=False):
    dense_label_2d = tifffile.imread('VREMS-data/lucchi/label.tif')[0] > 0
    print(dense_label_2d.shape, dense_label_2d.min(), dense_label_2d.max(), dense_label_2d.dtype)

    dense_labels_2d = skimage.measure.label(dense_label_2d)
    gen_pos = generatorM.gen_click_random_uniform_advanced(dense_labels_2d, click=2, d_step=25, d_margin=5)
    dense_label_2d_inv = dense_labels_2d
    for _ in range(5):
        dense_label_2d_inv = skimage.morphology.dilation(dense_label_2d_inv, skimage.morphology.disk(5))
    dense_label_2d_inv = np.where(skimage.morphology.dilation(dense_label_2d, skimage.morphology.disk(5)), 0, dense_label_2d_inv)
    gen_neg = generatorM.gen_click_around_border(dense_label_2d_inv, click=3, max_border_distance=np.inf)

    pos_click_map, _ = next(gen_pos)
    neg_click_map, _ = next(gen_neg)

    print(pos_click_map.shape, pos_click_map.min(), pos_click_map.max(), pos_click_map.dtype)
    print(neg_click_map.shape, neg_click_map.min(), neg_click_map.max(), neg_click_map.dtype)

    plt.imshow(utils.combine_image_and_maps(dense_label_2d, pos_click_map, neg_click_map, dilation=2))
    if export:
        plt.savefig('media/example_2d_m.png')
    plt.show()


def example_3d(export=False):
    dense_label_3d = tifffile.imread('VREMS-data/lucchi/label.tif')[0:128, 0:512, 0:512] > 0
    print(dense_label_3d.shape, dense_label_3d.min(), dense_label_3d.max(), dense_label_3d.dtype)
    # utils.show_stack(dense_label_3d, cmap="gray")

    dense_labels_3d = skimage.measure.label(dense_label_3d)
    gen_pos = generatorM.gen_click_random_uniform_advanced(dense_labels_3d, click=3, d_step=25, d_margin=5)
    dense_label_3d_inv = dense_labels_3d
    for _ in range(8):
        dense_label_3d_inv = skimage.morphology.dilation(dense_label_3d_inv, skimage.morphology.ball(2))
    dense_label_3d_inv = np.where(skimage.morphology.dilation(dense_label_3d, skimage.morphology.ball(2)), 0, dense_label_3d_inv)
    gen_neg = generatorM.gen_click_around_border(dense_label_3d_inv, click=5, max_border_distance=np.inf)

    pos_click_map, _ = next(gen_pos)
    neg_click_map, _ = next(gen_neg)

    print(pos_click_map.shape, pos_click_map.min(), pos_click_map.max(), pos_click_map.dtype)
    print(neg_click_map.shape, neg_click_map.min(), neg_click_map.max(), neg_click_map.dtype)

    save_filename = None
    if export:
        save_filename = 'media/example_3d_m.gif'
    utils.show_stack(utils.combine_image_and_maps(dense_label_3d, pos_click_map, neg_click_map), save_filename=save_filename)


def example_2d_extreme(export=False):
    dense_label_2d = tifffile.imread('VREMS-data/lucchi/label.tif')[0] > 0
    print(dense_label_2d.shape, dense_label_2d.min(), dense_label_2d.max(), dense_label_2d.dtype)
    pos_click_map, _ = generatorM.get_click_extreme_points(skimage.measure.label(dense_label_2d))
    print(pos_click_map.shape, pos_click_map.min(), pos_click_map.max(), pos_click_map.dtype)

    plt.imshow(utils.combine_image_and_maps(dense_label_2d, pos_click_map, np.zeros(dense_label_2d.shape), dilation=2))
    if export:
        plt.savefig('media/example_2d_m_extreme.png')
    plt.show()


def example_3d_extreme(export=False):
    dense_label_3d = tifffile.imread('VREMS-data/lucchi/label.tif')[0:128, 0:512, 0:512] > 0
    print(dense_label_3d.shape, dense_label_3d.min(), dense_label_3d.max(), dense_label_3d.dtype)
    pos_click_map, _ = generatorM.get_click_extreme_points(skimage.measure.label(dense_label_3d))
    print(pos_click_map.shape, pos_click_map.min(), pos_click_map.max(), pos_click_map.dtype)

    save_filename = None
    if export:
        save_filename = 'media/example_3d_m_extreme.gif'
    utils.show_stack(utils.combine_image_and_maps(dense_label_3d, pos_click_map, np.zeros(dense_label_3d.shape)), save_filename=save_filename)


def benchmark_(dense_label_3d):
    print(dense_label_3d.shape, dense_label_3d.min(), dense_label_3d.max(), dense_label_3d.dtype,
          np.sum(dense_label_3d > 0) / np.prod(dense_label_3d.shape))

    gen_pos = generatorM.gen_click_random_uniform(dense_label_3d, click=10)
    gen_pos_adv = generatorM.gen_click_random_uniform_advanced(dense_label_3d, click=10, d_margin=None)
    gen_neg = generatorM.gen_click_around_border(dense_label_3d, click=10)

    t0 = time.time()
    for _ in range(32):
        _, _ = next(gen_pos)
    t1 = time.time()
    print('| gen_click_random_uniform |', round(t1 - t0, 3), '|')

    t0 = time.time()
    for _ in range(32):
        _, _ = next(gen_pos_adv)
    t1 = time.time()
    print('| gen_click_random_uniform_advanced |', round(t1 - t0, 3), '|')

    t0 = time.time()
    for _ in range(32):
        _, _ = next(gen_neg)
    t1 = time.time()
    print('| gen_click_around_border |', round(t1 - t0, 3), '|')

    t0 = time.time()
    _, _ = generatorM.get_click_extreme_points(dense_label_3d)
    t1 = time.time()
    print('| get_click_extreme_points |', round(t1 - t0, 3), '|')


def benchmark():
    dense_label_3d = tifffile.imread('VREMS-data/lucchi/label.tif')[:, 0:512, 0:512] > 0
    benchmark_(skimage.measure.label(dense_label_3d))
    dense_label_3d_inv = np.logical_and(dense_label_3d == 0, edt.edt(np.abs(1 - dense_label_3d)) < 25)
    benchmark_(skimage.measure.label(dense_label_3d_inv))


if __name__ == "__main__":
    example_2d(export=True)
    example_3d(export=True)
    example_2d_extreme(export=True)
    example_3d_extreme(export=True)
    benchmark()
    exit(0)
