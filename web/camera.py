from subprocess import call, check_call

def enable_camera():
  """Enables the camera."""
  check_call(['sudo', 'systemctl', 'start', 'rpisurv'])

def disable_camera():
  """Disables the camera."""
  check_call(['sudo', 'systemctl', 'stop', 'rpisurv'])

def set_camera_state(state):
  """Sets the camera state.

  Args:
    state: The new camera state ['on', 'off'].
  """
  if state == 'on':
    enable_camera()
  elif state == 'off':
    disable_camera()
  else:
    assert False

def is_camera_enabled():
  """Checks whether the camera is enabled.

  Returns:
    True if the camera is enabled; False otherwise.
  """
  return call(['systemctl', 'status', 'rpisurv']) == 0

def current_camera_state():
  """Returns the current camera state.

  Returns:
    'on' if the camera is enabled; 'off' otherwise.
  """
  if is_camera_enabled():
    return 'on'
  else:
    return 'off'

