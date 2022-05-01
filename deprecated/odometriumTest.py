
from odometry import Odometrium
from ev3dev2.motor import OUTPUT_A, OUTPUT_B, OUTPUT_C, OUTPUT_D
from ev3dev2.sensor import INPUT_1, INPUT_2, INPUT_3, INPUT_4
from SturdyBotHW3Starter import SturdyBot
import time

config = {'left-motor':OUTPUT_C, 'right-motor': OUTPUT_B, "medium-motor":OUTPUT_D, "color-sensor":INPUT_1,
          "gyro-sensor":INPUT_2}
mainBot = SturdyBot('mainBot', config)

odoRobot = Odometrium(left='C', right='B')

# print(odoRobot.get_current_pos())
odoRobot.move(15,15,7)
# print(odoRobot.get_current_pos())