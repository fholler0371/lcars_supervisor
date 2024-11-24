from pydantic import BaseModel, Field
import time

def timestamp():
    return int(time.time())

class CacheEntry(BaseModel):
    value: float|int
    timestamp: int = Field(default=timestamp())
    
    @property
    def valid(self):
        return self.timestamp + 900 > timestamp() 