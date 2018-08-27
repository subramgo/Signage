from keras.models import load_model, Model, model_from_json
import os
import cv2
import numpy as np
from keras.layers import Input, Conv2D, Dense,MaxPooling2D, Flatten, Activation,Dense, Dropout, BatchNormalization,GlobalAveragePooling2D
import rpyc
import tensorflow as tf
from keras.layers import DepthwiseConv2D


rpyc.core.protocol.DEFAULT_CONFIG['allow_pickle'] = True



class  GenderClassifier(rpyc.Service):

    def __init__(self, conn, model,graph):
        self.x_test = None
        self.preprocessed = None
        self.y_test = None
        self.batch_size = 1
        self.model = model
        self.scores = None
        self.predictions = None
        target_size = (100,100)
        self.image_w = target_size[0]
        self.image_h = target_size[1]
        self.graph = graph
        self.gender_filter = {0:'male',1:'female'}

    def __call__(self, conn):
        return self.__class__(conn, self.model, self.graph)


    def on_disconnect(self, conn):
        self.__cleanup()

    def __evaluate(self):
        self.scores = self.model.evaluate(self.preprocessed, self.y_test, batch_size = self.batch_size)
    
    def __predict(self):
        print(self.preprocessed.shape)
        with self.graph.as_default():
            self.predictions = self.model.predict(self.preprocessed, batch_size=self.batch_size)

    def __cleanup(self):
        del self.model


    def input_preprocessing(self):
        """ Preprocessing to match the training conditions for this model. 
        Apply resize, reshape, other scaling/whitening effects.
        x_test can be any image size greater than 100x100 and it will be resized
        """
        image = rpyc.classic.obtain(self.x_test)
        image = image * (1./255.)
        resized = cv2.resize(image, (self.image_w, self.image_h)) 
        self.preprocessed = resized.reshape(1,self.image_w,self.image_h,3)


    def exposed_process(self,x_test,y_test,batch_size):
        self.x_test = x_test
        self.y_test = y_test
        self.batch_size = batch_size
        self.input_preprocessing()

        if y_test is not None:
            self.__evaluate()
            #print("Score {}".format(self.scores[1]))
            return None

        else:
            self.__predict()
            #print(self.predictions)
            idx = np.argmax(self.predictions)

            return self.gender_filter[idx]


def load_model():
  with open('/opt/signage/gender/4_try.json','r') as f:
    json = f.read()
  model = model_from_json(json)
  model.load_weights('/opt/signage/gender/4_try.h5')
  print("Gender Model Loaded")
  return model


def main():
    from rpyc.utils.server import ThreadedServer
    graph = tf.get_default_graph()
    t = ThreadedServer(GenderClassifier(conn = None,model=load_model(), graph=graph), port=18862)

    t.start()


if __name__ == '__main__':
    main()

