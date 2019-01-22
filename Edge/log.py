
import logging
from logging.handlers import RotatingFileHandler

def get_null_logger(name):
    hdlr = logging.NullHandler()
    logging.basicConfig(format="%(asctime)s: %(message)s")
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.addHandler(hdlr)
    return logger

def get_logger(cfg):
    name = 'SignageEdge'
    if cfg['logfile_path']:
        print("Logging to {}".format(cfg['logfile_path']))
        hdlr = RotatingFileHandler(cfg['logfile_path'],maxBytes=cfg['logfile_maxbytes'])
        logging.basicConfig(format="%(asctime)s: %(message)s")
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        logger.addHandler(hdlr)
        return logger
    else:
        print("Logging disabled.")
        hdlr = get_null_logger(name)

def get_ad_logger(cfg):
    name = 'SignageAds'
    if cfg['logfile_path']:
        print("Logging to {}".format(cfg['logfile_path']))
        hdlr = RotatingFileHandler(cfg['logfile_path'],maxBytes=cfg['logfile_maxbytes'])
        logging.basicConfig(format="%(asctime)s: %(message)s")
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        logger.addHandler(hdlr)
        return logger
    else:
        print("Logging disabled.")
        return get_null_logger(name)