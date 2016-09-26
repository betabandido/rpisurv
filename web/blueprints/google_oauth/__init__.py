from flask import Blueprint
from oauth2client.contrib.flask_util import UserOAuth2
from oauth2client.file import Storage

from ... import app

google_oauth = Blueprint(
    'google_oauth',
    __name__,
    template_folder='templates')

credentials_path = 'credentials'
scopes = ['https://www.googleapis.com/auth/drive.file']

app.config['GOOGLE_OAUTH2_CLIENT_SECRETS_FILE'] = \
    'config/client_secrets.json'
app.app_context().push()

storage = Storage(credentials_path)
oauth2 = UserOAuth2(app, storage=storage, scopes=scopes)

import views

