from ev3dev2.motor import MediumMotor, LargeMotor, MotorSet, MoveTank, MoveSteering
from ev3dev2.motor import OUTPUT_A, OUTPUT_B, OUTPUT_C, OUTPUT_D
from ev3dev2.sensor import INPUT_1, INPUT_2, INPUT_3, INPUT_4
from ev3dev2.sensor.lego import TouchSensor, UltrasonicSensor, GyroSensor, ColorSensor
from SturdyBotHW3Starter import SturdyBot
import PotentialFieldBrain
import time
import random
import math


config = {'left-motor':OUTPUT_C, 'right-motor': OUTPUT_B, "medium-motor":OUTPUT_D}
testBot = SturdyBot('testy', config)

testBot.pointerTurnBy(20)