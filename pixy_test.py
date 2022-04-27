from time import sleep

from ev3dev2.sensor import Sensor, INPUT_1
from ev3dev2.port import LegoPort


# Set LEGO port for Pixy on input port 1
in1 = LegoPort(INPUT_1)
in1.mode = 'auto'
# Wait 2 secs for the port to get ready
sleep(2)

# Connect Pixy camera
pixy = Sensor(INPUT_1)
