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
        # model = load_model('ann_models/model_all/model_16-06-2020_13-24-07.h5') # 3 > z
        # model = load_model(config.package_path + '/ann_models/model/model_17-06-2020_20-18-12.h5') # com = menos *
        # model = load_model(config.package_path + '/ann_models/model/model_21-06-2020_04-55-59.h5') # sem = mais *
        # model = load_model(config.package_path + '/ann_models/model/model_21-06-2020_05-47-41.h5') # sem =  mais *
        # model = load_model(config.package_path + '/ann_models/model/model_28-06-2020_21-45-32.h5') # sem =  mais *

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
