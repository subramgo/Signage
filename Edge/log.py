
import logging
from logging.handlers import RotatingFileHandler

def get_logger(cfg):
	if cfg['enabled']:
	    print("Logging to {}".format(cfg['logfile_path']))
	    hdlr = RotatingFileHandler(cfg['logfile_path'],maxBytes=cfg['logfile_maxbytes'])
	else:
	    print("Logging disabled.")
	    hdlr = logging.NullHandler()
	logging.basicConfig(format="[%(thread)-5d]%(asctime)s: %(message)s")
	logger = logging.getLogger('SignageEdge)')
	logger.setLevel(logging.INFO)
	logger.addHandler(hdlr)
	return logger