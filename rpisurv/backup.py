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

def _find_folder(service, name):
  """Find a folder in Drive.

  Args:
    service: The Drive service object.
    name: The folder name.

  Returns:
    The folder object.
  """
  result = service.files().list(
      q="name='{0}' and mimeType='{1}' and trashed=false".format(
        name,
        'application/vnd.google-apps.folder'),
      spaces='drive',
      fields='files(id)').execute()
  return result['files']

def _create_folder(service, name):
  """Create a folder in Drive.

  Args:
    service: The Drive service object.
    name: The folder name.

  Returns:
    The folder object.
  """
  folder_metadata = {
    'name': name,
    'mimeType': 'application/vnd.google-apps.folder'
  }
  folder = service.files().create(
      body=folder_metadata,
      fields='id').execute()
  return folder

def _create_unique_folder(service, name):
  """Create a folder in Drive only if it does not exist yet.

  If the folder already exists, this method returns the folder object.

  Args:
    service: The Drive service object.
    name: The folder name.

  Returns:
    The folder object for the created or existing folder.
  """
  files = _find_folder(service, name)
  if len(files) == 1:
    return files[0]

  if len(files) != 0:
    raise Exception('Duplicated folder name')

  return _create_folder(service, name)

def upload_jpeg_file(filename):
  """Uploads a JPEG file to Drive.

  The file will be placed in a folder for better organization. The folder name
  is the current date and hour. That means all the files uploaded within the
  same hour will be uploaded to the same folder.

  Args:
    filename: Name of the file to upload.
  """
  service = _build_service(get_credentials())
  folder_name = datetime.now().strftime('D%d-%m-%yT%I%p')
  folder = _create_unique_folder(service, folder_name)

  print('Uploading image to folder ID: {0}'.format(folder['id']))
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

