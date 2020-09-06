# -*- coding: utf-8 -*-
from rhme.config import Configuration
from rhme import helpers
from tensorflow.keras.models import load_model
import tensorflow as tf
import numpy as np
import os

config = Configuration()

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['GLOG_minloglevel'] = '3'
print('\n')


def fit(image):

    labels = helpers.get_labels()

    try:
        model = load_model(config.package_path + '/ann_models/model/model_11-07-2020_23-14-47.h5')

        prediction = model.predict(image)
        index = np.argmax(prediction)
        print(index)
        label_rec = labels["labels_parser"][str(index)]

        return {
            'label': labels["labels_recognition"][label_rec],
            'prediction': prediction,
            'type': 'not-number'
        }

    except Exception as e:
        raise e
