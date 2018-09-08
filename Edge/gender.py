from keras.models import model_from_json
import cv2
import numpy as np
import rpyc
import tensorflow as tf

rpyc.core.protocol.DEFAULT_CONFIG['allow_pickle'] = True

class  GenderClassifier(rpyc.Service):
    def __init__(self, conn, model,graph):
        self.__cleanup()
        self.model = model
        self.graph = graph

    def __call__(self, conn):
        return self.__class__(conn, self.model, self.graph)

    def on_disconnect(self, conn):
        self.__cleanup()

    def __evaluate(self,preprocessed_x,labels,batch_size):
        return self.model.evaluate(preprocessed_x, labels, batch_size = batch_size)

    def __predict(self,image,batch_size):
        print(image.shape)
        with self.graph.as_default():
            return self.model.predict(image, batch_size=batch_size)

    def __cleanup(self):
        self.batch_size = 1
        target_size = (100,100)
        self.image_w = target_size[0]
        self.image_h = target_size[1]
        self.gender_filter = {0:'male',1:'female'}
        self.x_test = None
        self.preprocessed = None
        self.y_test = None
        self.scores = None
        self.predictions = None

    def input_preprocessing(self,image):
        """ Preprocessing to match the training conditions for this model.
        Apply resize, reshape, other scaling/whitening effects.
        image can be any image size greater than 100x100 and it will be resized
        """
        image = rpyc.classic.obtain(image)
        image = image * (1./255.)
        resized = cv2.resize(image, (self.image_w, self.image_h))
        return resized.reshape(1,self.image_w,self.image_h,3)


    def exposed_process(self,x_test,y_test,batch_size):
        image = self.input_preprocessing(x_test)

        if y_test is not None:
            self.__evaluate(image,y_test,batch_size)
            #print("Score {}".format(self.scores[1]))
            return None

        else:
            predictions = self.__predict(image,batch_size)
            #print(predictions)
            idx = np.argmax(predictions)
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

