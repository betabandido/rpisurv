import base64
from datetime import datetime
from email.mime.text import MIMEText
from google import get_credentials
from googleapiclient import errors
from googleapiclient.discovery import build
from httplib2 import Http
import os.path
import yaml

from . import basepath

def _send_message(service, user_id, message):
  """Send an email message.

  Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    message: Message to be sent.

  Returns:
    Sent Message.
  """
  try:
    message = service.users().messages().send(
        userId=user_id,
        body=message).execute()
    print('Message sent: id={}'.format(message['id']))
    return message
  except errors.HttpError, error:
    print('An error occurred: {}'.format(error))

def _create_message(sender, to, subject, text):
  """Create a message for an email.

  Args:
    sender: Email address of the sender.
    to: Email address of the receiver.
    subject: The subject of the email message.
    text: The text of the email message.

  Returns:
    An object containing a base64 encoded email object.
  """
  message = MIMEText(text)
  message['to'] = to
  message['from'] = sender
  message['subject'] = subject
  return {'raw': base64.b64encode(message.as_string())}

def _build_service(credentials):
  """Build a Gmail service object.

  Args:
    credentials: OAuth 2.0 credentials.

  Returns:
    Gmail service object.
  """
  http = credentials.authorize(Http())
  return build('gmail', 'v1', http=http)

class MotionNotifier:
  def __init__(self, settings):
    with open(os.path.join(basepath, 'mail_secrets.yaml')) as f:
      doc = yaml.load(f)
      self.MAIL_FROM = doc['from']
      self.MAIL_TO = doc['to']

    self.last_time = None
    self.min_distance = settings['min_distance']

  def send_notification(self):
    curr_time = datetime.now()
    if self.last_time is not None \
        and (curr_time - self.last_time).total_seconds() < self.min_distance:
      return

    service = _build_service(get_credentials())
    msg = _create_message(
        self.MAIL_FROM,
        self.MAIL_TO,
        'Surveillance notification',
        'Motion detected at {0}'.format(str(datetime.now())))
    _send_message(service, "me", msg)

    self.last_time = curr_time

if __name__ == '__main__':
  from . import settings
  notifier = MotionNotifier(settings['notification'])
  notifier.send_notification()
  notifier.send_notification() # this one shouldn't be sent

