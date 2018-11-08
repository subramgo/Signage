
""" Create or update all YAML text files. """

import sys
import os
sys.path.append(os.path.abspath(('.')))
sys.path.append(os.path.abspath(('..')))

import signage
signage.cfg.dump()

import ads
ads.cfg.dump()

