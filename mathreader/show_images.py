from mathreader.config import Configuration
import numpy as np
import cv2
import os

config = Configuration()

image_path = '/treatment/treated_data_three/not-number_testing_images.npz'
number = np.load(config.package_path + image_path)
number = number['arr_0']

label_path = '/treatment/treated_data_three/not-number_testing_labels.npz'
label_t = np.load(config.package_path + label_path)
label_t = label_t['arr_0']


def show_image(image):
    for i in range(0, len(image), 100):
        cv2.imshow("Image", image[i])
        print(label_t[i])
        cv2.waitKey(0)


show_image(number)

cv2.destroyAllWindows()
