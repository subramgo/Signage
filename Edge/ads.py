import pexpect
import time
import rpyc
import sys
import logging
from logging.handlers import RotatingFileHandler

import signage
import rtsp
import config

class VLCPlayer(rpyc.Service):
    def __init__(self,cfg):
        #TODO
        pass


class OMXPlayer(rpyc.Service):

    def __init__(self,cfg):
        super().__init__()

        self._cfg_refresh(cfg)

        self.cam_uri = "{}{}@{}".format(self.camfig['protocol'],self.camfig['credentials'],self.camfig['stream_address'])

        self.video_file = self.adfig['library']+'/multi_ads.mov'

        if self.adfig['debug_view']:
            control = pexpect.spawn('/usr/bin/omxplayer  --win 0,0,640,480 ' + video_file, timeout=60)
            if cfg['cam_protocol'] == 'picam':
                control = pexpect.spawn('/usr/bin/omxplayer  --win 0,0,400,480 ' + video_file, timeout=60)
                import picamera
                cam = picamera.PiCamera()
                cam.start_preview(rotation=270
                        ,fullscreen=False
                        ,window=(400,0,400,480)
                        )
            elif cfg['cam_stream_address'] == 0:
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

    def _cfg_refresh(self,newfig = None):
        if newfig:
            self.cfg = newfig

        self.cfg.load()
        self.camfig = self.cfg['camera']
        self.adfig = self.cfg['ads']

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

def platform():
    """
    What platform are we running on? 
      * Raspberry Pi - 'linux'
      * Windows 10 - ???
      * Ubuntu - 'linux'
      * MacOS - 'darwin'
    """
    if sys.platform == 'linux':
        if os.uname().machine == 'armv7l':
            return 'pi'
    elif sys.platform == 'darwin':
        return 'mac'
    else:
        return 'windows'

def get_server(cfg):
    player_map = { 
          'pi' : OMXPlayer(cfg)
        , 'mac' : VLCPlayer(cfg)
        , 'windows' : VLCPlayer(cfg) 
        }

    return player_map[platform()]

def get_client(logger,cfg):
    ad_player = None
    if not cfg['enabled']:
        logger.info("Ad service is disabled.")
    else:
        logger.info("Ad service is enabled.")
        while not ad_player:
            try:
                ad_player = rpyc.connect(*cfg['ad_server']).root
                logger.info("Connected to ad server.")
            except Exception as e:
                logger.error(e)
                logger.info("Waiting then trying to connect to ad service.")
                time.sleep(3)
                continue
    return ad_player

def main():
    t = rpyc.utils.server.ThreadedServer(get_server(signage.cfg), port=18861)
    t.start()


if __name__ == '__main__':
    main()

