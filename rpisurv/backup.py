import os.path
from google import get_credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from httplib2 import Http

def _build_service(credentials):
  """Build a Drive service object.

  Args:
    credentials: OAuth 2.0 credentials.

  Returns:
    Drive service object.
  """
  http = credentials.authorize(Http())
  return build('drive', 'v3', http=http)

def upload_jpeg_file(filename):
  service = _build_service(get_credentials())
  media_body = MediaFileUpload(filename, mimetype='image/jpeg')
  service.files().create(
      body={'name': os.path.basename(filename)},
      media_body=media_body).execute()

if __name__ == '__main__':
  import argparse
  parser = argparse.ArgumentParser()
  parser.add_argument('--filename',
      required=True,
      help='Filename to upload')
  args = parser.parse_args()
  upload_jpeg_file(args.filename)

