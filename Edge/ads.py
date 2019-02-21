#!python3

import time
import os
import sys
import pathlib

import threading
import subprocess
#import rpyc
import random

import log
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

    def __init__(self,repeats=False,library_root_path = '/opt/signage/videos',logger=None):
        self._path = pathlib.PurePath(library_root_path)

        self.allow_repeats = repeats
        self.programming = config.Config(
                      filepath = self.path.joinpath("program.yml").as_posix()
                    , description = "Ad Programming")
        self.logger = logger

        self._catalogue = [x for x in os.listdir(self.path.as_posix()) if self._ismediafilename(x)]
        self._last_played = None # track & avoid repeats

    def _ismediafilename(self,filename):
        return filename.endswith('.mp4') or filename.endswith('.png') and \
           not filename.startswith('.')

    def newMedia(self,filters = []):
        """ Return file path for a new media item.
            `filters`: list of keys to `self.programming`. """
        
        newset = set(self.catalogue)

        if not self.allow_repeats:
            newset -= set([self._last_played])
        
        if not filters:
            filters = ['default']
        for _filter in filters:
            try:
                newset.intersection_update(self.programming[_filter])
            except:
                pass

        if newset:
            new = random.sample(newset,1)[0]
        else:
            new = random.sample(self.catalogue,1)[0]

        return self.path.joinpath(new).as_posix()

class NullPlayer:
    def demographics(self,demographics):
        pass
    def catalogue(self):
        return []

class ImagePlayer:
    def __init__(self,cfg = sharedconfig.cfg):
        #super().__init__()

        self._cfg_refresh(cfg)
        self.logger = log.get_ad_logger(self.adfig)

        if not self.adfig['enabled']:
            self.logger.info("Ad service is disabled.")
        else:
            self.logger.info("Starting ad server.")

        self.lib = Library(self.adfig['allow_repeats'],self.adfig['library'],self.logger)
        self._last_played = 0
        self._last_media = None
        self.audience = []

        thread = threading.Thread(target=self._playLoop)
        thread.start()

    def _cfg_refresh(self,newfig = None):
        if newfig:
            self.cfg = newfig

        self.cfg.load()
        #self.cfg.dump()
        self.camfig = self.cfg['camera']
        self.adfig = self.cfg['ads']

    def on_connect(self, conn):
        self.logger.info("Client connected to ad server.")

    def on_disconnect(self, conn):
        self.logger.info("Client disconnected from ad server.")

    def cooling_down(self):
        cld = self.adfig['cooldown_secs'] - (time.time()-self._last_played)
        if cld > 0:
            return cld
        else:
            return False

    def _playLoop(self):
        """ Run in background thread """
        if not self.adfig['enabled']:
            return
        self.playing = None
        self.play()
        while True:
            try:
                self.play()
                time.sleep(1)
            except (EOFError,TimeoutError) as e:
                continue

    def play(self):
        """ Respecting cooldown, interrupt and refresh current playback"""
        self._cfg_refresh()
        if self.cooling_down():
            return

        if len(self.audience) > 0:
            self._last_played = time.time()

        filters = self.ad_filters()
        media_path = self.lib.newMedia(filters)

        if self.adfig['allow_repeats'] and media_path == self._last_media:
            return
        else:
            self.logger.info("Selected media {}".format(media_path) + (" using filters \'{}\'".format('\',\''.join(filters)) if filters else '') )
            self._last_media = media_path

        #geomy,geomx,height,width = [str(x) for x in self.adfig['display']['window']]
        #rotation = self.adfig['display']['rotation']
        
        if platform()=='ubuntu':
            popen_args = "eog -w {}".format(media_path).split(' ')
        else:
            popen_args = ['open',media_path]
            if self.playing:
                self.playing.terminate()
        
        self.playing = subprocess.Popen(' '.join(popen_args),stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,shell=True)

    def ad_filters(self):
        if self.audience:
            ppl_log = self.audience
            self.audience = []

            # currently not using any of the other audience measures
            genders,ages = zip(*[(x.gender,x.age) for x in ppl_log])

            gender_ratio = sum([1.0 for g in genders if g=='male'])/len(genders)
            mean_age = int(sum(ages)/len(ages))
        else:
            gender_ratio,mean_age = None,None

        filters = []
        if mean_age:
            if mean_age > 30:
                filters.append('old')
            else:
                filters.append('young')

        if gender_ratio:
            if gender_ratio > 0.5:
                filters.append('male')
            else:
                filters.append('female')
        return filters

    def demographics(self,demographics):
        if demographics:
            self.audience += demographics

    def catalogue(self):
        return self.lib.catalogue

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


def get_client(logger,cfg):
    ad_player = None
    if not cfg['enabled']:
        logger.info("Ad service is disabled.")
        return NullPlayer()
    else:
        logger.info("Ad service is enabled.")
        while not ad_player:
            try:
                #ad_player = rpyc.connect(*cfg['server']).root
                ad_player = ImagePlayer()
                logger.info("Connected to ad server.")

                if not ad_player.catalogue():
                    logger.info("No videos in catalogue.")
                    ad_player = NullPlayer()
            except Exception as e:
                logger.error(e)
                logger.info("Waiting then trying to connect to ad service.")
                time.sleep(3)
                continue
    return ad_player

#def main():
#    t = rpyc.utils.server.ThreadedServer(ImagePlayer(), port=18861)
#    t.start()

if __name__ == '__main__':
    main()
