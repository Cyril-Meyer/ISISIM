import time
import numpy as np
import skimage.draw
import matplotlib.pyplot as plt

import utils
import generatorS


def example_2d(export=False):
    dense_label_2d = np.zeros((256, 256), dtype=np.uint8)
    dense_label_2d[skimage.draw.disk((128, 128), 64)] = 1
    print(dense_label_2d.shape, dense_label_2d.min(), dense_label_2d.max(), dense_label_2d.dtype)
    # plt.imshow(dense_label_2d, cmap="gray")
    # plt.show()

    gen_pos = generatorS.gen_click_random_uniform_advanced(dense_label_2d, click=5)
    gen_neg = generatorS.gen_click_around_border(np.abs(1 - dense_label_2d), click=5)

    pos_click_map, _ = next(gen_pos)
    neg_click_map, _ = next(gen_neg)

    print(pos_click_map.shape, pos_click_map.min(), pos_click_map.max(), pos_click_map.dtype)
    print(neg_click_map.shape, neg_click_map.min(), neg_click_map.max(), neg_click_map.dtype)

    plt.imshow(utils.combine_image_and_maps(dense_label_2d, pos_click_map, neg_click_map))
    if export:
        plt.savefig('media/example_2d_s.png')
    plt.show()


def example_3d(export=False):
    dense_label_3d = skimage.draw.ellipsoid(64, 64, 64)
    print(dense_label_3d.shape, dense_label_3d.min(), dense_label_3d.max(), dense_label_3d.dtype)
    # utils.show_stack(dense_label_3d, cmap="gray")

    gen_pos = generatorS.gen_click_random_uniform_advanced(dense_label_3d, click=5)
    gen_neg = generatorS.gen_click_around_border(np.abs(1 - dense_label_3d), click=8)

    pos_click_map, _ = next(gen_pos)
    neg_click_map, _ = next(gen_neg)

    print(pos_click_map.shape, pos_click_map.min(), pos_click_map.max(), pos_click_map.dtype)
    print(neg_click_map.shape, neg_click_map.min(), neg_click_map.max(), neg_click_map.dtype)

    save_filename = None
    if export:
        save_filename = 'media/example_3d_s.gif'
    utils.show_stack(utils.combine_image_and_maps(dense_label_3d, pos_click_map, neg_click_map), save_filename=save_filename)


def example_2d_extreme(export=False):
    dense_label_2d = np.zeros((256, 256), dtype=np.uint8)
    dense_label_2d[50:200, 80:150] = 1
    print(dense_label_2d.shape, dense_label_2d.min(), dense_label_2d.max(), dense_label_2d.dtype)
    # plt.imshow(dense_label_2d, cmap="gray")
    # plt.show()

    pos_click_map, _ = generatorS.get_click_extreme_points(dense_label_2d)

    print(pos_click_map.shape, pos_click_map.min(), pos_click_map.max(), pos_click_map.dtype)

    plt.imshow(utils.combine_image_and_maps(dense_label_2d, pos_click_map, np.zeros(dense_label_2d.shape)))
    if export:
        plt.savefig('media/example_2d_s_extreme.png')
    plt.show()


def example_3d_extreme(export=False):
    dense_label_3d = skimage.draw.ellipsoid(32, 64, 48)
    dense_label_3d = np.pad(dense_label_3d, ((0, 15), (12, 3), (12, 3)))
    print(dense_label_3d.shape, dense_label_3d.min(), dense_label_3d.max(), dense_label_3d.dtype)
    # plt.imshow(dense_label_2d, cmap="gray")
    # plt.show()

    pos_click_map, _ = generatorS.get_click_extreme_points(dense_label_3d)

    print(pos_click_map.shape, pos_click_map.min(), pos_click_map.max(), pos_click_map.dtype)

    save_filename = None
    if export:
        save_filename = 'media/example_3d_s_extreme.gif'
    utils.show_stack(utils.combine_image_and_maps(dense_label_3d, pos_click_map, np.zeros(dense_label_3d.shape)), save_filename=save_filename)


def benchmark_(dense_label_3d):
    print(dense_label_3d.shape, dense_label_3d.min(), dense_label_3d.max(), dense_label_3d.dtype,
          np.sum(dense_label_3d > 0) / np.prod(dense_label_3d.shape))

    gen_pos = generatorS.gen_click_random_uniform(dense_label_3d, click=10)
    gen_pos_adv = generatorS.gen_click_random_uniform_advanced(dense_label_3d, click=10)
    gen_neg = generatorS.gen_click_around_border(dense_label_3d, click=10)

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
    _, _ = generatorS.get_click_extreme_points(dense_label_3d)
    t1 = time.time()
    print('| get_click_extreme_points |', round(t1 - t0, 3), '|')


def benchmark():
    dense_label_3d = skimage.draw.ellipsoid(125, 125, 125)
    dense_label_3d = np.pad(dense_label_3d, ((2, 1), (2, 1), (2, 1)))
    benchmark_(dense_label_3d)
    benchmark_(np.abs(1 - dense_label_3d))

    dense_label_3d = skimage.draw.ellipsoid(32, 32, 32)
    dense_label_3d = np.pad(dense_label_3d, ((164, 25), (164, 25), (164, 25)))
    benchmark_(dense_label_3d)
    benchmark_(np.abs(1 - dense_label_3d))


if __name__ == "__main__":
    example_2d(export=True)
    example_3d(export=True)
    example_2d_extreme(export=True)
    example_3d_extreme(export=True)
    benchmark()
    exit(0)
