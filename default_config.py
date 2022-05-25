import os
class DefaultConfig:
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY')
    PROPAGATE_EXCEPTIONS = True
    UPLOADED_IMAGES_DEST = os.path.join('static', 'images')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    #JWT_REFRESH_TOKEN_EXPIRES = int(3600)
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']
    CACHE_TYPE = 'simple' 
    CACHE_DEFAULT_TIMEOUT = 10 * 60
    RATELIMIT_HEADERS_ENABLED = True