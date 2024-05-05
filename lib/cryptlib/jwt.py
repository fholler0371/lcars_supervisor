import jwt


class Jwt:
    def __init__(self, pem: str) -> None:
        self.key = pem
    
    def validate(self, token: str) -> dict:
        try:
            return jwt.decode(token.encode(), self.key, algorithms=["RS256"], options={'verify_aud': False})
        except Exception as e:
            print(e, flush=True)
            return None
