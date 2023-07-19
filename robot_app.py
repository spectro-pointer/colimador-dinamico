from flask import Flask, render_template, request ,Response,jsonify,redirect, url_for
import RPi.GPIO as GPIO
import serial
import datetime
from time import sleep      # Import sleep module from time library to add delays
#from camera_pi import Camera
import os
import sys

 
app = Flask(__name__)

# Global variables definition and initialization
global AZ
# global state_capture
# global servo1
# global state_Speed
# global state_led
# global state_html
AZ = ' '
# state_capture = ' '
# state_servo = ' '
# state_Speed = ' '
# state_led = ' '
# state_html = ' '

now = datetime.datetime.now()
timeString = now.strftime("%Y-%m-%d %H:%M:%S")

global arduino
arduino = serial.Serial('/dev/ttyACM1', 9600)  # invertir 1 x 0 segun los arduinos 
servo =  serial.Serial('/dev/ttyACM0', 9600)
m36=36  # led stop 18 pin
m40= 40 # led rojo para activar el espectroscopio buton3.py
m31=16  # // velocidad motores
m18=32  # // motores/ driver onn off
m11=11  #  // UP
m12=12  #  // DOWN
m21=13  #  //  RIGHT
m22=15  #   // LEF
m50=29   # // servo -on off
m6=31   #  // led blanco
m13=33  # // laser on-off
m19=35  #  // zorrino
m26=37  #   // limpia vidrio
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(m11, GPIO.OUT)
GPIO.setup(m12, GPIO.OUT)
GPIO.setup(m21, GPIO.OUT)
GPIO.setup(m22, GPIO.OUT)
GPIO.setup(m18, GPIO.OUT)
GPIO.setup(m31, GPIO.OUT)
GPIO.setup(m50, GPIO.OUT)
GPIO.setup(m6, GPIO.OUT)
GPIO.setup(m13, GPIO.OUT)
GPIO.setup(m19, GPIO.OUT)
GPIO.setup(m26, GPIO.OUT)
GPIO.setup(m40, GPIO.OUT)
GPIO.setup(m36, GPIO.OUT)

GPIO.output(m11 , 0)
GPIO.output(m12 , 0)
GPIO.output(m21, 0)
GPIO.output(m22, 0)
GPIO.output(m18, 0)
GPIO.output(m31, 0)
GPIO.output(m50, 0)
GPIO.output(m6, 0)
GPIO.output(m13, 0)
GPIO.output(m19, 0)
GPIO.output(m26, 0)
GPIO.output(m40, 0)
GPIO.output(m36, 0)

data1=1

@app.route('/')
def index():
      
    templateData = {
      'AZ'   : AZ,
      'time' : timeString,
      
     }
    
    pin18 = GPIO.input(m18)
    if pin18 == 0:
       state_html = "Activated"
    else:
       state_html = "Deactivated"
    pin31 = GPIO.input(m6)
    if pin31 == 1:
       state_led = "ActivatedLL"
    else:
       state_led = "DeactivatedLL" 
    pin16 = GPIO.input(m31)
    if pin16 == 0:
       state_Speed = "Activated"
    else:
       state_Speed = "Deactivated"  
    pin29 = GPIO.input(m50)
    if pin29 == 1:
       servo1 = "ActivatedSS"
    else:
       servo1 = "DeactivatedSS"    
    pin40 = GPIO.input(m40)
    if pin40 == 1:
       state_capture = "Activated"
    else:
       state_capture = "Deactivated"   
      
       
    return render_template('robot.html',state_html=state_html,servo1=servo1, state_Speed=state_Speed,state_led=state_led, state_capture=state_capture, **templateData)


@app.route('/left_side')
def left_side():
    data1="LEFT"
    GPIO.output(m22 , 1)
    return jsonify({"message": "LEFT"})

@app.route('/right_side')
def right_side():
   data1="RIGHT"
   GPIO.output(m21 , 1)
   return jsonify({"message": "RIGHT"})

@app.route('/up_side')
def up_side():
   data1="FORWARD"
   GPIO.output(m11 , 1)
   
   return jsonify({"message": "UP"})

