from typing import Any
import sys
import logging
import logging.config
import logging.handlers
from logging.handlers import QueueHandler

from .mylogger import MyJSONFormatter
from corelib import BaseObj, Core

from pprint import pprint



class Logger(BaseObj):
    def __init__(self, core: Core) -> None:
        BaseObj.__init__(self, core)
        self._dummy = core.log
        _config = self.core.cfg.logger
        if not _config:
            self.core.log.critical('Kein Konfigurationseintrag')
            sys.exit(-1)
        for handler_name in _config.get('handlers', []):
            if 'filename' in _config['handlers'][handler_name]:
                _config['handlers'][handler_name]['filename'] = _config['handlers'][handler_name]['filename'].replace('%log_folder%', str(self.core.path.log))
        try:
            logging.config.dictConfig(config=_config)
            self._logger = logging.getLogger(sys.argv[0].split('/')[-1].split('.')[0])
        except Exception as e:
            print(e)
            
    def __getattr__(self, name: str) -> Any:
        func = getattr(self._logger, name)
        if func:
            return func    
        func = getattr(self._dummy, name)
        if func:
            return func    
        else:
            raise AttributeError
