import os.path
import yaml

basepath = os.path.dirname(os.path.realpath(__file__))
with open(os.path.join(basepath, 'settings.yaml')) as f:
  settings = yaml.load(f)