@app.route('/down_side')
def down_side():
   data1="BACK"
   GPIO.output(m12 , 1)
   return jsonify({"message": "DOWN"})

@app.route('/stop')
def stop():
   data1="STOP"
   GPIO.output(m11 , 0)
   GPIO.output(m12 , 0)
   GPIO.output(m21 , 0)
   GPIO.output(m22 , 0)
   return  jsonify({"message": "STOP"})

@app.route('/ZO_side')
def ZO():
   data1="Z+"
   servo.write("75" + '\n')
   return  jsonify({"message": "Z+"})

@app.route('/zo_side')
def zo():
   data1="Z-"
   servo.write("120" + '\n')
   return  jsonify({"message": "Z-"})

@app.route('/centro')
def centro():
   data1="centro"
   servo.write("90" + '\n' )
   return  jsonify({"message": "centro"})
   
@app.route('/enableOFF_side')
def enableOFF():
   data1="motorOFF"
   GPIO.output(m18,1)
   
   
   return jsonify({"message": "driverOFF"})
@app.route('/enableON_side')
def enableON():
   data1="motorON"
   GPIO.output(m18,0)
   
   
   return  jsonify({"message": "driverON"})
@app.route('/SpeedOFF_side')
def SeepdOFF():
   data1="Speed++"
   GPIO.output(m31,0)
   return  jsonify({"message": "speedON"})
@app.route('/SPEEDON_side')
def SeepdON():
   data1="Speed--"
   GPIO.output(m31,1)
   #sleep(1)
   return jsonify({"message": "speedOFF"})   
@app.route('/LEDoff_side')
def LEDoff():
   data1="off"
   GPIO.output(m50,0)
   return  jsonify({"message": "LEDoff"})
@app.route('/LEDon_side')
def LEDon():
   data1="on"
   GPIO.output(m50,1)
   #sleep(1)
   return jsonify({"message": "LEDon"})      
@app.route('/SERVOoff_side')
def SERVOoff():
   data1="off"
   GPIO.output(m6,0)
   return  jsonify({"message": "SERVOoff"})
@app.route('/SERVOon_side')
def SERVOon():
   data1="on"
   GPIO.output(m6,1)
   #sleep(1)
   return jsonify({"message": "SERVOon"}) 
@app.route('/captureON_side')
def captureON():
   data1="ON"
   GPIO.output(m40,1)
   GPIO.output(m36,0)
   return  jsonify({"message": "Capture_Spectro_ON"})
@app.route('/captureOFF_side')
def captureOFF():
   data1="OFF"
   GPIO.output(m40,0)
   GPIO.output(m36,1)
   return jsonify({"message": "Capture_Spectro_OFF"})     
   
@app.route('/addRegion', methods = ['GET','POST'])
def addRegion():
   if request.method == "POST":
    AZ = str(request.form["AZ"])
    returnString = AZ  
    returnString = " {}".format(AZ)
    #print(returnString)
    arduino.write(returnString +'\n' )
   pin18 = GPIO.input(m18)
   if pin18 == 0:
      state_html = "Activated"
   else:
      state_html = "Deactivated"
   pin31 = GPIO.input(m6)
   if pin31 == 1:
      state_led = "Activated"
   else:
      state_led = "Deactivated" 
   pin16 = GPIO.input(m31)
   if pin16 == 0:
      state_Speed = "Activated"
   else:
      state_Speed = "Deactivated"  
   pin29 = GPIO.input(m50)
   if pin29 == 1:
      servo1 = "Activated"
   else:
      servo1 = "Deactivated"    
   pin40 = GPIO.input(m40)
   if pin40 == 1:
      state_capture = "Activated"
   else:
      state_capture = "Deactivated"  
      
    
   return render_template('robot.html', AZ=AZ ,state_html=state_html,servo1=servo1, state_Speed=state_Speed,state_led=state_led, state_capture=state_capture) 



   

if __name__ == "__main__":
   app.run(host='0.0.0.0', port=8083, debug=True , threaded=True)