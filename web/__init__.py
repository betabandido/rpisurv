from flask import Flask
import os.path
import yaml

basepath = os.path.dirname(os.path.realpath(__file__))

with open(os.path.join(basepath, 'secrets.yaml')) as f:
  secrets = yaml.load(f)

with open(os.path.join(basepath, 'settings.yaml')) as f:
  settings = yaml.load(f)

app = Flask(__name__)
app.secret_key = secrets['secret_key']

# Blueprints are defined here since they might need to import 'app'.
from blueprints.setup import setup
from blueprints.google_oauth import google_oauth

app.register_blueprint(setup, url_prefix='/setup')
app.register_blueprint(google_oauth, url_prefix='/google_oauth')

from auth import login_manager
login_manager.init_app(app)
login_manager.login_view = 'login'

import views

print('url_map: {}'.format(app.url_map))
