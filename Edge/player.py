import pexpect
import time
import rpyc
import yaml

###########################################################
##############         Configuration         ##############
###########################################################
with open("/boot/signage/config.yml", 'r') as ymlfile:
    all_cfg = yaml.load(ymlfile)

cfg = all_cfg['ad_server']

# TODO if cfg['source_camera_inset'], overlay source camera feed

class Player(rpyc.Service):
    def on_connect(self, conn):
        self.video_file = cfg['video_uri']
        if cfg['debug_positions']:
        	self.control = pexpect.spawn('/usr/bin/omxplayer  --win 0,0,640,480 ' + self.video_file)
        	#Popen(debug_stream,preexec_fn=os.setsid,stdin=subprocess.PIPE, stdout=subprocess.PIPE,stderr=subprocess.PIPE,close_fds=True)
        	self.debug_control = pexpect.spawn('/usr/bin/omxplayer  --win 641,480,1280,960 --avdict rtsp_transport:tcp ' + all_cfg['cam_uri'])
        	self.debug_control.expect("Video")
        else:
        	self.control = pexpect.spawn('/usr/bin/omxplayer ' + self.video_file)
        print("Client connected and video loaded.")

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
    print("Ad server starting.")

    t.start()


if __name__ == '__main__':
    main()


