
__author__ = 'Nicolas Tomatis'
__version__ = "Version 1.3"
__copyright__ = "Copyright 2016, PydevAr"
__email__ = "pydev.ar@gmail.com"

# Configuration options
#from config import *
from utils import *
import struct

PRA_DEFAULT = 0xFF
PRB_DEFAULT = 0xFA
ADDITIONAL_BYTES = 5

# Constants to be defined.
DEBUG = False  # Use for developers.
SIZE = tuple([int(s) for s in RESOLUTION.split('x') if s.isdigit()])  # Camera resolution in (x, y)
#CR = CENTER_RADIUS #= CR
SHOW_IMAGE = True  # View the camera.
entrada = 40 
# Python libraries
import time
import cv2
import sys
import datetime
import serial
import io
import os
import numpy as np
from flask import Response
import threading

lock = threading.Lock()

import socket
import time

# Global variable to store the list of all light points seen in the last 30 seconds
all_light_points = []
oldTime = time.time()

# Threshold for proximity
proximity_threshold = 10  # Adjust this value based on your requirements


teensy_servidor_ip = "192.168.1.100"  # Dirección IP del Teensy servidor
teensy_servidor_puerto = 8888  # Puerto del Teensy servidor

pc_servidor_ip = "192.168.1.181"
pc_servidor_puerto = 8888

def nothing(a):
    pass

#cv2.imshow("b_clone", b_frame)
#cv2.namedWindow('threshold')                          ### gustavo
#cv2.createTrackbar('TH','threshold',50,255,nothing)  ### gustavo
 
#while not key == ord('q'):
TH = cv2.getTrackbarPos('TH','threshold')        ### gustavo 
upper_white = np.array([TH], dtype=np.uint8)  ### gustavo

#try:
#    arduino = serial.Serial('/dev/ttyACM0', 115200) ### gustavo
#except:
#    arduino = serial.Serial('/dev/ttyACM1', 115200) ### gustavo


# FOURCC = cv2.cv.CV_FOURCC(*'XVID') #Deprecated
FOURCC = cv2.VideoWriter_fourcc(*'XVID')

if not USE_RASPBERRY:
    GPIO = None
else:
    try:
        # Raspberry Pi Library
        import RPi.GPIO as GPIO

        from picamera.array import PiRGBArray
        from picamera import PiCamera
        PiCamera.ISO = 100
    except ImportError:
        print("Error: picamera module not recognized. Make sure you are using a Raspberry.")
        print("Also make sure that you have installed the following module: pip install picamera[array]")
        sys.exit(0)

def create_payload(cx, cy, Tx, Ty, visible):
    # The format string '<2i?' indicates:
    # '<' - little-endian,
    # '2i' - two integers,
    # '?' - one boolean value.
    # Adjust the endianness and format according to your needs.
    payload = struct.pack('<4i?', cx, cy, Tx, Ty, visible)
    return payload
	
def encode(packet_id, payload):
    # Calculate the checksum by summing all the bytes in the payload
    checksum = sum(payload) & 0xFF  # Ensure checksum is a single byte

    # Construct the packet with the preamble, packet ID, length, payload, and checksum
    packet = bytearray([PRA_DEFAULT, PRB_DEFAULT, packet_id, len(payload)]) + bytearray(payload) + bytearray([checksum])
    
    return packet

