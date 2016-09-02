from backup import upload_jpeg_file
from daemon import runner
from motion import MotionDetector
import os
from picamera import PiCamera
from picamera.array import PiRGBArray
from PIL import Image
from sendmail import MotionNotifier
from time import sleep
import yaml

basepath = os.path.dirname(os.path.realpath(__file__))
with open(os.path.join(basepath, 'settings.yaml')) as f:
  settings = yaml.load(f)
  print str(settings)

camera_settings = settings['camera']

def create_camera():
  camera = PiCamera()
  camera.hflip = True
  camera.vflip = True
  camera.resolution = tuple(camera_settings['resolution'])
  camera.framerate = camera_settings['fps']
  return camera

terminated = False

def terminate_daemon(signal_number, stack_frame):
  global terminated
  terminated = True

class Application:
  def __init__(self):
    app_settings = settings['app']
    self.stdin_path = '/dev/null'
    self.stdout_path = app_settings['out_path']
    self.stderr_path = app_settings['err_path']
    self.pidfile_path = app_settings['pidfile_path']
    self.pidfile_timeout = 5

  def run(self):
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
        global terminated
        if terminated:
          break

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
            print('An error occurred: {0}'.format(error))

        raw_capture.truncate(0)

    print('Exiting')
    # This seems necessary to kill threads created by libbcm_host
    os.killpg(os.getpgid(0), signal.SIGKILL)

if __name__ == '__main__':
  import signal
  app = Application()
  daemon_runner = runner.DaemonRunner(app)
  daemon_runner.daemon_context.signal_map[signal.SIGTERM] = terminate_daemon
  daemon_runner.do_action()

