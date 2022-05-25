import os
class Config:
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ['SECRET_KEY']
    PROPAGATE_EXCEPTIONS = True
    UPLOADED_IMAGES_DEST = os.path.join("static", "images")