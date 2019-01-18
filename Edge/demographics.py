from keras.models import model_from_json
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



class  DemographicsClassifier():
    def __init__(self, gender_model,age_model,graph):
        self.__cleanup()
        self.gender_model = gender_model
        self.age_model = age_model
        self.graph = graph

    def __predict(self,model,image,batch_size):
        with self.graph.as_default():
            return model.predict(image, batch_size=batch_size)

    def __cleanup(self):
        self.batch_size = 1
        self.gender_target_size = (100,100)
        self.age_target_size = (128, 128)
        self.gender_filter = {0:'male',1:'female'}
        #self.age_filter = {'(0, 2)' :0, '(4, 6)':1 , '(8, 12)':2, '(15, 20)':3,'(25, 32)':4,'(38, 43)':5, '(48, 53)':6, '(60, 100)':7}
        self.age_filter = {0: '(0, 2)', 1:'(4, 6)' , 2:'(8, 12)', 3:'(15, 20)',4:'(25, 32)',5:'(38, 43)', 6:'(38, 43)', 7:'(38, 43)'}

        self.x_test = None
        self.preprocessed = None
        self.y_test = None
        self.scores = None
        self.predictions = None

    def input_preprocessing(self,image,image_w, image_h):
        """ Preprocessing to match the training conditions for this model.
        Apply resize, reshape, other scaling/whitening effects.
        image can be any image size greater than 100x100 and it will be resized
        """
        image = image * (1./255.)
        resized = cv2.resize(image, (image_w, image_h))
        return resized.reshape(1,image_w,image_h,3)

    def process_face(self,x_test,y_test,batch_size):
        # Gender Prediction
        w, h = self.gender_target_size[0], self.gender_target_size[1]
        image = self.input_preprocessing(x_test, w,h)
        predictions = self.__predict(self.gender_model,  image, batch_size)
        idx = np.argmax(predictions)
        gender = self.gender_filter[idx]

        # Age Prediction
        w, h = self.age_target_size[0], self.age_target_size[1]
        image = self.input_preprocessing(x_test, w,h)
        predictions = self.__predict(self.age_model,  image, batch_size)
        idx = np.argmax(predictions)
        age = self.age_filter[idx]

        return gender, age

    def process(self,faces):
        return [(self.process_face(x_test=face, y_test=None, batch_size=1)) for face in faces]

def log_summary(logger,processed_output):
    # print for human readers
    rpt = "Demographics on faces: "
    rpt += ", ".join(["{} aged {}".format(gender,age) for gender,age in processed_output])
    rpt += "."
    logger.info(rpt)


def get_client(logger,cfg):
    demographics_object = None
    if not cfg['enabled']:
        logger.info("Demographics classification is disabled.")
    else:
        logger.info("Demographics service is enabled.")
        graph = tf.get_default_graph()
        gender_model, age_model = load_model()
        return DemographicsClassifier(gender_model=gender_model,age_model=age_model, graph=graph)

def load_model():
    print("Loading models...")
    with open('/opt/signage/models/gender.json','r') as f:
        json = f.read()
    gender_model = model_from_json(json)
    gender_model.load_weights('/opt/signage/models/gender.h5')
    print("  - gender model loaded")

    with open('/opt/signage/models/age.json','r') as f:
        json = f.read()
    age_model = model_from_json(json)
    age_model.load_weights('/opt/signage/models/age.h5')
    print("  - age model loaded")

    print("All models loaded.")
    return gender_model, age_model

