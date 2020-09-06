from rhme.config import Configuration
import os
import cv2 as cv
import idx2numpy
import json

config = Configuration()

subst = {
    'frac': [{
        '-': "\\frac",
        'above': '',
    }],
    'below': [{
        'below': ''
    }],
    'sqrt': [{
        'sqrt': '\\sqrt'
    }],
    'super': [{
        'super': '^'
    }],
    'mult': [{
        '*': '\cdot'
    }],
    'subsc': [
        {
            'subsc': '',
            '{': '',
            '.': '.',
            '}': ''
        },
        {
            'subsc': '_'
        }
    ],
    'neq': [{
        'neq': '\\neq'
    }]
}


def create_dir(name):
    dirname = name
    if not os.path.exists(dirname):
        os.mkdir(dirname)
    return dirname


def show_image(image):
    conf = config.get_configs()
    if conf["application"]["debug_mode_image"] == "active":
        cv.namedWindow("Imagem", cv.WINDOW_NORMAL)
        # cv.resizeWindow("Imagem", 725, 325)
        # cv.moveWindow("Imagem", 40,525)
        cv.imshow("Imagem", image)
        cv.waitKey(0)
        cv.destroyAllWindows()


def save_image(self, dirname, roi, i):
    filename = "char" + str(i) + ".png"
    cv2.imwrite(dirname + "/" + filename, roi)


def get_labels():

    config_path = '/docs/config/config_all.json'

    try:
        with open(config.package_path + config_path) as json_file:
            labels_json = json_file.read()
            labels_dict = json.loads(labels_json)
            labels = labels_dict
    except Exception as e:
        print(e)
        labels = {}

    return labels


def save_json_file(path, data):
    with open(path, 'w') as f:
        f.write(json.dumps(data))


def debug(data):
    conf = config.get_configs()
    if conf and "application" in conf:
        if conf["application"]["debug_mode"] == "active":
            print(data)
