from flask import redirect, render_template

from . import setup

@setup.route('/')
def index():
  return render_template('setup.html')

@setup.route('/google')
def google():
  return render_template('google.html')

