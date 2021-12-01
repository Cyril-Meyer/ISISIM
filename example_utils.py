import time
import numpy as np
import tifffile
import edt
import skimage.measure
import skimage.morphology
import matplotlib.pyplot as plt

import utils

dense_label_2d = tifffile.imread('VREMS-data/lucchi/label.tif')[0] > 0

dense_labels_2d = skimage.measure.label(dense_label_2d)
dense_label_2d_inv = utils.get_exterior_neighborhood(dense_labels_2d, 10, 4)

plt.imshow(dense_labels_2d + dense_label_2d_inv)
plt.show()


dense_label_3d = tifffile.imread('VREMS-data/lucchi/label.tif')[0:128, 0:512, 0:512] > 0

dense_labels_3d = skimage.measure.label(dense_label_3d)
dense_label_3d_inv = utils.get_exterior_neighborhood(dense_labels_3d, 10, 4, se_radius=2)

utils.show_stack(dense_labels_3d + dense_label_3d_inv, save_filename=None)