def set_up_leds():
    """
    Configures leds as output
    And creates a dictionary with leds configured by HW.
    """
    global available_leds

    if USE_RASPBERRY:
        # BCM convention is to be used.
        GPIO.setmode(GPIO.BOARD)

        # This tells Python not to print GPIO warning messages to the screen.
        GPIO.setwarnings(False)

    # Pins sorted with NAMES.
    available_leds = {
        "LED_YELLOW": 12,
        "LED_RED": 16,
        "LED_G_RIGHT": 18,
        "LED_G_LEFT": 11,
        "LED_G_UP": 13,
        "LED_G_DOWN": 15,
 	"LED_STOP":36  # gustavo
    }
    if USE_RASPBERRY:
        for led in available_leds.values():
            if DEBUG:
                print("led %i is configured as output" % led)
            GPIO.setup(led, GPIO.OUT)
            GPIO.setup(entrada, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # gustavo
		
            

def led_action(led, status):
    """
    Function to turn on/off the leds
    :param led = number of GPIO port
    :param status = string 'on'/'off'
    :return 0 when correctly, -1 when error.
    """
    if DEBUG:
        print(led, status)
    if led not in available_leds.values():
        print("Led not found:", led)
        return -1

    if USE_RASPBERRY:
        if status == "on":
            GPIO.output(led, GPIO.HIGH)
        elif status == "off":
            GPIO.output(led, GPIO.LOW)
        else:
            print("Unknown command:", status)
    return 0


def blink(led):
    """
    A led blinks for .5ms
    """
    led_action(led, "on")
    time.sleep(.5)
    led_action(led, "off")


def sequence_test():
    """
    This function is used only to test the leds of the Raspberry Pi Board
    """
    global available_leds
    print(sequence_test.__doc__)
    print("yellow led will blink...")
    blink(available_leds["LED_YELLOW"])

    print("now red led will blink...")
    blink(available_leds["LED_RED"])
    blink(available_leds["LED_STOP"]) # gustavo
    print("now the green led will blink in clockwise...")
    blink(available_leds["LED_G_UP"])
    blink(available_leds["LED_G_RIGHT"])
    blink(available_leds["LED_G_DOWN"])
    blink(available_leds["LED_G_LEFT"])

    print("The sequence has concluded.")

def camera_attr(camera=None,stream=None):
    if PiCamera is type(camera):
        time.sleep(2)
        camera.resolution         = RESOLUTION
        camera.framerate          = FRAMERATE
        camera.sensor_mode        = SENSOR_MODE
        camera.shutter_speed      = SHUTTER_SPEED
        camera.iso                = ISO
        stream = PiRGBArray(camera, size=SIZE)
        time.sleep(0.1)  # allow the camera to warmup

    return camera,stream

def set_up_camera():
    """
    Initializes Raspberry Pi Camera.
    :returns: (camera, stream)
    """
    print("Press 2 to exit, 3 to stop, 4 to continue")
    try:
        camera = PiCamera()
#        camera.roi (0.5,0.5,0.25,0.25)
        stream = PiRGBArray(camera, size=SIZE)
        camera,stream = camera_attr(camera,stream)
    except:
        print("Error with Raspberry Pi Camera")
        sys.exit(0)
    return camera, stream

def capture_frame(camera, stream):
    """
    Captures Current Frame
    This function should be called inside a loop.
    :returns: frame"""
    frame = None
    try:
        camera.capture(stream, format='bgr', use_video_port=True)
        frame = stream.array
    except:
        print("Error with camera.capture")
    return frame


def wait_key():
    """
    Waits for a key interruption for 1 ms.
    It should be used to show current frame.
    :key 1: Program exits.
    :key 2: The main loop breaks.
    :key 3: The program is paused.
    :key 4: The program is continued.
    """
    keypressed = cv2.waitKey(1) & 0xFF
    if keypressed == ord('1'):
        print("The program is exited by Key Interruption.")
        sys.exit()
    elif keypressed == ord('2'):
        cv2.destroyAllWindows()
        return "break"
    elif keypressed == ord('3'):
        while keypressed != ord('4'):
            keypressed = cv2.waitKey(1) & 0xFF
    return ""


def create_coordinates(image):

    cv2.line(image, (0, int(SIZE[1]/2)), (int(SIZE[0]), int(SIZE[1]/2)), (255, 0, 0), 1)
    cv2.line(image, (int(SIZE[0]/2), 0), (int(SIZE[0]/2), int(SIZE[1])), (255, 0, 0), 1)
    cv2.circle(image, (int(SIZE[0]/2), int(SIZE[1]/2)), CENTER_RADIUS, (80, 80, 200), 1)
    timestamp = datetime.datetime.now()
    cv2.putText(image, timestamp.strftime( "%I:%M:%S%p"), (10, image.shape[0] - 10),
    cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)
    if  GPIO.input(entrada) == GPIO.HIGH:
        cv2.putText(image, ( "AUTOMATICO"), (10, image.shape[0] - 20),
        cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 255, 0), 1)
    else:
        cv2.putText(image, ( "Track Manual"), (10, image.shape[0] - 20),
        cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)
    return image


