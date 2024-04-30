import base64
import hashlib
from cryptography.fernet import Fernet


class Aes:
    def __init__(self, secret):
        while len(secret) < 32:
            secret += secret
        self.f = Fernet(self.passcode(secret))
        
    def passcode(self, passcode:str) -> bytes:
        passcode = passcode.encode('utf-8')
        hlib = hashlib.md5()
        hlib.update(passcode)
        return base64.urlsafe_b64encode(hlib.hexdigest().encode('latin-1'))

    def encode(self, data):
        if isinstance(data, str):
            data = data.encode()
        return self.f.encrypt(data)
    
    def decode(self, data):
        return self.f.decrypt(data).decode()