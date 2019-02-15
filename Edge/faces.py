
import numpy as np
import dlib
import cv2
import log

class FaceDetector:

    def __init__(self,logger = log.get_null_logger('face detector')):
        self.detector = dlib.get_frontal_face_detector()
        self.logger = logger

    def detect_faces(self,frame):
        """ Given a PIL image, return faces and windows. """

        # for dlib detector
        frame = frame.convert('RGB')
        width, height = frame.size

        frame = np.copy(np.asarray(frame))
        frame.setflags(write=True)

        dets = self.detector(frame, 1)
        windows = []
        faces = []
        for i, d in enumerate(dets):
            window = self._pad_box([d.left(), d.top(), d.right(), d.bottom()],width, height)
            windows.append(window)
            cv2.rectangle(frame, (d.left(), d.top()), (d.right(), d.bottom()), (255, 0, 255), 2)
            faces.append(frame[d.top():d.bottom(), d.left():d.right()])

        if faces:
            self.logger.info("Count of faces detected: {}".format(len(faces)))
        else:
            self.logger.info("No faces detected.")

        return (faces,windows)
    
    def _pad_box(self,box, width, height):
        """Pad a box size for context."""
        ratio = 0.1

        w = int(ratio*(box[2]-box[0]))
        h = int(ratio*(box[3]-box[1]))

        return [max(box[0]-w,0)
               ,max(box[1]-h,0)
               ,min(box[2]+w,width)
               ,min(box[3]+h,height)
                ]