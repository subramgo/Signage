from keras.models import model_from_json
import cv2
import numpy as np
import rpyc
import tensorflow as tf

rpyc.core.protocol.DEFAULT_CONFIG['allow_pickle'] = True

class  DemographicsClassifier(rpyc.Service):
    def __init__(self, conn, gender_model,age_model,graph):
        self.__cleanup()
        self.gender_model = gender_model
        self.age_model = age_model
        self.graph = graph

    def __call__(self, conn):
        return self.__class__(conn, self.gender_model, self.age_model ,self.graph)

    def on_disconnect(self, conn):
        self.__cleanup()

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
        image = rpyc.classic.obtain(image)
        image = image * (1./255.)
        resized = cv2.resize(image, (image_w, image_h))
        return resized.reshape(1,image_w,image_h,3)


    def exposed_process(self,x_test,y_test,batch_size):
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


def load_model():
    with open('/opt/signage/gender/4_try.json','r') as f:
        json = f.read()
    gender_model = model_from_json(json)
    gender_model.load_weights('/opt/signage/gender/4_try.h5')
    print("Gender Model Loaded")

    with open('/opt/signage/age/2_try.json','r') as f:
        json = f.read()
    age_model = model_from_json(json)
    age_model.load_weights('/opt/signage/age/2_try.h5')
    print("Age Model Loaded")

    return gender_model, age_model


def main():
    from rpyc.utils.server import ThreadedServer
    graph = tf.get_default_graph()
    gender_model, age_model = load_model()
    t = ThreadedServer(DemographicsClassifier(conn = None,gender_model=gender_model,age_model=age_model, graph=graph), port=18862)
    t.start()


if __name__ == '__main__':
    main()

