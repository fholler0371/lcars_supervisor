from pydantic import BaseModel, ConfigDict
from typing import Any, Dict
from time import time


class IpState(BaseModel):
    last : int = 0
    change : int = 0
    changed : bool = False
    ip4 : str = ''
    ip6 : str = ''
    prefix : str = ''
    
    model_config = ConfigDict(validate_assignment=True)
    
    def update(self, **new_data):
        for field, value in new_data.items():
            self.last = int(time())
            if getattr(self, field) != value:
                self.change = self.last
                self.changed = True
            setattr(self, field, value)
