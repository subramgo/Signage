from subprocess import Popen
import os
import pexpect
import time

class Player():
	def __init__(self):
		self.video_file = '/opt/signage/videos/multi_ads.mov'
		self.control = pexpect.spawn('/usr/bin/omxplayer ' + self.video_file)
		print("Video Loaded")

	def play_default(self):
		self.control.send("i")
	
	def play_male(self):
		self.control.send('i')
		time.sleep(.5)
		self.control.send ('\x1b[C') # jump ahead 30 seconds
	
	def play_female(self):
		self.control.send("i")
		time.sleep(.5)
		self.control.send ('\x1b[C') # jump ahead 30 seconds