def show_center(image, cx, cy):
    cv2.circle(image, (cx, cy), int(CENTER_RADIUS/4), (80, 200, 80), -1) # -1 hace  el relleno del circulo
    return image

def show_number_at_position(image, number, cx, cy):
    """
    Show a number at a given position on the image.
    """
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.5
    font_thickness = 1
    font_color = (0, 0, 255)  # White color for the text

    cv2.putText(image, str(number), (cx, cy), font, font_scale, font_color, font_thickness, cv2.LINE_AA)

    return image


def camera_test():
    """
    This function is used only to test the Picamera of the Raspberry Pi Board
    """
    camera, stream = set_up_camera()
    while True:
        frame = capture_frame(camera, stream)
        if frame is None:
            cv2.destroyAllWindows()
            break

 #       cv2.imshow("image", frame)

        if wait_key() == "break":
            break
        # reset the stream before the next capture
        stream.seek(0)
        stream.truncate()
    cv2.destroyAllWindows()


def check_quadrant(cx, cy, result):
    """
    Obtain in which quadrant the light is,
    and turn on corresponding leds:
    Green shows the positioning.
    Red shows that the camera is centered.
    """
    visible = True
	
    if cx < 0 or cy < 0:
        visible = False 

    Tx = int(SIZE[0])
    Ty = int(SIZE[1])

    payload = create_payload(cx, cy, Tx, Ty, visible)
	
    # Now you can use the payload as input for the encode function
    packet_id = 0x01  # Example packet ID
    encoded_packet = encode(packet_id, payload)

    # arduino.write(encoded_packet)  # This will print the encoded packet as a bytearray 

    # String to send
    #message = "Hello world"

    # Encode the string to bytes before sending
    #encoded_message = message.encode('utf-8')

    # Send the encoded message

    cliente = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    cliente.sendto(encoded_packet, (teensy_servidor_ip, teensy_servidor_puerto))

    # Select the top 3 points
    top_3_points = result[:3]

    # Format the message
    formatted_message = " ".join([f"Point{i + 1}: {x},{y}" for i, (x, y) in enumerate(top_3_points)])

    cliente.sendto(formatted_message.encode('utf-8'), (pc_servidor_ip, pc_servidor_puerto))
    cliente.close()

    # print(formatted_message)

    global available_leds
    if GPIO.input(entrada) == GPIO.LOW:   # funcion para el auto tracking con la activacion alta del pin entrada 40 
        led_action(available_leds["LED_G_LEFT"], "off")
        led_action(available_leds["LED_G_RIGHT"], "off")
        led_action(available_leds["LED_G_UP"], "off")
        led_action(available_leds["LED_G_DOWN"], "off")
        return
#    returnString ="{} , {}".format(cx,cy)  ### gustavo
    result = ""
#    print(returnString)                    ### gustavo

