import hashlib
import time
from pydantic import BaseModel, model_serializer

def timestamp():
    return str(int(time.time()))
               
class NotifyMessage(BaseModel):
    token: str
    level: str = 'info'
    text: str 
    md5: str = ''
    use_timestamp: bool = False
    timestamp: str|None = None

    def model_post_init(self, __context):
        if not self.timestamp:
            self.timestamp = timestamp()
            if self.md5 == '':
                text = f"{self.token}{self.level}{self.text}"
                if self.use_timestamp:
                    text = f"{text}{self.timestamp}"
            else:
                text = self.md5
            self.md5 = hashlib.md5(text.encode()).hexdigest()
