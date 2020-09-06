from mathreader import helpers
import numpy as np
import cv2
import imutils
import os


class ImagePreprocessing:

    def __init__(self, configs={}):
        self.configs = {
            'black': False,
            'dilate': False,
            'dataset': False,
            'erode': False,
            'resize': 'smaller'
        }

        if configs:
            self.configs.update(configs)

    def print_bounding_box(self, image, coordinates):
        image_rect = image
        x, y, w, h = coordinates
        cv2.rectangle(image_rect, (x, y), (x + w, y + h), (100, 100, 100), 2)
        # helpers.show_image(image_rect)
        return image_rect

    def save_image_255(self, image, name):
        img = cv2.convertScaleAbs(image, alpha=(255.0))
        cv2.imwrite('%s.jpg' % name, img)

    def to_gray_denoise(self, image):
        helpers.debug('[preprocessing.py] to_gray_denoise()')
        img = image.copy()

        if img.ndim == 3:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        img = cv2.fastNlMeansDenoising(img, None, 5, 9)
        img = np.array(img)
        return img

    def invert(self, image):
        helpers.debug('[preprocessing.py] invert()')
        img = image.copy()
        return 255-img

    def binarization(self, image):
        helpers.debug('[preprocessing.py] binarization()')
        img = image.copy()
        img = self.invert(img)
        # img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                    cv2.THRESH_BINARY, 9, 2)
        img = self.invert(img)
        return img

    def normalize(self, image):
        helpers.debug('[preprocessing.py] normalize()')
        img = image.copy()
        img = self.to_gray_denoise(image)

        if not self.configs['black']:
            img = self.invert(img)

        kernel = np.ones((2, 2), np.uint8)

        if 'dilate' in self.configs:
            if self.configs['dilate']:
                img = cv2.dilate(img, kernel, iterations=2)

        if 'erode' in self.configs:
            if self.configs['erode']:
                img = cv2.erode(img, kernel, iterations=1)

        return img

    def _255_to_1(self, image):
        helpers.debug('[preprocessing.py] _255_to_1()')
        img = image.copy()
        return (img / 255)

    def resize(self, image):
        helpers.debug('[preprocessing.py] resize()')
        old_size = image.shape[:2]  # (height, width)
        height, width = old_size[0], old_size[1]

        ratio = float(26) / max(old_size)
        size = tuple([int(x*ratio) for x in old_size])

        size_height, size_width = size[0], size[1]
        size_height = size_height if size_height > 0 else 1
        size_width = size_width if size_width > 0 else 1

        division_height = int(height/2)
        division_width = int(width/2)
        around_w = round(width * 20 / 100)
        around_h = round(height * 20 / 100)

        middle_width = [
            image[division_height][division_width-1],
            image[division_height][division_width],
            image[division_height][division_width+1]
        ]

        middle_height = []
        for a in range(division_height-around_h, division_height+around_h):
            middle_height.append(
                image[a][division_width],
            )

        middle_width = []
        for b in range(division_width-around_w, division_width+around_w):
            middle_width.append(
                image[division_height][division_width],
            )

        helpers.debug('[preprocessing.py] segment() | \
            before line and sqrt processing')
        if size_height <= 15 and size_width >= 20 and \
            (any(i > 0.0000 for i in middle_height) or
                any(i > 0.0000 for i in middle_width)):

            # For horizontal line
            nsize = 4 if size_height < 5 else size_height
            nsize = 10 if size_height > 10 else size_height
            print('hor ', size_height)
            new_size = tuple([int(nsize), 26])

        else:
            if size_width / size_height >= 2:
                # For rectangle (sqrt)
                kernel = np.ones((2, 2), np.uint8)
                image = cv2.dilate(image, kernel, iterations=7)
                # xinit = int(width * 2 / 100) # validation
                # xend = int(width * 65 / 100) # validation
                xinit = int(width * 5 / 100)
                xend = int(width * 85 / 100)
                image = image[0:height, xinit:xend]

            new_size = size

        helpers.debug('[preprocessing.py] segment() | \
            after line and sqrt processing')

        helpers.debug('[preprocessing.py] segment() | \
            before resize')

        if self.configs['resize'] == 'smaller':
            image = cv2.resize(image.copy(), (new_size[1], new_size[0]),
                               interpolation=cv2.INTER_AREA)
        elif self.configs['resize'] == 'bigger':
            image = cv2.resize(image.copy(), (new_size[1], new_size[0]),
                               interpolation=cv2.INTER_LINEAR)
        helpers.debug('[preprocessing.py] segment() | after resize')

        # Cria borda ao redor do símbolo e normaliza para 28x28 px
        helpers.debug('[preprocessing.py] segment() | before border')
        delta_w = 28 - new_size[1]
        delta_h = 28 - new_size[0]
        top, bottom = delta_h//2, delta_h-(delta_h//2)
        left, right = delta_w//2, delta_w-(delta_w//2)
        color = [0, 0, 0]
        image = cv2.copyMakeBorder(image.copy(), top, bottom,
                                   left, right, cv2.BORDER_CONSTANT,
                                   value=color)

        helpers.debug('[preprocessing.py] segment() | after border')
        return image

    def resize_full_image(self, image):
        helpers.debug('[preprocessing.py] resize_full_image()')
        h, w = image.shape[:2]
        if w > 4000:
            width = int(w * 20 / 100)
            r = width / float(w)
            size = (width, int(h * r))
            image = cv2.resize(image, size)
        return image

    def segment(self, img):
        helpers.debug('[preprocessing.py] segment()')
        image = img.copy()
        symbols = []
        cnts, somethingElse = cv2.findContours(image.copy(), cv2.RETR_EXTERNAL,
                                               cv2.CHAIN_APPROX_SIMPLE)

        helpers.debug('[preprocessing.py] segment() | contours founded:')
        helpers.debug(len(cnts))

        for i in range(len(cnts)):
            # It was 0 and was changed to 10 to try reducing the noise
            if(cv2.contourArea(cnts[i]) < 10):
                continue

            if(self.configs['dataset'] and len(cnts) > 1):
                continue

            try:
                # Draw contour in new image (mask)
                mask = np.zeros_like(image)
                cv2.drawContours(mask, cnts, i, (255, 255, 255), -50)
                out = np.zeros_like(image)

                '''
                At the position where the mask is 255
                it paints the normalized position
                with the same positions from mask were it is 255

                I.e. mask has the inner part of "2" painted,
                but the normalized doesn't have it.

                It was changed to > 0 instead of 255
                this prevents the image from having to be binarized
                '''
                out[mask > 0] = image[mask > 0]

                # # Get bounding box coordinates
                _x, _y, _w, _h = cv2.boundingRect(cnts[i])

                # For now, it's worthless
                # ALL points where the mask == 255
                # list_y, list_x = np.where(out > 0)
                # (topx, topy) = (np.min(list_x), np.min(list_y))
                # (bottomx, bottomy) = (np.max(list_x), np.max(list_y))

                # Crop the image
                ycrop = _y + _h + 1
                xcrop = _x + _w + 1
                cropped = out[_y: ycrop, _x: xcrop]

                resized = self.resize(cropped)

                # Test - It was not here during validation
                binarized = self.binarization(resized)
                result_image = self._255_to_1(binarized)

                # result_image = self._255_to_1(resized)
                helpers.show_image(result_image)

                attributes = {
                    'index': i,
                    'image': result_image.copy(),
                    'xmin': _x,
                    'xmax': _x+_w,
                    'ymin': _y,
                    'ymax': _y+_h,
                    'w': _w,
                    'h': _h,
                    'centroid': [(_x + (_x+_w))/2, (_y + (_y+_h))/2]
                }

                symbols.append(attributes)

                mask = None
                out = None
                cropped = None
                resized = None
                binarized = None
                result_image = None

                # self.image = self.print_bounding_box(image, (_x, _y, _w, _h))
                self.image = image

            except BaseException as e:
                print(e)
                continue

        return (symbols, self.image)

    def mnist(self, img):
        try:
            if type(img) is str:
                image = cv2.imread(img)
            else:
                image = img

            normalized = self.normalize(image)
            result_image = self._255_to_1(normalized)
            return result_image
        except BaseException as e:
            print(e)
            return None

    def treatment_sem_segment(self, img):
        try:
            if type(img) is str:
                image = cv2.imread(img)
            else:
                image = img

            normalized = self.normalize(image)
            resized = self.resize(normalized)
            result_image = self._255_to_1(resized)
            return result_image
        except BaseException as e:
            print(e)
            return None

    def treatment(self, img):
        helpers.debug('[preprocessing.py] treatment()')
        try:
            if type(img) is str:
                image = cv2.imread(img)
            else:
                image = img

            original = image.copy()
            image = self.resize_full_image(image)
            normalized = self.normalize(image)
            self.image = normalized.copy()

            symbols = self.segment(normalized)

            return symbols
        except BaseException as e:
            print(e)
            return []


if __name__ == "__main__":

    p = ImagePreprocessing()
    segmentation, image = p.treatment('images/numbers/teste10.png')

    try:
        for s in segmentation:
            s.__delitem__('image')
    except Exception as identifier:
        print(identifier)

    print(segmentation)