#    arduino.write(returnString.encode() + '\n'.encode())    ### gustavo
    # When no contour has been detected:
    # It turns on LED_YELLOW and returns ""
    if cx < 0 or cy < 0:
        led_action(available_leds["LED_YELLOW"], "on")
        led_action(available_leds["LED_G_LEFT"], "off")
        led_action(available_leds["LED_G_RIGHT"], "off")
        led_action(available_leds["LED_G_UP"], "off")
        led_action(available_leds["LED_G_DOWN"], "off")
        led_action(available_leds["LED_RED"], "off")
        return result
    else:
        led_action(available_leds["LED_YELLOW"], "off")

    # If the image is centered:
    # It turns on LED_RED
    if abs(cx - SIZE[0]/2) < CENTER_RADIUS and abs(cy - SIZE[1]/2) < CENTER_RADIUS:
        led_action(available_leds["LED_RED"], "on")
        led_action(available_leds["LED_STOP"],"off")  # gustavo
    else:
        led_action(available_leds["LED_RED"], "off")
        led_action(available_leds["LED_STOP"],"on")   # gustavo

    # Turns on green leds, when the contour is at the left / right
    if abs(cx - SIZE[0]/2) < CENTER_RADIUS:
        result = "x-center"
        led_action(available_leds["LED_G_LEFT"], "off")
        led_action(available_leds["LED_G_RIGHT"], "off")
    elif cx < SIZE[0]/2:
        result = "left"
        led_action(available_leds["LED_G_LEFT"], "on")
        led_action(available_leds["LED_G_RIGHT"], "off")
    elif cx > SIZE[0]/2:
        result = "right"
        led_action(available_leds["LED_G_LEFT"], "off")
        led_action(available_leds["LED_G_RIGHT"], "on")

    # Turns on green leds, when the contour is up / down
    if abs(cy - SIZE[1]/2) < CENTER_RADIUS:
        result += " y-center"
        led_action(available_leds["LED_G_UP"], "off")
        led_action(available_leds["LED_G_DOWN"], "off")
    elif cy < SIZE[1]/2:
        result += " up"
        led_action(available_leds["LED_G_UP"], "on")
        led_action(available_leds["LED_G_DOWN"], "off")
    elif cy > SIZE[1]/2:
        result += " down"
        led_action(available_leds["LED_G_UP"], "off")
        led_action(available_leds["LED_G_DOWN"], "on")

    # A string is returned with the corresponding place where the contour was detected
    return result


