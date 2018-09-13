
import yaml

class Config(dict):
    """ Dictionary with optional YAML text file to override its values. """

    @property
    def filepath(self):
        return self._filepath

    def __init__(self,description = None, filepath = None, dictionary = None):
        self.description = description
        self._filepath = filepath

        ### Important to do these in this order. Defines precedence.
        if dictionary:
            self.update(dictionary)
        if filepath:
            self.load()

    def dump(self,filepath=None):
        """ Serialize to YAML """
        if filepath:
            self._filepath = filepath
        try:
            with open(self.filepath,'w') as ymlfile:
                ymlfile.write("%YAML 1.1\n---\n")
                ymlfile.write("# this file should be located at {}\n".format(self.filepath))
                ymlfile.write("\n\n")
                ymlfile.write("###########################################################\n")
                ymlfile.write("####{: ^50} ####\n".format(self.description))
                ymlfile.write("###########################################################\n")
                ymlfile.write("\n\n")
                _yaml = yaml.dump(dict(self.items()),default_flow_style=False,indent=4)
                ymlfile.write(_yaml)
                ymlfile.write("\n\n")

        except Exception as e:
            print("Couldn't write to {} : {}".format(self.filepath,e))

    def load(self):
        """ Load from filepath and overwrite local items. """
        try:
            with open(self.filepath,'r') as ymlfile:
                newstuff = yaml.load(ymlfile)
                self.update(newstuff)
        except FileNotFoundError:
            print("No YAML file to load from.")
        except Exception as e:
            import pdb
            pdb.set_trace()
            print("Couldn't load from {} : {}".format(self.filepath,e))

def generate_defaults():
    """ For other packages using a Config object, create/update the source files. """
    pass
    #TODO create locations for config objects
    #TODO call `dump` on all Config objects in other modules

