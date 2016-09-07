# rpisurv
Surveillance system based on Raspberry Pi

## Dependencies

Detection daemon:
* [oauth2client](https://github.com/google/oauth2client)
* [google-api-python-client](https://github.com/google/google-api-python-client)
* [PyYAML](http://pyyaml.org/wiki/PyYAML)
* [lockfile](https://pypi.python.org/pypi/lockfile)
* [python-daemon](https://pypi.python.org/pypi/python-daemon/)
* [opencv](http://opencv.org)
* [numpy](http://www.numpy.org)
* [imutils](https://pypi.python.org/pypi/imutils)
* [picamera](http://picamera.readthedocs.io/en/latest/)
* [Pillow](http://pillow.readthedocs.io/en/latest/)
* [Advanced Python Scheduler](http://apscheduler.readthedocs.io/en/latest/)

Web interface:
* [Flask](http://flask.pocoo.org)
* [Flask-Login](https://flask-login.readthedocs.io/en/latest/)
* [Flask-WTF](https://flask-wtf.readthedocs.io/en/latest/index.html)
* [WTForms](https://wtforms.readthedocs.io/en/latest/)
* [uwsgi](http://uwsgi-docs.readthedocs.io/en/latest/)
* [nginx](http://nginx.org)

## Configuration

### Installing dependencies

`apt-get install python-opencv nginx` 

First create a virtual environment:
`virtualenv venv`

Then install all the dependencies:
```
pip install oauth2client \
  google-api-python-client \
  PyYAML \
  lockfile \
  python-daemon \
  numpy \
  imutils \
  picamera \
  Pillow \
  Flask \
  uwsgi
```

### Setting up Google credentials

Run the following command:
`python rpisurv/google.py --noauth_local_webserver`

Copy and paste the link in a browser and allow for the requested permissions. Then copy and paste the code that appears on the browser back into the terminal where the previous command was executed.
