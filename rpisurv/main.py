from backup import upload_jpeg_file
from daemon import runner
from motion import MotionDetector
import os
from picamera import PiCamera
from picamera.array import PiRGBArray
from PIL import Image
from sendmail import MotionNotifier
import signal
import sys
from time import sleep

from . import basepath, settings

camera_settings = settings['camera']

"""When True surveillance will stop."""
terminated = False

def terminate_surveillance():
  """Terminate surveillance."""
  global terminated
  terminated = True

def is_surveillance_terminated():
  """Returns whether surveillance must be ended.

  Returns:
    True if surveillance must be ended; False otherwise.
  """
  return terminated

def signal_handler(signal_number, stack_frame):
  """Handles termination signal by daemon runner.

  Args:
    signal_number: The signal number.
    stack_frame: The stack frame.
  """
  if signal_number in [signal.SIGTERM, signal.SIGINT]:
    terminate_surveillance()

def create_camera():
  """Creates the camera object.

  Information from the settings file is used to initialize the camera.

  Returns:
    The camera object.
  """
  camera = PiCamera()
  camera.hflip = True
  camera.vflip = True
  camera.resolution = tuple(camera_settings['resolution'])
  camera.framerate = camera_settings['fps']
  return camera

def save_frame(frame):
  """Saves a frame to a file."""
  try:
    img = Image.fromarray(frame.array, 'RGB')
    out_path = settings['app']['web_path']
    if not os.path.isabs(out_path):
      out_path = os.path.join(basepath, out_path)
    filename = os.path.join(out_path, 'static', 'latest.jpg')
    tmp_filename = '{}.part'.format(filename)
    img.save(tmp_filename, 'jpeg')
    os.rename(tmp_filename, filename)
  except Exception, error:
    print('Error saving frame: {}'.format(error))

def surveil():
  """Surveillance loop.

  This method implements the surveillance loop. It only returns once
  surveillance is requested to be stopped by calling terminate_surveillance().
  """
  print('Initializing')
  motion_detector = MotionDetector(settings['motion'])
  motion_notifier = MotionNotifier(settings['notification'])

  with create_camera() as camera:
    raw_capture = PiRGBArray(camera, size=camera.resolution)
    sleep(camera_settings['warmup_time'])

    print('Surveilling')
    image_count = 0
    for frame in camera.capture_continuous(
        raw_capture,
        format='bgr',
        use_video_port=True):
      if is_surveillance_terminated():
        break

      save_frame(frame)

      if motion_detector.detect_motion(frame.array):
        print('*** MOTION DETECTED ***')
        try:
          motion_notifier.send_notification()
          img = Image.fromarray(frame.array, 'RGB')
          filename = os.path.join(
              settings['backup']['output_path'],
              'motion{0:04d}.jpg'.format(image_count))
          img.save(filename)
          upload_jpeg_file(filename)
          os.remove(filename)
          image_count += 1
        except Exception, error:
          print('An error occurred: {}'.format(error))

      raw_capture.truncate(0)

  print('Exiting')

class Application:
  """Application class to use with daemon runner."""

  def __init__(self):
    app_settings = settings['app']
    self.stdin_path = '/dev/null'
    self.stdout_path = os.path.join(
        app_settings['out_path'],
        'out-{}.txt'.format(os.getpid()))
    self.stderr_path = os.path.join(
        app_settings['out_path'],
        'err-{}.txt'.format(os.getpid()))
    self.pidfile_path = app_settings['pidfile_path']
    self.pidfile_timeout = 5

  def run(self):
    surveil()

if __name__ == '__main__':
  import argparse
  parser = argparse.ArgumentParser()
  parser.add_argument('--no-daemon',
      dest='daemon', action='store_false', help='Do not run as a daemon')
  parser.add_argument('daemon-action',
      nargs='?', help='Daemon action')
  parser.set_defaults(daemon=True)
  args = parser.parse_args()

  if args.daemon:
    app = Application()
    daemon_runner = runner.DaemonRunner(app)
    daemon_runner.daemon_context.signal_map[signal.SIGTERM] = signal_handler
    daemon_runner.do_action()
  else:
    signal.signal(signal.SIGINT, signal_handler)
    surveil()

