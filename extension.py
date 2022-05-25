from flask_marshmallow import Marshmallow
from flask_jwt_extended import JWTManager
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

ma = Marshmallow()
jwt = JWTManager()
cache = Cache()
limiter = Limiter(key_func=get_remote_address)