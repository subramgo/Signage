"""
    Configuration
      * Serialization to YAML file
        * optional
        * Easy loading and dumping
        * give a second file to manage sensitive credentials
      * Defaults defined as Python `dict`
        * Seamless interface for Python code
        * Single authority and location for config definition
        * Updated default dict will auto-update YAML files
      * Simple Precedence
        * YAML *values* override `defaults_dict` *values*
        * `defaults_dict` *keys* define config *keys*

    Mask sensitive credentials from the default filepath:
      1. provide
        * 'mask' default value to store
        * secure that path yourself
      2. internal storage is updated when default has been changed
"""

import yaml
from functools import reduce as _reduce

class Config(dict):
    @property
    def filepath(self):
        return self._filepath

    def __init__(self,description = None, filepath = None, defaults_dict = None, maskedpath = None):
        self.description = description
        self._filepath = filepath
        self._intered = None
        self._masks = {}

        if maskedpath:
            self._intered = Config(filepath=maskedpath,description="masked configs")

        ### Precedence of YAML over defaults
        if defaults_dict:
            self.update(defaults_dict)
        if filepath:
            self.load()

    def dump(self,filepath=None):
        """ Serialize to YAML """
        if filepath:
            self._filepath = filepath
        try:
            self._mask()
            with open(self.filepath,'w') as ymlfile:
                ymlfile.write("%YAML 1.1\n---\n")
                ymlfile.write("# this file should be located at {}\n".format(self.filepath))
                ymlfile.write("\n\n")
                ymlfile.write("###########################################################\n")
                if self.description: ymlfile.write("####{: ^50} ####\n".format(self.description))
                ymlfile.write("###########################################################\n")
                ymlfile.write("\n\n")
                _yaml = yaml.dump(dict(self.items()),default_flow_style=False,indent=4)
                ymlfile.write(_yaml)
                ymlfile.write("\n\n")
            self._unmask()
            
        except Exception as e:
            print("Couldn't write to {} : {}".format(self.filepath,e))

    def _recursive_strict_update(self,a,b):
        """ Update only items from 'b' which already have a key in 'a'.
            This defines behavior when there is a "schema change".
            a is used for the input dictionary
            b is used for the serialized YAML file:
              * only items defined in 'a' are kept
              * values present in 'b' are given priority
         """
        if not a:
            a.update(b)
            return
        if not b:
            return

        for key in b.keys():
            if key in a.keys():
                if isinstance(b[key],dict):
                    self._recursive_strict_update(a[key],b[key])
                else:
                    a[key] = b[key]
        
    def load(self,verbose=True):
        """ Load from filepath and overwrite local items. """
        try:
            with open(self.filepath,'r') as ymlfile:
                newstuff = yaml.load(ymlfile)
                self._recursive_strict_update(self,newstuff)
            self._unmask()
        except Exception as e:
            if verbose:
                if 'No such file' in e.strerror:
                    self.dump()
                    print("Initialized config file {}".format(self.filepath))
                else:
                    print("Didn't load from {} : {}".format(self.filepath,e))

    def _nestupdate(self,key,val):
        cfg = self
        key = key.split('.')
        if len(key) > 1:
            cfg = cfg[key.pop(0)]
        cfg[key[0]] = val

    def _nestread(self,key):
        if len(key.split('.')) > 1:
            return _reduce(dict.get, key.split('.'), self) 
        else:
            return self[key] 

    def mask(self,cfg_key,mask):
        """ Good for sensitive credentials.
            Mask is serialized to `self.filepath`.
            True value serialized to `self.maskedpath`. """
        if self._intered is None:
            raise Exception('Cannot mask without a maskedpath serializing path.')

        self._masks[cfg_key] = mask
        if self._nestread(cfg_key) != mask:
            self._intered[cfg_key] = self._nestread(cfg_key)
        self._unmask()

    def _mask(self):
        if self._masks:
            self._intered.update({'_masks':self._masks})
            self._intered.dump()

            for key,mask in self._intered.pop('_masks').items():
                self._nestupdate(key,mask)

    def _unmask(self):
        """ resolve hierarchy: {new_val > interred > mask} """
        if not self._intered:
            return
        self._intered.load(verbose=False)

        try:
            self._masks.update(self._intered.pop('_masks'))
        except KeyError:
            pass
        
        for key,mask in self._masks.items():
            current = self._nestread(key) 

            if current != mask:
                self._intered[key] = current
                self._intered.dump() # write to protected YAML
                self.dump()          # write to external YAML

            try:
                self._nestupdate(key,self._intered[key])
            except KeyError:
                pass

def rUpdate(a,b,strict=False):
    """ recursive update: Preserve a.keys() not in b.keys()
        strict mode: only overwrite existing a.keys() """
    pass
    #TODO
