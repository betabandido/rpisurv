from apscheduler.schedulers.background import BackgroundScheduler
from backup import upload_jpeg_file
from daemon import runner
import logging
from motion import MotionDetector
import os
from picamera import PiCamera
from picamera.array import PiRGBArray
from PIL import Image
from sendmail import EventNotifier
import signal
import sys
from time import sleep

from . import basepath, settings

# APScheduler uses logging
logging.basicConfig()

camera_settings = settings['camera']

"""When set to True surveillance will stop."""
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

class SurveillanceManager:
  def __init__(self):
    print('Initializing')
    self.motion_detector = MotionDetector(settings['motion'])
    self.event_notifier = EventNotifier(settings['notification'])
    self.scheduler = BackgroundScheduler()
    self.image_count = 0

  def __enter__(self):
    return self

  def __exit__(self, type, value, traceback):
    try:
      self.stop_job_scheduler()
    except Exception, error:
      print('ERROR: {}'.format(error))

  def surveil(self):
    """Surveillance loop.

    This method implements the surveillance loop. It only returns once
    surveillance is requested to be stopped by calling terminate_surveillance().
    """
    self.schedule_alive_job()
    self.scheduler.start()

    with create_camera() as camera:
      raw_capture = PiRGBArray(camera, size=camera.resolution)
      sleep(camera_settings['warmup_time'])

      print('Surveilling')
      self.event_notifier.send_message('Surveillance started')

      for frame in camera.capture_continuous(
          raw_capture,
          format='bgr',
          use_video_port=True):
        if is_surveillance_terminated():
          break
        save_frame(frame)
        if self.motion_detector.detect_motion(frame.array):
          self.handle_motion_detection(frame)
        raw_capture.truncate(0)

    print('Exiting')
    self.event_notifier.send_message('Surveillance stopped')
    self.stop_job_scheduler()

  def schedule_alive_job(self):
    """Schedules the job that sends alive notifications.

    Args:
      scheduler: The job scheduler.
    """
    if 'alive-notification' not in settings:
      return

    self.scheduler.add_job(
        lambda: self.event_notifier.send_message('Surveillance is alive'),
        **settings['alive-notification'])

  def stop_job_scheduler(self):
    """Stops the job scheduler."""
    if self.scheduler.running:
      self.scheduler.shutdown()

  def handle_motion_detection(self, frame):
    """Handles motion detection.

    Args:
      frame: The frame to compare for movement.
    """
    try:
      print('*** MOTION DETECTED ***')
      self.event_notifier.send_motion_notification()
      img = Image.fromarray(frame.array, 'RGB')
      filename = os.path.join(
          settings['backup']['output_path'],
          'motion{0:04d}.jpg'.format(self.image_count))
      img.save(filename)
      upload_jpeg_file(filename)
      os.remove(filename)
      self.image_count += 1
    except Exception, error:
      print('ERROR: {}'.format(error))

def surveil():
  """This method creates the surveillance manager and starts surveillance."""
  try:
    with SurveillanceManager() as manager:
      manager.surveil()
  except Exception, error:
    print('ERROR: {}'.format(error))

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
    # See (https://lists.freedesktop.org/archives/systemd-devel/2014-January/016544.html)
    # However, you must ensure that when creating a DaemonContext() object, you should
    # specify detach_process=True. This is because, if python-daemon detects that it 
    # is running under a init manager, it doesn’t detach itself unless the keyword is 
    # explicitly set to True, as above (you can see the code in daemon.py). 
    # Hence, although not setting the above keyword would work under SysV Init, it doesn’t 
    # work under systemd (with Type=Forking), since the daemon doesn’t fork at all and 
    # systemd expects it to fork (and finally kills it).
    daemon_runner.daemon_context.detach_process = True
    daemon_runner.daemon_context.signal_map[signal.SIGTERM] = signal_handler
    daemon_runner.do_action()
  else:
    signal.signal(signal.SIGINT, signal_handler)
    surveil()

