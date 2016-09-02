from flask import Flask, flash, redirect, render_template, request, Response, url_for
from functools import wraps
from lockfile.pidlockfile import PIDLockFile
import os.path
import subprocess
import yaml

basepath = os.path.dirname(os.path.realpath(__file__))
rpisurv_path = os.path.realpath(os.path.join(basepath, '..', 'rpisurv', 'main.py'))

with open(os.path.join(basepath, 'secrets.yaml')) as f:
  secrets = yaml.load(f)

with open(os.path.join(basepath, 'settings.yaml')) as f:
  settings = yaml.load(f)

app = Flask(__name__)
app.secret_key = secrets['secret_key']

def check_auth(username, password):
  return username == secrets['username'] and password == secrets['password']

def authenticate():
  return Response(
      'Could not verify your access level for that URL.\n'
      'You have to login with proper credentials', 401,
      {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
  @wraps(f)
  def decorated(*args, **kwargs):
    auth = request.authorization
    if not auth or not check_auth(auth.username, auth.password):
      return authenticate()
    return f(*args, **kwargs)
  return decorated

def enable_camera():
  subprocess.check_call([
    '/usr/bin/env',
    'python',
    rpisurv_path,
    'start'])

def disable_camera():
  subprocess.check_call([
    '/usr/bin/env',
    'python',
    rpisurv_path,
    'stop'])

def set_camera_state(state):
  if state == 'on':
    enable_camera()
  elif state == 'off':
    disable_camera()
  else:
    assert False

def is_camera_enabled():
  f = PIDLockFile(settings['pidfile_path'])
  return f.is_locked()

def current_camera_state():
  if is_camera_enabled():
    return 'on'
  else:
    return 'off'

@app.route('/')
@requires_auth
def index():
  return render_template('index.html', camera_state=current_camera_state())

@app.route('/settings')
@requires_auth
def settings_form():
  camera_state = ''
  if is_camera_enabled():
    camera_state = 'checked'
  return render_template('settings.html', camera_state=camera_state)

@app.route('/update-settings', methods=['POST'])
@requires_auth
def update_settings():
  requested_camera_state = request.form.get('enable-camera', 'off')
  #recipients = request.form.get('recipients', '')
  #notification_limit = request.form.get('notification-limit', '60')

  if current_camera_state() != requested_camera_state:
    try:
      set_camera_state(requested_camera_state)
      flash('Camera set to {}'.format(requested_camera_state))
    except Exception, e:
      flash('Error setting camera state: {}'.format(str(e)))

  return redirect(url_for('index'))

"""
@app.route('/on')
def on():
  try:
    enable_camera()
    flash('Camera was enabled')
  except Exception, e:
    flash('Error enabling camera: {}'.format(str(e)))
  return redirect(url_for('index'))

@app.route('/off')
def off():
  try:
    disable_camera()
    flash('Camera was disabled')
  except Exception, e:
    flash('Error disabling camera: {}'.format(str(e)))
  return redirect(url_for('index'))
"""

if __name__ == '__main__':
  app.run(host='0.0.0.0')

