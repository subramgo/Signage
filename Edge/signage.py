"""
    Signage Edge Operations
      * IP camera client
      * orchestrates image services
      * reports resulting data to Signage database

    Also does:
      * face detection
"""

import sys

import config
import log
import data
import demographics
import ads
import faces
import camera


###########################################################
##############         Configuration         ##############
###########################################################

cfg_defaults = { 
      'camera'                : {
          'enabled'           : False
        , 'stream_address'    : '192.168.1.168/usecondstream'
        , 'protocol'          : 'rtsp://'
        , 'location_name'     : 'signage-analysis-demo'
        , 'name'              : 'signage-camera-1'
        , 'credentials'       : '*user*:*pass*'
    }
    
    , 'logging'               : {
          'enabled'           : True
        , 'logfile_path'      : 'signage.log'
        , 'logfile_maxbytes'  : 375000000
    }
 
    , 'ads'                   : {
          'enabled'           : False
        , 'server'            : ['localhost',18861]
        , 'rotation'          : 0
        , 'window'            : (400,0,400,480)
        , 'library'           : '/opt/signage/videos'
    }

    , 'data'                  : {
          'enabled'           : False
        , 'credentials'       : '*user*:*pass*'
        , 'data_server'       : '127.0.0.1:5000'
        , 'data_protocol'     : 'http://'
    }

    , 'demographics'          : {
          'enabled'           : False
        , 'server'            : ['localhost',18862]
    }
    }

cfg = config.Config(
      filepath = "/boot/signage/config.yml"
    , description = "Orchestration and Image Feed"
    , dictionary = cfg_defaults
    , maskedpath = "/opt/signage/credentials.yml")

cfg.mask('data.credentials'   ,'*user*:*pass*')
cfg.mask('camera.credentials' ,'*user*:*pass*')
#cfg.dump()


###########################################################
##############           Interfaces           #############
###########################################################
logger = log.get_logger(cfg)
camera = camera.CamClient(logger,cfg['camera'])
face_detector = faces.FaceDetector(logger)
dataClient = data.DataClient(logger,cfg['data'])
ads = ads.get_client(logger,cfg['ads'])
demo = demographics.get_client(logger,cfg['demographics'])


###########################################################
##############          Orchestration         #############
###########################################################
def refresh():
    """ Check configuration files for new settings and update interfaces """
    global cfg
    cfg.load()

def main():
    while cfg['camera']['enabled']:
        frame = camera.grab_frame()

        ### Detection
        faces, windows = face_detector.detect_faces(frame)
        
        ### Find genders if faces detected.
        if faces:
            dataClient.upload_faces(windows)

            if demo:
                _demographics = demo.process(faces)
                demographics.log_summary(logger,_demographics)
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
