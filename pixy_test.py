from time import sleep
from ev3dev2.display import Display
from ev3dev2.sensor import Sensor, INPUT_1
from ev3dev2.port import LegoPort
from ev3dev2.button import Button


# EV3 Display
lcd = Display()

# Connect TouchSensor
bttn = Button()

# Set LEGO port for Pixy on input port 1
in1 = LegoPort(INPUT_1)
in1.mode = 'auto'
# Wait 2 secs for the port to get ready
sleep(2)

# Connect Pixy camera
pixy = Sensor(INPUT_1)
pixy.mode = 'SIG1'


# mode all
sig = pixy.value(1)*256 + pixy.value(0) # Signature of largest object
x_centroid = pixy.value(2)    # X-centroid of largest SIG1-object
y_centroid = pixy.value(3)    # Y-centroid of largest SIG1-object
width = pixy.value(4)         # Width of the largest SIG1-object
height = pixy.value(5)        # Height of the largest SIG1-object

# mode sig1
count = pixy.value(0)  # The number of objects that match signature 1
x = pixy.value(1)      # X-centroid of the largest SIG1-object
y = pixy.value(2)      # Y-centroid of the largest SIG1-object
w = pixy.value(3)      # Width of the largest SIG1-object
h = pixy.value(4)      # Height of the largest SIG1-object
# #
# from time import sleep
#
# from ev3dev2.display import Display
# from ev3dev2.sensor import Sensor, INPUT_1, INPUT_4
# from ev3dev2.sensor.lego import TouchSensor
# from ev3dev2.port import LegoPort
# from SturdyBotHW3Starter import SturdyBot
# from ev3dev2.button import Button
#
#
# # EV3 Display
# lcd = Display()
#
# # Connect TouchSensor
# bttn = Button()
#
# # Set LEGO port for Pixy on input port 1
# in1 = LegoPort(INPUT_1)
# in1.mode = 'auto'
# # Wait 2 secs for the port to get ready
# sleep(2)
#
# # Connect Pixy camera
# pixy = Sensor(INPUT_1)
#
# # Set mode to detect signature 1 only
# pixy.mode = 'SIG1'
#
# # Read and display data until TouchSensor is pressed
# while not bttn.backspace:
#     # Clear EV3 display
#     lcd.clear()
#     # Read values from Pixy
#     x = pixy.value(1)     # X-coordinate of centerpoint of object
#     y = pixy.value(2)     # Y-coordinate of centerpoint of object
#     w = pixy.value(3)     # Width of rectangle around detected object
#     h = pixy.value(4)     # Heigth of rectangle around detected object
#     # scale to resolution of EV3 display:
#     # Resolution Pixy while color tracking: (255x199)
#     # Resolution EV3 display: (178x128)
#     x *= 0.7
#     y *= 0.6
#     w *= 0.7
#     h *= 0.6
#     # Calculate reactangle to draw on EV3-display
#     dx = int(w/2)         # Half of the width of the rectangle
#     dy = int(h/2)         # Half of the height of the rectangle
#     xa = x - dx           # X-coordinate of top-left corner
#     ya = y + dy           # Y-coordinate of the top-left corner
#     xb = x + dx           # X-coordinate of bottom-right corner
#     yb = y - dy           # Y-coordinate of the bottom-right corner
#     # Draw rectangle on display
#     lcd.draw.rectangle((xa, ya, xb, yb), fill='black')
#     # Update display to show rectangle
#     lcd.update()