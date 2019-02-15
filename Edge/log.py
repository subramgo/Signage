
import logging
from logging.handlers import RotatingFileHandler

def get_null_logger(name = ''):
    hdlr = logging.NullHandler()
    logging.basicConfig(format="%(asctime)s: %(message)s")
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.addHandler(hdlr)
    return logger

def get_logger(cfg):
    name = 'SignageEdge'
    logging.basicConfig(format="%(asctime)s Cam: %(message)s")    
    if cfg['logfile_path']:
        print("Logging to {}".format(cfg['logfile_path']))
        hdlr = RotatingFileHandler(cfg['logfile_path'],maxBytes=cfg['logfile_maxbytes'])
        logger = logging.getLogger(name)
        logger.addHandler(hdlr)
    else:
        print("Logfile disabled.")
        logger = get_null_logger(name)
    
    level = logging.ERROR if 'err' in cfg['log_level'].lower() else logging.INFO
    logger.setLevel(level)    
    return logger

def get_ad_logger(cfg):
    name = 'SignageAds'
    logging.basicConfig(format="%(asctime)s Ads: %(message)s")
    if cfg['logfile_path']:
        print("Logging to {}".format(cfg['logfile_path']))
        hdlr = RotatingFileHandler(cfg['logfile_path'],maxBytes=cfg['logfile_maxbytes'])
        logger = logging.getLogger(name)
        logger.addHandler(hdlr)
    else:
        print("Logfile disabled.")
        logger = get_null_logger(name)

    level = logging.ERROR if 'err' in cfg['log_level'].lower() else logging.INFO
    logger.setLevel(level)
    return logger