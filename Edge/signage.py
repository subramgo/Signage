"""
    Signage Edge Operations
      * IP camera client
      * orchestrates image services
      * reports resulting data to Signage database

    Also does:
      * face detection
"""

import logging
from logging.handlers import RotatingFileHandler
import sys
import rpyc

import config
import data
import demographics
import ads
import faces
import camera

rpyc.core.protocol.DEFAULT_CONFIG['allow_pickle'] = True

###########################################################
##############         Configuration         ##############
###########################################################

cfg_defaults = { 
     'cam_stream_address'    : '192.168.1.168/usecondstream'
   , 'cam_protocol'          : 'rtsp://'

   , 'cam_location_name'     : 'signage-analysis-demo'
   , 'cam_name'              : 'signage-camera-1'
   , 'logfile_path'          : '/home/pi/logs_signage.log'
   , 'logfile_maxbytes'      : 375000000

   , 'log_service'           : True
   , 'ad_service'            : True
   , 'demographics_service'  : True
   , 'data_service'          : True

   , 'data_server'           : '127.0.0.1:5000'
   , 'data_protocol'         : 'http://'
   , 'demographics_server'   : ['localhost',18862]
   , 'ad_server'             : ['localhost',18861]
    }

cfg = config.Config(
      filepath = "/boot/signage/config.yml"
    , description = "Orchestration and Image Feed"
    , dictionary = cfg_defaults)

credentials = config.Config(filepath="/opt/signage/credentials.yml")


if cfg['log_service']:
    print("Logging to {}".format(cfg['logfile_path']))
    hdlr = RotatingFileHandler(cfg['logfile_path'],maxBytes=cfg['logfile_maxbytes'])
else:
    print("No logging.")
    hdlr = logging.NullHandler()
logging.basicConfig(format="[%(thread)-5d]%(asctime)s: %(message)s")
logger = logging.getLogger('SignageEdge)')
logger.setLevel(logging.INFO)
logger.addHandler(hdlr)


###########################################################
##############           Interfaces           #############
###########################################################
camera = camera.CamClient(logger,cfg,credentials)
face_detector = faces.FaceDetector(logger)
dataClient = data.DataClient(logger,cfg,credentials)
ads = ads.get_client(logger,cfg)
demographics = demographics.get_client(logger,cfg)

def dprint(processed_output):
    # print results of `process` for human readers
    rpt = "Demographics on faces: "
    rpt += ", ".join(["{} aged {}".format(gender,age) for gender,age in processed_output])
    rpt += "."
    return rpt

###########################################################
##############          Orchestration         #############
###########################################################
def main():
    while True:
        frame = camera.grab_frame()

        ### Detection
        faces, windows = face_detector.detect_faces(frame)
        
        ### Find genders if faces detected.
        if faces:
            dataClient.upload_faces(windows)

            if demographics:
                _demographics = [(demographics.process(x_test=face, y_test=None, batch_size=1)) for face in faces]
                logger.info(dprint(_demographics))
                dataClient.upload_demographics(_demographics)

                # Switch ads based on demographics        
                if ads:
                    ads.demographics(_demographics)
       
        # Restart the video for every 10th frame
        # TODO remove this when ad player supports it
        if camera.frame_ind%20 == 0:
            if ads:
                ads.play_default()

        frame_limit = 500
        if camera.frame_ind >= frame_limit:
            logger.info("Retrieved {} frames. Stopping to help manage video buffer.".format(frame_limit))
            sys.exit(0)


if __name__ == "__main__":
    main()
