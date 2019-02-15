from keras.models import load_model
from keras.preprocessing.image import img_to_array
import cv2
import numpy as np
import time

### Quiet Tensorflow Import
# https://github.com/keras-team/keras/commit/83aaadaa9d69214880d20b1e2bd9715a6c37fbe6
import sys as _sys
import os as _os
_stderr = _sys.stderr
_sys.stderr = open(_os.devnull, 'w')
# Do Importing Here
import tensorflow as tf
# Importing is Done; Restore Environment
_sys.stderr = _stderr
# disables some tensorflow noise (but not all)
_os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
# silences ALL warnings, helps with tensorflow noise again
import warnings as _warnings
_warnings.simplefilter("ignore")


class DemographicsClassifier():

    def __init__(self, logger, cfg):


        self.logger = logger
        self.cfg = cfg
        if not cfg['enabled']:
            logger.info("Demographics classification is disabled.")

        else:
            logger.info("Demographics service is enabled.")

            self.model = None
            self.model_path = self.cfg['model_path']
            self.__load_model()

    def __load_model(self):
      
      self.model = load_model(self.model_path)
      self.model._make_predict_function() 

    def process_face(self, in_image):
        
        image = in_image.resize((64, 64))
        image = img_to_array(image)
        image = np.expand_dims(image, axis=0)
        results = self.model.predict(np.asarray(image))

        predicted_genders = results[0][0]
        female_prob = np.round(predicted_genders[0],2)
        male_prob   = np.round(predicted_genders[1],2)
        ages = np.arange(0, 101).reshape(101, 1)
        predicted_ages = results[1].dot(ages).flatten()
        age = np.floor(predicted_ages[0])

        return_gender = None
        if male_prob > female_prob:
            return_gender = 'male'
        else:
            return_gender = 'female'

        return return_gender, age

    def process(self,faces):
        if self.cfg['enabled']:
            measures = []
            for face in faces:
                try:
                    measures.append(self.process_face(in_image=face))
                except Exception as e:
                    self.logger.error("face processing error "+str(e))

            self.log_summary(measures)
            return measures
        else:
            return None

    def log_summary(self,processed_output):
        # print for human readers
        rpt = "Face summary: "
        rpt += ", ".join(["{} aged {}".format(gender,age) for gender,age in processed_output])
        rpt += "."
        self.logger.info(rpt)