def obtain_single_contour(b_frame):
    """
    Obtain the x and y coordinates of a single contour.
    When none is found, it returns: (-1, -1)
    """
    try:
        contours, _h = cv2.findContours(b_frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    except ValueError:
        _, contours, _h = cv2.findContours(b_frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cx, cy = (-1, -1)  # When none is found, a negative coordinates are returned.
    for blob in contours:
        M = cv2.moments(blob)
        if M['m00'] != 0:
            cx, cy = int(M['m10']/M['m00']), int(M['m01']/M['m00'])
    return cx, cy


def obtain_top_contours(b_frame, n=10):
    """
    Obtain the top n x and y coordinates of the brightest contours.
    When none is found, it returns a list of (-1, -1).
    """
    try:
        contours, _h = cv2.findContours(b_frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    except ValueError:
        _, contours, _h = cv2.findContours(b_frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        return [(-1, -1)] * n

    contour_brightness = []

    for blob in contours:
        M = cv2.moments(blob)
        if M['m00'] != 0:
            cx, cy = int(M['m10'] / M['m00']), int(M['m01'] / M['m00'])
            contour_brightness.append(((cx, cy), cv2.contourArea(blob)))

    # Sort contours based on brightness
    sorted_contours = sorted(contour_brightness, key=lambda x: x[1], reverse=True)

    # Return the top n contours
    top_contours = [point for point, _ in sorted_contours[:n]]

    return top_contours


def is_point_close_with_motion_estimation(x1, y1, x2, y2, speed_x1, speed_y1, acceleration_x1, acceleration_y1, timestamp1, timestamp2, threshold):
    """
    Check if two points are close to each other based on the estimated position.
    """
    delta_t = timestamp2 - timestamp1

    # Estimate the next position based on the last known position, speed, and acceleration for both x and y
    estimated_x = x1 + speed_x1 * delta_t + 0.5 * acceleration_x1 * delta_t**2
    estimated_y = y1 + speed_y1 * delta_t + 0.5 * acceleration_y1 * delta_t**2

    # Check if the new position is close to the estimated position
    position_close = abs(x2 - estimated_x) <= threshold and abs(y2 - estimated_y) <= threshold

    return position_close

def calculate_speed_and_acceleration(last_position, current_position, last_timestamp, current_timestamp):
    """
    Calculate speed and acceleration given the last and current positions and timestamps for each coordinate (x and y).
    """
    if last_position is None or last_timestamp is None:
        return 0, 0, 0, 0  # Initial values for speed and acceleration

    delta_t = current_timestamp - last_timestamp
    if delta_t == 0:
        return 0, 0, 0, 0  # Avoid division by zero

    delta_x = current_position[0] - last_position[0]
    delta_y = current_position[1] - last_position[1]

    # Calculate speed and acceleration for both x and y coordinates
    speed_x = delta_x / delta_t
    speed_y = delta_y / delta_t

    acceleration_x = speed_x / delta_t
    acceleration_y = speed_y / delta_t

    return speed_x, speed_y, acceleration_x, acceleration_y

def process_and_store_light_points(new_points):
    global all_light_points

    # Get the current timestamp
    current_time = time.time()

    # Process new points
    for new_x, new_y in new_points:
        point_found = False

        for i, (existing_x, existing_y, existing_timestamp, existing_speed_x, existing_speed_y, existing_acceleration_x, existing_acceleration_Y)in enumerate(all_light_points):
            if is_point_close_with_motion_estimation(existing_x, existing_y, new_x, new_y, existing_speed_x, existing_speed_y, existing_acceleration_x, existing_acceleration_Y, existing_timestamp, current_time, proximity_threshold):
                # Replace old point values with the most recent and compute new acceleration and speed
                speed_x, speed_y, acceleration_x, acceleration_y = calculate_speed_and_acceleration((existing_x, existing_y), (new_x, new_y), existing_timestamp, current_time)
                print("Point %d updated: (%d, %d, %f, %f, %f, %f)" % (i + 1, new_x, new_y, speed_x, speed_y, acceleration_x, acceleration_y))
                all_light_points[i] = (new_x, new_y, current_time, speed_x, speed_y, acceleration_x, acceleration_y)
                point_found = True
                break

        if not point_found:
            # Add new point to the list with acceleration and speed = 0 for both x and y
            all_light_points.append((new_x, new_y, current_time, 0, 0, 0, 0))

    # Remove points older than 10 seconds
    all_light_points = [(x, y, timestamp, speed_x, speed_y, acceleration_x, acceleration_y) for x, y, timestamp, speed_x, speed_y, acceleration_x, acceleration_y in all_light_points if current_time - timestamp <= 3]

    # Your additional processing logic can go here

    # Print the updated list of all light points
    #print("All Light Points (last 3 seconds):", all_light_points)

# def process_and_store_light_points(new_points):
#     global all_light_points

#     # Get the current timestamp
#     current_time = time.time()

#     # Process new points
#     for new_x, new_y in new_points:
#         point_found = False

#         for i, (existing_x, existing_y, existing_timestamp, existing_speed, existing_acceleration) in enumerate(all_light_points):
#             if is_point_close_with_motion_estimation(existing_x, existing_y, new_x, new_y, existing_speed, existing_acceleration, existing_timestamp, current_time, proximity_threshold):
#                 # Replace old point values with the most recent
#                 speed, acceleration = calculate_speed_and_acceleration((existing_x, existing_y), (new_x, new_y), existing_timestamp, current_time)
#                 print("Point %d updated: (%d, %d, %f, %f)" % (i + 1, new_x, new_y, speed, acceleration))
#                 all_light_points[i] = (new_x, new_y, current_time, speed, acceleration)
#                 point_found = True
#                 break

#         if not point_found:
#             # Add new point to the list with acceleration and speed = 0
#             all_light_points.append((new_x, new_y, current_time, 0, 0))

#     # Remove points older than 10 seconds
#     all_light_points = [(x, y, timestamp, speed, acceleration) for x, y, timestamp, speed, acceleration in all_light_points if current_time - timestamp <= 3]

#     # Your additional processing logic can go here

#     # Print the updated list of all light points
#     # print("All Light Points (last 10 seconds):", all_light_points)

def record_action(place, frame, take_photo, take_video):
    """
    Take a photo when a contour is detected for the first time.
    Take a photo when a contour is centered for the first time.
    Records a video for a limited time:
        It starts when an object is found,
        It finishes when the object is centered,
        If it takes more than 30 seconds, the video is cut.
    """

    global contour_appeared, contour_centered, record_video, object_appeared, video_writer

    # If there is not contour in the image
    if place == "":
        contour_appeared = False
        contour_centered = False
    # A contour has appeared
    elif not contour_appeared:
        contour_appeared = True
        object_appeared = datetime.datetime.now()
        print("A contour has appeared.")

        if take_photo:  # The image is saved if it is explicitly told.
            # When the contour appears a photo is taken
            appeared_txt = "appeared_%s.jpg" % object_appeared.strftime('%d%m%y-%H%M%S')
            cv2.imwrite(appeared_txt, frame)

        if take_video:  # The video is saved if it is explicitly told.
            # And video starts recording
            record_video = "on"
            video_writer = cv2.VideoWriter("detection_%s.avi" % object_appeared.strftime('%d%m%y-%H%M%S'), FOURCC, 20, SIZE)

    # A contour is centered
    elif not contour_centered and place == "x-center y-center":
        contour_centered = True
        print("A contour is centered.")

        if take_photo:
            # When the contour appears a photo is taken
            centered_txt = "centered%s.jpg" % datetime.datetime.now().strftime('%d%m%y-%H%M%S')
            cv2.imwrite(centered_txt, frame)

        if take_video:
            record_video = "finish"

    if take_video:
        if record_video == "on":
            if (datetime.datetime.now() - object_appeared).seconds <= RECORD_SECONDS:
                # The video is recorded.
                video_writer.write(frame)
            else:
                # The video finishes after 30 seconds.
                print("The video has been saved.")
                video_writer.write(frame)
                video_writer.release()
                record_video = "off"
        elif record_video == "finish":
            # The video finishes when it has been centered.
            print("The video has been saved.")
            video_writer.write(frame)
            video_writer.release()
            record_video = "off"

def update_params(app,set_camera_attr_en=False):
    global SIZE, USE_RASPBERRY,CORRECT_VERTICAL_CAMERA,CORRECT_HORIZONTAL_CAMERA,CENTER_RADIUS,SHOW_CENTER_CIRCLE,ENABLE_PHOTO,ENABLE_VIDEO,RECORD_SECONDS,TH,RESOLUTION,FRAMERATE,SENSOR_MODE,SHUTTER_SPEED,ISO,camera,stream

    USE_RASPBERRY             = get_sp_config('USE_RASPBERRY',app)
    CORRECT_VERTICAL_CAMERA   = get_sp_config('CORRECT_VERTICAL_CAMERA',app)
    CORRECT_HORIZONTAL_CAMERA = get_sp_config('CORRECT_HORIZONTAL_CAMERA',app)
    CENTER_RADIUS             = get_sp_config('CENTER_RADIUS',app)
    SHOW_CENTER_CIRCLE        = get_sp_config('SHOW_CENTER_CIRCLE',app)
    ENABLE_PHOTO              = get_sp_config('ENABLE_PHOTO',app)
    ENABLE_VIDEO              = get_sp_config('ENABLE_VIDEO',app)
    RECORD_SECONDS            = get_sp_config('RECORD_SECONDS',app)
    TH                        = get_sp_config('THRESHOLD',app)

    #---------------------------------------------------------
    # Camera settings
    FRAMERATE                 = get_sp_config('FRAMERATE',app)
    SENSOR_MODE               = get_sp_config('SENSOR_MODE',app)
    SHUTTER_SPEED             = get_sp_config('SHUTTER_SPEED',app)
    ISO                       = get_sp_config('ISO',app)
    RESOLUTION                = get_sp_config('RESOLUTION',app)
    SIZE = tuple([int(s) for s in RESOLUTION.split('x') if s.isdigit()])

    if set_camera_attr_en:
        camera,stream = camera_attr(camera,stream)

def camera_loop(app):
    """
    Main Loop where the Image processing takes part.
    """
    global contour_appeared, contour_centered, record_video, outputFrame, lock, TH,camera,stream, oldTime
    update_params(app)
    camera, stream = set_up_camera()

    # Global variables initialized.
    contour_appeared = False
    contour_centered = False
    record_video = "off"
    while True:
        # TH = cv2.getTrackbarPos('TH','threshold') ### gustavo
        frame = capture_frame(camera, stream)
        if frame is None:
            cv2.destroyAllWindows()
            break

        if CORRECT_VERTICAL_CAMERA:
            # To flip camera vertically (only when necessary)
            frame = cv2.flip(frame, 0)

        if CORRECT_HORIZONTAL_CAMERA:
            # To flip camera horizontally (only when necessary)
            frame = cv2.flip(frame, 1)

        original = frame.copy()
        # Shows current frame
        # cv2.imshow("original", original)

        #################### Image processing starts ###########################

        # Change frame to grey color.
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	
        # Apply Threshold.
        _dummy, b_frame = cv2.threshold(gray_frame,TH, 255, cv2.THRESH_BINARY) ### gustavo
  #      cv2.imshow("threshold", b_frame)  ### gustavo



        # Obtain a single contour.
        cx, cy = obtain_single_contour(b_frame)
        result = obtain_top_contours(b_frame, 10)

        process_and_store_light_points(result)

        # Check in which quadrant the center of the contour is
        # And show it in the leds.
        # Returns the place where the contour is.
        place = check_quadrant(cx, cy, result)

        # Create coordinates and show them as lines.
        frame = create_coordinates(frame)


        if SHOW_CENTER_CIRCLE:
            # Show center of circle detected
            frame = show_center(frame, cx, cy)

        # Show the number of all points on the global list using the function show_number_at_position
        for i, (x, y, _, _, _, _, _) in enumerate(all_light_points):
            frame = show_number_at_position(frame, i + 1, x, y)

        # Print on the picture the real measured frame rate of the camera
        cv2.putText(frame, "FPS: %.2f" % 1/(time.time()-oldTime), (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
        oldTime = time.time()

        # Takes photos and videos when contour is detected/centered.
        record_action(place, frame, ENABLE_PHOTO, ENABLE_VIDEO)

        if SHOW_IMAGE:

            lst = list()
            lst.append((frame, "frame"))
            #The lock in necessary to not generate conflicts with thread
            with lock:
                #The left side of the tuple is the original image and the right side the processed one
                outputFrame = tuple([frame.copy(),b_frame.copy()])
            show_images(lst, SIZE)
        # cv2.imshow("frame", frame)

        if wait_key() == "break":
            break
        # reset the stream before the next capture
        stream.seek(0)
        stream.truncate()
    cv2.destroyAllWindows()

def generate(select_source):
    # grab global references to the output frame and lock variables
    global outputFrame, lock
    # loop over frames from the output stream
    while True:
        # wait until the lock is acquired
        with lock:
            # check if the output frame is available, otherwise skip
            # the iteration of the loop
            if outputFrame is None:
                continue
            # encode the frame in JPEG format
            if select_source == 'VIDEO':
                flag, encodedImage = cv2.imencode(".jpg", outputFrame[0])
            if select_source == 'THR':
                flag, encodedImage = cv2.imencode(".jpg", outputFrame[1])

        # yield the output frame in the byte format
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + encodedImage.tostring() + b'\r\n')

def show_images(lst, size):
    """
    Input: List of tuples containing frame and name.
    It shows a list of images one after the other one, with an specified size.
    Each window has it's own name, and each name must bbe different from each other.
    """
    counter = 0
    for frame, name in lst:
        resized_frame = cv2.resize(frame, size)
   #     cv2.imshow(name, resized_frame)
        cv2.moveWindow(name, int(size[0]*(counter % 4)), int((size[1]+35)*((counter / 4) % 3)))
        counter += 1

def fun():
    """
    Code to test leds and camera.
    This function doesn't need to be used in the main loop.
    """
    set_up_leds()
    sequence_test()
    camera_test()

    # when code ends, the GPIO is freed...
    GPIO.cleanup()
    print("The program ended successfully.")

if __name__ == "__main__":
    fun()
