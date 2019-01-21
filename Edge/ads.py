#!python3

import time
import os
import sys
import pathlib

import pexpect
import rpyc
import logging
from logging.handlers import RotatingFileHandler

import random
import vlc

import rtsp
import config
import sharedconfig

class Library:
    """
        Class to manage ad library & programming.
        Uniform-random programming schedule.
        Semantic programming by audience:
          * program.yml within library root path
          * need listed media to be present
          * need demographics provided
    """
    @property
    def path(self):
        return self._path

    @property
    def catalogue(self):
        return self._catalogue

    def __init__(self,library_root_path = '/opt/signage/videos'):
        self._path = pathlib.PurePath(library_root_path)

        self.programming = config.Config(
                      filepath = self.path.joinpath("program.yml").as_posix()
                    , description = "Ad Programming")

        self._catalogue = [x for x in os.listdir(self.path.as_posix()) if x.endswith('.mp4')]
        self._now_playing = None # track & avoid repeats

    def newMedia(self,filters = []):
        """ Return file path for a new media item.
            `filters`: list of keys to `self.programming`. """
        newset = set(self.catalogue) - set([self._now_playing])
        
        for _filter in filters:
            print("filtering for {}".format(_filter))
            newset.intersection_update(self.programming[_filter])

        if newset:
            print("randomly sampling from {}".format(newset))
            new = random.sample(newset,1)[0]
        else:
            print("defaulting to a random video")
            new = random.sample(self.catalogue,1)[0]

        self._now_playing = new
        return self.path.joinpath(new).as_posix()

class NullPlayer:
    def demographics(self,demographics):
        pass

    def catalogue(self):
        return []

class VLCPlayer(rpyc.Service):
    def __init__(self,cfg = sharedconfig.cfg):
        super().__init__()

        self._cfg_refresh(cfg)

        self.lib = Library(self.adfig['library'])
        self._last_played = 0
        self.play()

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

    def ready(self):
        return self.adfig['enabled'] and \
               self.adfig['pause_secs'] < (time.time()-self._last_played)

    def play(self,video_path = None):
        if not self.ready():
            return
        if not video_path:
            video_path = self.lib.newMedia()

        print(" *plays {} advertisingly*".format(video_path))

    def exposed_demographics(self,demographics):
        filters = []
        male_ct = sum([1 for g in demographics if g[0]=='male'])
        mean_age = 45 # TODO fix this count

        if mean_age > 30:
            filters.append('old')
        else:
            filters.append('young')

        if male_ct > (len(demographics)/2):
            filters.append('male')
        else:
            filters.append('female')

        print("Processed demographics filters: {}".format(filters))
        self.play(self.lib.newMedia(filters))

    def exposed_catalogue(self):
        return self.lib.catalogue

def get_client(logger,cfg):
    ad_player = None
    if not cfg['enabled']:
        logger.info("Ad service is disabled.")
        return NullPlayer()
    else:
        logger.info("Ad service is enabled.")
        while not ad_player:
            try:
                ad_player = rpyc.connect(*cfg['server']).root
                logger.info("Connected to ad server.")
                
                import IPython
                IPython.embed()

                if not ad_player.catalogue():
                    logger.info("No videos in catalogue.")
                    ad_player = NullPlayer()
            except Exception as e:
                logger.error(e)
                logger.info("Waiting then trying to connect to ad service.")
                time.sleep(3)
                continue
    return ad_player


def main():
    t = rpyc.utils.server.ThreadedServer(VLCPlayer(), port=18861)
    t.start()


if __name__ == '__main__':
    main()

def platform():
    """ pi , ubuntu , mac , windows """
    if sys.platform == 'linux':
        if os.uname().machine == 'armv7l':
            return 'pi'
        else:
            return 'ubuntu'
    elif sys.platform == 'darwin':
        return 'mac'
    else:
        return 'windows'
