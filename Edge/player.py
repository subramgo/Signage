import pexpect
import time
import rpyc
import yaml

# TODO if cfg['source_camera_inset'], overlay source camera feed

###########################################################
##############         Configuration         ##############
###########################################################
with open("/boot/signage/config.yml", 'r') as ymlfile:
    all_cfg = yaml.load(ymlfile)
with open("/opt/signage/credentials.yml",'r') as ymlfile:
    credentials = yaml.load(ymlfile)

cfg = all_cfg['ad_server']
cam_uri = all_cfg['cam_protocol']+credentials['video_stream']+"@"+all_cfg['cam_stream_address']
video_file = cfg['video_uri']

class Player(rpyc.Service):

    def __init__(self):
        super().__init__()
        if cfg['debug_positions']:
            control = pexpect.spawn('/usr/bin/omxplayer  --win 0,0,640,480 ' + video_file, timeout=60)
            debug_control = pexpect.spawn('/usr/bin/omxplayer  --win 641,480,1280,960 --avdict rtsp_transport:tcp ' + cam_uri)
            debug_control.expect("Video", timeout=60)
        else:
            control = pexpect.spawn('/usr/bin/omxplayer ' + video_file)
            debug_control = None

        control.send("i")
        print("Ad server starting.")
        self.control = control
        self.debug_control = debug_control

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

def main():
    t = rpyc.utils.server.ThreadedServer(Player(), port=18861)
    t.start()


if __name__ == '__main__':
    main()

