__author__ = 'Nicolas Tomatis'
__version__ = "Version 1.3"
__copyright__ = "Copyright 2016, PydevAr"
__email__ = "pydev.ar@gmail.com"


# ------------------------- CAMERA CONFIGURATION ------------------------------ #
USE_RASPBERRY = True
# True when used with a Raspberry, False for debug on PC.

CORRECT_VERTICAL_CAMERA = True
# Use this when camera is upside down only. Options (True/False)

CORRECT_HORIZONTAL_CAMERA = True
# Use this when camera is showing mirrored image only. Options (True/False)

# ------------------------- IMAGE CONFIGURATION ------------------------------- #
CENTER_RADIUS = 20
# Radius of circle that is detected. Unit is pixels.
# The center of the light circle must be within this radius to appear as centered.

SHOW_CENTER_CIRCLE = True
# Shows the center of the circle detected.

THRESHOLD = 230  # modificado se ajusta desde la ventana 
# Threshold of brightness of lights to be detected (Range 0: darkest - 255 brightest)

RESOLUTION = '640x480'
# Retrieves or sets the resolution at which image captures, video recordings, and previews will be captured.
# The resolution can be specified as 'WIDTHxHEIGHT', or as a string containing a commonly recognized display resolution name
# (e.g. “VGA”, “HD”, “1080p”, etc)

FRAMERATE = 30
# Retrieves or sets the framerate at which video-port based image captures, video recordings, and previews will run.
# The framerate can be specified as an int, float, Fraction, or a (numerator, denominator) tuple.

SENSOR_MODE = 0
# Retrieves or sets the input mode of the camera’s sensor.
# Valid values are currently between 0 and 7.

SHUTTER_SPEED = 0
# Retrieves or sets the shutter speed of the camera in microseconds.
# When set, the property adjusts the shutter speed of the camera, which most obviously affects the illu-
# mination of subsequently captured images. Shutter speed can be adjusted while previews or recordings
# are running. The default value is 0 (auto).

ISO = 0 
# Retrieves or sets the apparent ISO setting of the camera.
# When set, the property adjusts the sensitivity of the camera (by adjusting the analog gain and digital_gain). 
# Valid values are between 0 (auto) and 1600. The actual value used when iso is explicitly set 
# will be one of the following values (whichever is closest): 100, 200, 320, 400, 500, 640, 800.

# ---------------------------- OUTPUT FILES --------------------------------- #
ENABLE_PHOTO = False
# When set to True, photos are taken when the object appears, and is centered.

ENABLE_VIDEO = False
# When set to True, a video is taken starting when the object appears and finishes when the object
# is centered. The video takes a limited times of seconds, if that time passes, the video is cut.

RECORD_SECONDS = 30
# Number of seconds the video will last as maximum.
