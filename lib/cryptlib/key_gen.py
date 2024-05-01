import secrets
import string


def key_gen(length):
    return ''.join(secrets.choice(string.ascii_letters+string.digits) for i in range(length))