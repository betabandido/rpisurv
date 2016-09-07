import cv2
import imutils
from PIL import Image

class DummyInspector:
  def dump(self, frame, step):
    pass

def index_generator():
  i = 0
  while True:
    yield i
    i += 1

class BasicInspector:
  generators = {}

  def generate_filename(self, step):
    if step not in self.generators:
      self.generators[step] = index_generator()
    gen = self.generators[step]
    return 'img-{}-{}.jpg'.format(step, next(gen))

  def dump(self, frame, step):
    img = Image.fromarray(frame, 'L')
    img.save(self.generate_filename(step))

class MotionDetector:
  def __init__(self, settings, inspector=DummyInspector()):
    self.delta_threshold = settings['delta_threshold']
    self.min_area = settings['min_area']
    self.resize_width = settings['resize_width']
    self.inspector = inspector

    self.avg = None

  def detect_motion(self, frame):
    frame = imutils.resize(frame, self.resize_width)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0) # TODO add setting
    self.inspector.dump(gray, 'gray')

    if self.avg is None:
      self.avg = gray.copy().astype('float')
      return False

    cv2.accumulateWeighted(gray, self.avg, 0.5)
    delta = cv2.absdiff(gray, cv2.convertScaleAbs(self.avg))
    self.inspector.dump(delta, 'delta')

    threshold = cv2.threshold(delta, self.delta_threshold, 255, cv2.THRESH_BINARY)[1]
    threshold = cv2.dilate(threshold, None, iterations=2)
    self.inspector.dump(threshold, 'threshold')
    (cnts, _) = cv2.findContours(threshold.copy(),
        cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    motion_detected = False

    for c in cnts:
      print('ca:{}'.format(cv2.contourArea(c)))
      if cv2.contourArea(c) < self.min_area:
        continue
      motion_detected = True

    return motion_detected

if __name__ == '__main__':
  from . import settings
  import argparse
  from numpy import array
  parser = argparse.ArgumentParser()
  parser.add_argument('input_images',
      nargs='+',
      help='Input images')
  args = parser.parse_args()
  detector = MotionDetector(settings['motion'], inspector=BasicInspector())
  for fname in args.input_images:
    img = array(Image.open(fname))
    motion = detector.detect_motion(img)
    print('Motion: {}'.format(motion))

