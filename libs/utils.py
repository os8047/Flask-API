import re
from extension import cache
from passlib.hash import pbkdf2_sha256


def hash_password(password: str) -> str:
    return pbkdf2_sha256.hash(password)

def check_password(password: str, hashed: str) -> bool:
    return pbkdf2_sha256.verify(password, hashed)

def validate_password(password: str) -> bool:
    regex = "[A-Za-z0-9@#$%^&+=]{8,}"
    return re.match(regex, password)

def clear_cache(key_prefix):
    keys = [key for key in cache.cache._cache.keys() if key.startswith(key_prefix)]
    cache.delete_many(*keys)
    
    