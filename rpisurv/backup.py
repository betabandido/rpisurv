from datetime import datetime
from google import get_credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from httplib2 import Http
import os.path

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
  folder_metadata = {
    'name': datetime.now().strftime('D%d-%m-%yT%I%p'),
    'mimeType': 'application/vnd.google-apps.folder'
  }

  # try to find folder
  folder = service.files().list(
      q="name='{0}' and mimeType='{1}' and trashed=false".format(
        folder_metadata['name'],
        folder_metadata['mimeType']),
      spaces='drive',
      fields='files(id)').execute()
  if len(folder['files']) == 0:
    # create folder if it doesn't exist
    folder = service.files().create(
        body=folder_metadata,
        fields='id').execute()
  elif len(folder['files']) == 1:
    folder = folder['files'][0]
  else:
    raise Exception('Duplicated name')

  print('Folder ID: {0}'.format(folder['id']))

  media_body = MediaFileUpload(filename, mimetype='image/jpeg')
  service.files().create(
      body={'name': os.path.basename(filename), 'parents': [folder['id']]},
      media_body=media_body).execute()

if __name__ == '__main__':
  import argparse
  parser = argparse.ArgumentParser()
  parser.add_argument('--filename',
      required=True,
      help='Filename to upload')
  args = parser.parse_args()
  upload_jpeg_file(args.filename)

