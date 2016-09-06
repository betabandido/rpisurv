from flask import request, Response
from functools import wraps

from config import basepath, secrets, settings

def check_auth(username, password):
  """Checks authentication values.

  Args:
    username: The username.
    password: The password.
  """
  return username == secrets['username'] \
      and password == secrets['password']

def authenticate():
  """Returns a response letting users know they must authenticate.
  
  Returns:
    The response object.
  """
  return Response(
      'Could not verify your access level for that URL.\n'
      'You have to login with proper credentials', 401,
      {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
  """Wrapper to use in routes that require authentication.

  Args:
    f: route function.

  Returns:
    The decorated route function.
  """
  @wraps(f)
  def decorated(*args, **kwargs):
    auth = request.authorization
    if not auth or not check_auth(auth.username, auth.password):
      return authenticate()
    return f(*args, **kwargs)
  return decorated

