from mathreader.classification import classification as classification
from mathreader.image_processing import preprocessing as preprocessing
from mathreader.image_processing import postprocessing as postprocessing
from mathreader import helpers
import os
import re
import json
import numpy as np
import json
import cv2 as cv

helpers_labels = helpers.get_labels()
labels = helpers_labels['labels_parser']


class Recognize:

    def __init__(self, image):
        self.prediction = []
        self.image = None

        try:
            if isinstance(image, str):
                nparr = np.fromstring(image, np.uint8)
                img = cv.imdecode(nparr, cv.IMREAD_COLOR)
            else:
                img = image.copy()
            self.image = img
        except Exception as e:
            print("[recognize.py] __init__ | Exception:")
            raise e

    def __recognize(self, img):
        img = img.reshape(1, 28, 28, 1)
        return classification.fit(img)

    def to_recognize(self):

        expression = {}

        helpers.debug("[recognize.py] to_recognize | \
            Showing the image of the expression...\n")

        helpers.debug("[recognize.py] to_recognize | \
            Starting image preprocessing...\n")
        p = preprocessing.ImagePreprocessing()
        segmentation, normalized_image = p.treatment(self.image)

        helpers.debug("[recognize.py] to_recognize | \
            Showing preprocessed image\n")

        helpers.debug("[recognize.py] to_recognize | \
            Image preprocessing finished.\n")

        helpers.debug("[recognize.py] to_recognize | \
            Starting symbol classification...\n")

        try:
            for s in segmentation:

                helpers.debug('... segmentation ...')
                helpers.debug('... recognize ...')

                reconhecer = self.__recognize(s['image'])
                reconhecer['label'] = str(reconhecer['label'])

                s['label'] = reconhecer['label']
                s['prediction'] = reconhecer['prediction']

                symbol_prediction = {
                    'identity': labels[s['label']]
                }

                symbol_prediction.update(reconhecer)
                self.prediction.append(symbol_prediction)

                helpers.debug('[recognize.py] to_recognize | \
                    Símbolo: %s ' % labels[s['label']])

            helpers.debug("\n[recognize.py] to_recognize | \
                << Symbol classification finished.\n")

        except Exception as e:
            print("[recognize.py] to_recognize | Exception:")
            raise e

        pos = postprocessing.ImagePostprocessing(normalized_image)
        new = pos.segment_equality(segmentation)

        # teste
        for n in new:
            print('label: ', n['label'])

        expression['symbols'] = new

        return (expression, normalized_image)
