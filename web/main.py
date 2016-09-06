from flask import Flask, flash, redirect, render_template, request, url_for
import os
from subprocess import call, check_call
import time

from auth import requires_auth
from config import basepath, secrets, settings

app = Flask(__name__)
app.secret_key = secrets['secret_key']

def enable_camera():
  """Enables the camera."""
  check_call(['sudo', 'systemctl', 'start', 'rpisurv'])

def disable_camera():
  """Disables the camera."""
  check_call(['sudo', 'systemctl', 'stop', 'rpisurv'])

def set_camera_state(state):
  """Sets the camera state.

  Args:
    state: The new camera state ['on', 'off'].
  """
  if state == 'on':
    enable_camera()
  elif state == 'off':
    disable_camera()
  else:
    assert False

def is_camera_enabled():
  """Checks whether the camera is enabled.

  Returns:
    True if the camera is enabled; False otherwise.
  """
  return call(['systemctl', 'status', 'rpisurv']) == 0

def current_camera_state():
  """Returns the current camera state.

  Returns:
    'on' if the camera is enabled; 'off' otherwise.
  """
  if is_camera_enabled():
    return 'on'
  else:
    return 'off'

@app.route('/')
@requires_auth
def index():
  try:
    latest_time = time.ctime(os.path.getmtime(
        os.path.join(basepath, 'static', 'latest.jpg')))
  except Exception:
    latest_time = ''

  try:
    camera_state = current_camera_state()
  except Exception, e:
    flash('Error obtaining camera state: {}'.format(str(e)))
    camera_state = ''

  # TODO handle the case when there is no latest image yet.
  return render_template('index.html',
      camera_state=camera_state,
      latest_time=latest_time)

@app.route('/settings')
@requires_auth
def settings_form():
  try:
    camera_state = ''
    if is_camera_enabled():
      camera_state = 'checked'
    return render_template('settings.html', camera_state=camera_state)
  except Exception, e:
    flash('Error: {}'.format(str(e)))
    return redirect(url_for('index'))

@app.route('/update-settings', methods=['POST'])
@requires_auth
def update_settings():
  requested_camera_state = request.form.get('enable-camera', 'off')
  #recipients = request.form.get('recipients', '')
  #notification_limit = request.form.get('notification-limit', '60')

  try:
    if current_camera_state() != requested_camera_state:
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

