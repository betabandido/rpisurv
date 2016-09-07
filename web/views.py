from flask import flash, redirect, render_template, request, url_for
from flask_login import login_required, login_user, logout_user
import os
import time

from . import app, basepath
from auth import check_auth, LoginForm, User
import camera

@app.route('/login', methods=['GET', 'POST'])
def login():
  form = LoginForm()
  if form.validate_on_submit():
    username = form.username.data
    password = form.password.data
    if check_auth(username, password):
      user = User(username)
      login_user(user)
      flash('Logged in successfully')
      return redirect(url_for('index'))
    else:
      flash('Invalid login')
  return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
  logout_user()
  flash('Logged out successfully')
  return redirect(url_for('index'))

@app.route('/')
@login_required
def index():
  try:
    latest_time = time.ctime(os.path.getmtime(
        os.path.join(basepath, 'static', 'latest.jpg')))
  except Exception, error:
    print('Error: {}'.format(error))
    latest_time = ''

  try:
    camera_state = camera.current_camera_state()
  except Exception, e:
    flash('Error obtaining camera state: {}'.format(e))
    camera_state = ''

  # TODO handle the case when there is no latest image yet.
  return render_template('index.html',
      camera_state=camera_state,
      latest_time=latest_time)

@app.route('/settings')
@login_required
def settings_form():
  try:
    camera_state = ''
    if camera.is_camera_enabled():
      camera_state = 'checked'
    return render_template('settings.html', camera_state=camera_state)
  except Exception, e:
    flash('Error: {}'.format(e))
    return redirect(url_for('index'))

@app.route('/update-settings', methods=['POST'])
@login_required
def update_settings():
  requested_camera_state = request.form.get('enable-camera', 'off')

  try:
    if camera.current_camera_state() != requested_camera_state:
      camera.set_camera_state(requested_camera_state)
      flash('Camera set to {}'.format(requested_camera_state))
  except Exception, e:
    flash('Error setting camera state: {}'.format(e))

  return redirect(url_for('index'))

