# config.py
import logging
from configparser import ConfigParser
from pathlib import Path
from . import LOGGER_NAME

__path_default = Path.home().joinpath('.ghost-backup.cfg')

class BackUpConfig:
   
   def __init__(self, cfg:ConfigParser):
      self.__cfg = cfg
   
   def getGhost(self):
      return self.__cfg["Ghost"] 
   
   def getOCI(self):
      return self.__cfg['OCI']

   def getDB(self):
      return self.__cfg['DB']


def loadConfig(cfg_path:Path) -> BackUpConfig :
   path = cfg_path or __path_default
   if path.exists():
      cfg = ConfigParser()
      cfg.read(path)
      #todo: improve sanity check
      if  not('Ghost' in cfg and 'AccessToken' in cfg['Ghost']):
         raise Exception("Expected configuration for Ghost at '%s' containing 'AcccesToken'", path)
      else:
         logging.getLogger(LOGGER_NAME).debug("Loaded config from %s", path)
         return BackUpConfig(cfg=cfg)
   else:
      logging.getLogger(LOGGER_NAME).warning("No Configuration File at '%s': no configuration built", path.absolute())
      e = FileNotFoundError()
      e.filename = path.absolute()
      raise e