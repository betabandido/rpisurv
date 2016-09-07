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

from auth import login_manager
login_manager.init_app(app)
login_manager.login_view = 'login'

import views

