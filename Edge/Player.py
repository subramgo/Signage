from subprocess import Popen
import os

class Player():
	def __init__(self, video_list):
		self.videos_root_folder = '/opt/signage/videos/'
		self.default_video = self.videos_root_folder + 'cold-brew.mp4'
		self.male_ads = self.videos_root_folder +  'mobile-order.mp4'
		self.female_ads = self.videos_root_folder + 'red-cups.mp4'
		self.video_play_list = video_list

	def _play(self,path):
		""" Play the required video identfied by index"""
		os.system('killall omxplayer.bin')
		omxc = Popen(['omxplayer', '-b','-r','-o local', '--loop',path])

	def play_default(self):
		self._play(self.default_video)

	def play_male(self):
		self._play(self.play_male)

	def play_female(self):
		self._play(self.play_female)



