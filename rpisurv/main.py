from backup import upload_jpeg_file
from motion import MotionDetector
import os.path
from PIL import Image
from picamera import PiCamera
from picamera.array import PiRGBArray
from sendmail import MotionNotifier
import time
import yaml

with open('settings.yaml') as f:
  settings = yaml.load(f)
  print str(settings)

camera_settings = settings['camera']
camera = PiCamera()
camera.hflip = True
camera.vflip = True
camera.resolution = tuple(camera_settings['resolution'])
camera.framerate = camera_settings['fps']
raw_capture = PiRGBArray(camera, size=tuple(camera_settings['resolution']))

motion_detector = MotionDetector(settings['motion'])
motion_notifier = MotionNotifier(settings['notification'])

time.sleep(camera_settings['warmup_time'])

print('Surveilling')

image_count = 0

for frame in camera.capture_continuous(
    raw_capture,
    format='bgr',
    use_video_port=True):
  if motion_detector.detect_motion(frame.array):
    print('*** MOTION DETECTED ***')
    motion_notifier.send_notification()
    img = Image.fromarray(frame.array, 'RGB')
    filename = os.path.join(
        settings['backup']['output_path'],
        'motion{0:04d}.jpg'.format(image_count))
    img.save(filename)
    upload_jpeg_file(filename)
    image_count += 1

  raw_capture.truncate(0)

