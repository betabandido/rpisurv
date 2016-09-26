from flask import redirect

from . import google_oauth, oauth2

@google_oauth.route('/')
def index():
  return redirect(oauth2.authorize_url('/'))

