
import rtsp
import time

class CamClient():
    def __init__(self,logger,cfg):
        if cfg['protocol'] in 'picamera':
            self.cam_address = 'picam'
        elif cfg['protocol'] in 'webcam':
            self.cam_address = 0
        else:
            self.cam_address = cfg['protocol']+cfg['credentials']+"@"+cfg['stream_address']
    
        self.logger = logger
        self.cfg = cfg

        if not cfg['enabled']:
            logger.info("Camera is disabled.")
        else:
            self.discard_frames = self.cfg.get('discard_frames',30)
            self.frame_ind = 1
            self.old_frame = None
            self.frame = None
            self.logger.info("Connecting to "+str(self.cam_address))

            self.cap = rtsp.Client(self.cam_address,verbose=True)

    def grab_frame(self):
        # Clear the buffer
        # TODO remove this when rtsp package supports
        #if isinstance(self.cam_address,str) and self.cam_address.lower() not in 'picamera':
        #    for i in range(self.discard_frames):
        #        self.cap.read()

        frame = self.cap.read()

        while frame == self.old_frame or not self.cap.isOpened():
            self.logger.error("No new image yet.")
            time.sleep(3)
            frame = self.cap.read()
            if not self.cap.isOpened():
                self.logger.info("Attempting reconnect to "+self.cam_address+"...")
                self.cap.open(self.cam_address)
        self.old_frame = frame

        self.logger.info("Retrieved frame {}".format(self.frame_ind))
        self.frame_ind+=1

        if self.cfg['rotation'] != 0:
            frame = frame.rotate(self.cfg['rotation'])
        return frame
