__author__ = 'Nicolas Tomatis'
__version__ = "Version 1.3"
__copyright__ = "Copyright 2016, PydevAr"
__email__ = "pydev.ar@gmail.com"

from tracker_lib import *
from webstreaming import *
from config import *
from utils import *


def main():
    set_up_leds()
    start_webstreaming()
    # camera_loop()

    # when code ends, the GPIO is freed...
    GPIO.cleanup()
#    print "The program ended successfully."


if __name__ == "__main__":
    main()
