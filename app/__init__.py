from flask import Flask
from flask_oauthlib.client import OAuth
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('config')

db = SQLAlchemy(app)

oauth = OAuth(app)
zotero = oauth.remote_app(
    'zotero',
    base_url='https://api.zotero.org',
    request_token_url='https://www.zotero.org/oauth/request',
    access_token_url='https://www.zotero.org/oauth/access',
    authorize_url='https://www.zotero.org/oauth/authorize',
    app_key='ZOTERO'
)

from app import views, dbmodels
