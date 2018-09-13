import pexpect
import time
import rpyc
import logging
from logging.handlers import RotatingFileHandler

import rtsp

import config

# TODO if cfg['source_camera_inset'], overlay source camera feed

###########################################################
##############         Configuration         ##############
###########################################################
cfg_defaults = { 
        'source_camera_inset'    : True
      , 'source_camera_protocol' : 'rtsp://'
      , 'source_camera_address'  : '192.168.1.168/usecondstream'
      , 'debug_positions'        : False
      , 'video_path'             : '/opt/signage/videos/multi_ads.mov'
      , 'log_service'            : False
      , 'logfile_path'           : '/home/pi/logs_ads.log'
      , 'logfile_maxbytes'       : 375000000
    }

cfg = config.Config(
      filepath = "/boot/signage/ads.yml"
    , description = "Ad Service"
    , dictionary = cfg_defaults)

if cfg['log_service']:
    hdlr = RotatingFileHandler(cfg.get('logfile_path'),maxBytes=cfg.get('logfile_maxbytes'))
else:
    hdlr = RotatingFileHandler('/dev/null')

logging.basicConfig(format="[%(thread)-5d]%(asctime)s: %(message)s")
logger = logging.getLogger('client')
logger.setLevel(logging.INFO)
logger.addHandler(hdlr)


credentials = config.Config(filepath="/opt/signage/credentials.yml")
all_cfg     = config.Config(filepath="/boot/signage/config.yml")

cam_uri = "{}{}@{}".format(all_cfg['cam_protocol'],credentials['video_stream'],all_cfg['cam_stream_address'])
video_file = cfg['video_path']

class Player(rpyc.Service):

    def __init__(self):
        super().__init__()
        if cfg['debug_positions']:
            control = pexpect.spawn('/usr/bin/omxplayer  --win 0,0,640,480 ' + video_file, timeout=60)
            if all_cfg['cam_stream_address'] == 'picam':
                import picamera
                cam = picamera.PiCamera()
                cam.resolution = picamera.PiResolution(480,400)
                cam.start_preview(rotation=270,fullscreen=False,window=(400,0,400,480))
            elif all_cfg['cam_stream_address'] == 0:
                rtsp.Client(0).preview()
            else:
                debug_control = pexpect.spawn('/usr/bin/omxplayer  --win 641,0,1281,480 --avdict rtsp_transport:tcp ' + cam_uri)
                debug_control.expect("Video", timeout=60)
        else:
            control = pexpect.spawn('/usr/bin/omxplayer ' + video_file)
            debug_control = None

        control.send("i")
        print("Ad server starting.")
        self.control = control

    def on_connect(self, conn):
        print("Client connected to ad server.")

    def on_disconnect(self, conn):
        print("Client disconnected from ad server.")

    def exposed_start_video(self):
        self.start_video()

    def exposed_play_default(self):
        self.play_default()

    def exposed_play_male(self):
        self.play_male()

    def exposed_play_female(self):
        self.play_female()

    def start_video(self):
        self.control.expect("Video")
        #self.control.send('p') # Play

    def play_default(self):
        self.control.send("i")
        """
        if self.video_started:
            self.control.send('i') # go to start of the video
        else:
            self.video_started = True
            self.start_video()
        """

    def play_male(self):
        print("received command for male ad")
        self.control.send('i')
        time.sleep(.5)
        self.control.send ('\x1b[C') # jump ahead 30 seconds

    def play_female(self):
        print("received command for female ad")
        self.control.send("i")
        time.sleep(.5)
        self.control.send ('\x1b[C') # jump ahead 30 seconds

    def demographics(self,demographics):
        if sum([1 for g in demographics if g[0]=='male']) > (len(demographics)/2):
            logger.info("more males now")
            self.play_male()
        else:
            logger.info("more females now")
            self.play_female()

def get_client(logger,client_cfg):
    ad_player = None
    if not client_cfg['ad_service']:
        logger.info("Ad service is disabled.")
    else:
        while not ad_player:
            try:
                ad_player = rpyc.connect(*cfg['ad server']).root
                logger.info("Connected to ad server.")
            except:
                logger.info("Waiting then trying to connect to ad service.")
                time.sleep(3)
                continue
    return ad_player

def main():
    t = rpyc.utils.server.ThreadedServer(Player(), port=18861)
    t.start()


if __name__ == '__main__':
    main()

