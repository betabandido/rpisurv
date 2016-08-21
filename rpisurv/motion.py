import cv2
import imutils

class MotionDetector:
  def __init__(self, settings):
    self.delta_threshold = settings['delta_threshold']
    self.min_area = settings['min_area']
    self.resize_width = settings['resize_width']

    self.avg = None

  def detect_motion(self, frame):
    frame = imutils.resize(frame, self.resize_width)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0) # TODO add setting

    if self.avg is None:
      self.avg = gray.copy().astype('float')
      return False

    cv2.accumulateWeighted(gray, self.avg, 0.5)
    delta = cv2.absdiff(gray, cv2.convertScaleAbs(self.avg))

    threshold = cv2.threshold(delta, self.delta_threshold, 255, cv2.THRESH_BINARY)[1]
    threshold = cv2.dilate(threshold, None, iterations=2)
    (cnts, _) = cv2.findContours(threshold.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    motion_detected = False

    for c in cnts:
      if cv2.contourArea(c) < self.min_area:
        continue
      motion_detected = True

    return motion_detected

