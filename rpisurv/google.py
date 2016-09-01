import oauth2client
from oauth2client import client
from oauth2client import file
from oauth2client import tools
import os.path

SCOPES = [
  'https://www.googleapis.com/auth/gmail.send',
  'https://www.googleapis.com/auth/drive.file']
basepath = os.path.dirname(os.path.realpath(__file__))
CLIENT_SECRET_FILE = os.path.join(
    basepath,
    'client_secrets.json')
APPLICATION_NAME = 'rpisurv'

def get_credentials(flags=None):
  """Gets valid user credentials from storage.

  If nothing has been stored, or if the stored credentials are invalid,
  the OAuth2 flow is completed to obtain the new credentials.

  Returns:
    Credentials, the obtained credential.
  """
  home_dir = os.path.expanduser('~')
  credential_dir = os.path.join(home_dir, '.credentials')
  if not os.path.exists(credential_dir):
    os.makedirs(credential_dir)
  credential_path = os.path.join(credential_dir,
                                 'rpisurv.json')

  store = oauth2client.file.Storage(credential_path)
  credentials = store.get()
  if not credentials or credentials.invalid:
    flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
    flow.user_agent = APPLICATION_NAME
    if flags:
      credentials = tools.run_flow(flow, store, flags)
    else: # Needed only for compatibility with Python 2.6
      credentials = tools.run_flow(flow, store)
    print('Storing credentials to ' + credential_path)
  return credentials

if __name__ == '__main__':
  print('Setting up Google credentials')
  try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
  except ImportError:
    flags = None
  
  get_credentials(flags)

