
import numpy as np
import dlib
import cv2


class FaceDetector:

    def __init__(self,logger):
        self.detector = dlib.get_frontal_face_detector()
        self.logger = logger

    def detect_faces(self,frame):
        """ Given a PIL image, return faces and windows. """

        # for dlib detector    
        frame = np.asarray(frame)
        frame.setflags(write=True)
        
        dets = self.detector(frame, 1)
        windows = []
        faces = []
        for i, d in enumerate(dets):
            windows.append([d.left(), d.top(), d.right(), d.bottom()])
            cv2.rectangle(frame, (d.left(), d.top()), (d.right(), d.bottom()), (255, 0, 255), 2)
            faces.append(frame[d.top():d.bottom(), d.left():d.right()])

        if faces:
            self.logger.info("Count of faces detected: {}".format(len(faces)))
        else:
            self.logger.info("No faces detected.")

        return (faces,windows)