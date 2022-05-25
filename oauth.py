import os
import google.oauth2.credentials
from flask import g
from flask_oauthlib.client import OAuth

oauth = OAuth()

google = oauth.remote_app(
    'google',
    consumer_key=os.getenv('GMAIL_CLIENT_ID'),
    consumer_secret=os.getenv('GMAIL_CLIENT_SECRET'),
    request_token_params={"scope": "openid email profile"},
    base_url="https://www.googleapis.com/oauth2/v1/",
    request_token_url=None,
    access_token_method="POST",
    access_token_url="https://oauth2.googleapis.com/token",
    authorize_url="https://accounts.google.com/o/oauth2/auth"
)


@google.tokengetter
def get_google_token():
    if 'access_token' in g:
        return g.access_token