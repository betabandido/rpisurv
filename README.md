# rpisurv
Surveillance system based on Raspberry Pi

## Dependencies
* [oauth2client](https://github.com/google/oauth2client)
* [google-api-python-client](https://github.com/google/google-api-python-client)
* [PyYAML](http://pyyaml.org/wiki/PyYAML)

## Configuration

### Setting up Google credentials

Run the following command:
`python rpisurv/google.py --noauth_local_webserver`

Copy and paste the link in a browser and allow for the requested permissions. Then copy and paste the code that appears on the browser back into the terminal where the previous command was executed.
