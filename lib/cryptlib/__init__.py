try:
    AKTIV = True
    from .aes import Aes
    from .key_gen import key_gen
    from .jwt import Jwt
except:
    AKTIV = False