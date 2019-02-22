#!/home/jci/.pyenv/shims/python3

import rtsp
from os import path
import sys

sys.path.append(path.dirname(__file__)+"/..")
import detection

im = rtsp.Client(0).read()
dets = detection.FaceDetector().detect_faces(im)

if dets:
    face = dets[0]

    A_face  = face.size[0]*face.size[1]
    A_frame = im.size[0]*im.size[1]

    A_norm = float(A_face)/A_frame

    print("Face Proportionate-Area: {}".format(A_norm))

else:
    print("No faces found. Try again.")
