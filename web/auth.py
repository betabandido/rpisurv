from flask_login import LoginManager
from flask_wtf import Form
from wtforms import PasswordField, StringField
from wtforms.validators import InputRequired

from . import secrets

def check_auth(username, password):
  """Checks authentication values.

  Args:
    username: The username.
    password: The password.
  """
  return username == secrets['username'] \
      and password == secrets['password']

login_manager = LoginManager()

class User:
  def __init__(self, username):
    self.username = username

  def is_authenticated(self):
    return True

  def is_active(self):
    return True

  def is_anonymous(self):
    return False

  def get_id(self):
    return self.username

@login_manager.user_loader
def load_user(user_id):
  print('load_user: {}'.format(user_id))
  return User(user_id)

class LoginForm(Form):
  username = StringField('username', validators=[InputRequired()])
  password = PasswordField('password', validators=[InputRequired()])

