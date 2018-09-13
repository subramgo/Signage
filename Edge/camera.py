
import rtsp
import time

class CamClient():
    def __init__(self,logger,cfg,credentials):
        try:
            self.cam_address = cfg['cam_protocol']+credentials[cfg['cam_stream_address']]+"@"+cfg['cam_stream_address']
        except:
            self.cam_address = 0

        self.logger = logger
        self.cfg = cfg
        self.credentials = credentials

        self.discard_frames = self.cfg.get('discard_frames',30)
        self.frame_ind = 1
        self.old_frame = None
        self.frame = None
        self.logger.info("Connecting to "+str(self.cam_address))

        self.cap = rtsp.Client(self.cam_address,drop_frame_limit=5, retry_connection=False, verbose=True)

    def grab_frame(self):
        # Clear the buffer
        # TODO remove this when rtsp package supports
        if self.cam_address != 0:
            for i in range(self.discard_frames):
                self.cap.read()

        self.logger.info("Camera connection is "+("opened."if self.cap.isOpened() else "closed."))

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
        return frame
