
import yaml
from functools import reduce as _reduce

class Config(dict):
    """ Dictionary with optional YAML text file to override its values.
        
        Mask sensitive credentials from the default filepath:
          1. provide a secure path for internal storage
          2. give a 'mask' or default value to store
          3. internal storage is updated when default has been changed
     """

    @property
    def filepath(self):
        return self._filepath

    def __init__(self,description = None, filepath = None, dictionary = None, internalpath = None):
        self.description = description
        self._filepath = filepath
        self._intered = None
        self._masks = {}

        if internalpath:
            self._intered = Config(filepath=internalpath,description="masked configs")

        ### This order defines precedence.
        if dictionary:
            self.update(dictionary)
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

        except Exception as e:
            print("Couldn't write to {} : {}".format(self.filepath,e))
        
    def load(self,verbose=True):
        """ Load from filepath and overwrite local items. """
        try:
            with open(self.filepath,'r') as ymlfile:
                newstuff = yaml.load(ymlfile)
                if newstuff:
                    self.update(newstuff)
            self._unmask()
        except Exception as e:
            if verbose:
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
            True value serialized to `self.internalpath`. """
        self._masks[cfg_key] = mask
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
                
            self._nestupdate(key,self._intered[key])
