from subprocess import Popen
import os
import pexpect
import time
import rpyc
import yaml

###########################################################
##############         Configuration         ##############
###########################################################
with open("/boot/signage/config.yml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile)['ad_server']

# TODO if cfg['source_camera_inset'], overlay source camera feed
# TODO? if cfg['debug_positions'], make main player show behind other windows so the screen can be used?

class Player(rpyc.Service):
    def on_connect(self, conn):
        self.video_file = '/opt/signage/videos/multi_ads.mov'
        #self.control = pexpect.spawn('/usr/bin/omxplayer  --win 0,0,640,480 ' + self.video_file)
        self.control = pexpect.spawn('/usr/bin/omxplayer ' + self.video_file)
        print("Video Loaded")

    def on_disconnect(self, conn):
        self.control.send ('q')

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
        self.control.send('i')
        time.sleep(.5)
        self.control.send ('\x1b[C') # jump ahead 30 seconds
        
    def play_female(self):
        self.control.send("i")
        time.sleep(.5)
        self.control.send ('\x1b[C') # jump ahead 30 seconds
        

def main():
    from rpyc.utils.server import ThreadedServer
    t = ThreadedServer(Player, port=18861)
    print("Video Loaded")
    t.start()


if __name__ == '__main__':
    main()


