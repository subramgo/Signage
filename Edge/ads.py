#!python3

import time
import os
import sys
import pathlib

import threading
import subprocess
import rpyc
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
        self._now_playing = None # track & avoid repeats

    def _ismediafilename(self,filename):
        return filename.endswith('.mp4') or filename.endswith('.png') and \
           not filename.startswith('.')

    def newMedia(self,filters = []):
        """ Return file path for a new media item.
            `filters`: list of keys to `self.programming`. """
        
        newset = set(self.catalogue)

        if not self.allow_repeats:
            newset -= set([self._now_playing])
        
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

        self.logger.info("Selected media {}".format(new) + (" using filters {}".format(','.join(filters)) if filters else '') )

        self._now_playing = new
        return self.path.joinpath(new).as_posix()

class Demographics:
    @property
    def audience(self):
        try:
            return self._audience
        except:
            self._audience = []
            return self._audience
    
    @property
    def summary(self):
        return self.summarize()

    @property
    def ad_filters(self):
        headcount,gender_ratio,mean_age = self.summary
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

    def __init__(self,logger):
        self.logger = logger

    def __nonzero__(self):
        return len(self.audience) > 0

    def update(self,new_headcounts):
        self._audience += new_headcounts

    def target_ad(self,ad_library):
        if self.audience:
            self.logger.info("Serving ad by demographics: {}-count, male-ratio={:.2}, mean-age={}.".format(*self.summary))
        ad = ad_library.newMedia(self.ad_filters)
        self._audience = []
        return ad

    def summarize(self,ppl_log = None):
        if not ppl_log:
            if not self.audience:
                return 0,None,None
            ppl_log = self.audience

        age_translate = {'(0, 2)': 1, '(4, 6)': 5 , '(8, 12)': 10, '(15, 20)':18, '(25, 32)':28 , '(38, 43)':40}
        ages = [age_translate[x[1]] for x in ppl_log]

        gender_ratio = sum([1.0 for g in ppl_log if g[0]=='male'])/len(ppl_log)
        mean_age = int(sum(ages)/len(ages))

        return len(ppl_log),gender_ratio,mean_age

class NullPlayer:
    def demographics(self,demographics):
        pass
    def catalogue(self):
        return []

class ImagePlayer(rpyc.Service):
    def __init__(self,cfg = sharedconfig.cfg):
        super().__init__()

        self._cfg_refresh(cfg)
        self.logger = log.get_ad_logger(self.adfig)

        if not self.adfig['enabled']:
            self.logger.info("Ad service is disabled.")
        else:
            self.logger.info("Starting ad server.")

        self.lib = Library(self.adfig['allow_repeats'],self.adfig['library'],self.logger)
        self._last_played = 0
        self._playing = False
        self._demographics = Demographics(self.logger)

        thread = threading.Thread(target=self._playLoop)
        thread.start()

    def _cfg_refresh(self,newfig = None):
        if newfig:
            self.cfg = newfig

        self.cfg.load()
        self.cfg.dump()
        self.camfig = self.cfg['camera']
        self.adfig = self.cfg['ads']

    def on_connect(self, conn):
        self.logger.info("Client connected to ad server.")

    def on_disconnect(self, conn):
        self.logger.info("Client disconnected from ad server.")

    def cooling_down(self):
        return self.adfig['cooldown_secs'] > (time.time()-self._last_played)

    def _playLoop(self):
        """ Run in background thread """
        if not self.adfig['enabled']:
            return
        self.playing = None
        self.play()
        while True:
            self.play()
            time.sleep(1)

    def play(self):
        """ Respecting cooldown, interrupt and refresh current playback"""
        self._cfg_refresh()
        if self.cooling_down():
            return

        if self._demographics:
            self._last_played = time.time()

        media_path = self._demographics.target_ad(self.lib)

        #geomy,geomx,height,width = [str(x) for x in self.adfig['display']['window']]
        #rotation = self.adfig['display']['rotation']
        
        popen_args = ['xdg-open'] if platform()=='ubuntu' else ['open']
        popen_args.append(media_path)

        if self.playing:
            self.playing.terminate()
        self.playing = subprocess.Popen(' '.join(popen_args),stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,shell=True)

    def exposed_demographics(self,demographics):
        if not demographics:
            return
            
        cooldown = self.adfig['cooldown_secs'] - (time.time()-self._last_played)
        if cooldown >=0:
            self.logger.info("Received new demographics but still on cooldown - {:.4} secs".format(cooldown))

        self._demographics.update(demographics)

        self.play()

    def exposed_catalogue(self):
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
                ad_player = rpyc.connect(*cfg['server']).root
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

def main():
    t = rpyc.utils.server.ThreadedServer(ImagePlayer(), port=18861)
    t.start()

if __name__ == '__main__':
    main()
