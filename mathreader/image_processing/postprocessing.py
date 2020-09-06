from mathreader.image_processing import preprocessing as preprocessing
from mathreader import helpers
import numpy as np
import cv2
import imutils
import os


class ImagePostprocessing:

    def __init__(self, image):
        self.image = image

    def segment_equality(self, symbols):
        xmin_sorted = sorted(symbols, key=lambda i: i['xmin'], reverse=False)
        xmin_ymin_sorted = sorted(symbols, key=lambda i: (i['xmin'],
                                  i['ymin']), reverse=False)

        try:
            c = 0
            i = 0
            candidate_index = 0

            for symbol in xmin_sorted:

                if c == 0 and symbol['label'] == '10':
                    # First candidate

                    candidate = symbol.copy()
                    c = 1  # found 1 candidate
                    candidate_index = i  # stores the candidate index

                elif c == 1 and symbol['label'] == '10':
                    # Second candidate

                    diff = abs(candidate['w'] / symbol['w'])

                    line1x = range(candidate['xmin'], candidate['xmax']+1)
                    line2x = range(symbol['xmin'], symbol['xmax']+1)
                    len_line1x = len(line1x)
                    len_line2x = len(line2x)
                    x_set = set(line1x) if len_line1x < len_line2x else set(line2x)
                    x_intersection = x_set.intersection(line1x if len_line1x >= len_line2x else line2x)

                    if x_intersection and diff <= 2 and diff >= 0.5:
                        c = 0

                        abacate = self.image.copy()

                        ymin = min(symbol['ymin'], candidate['ymin'])
                        ymax = max(symbol['ymax'], candidate['ymax'])

                        xmin = min(symbol['xmin'], candidate['xmin'])
                        xmax = max(symbol['xmax'], candidate['xmax'])

                        cropped = abacate[
                            ymin:ymax + 1,
                            xmin:xmax + 1
                        ]

                        pre = preprocessing.ImagePreprocessing()
                        resized = pre.resize(cropped)
                        resized = pre.binarization(resized)
                        resized = pre._255_to_1(resized)

                        symbol['image'] = resized
                        symbol['label'] = '30'
                        symbol['xmin'] = xmin
                        symbol['xmax'] = xmax
                        symbol['ymin'] = ymin
                        symbol['ymax'] = ymax
                        symbol['w'] = xmax - xmin
                        symbol['h'] = ymax - ymin
                        symbol['centroid'] = [xmin + (xmax-xmin) / 2, ymin + (ymax-ymin) / 2]

                        del xmin_sorted[candidate_index]

                    else:
                        candidate = symbol.copy()
                        candidate_index = i
                i += 1

        except BaseException as e:
            print(e)

        return xmin_sorted
