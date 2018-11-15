
import yaml

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
        # TODO: have to serialize the masks
        if filepath:
            self._filepath = filepath
        try:
            with open(self.filepath,'w') as ymlfile:
                if self._masks:
                    self._intered.update({'_masks':self._masks})
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
                if self._masks:
                    self._intered.dump()
                    self._intered.pop('_masks')

        except Exception as e:
            print("Couldn't write to {} : {}".format(self.filepath,e))

    def load(self):
        """ Load from filepath and overwrite local items. """
        try:
            with open(self.filepath,'r') as ymlfile:
                newstuff = yaml.load(ymlfile)
                if newstuff:
                    self.update(newstuff)
                if self._intered:
                    try:
                        self._masks.update(self._intered.pop('_masks'))
                        self.update(self._intered.items())
                    except KeyError:
                        pass
                    #self._unmask()
        except FileNotFoundError:
            pass
            #print("No YAML file to load from.")
        except Exception as e:
            import pdb
            pdb.set_trace()
            print("Couldn't load from {} : {}".format(self.filepath,e))

    def mask(self,cfg_key,mask):
        """ Hide a configuration internally. Check external mask for updates.
            Good for sensitive credentials. Must have supplied an `internalpath`. """
        self._masks[cfg_key] = mask
        self._unmask()

    def _unmask(self):
        self._intered.load()
        for key,default in self._masks.items():
            if self[key] != default:
                self._intered[key] = self.get(key)
                self._intered.dump() # write to protected YAML

                self.update({key:default})
                self.dump()         # write to external YAML
