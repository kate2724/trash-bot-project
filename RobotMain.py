from ev3dev2.motor import OUTPUT_A, OUTPUT_B, OUTPUT_C, OUTPUT_D
from ev3dev2.sensor import INPUT_1, INPUT_2, INPUT_3, INPUT_4
from ev3dev2.display import Display
from ev3dev2.sensor import Sensor
from ev3dev2.port import LegoPort
from SturdyBotHW3Starter import SturdyBot
import time

from dataclasses import dataclass

class TrashBot:
    def __init__(self):
        config = {'left-motor':OUTPUT_C, 'right-motor': OUTPUT_B, "medium-motor":OUTPUT_D, "color-sensor":INPUT_1,
                  "gyro-sensor":INPUT_2, "ultra-sensor":INPUT_3}
        self.mainBot = SturdyBot('mainBot', config)
        self.pixy = Sensor(INPUT_1)
        self.initialize()
        self.state, self.foundTrash, self.remainingTrash, self.sensorResult, self.halt = (None for i in range(5))
        # pixy cam is 320 by 200, and it measures coordinates starting from (0, 0) in the top left.
        self.GRABBER_CENTROID = (160, 170)
        self.GRABBER_DIMS = (100, 20) # TODO: these grabber constants are completely arbitrary
        self.grabber_hmap = linearMap(min_in=-160, max_in=160, min_out=-5, max_out=5)
        self.grabber_vmap = linearMap(min_in=-30, max_in=30, min_out=-5, max_out=5, inverse=True)
        self.PIXY_TRASH_MODE = "SIG1"
        self.PIXY_DUMPSTER_MODE = "SIG2"

    def initialize(self):
        self.state = "looking for trash"
        self.pixy.mode = self.PIXY_TRASH_MODE
        self.foundTrash = []
        self.remainingTrash = ['blue']
        self.sensorResult = None
        self.halt = False  # emergency stop

    def sense(s):
        trashList = []
        if s.pixy.mode == s.PIXY_TRASH_MODE:
            # should fill with 'TrashObject' objects based on objects camera can see.
            # as we currently understand it, the lego API only allows the pixycam to report one
            # detected object at a time, so in practice, this list is always either empty or len 1
            x = s.pixy.value(1)
            y = s.pixy.value(2)
            color = "blue"  # ideally, the pixycam would find trash objects of multiple colors,
                            # recognize their colors by their signature, and report the color here.
                            # in practice, we're only detecting blue objects.
            if x > 0 or y > 0:
                # I'm assuming here that pixy will report x, y == 0, 0 if no object is found
                # TODO: check this assumption
                trashList.append(TrashObject(color, x, y))
        seesTrash = len(trashList) > 0

        # checks if any of the discovered trash objects are within the grabber's grasp
        withinGrabber = None
        if seesTrash:
            for trash in trashList:
                if withinRect(s.GRABBER_CENTROID, s.GRABBER_DIMS, trash.x, trash.y):
                    withinGrabber = True
        if withinGrabber is None:
            withinGrabber = False

        dumpsterX = -1
        if s.pixy.mode == s.PIXY_DUMPSTER_MODE:
            dumpsterX = s.pixy.value(1)
        foundDumpster = dumpsterX > 0

        return SensorReading(seesTrash, withinGrabber, tuple(trashList), foundDumpster, dumpsterX)

    def run(s, time_limit):
        s.initialize()
        startTime = time.time()
        elapsedTime = 0.0
        while elapsedTime < time_limit and len(s.remainingTrash) > 0 and not s.halt:
            s.sensorResult = s.sense()
            s.cleanUpStep()
            elapsedTime = time.time() - startTime
            if s.mainBot.bttn.backspace:
                s.halt = True
        if len(s.remainingTrash) == 0:
            print("success")
        else:
            print("timeout")
        s.mainBot.stop()

    def cleanUpStep(s):
        if s.state == "looking for trash":
            s.searchForTrash()
        elif s.state == "grabbing trash":
            s.grabTrash()
        elif s.state == "transporting trash":
            s.transportTrash()
        elif s.state == "releasing trash":
            s.releaseTrash()

    def searchForTrash(s):
        if s.sensorResult.seesTrash:

        if s.sensorResult.foundTrash:
            # come back to this
            if s.sensorResult.withinGrabber:
                s.state = "grabbing trash"
                s.grabTrash()
            else:
                s.fineTunePosition()
        else:
            s.wander()

    def wander(s):
        if s.mainBot.readDistance() < 30:
            s.mainBot.turnLeft(10)
            leftDistance = s.mainBot.readDistance()
            s.mainBot.turnRight(10)
            s.mainBot.turnRight(10)
            rightDistance = s.mainBot.readDistance()

            if leftDistance > rightDistance:
                s.mainBot.turnLeft(10)
                s.mainBot.turnLeft(10)
        else:
            s.mainBot.forward(10)

    def transportTrash(s):
        flagFound= False
        floorReflectance = s.mainBot.readReflect()
        reachedDumpster = floorReflectance>20
        if reachedDumpster:
            s.state = "releasing trash"
            s.releaseTrash()
        else:
            originalAngle = s.mainBot.readGyroAngle()
            currentAngle = s.mainBot.readGyroAngle()
            while abs(originalAngle - currentAngle)<359 and flagFound==False:
                s.mainBot.turnRight(4)
                currentAngle = s.mainBot.readGyroAngle()
                s.sense()
                # dumpsterLocation = s.sensorResult.dumpsterX
                if(s.sensorResult.foundDumpster):
                    flagFound = True
            if s.sensorResult.foundDumpster:
                s.goToDumpster(s.sensorResult.dumpsterX)
            else:
                s.wander()

    def fineTunePosition(s):
        # this method will only be called when the trash isn't already within the grabber's claw
        # it should also only be called when there is definitely a trash object (trashList not empty)
        trash = s.sensorResult.trashList[0]
        grabber_x, grabber_y = s.GRABBER_CENTROID

        horizontal_diff = (trash.x - grabber_x)  # this is negative when the bot needs to turn left
        vertical_diff = (trash.y - grabber_y)  # this is negative when the bot needs to drive forward
        horizontal_impulse = s.grabber_hmap(horizontal_diff)  # maps negatives to negatives
        vertical_impulse = s.grabber_vmap(vertical_diff)  # maps negatives to positives

        # if the left motor < power than right motor, then bot turns left.
        # so, if horizontal_impulse is negative, these eqns give left_speed < right_speed
        left_speed = vertical_impulse + horizontal_impulse
        right_speed = vertical_impulse - horizontal_impulse

        s.mainBot.curve(left_speed, right_speed)

        # want to minimize abs(trash.x - grabber_x) (and y).
        # can minimize x's by turning left or right
        # can minimize y's by driving forward or back
        # should slow down as it approaches the correct position
        # should tend towards overshooting?

    def goToDumpster(s, dumpLocation):
        pass

    def releaseTrash(s):
        s.mainBot.pointerTurnBy(100, speed=20)
        s.state = "looking for trash"
        s.pixy.mode = s.PIXY_TRASH_MODE

    def grabTrash(s):
        s.mainBot.pointerTurnBy(-100, speed=20)
        s.state = "transporting trash"
        s.pixy.mode = s.PIXY_DUMPSTER_MODE

def withinRect(centroid, dims, x, y):
    if centroid[0] + dims[0] > x:
        return False
    if centroid[0] - dims[0] < x:
        return False
    if centroid[1] + dims[1] > y:
        return False
    if centroid[1] + dims[1] < y:
        return False
    return True
    # jesus this is the worst possible way to evaluate this

def linearMap(min_in, max_in, min_out, max_out, inverse=False):
    def map(x):
        if x <= min_in:
            input_distance = 0
        elif x >= max_in:
            input_distance = 1
        else:
            input_distance = (x - min_in) / (max_in - min_in)
        output_range = max_out - min_out
        if inverse:
            return max_out - input_distance * output_range
        else:
            return min_out + input_distance * output_range
    return map

@dataclass
class SensorReading:
    seesTrash: bool
    withinGrabber: bool
    trashList: tuple
    foundDumpster: bool
    dumpsterX: int

@dataclass
class TrashObject:
    color: str
    x: int
    y: int

    # def setup(time_limit):
    #     startTime = time.time()
    #     elapsedTime = 0.0
    #
    #     while elapsedTime < time_limit:
    #         step()
    #         elapsedTime = time.time() - startTime
    #         light = mainBot.readReflect()
    #         print("light", light)
    #         if light >= 10:
    #             print("Success! elapsed time:", elapsedTime)
    #             mainBot.stop()
    #             mainBot.snd.speak("found color")
    #             break
    #     if elapsedTime >= time_limit:
    #         mainBot.stop()
    #         print("Failure. ran out of time (limit", time_limit, "seconds")
    #         mainBot.snd.speak("I failed :(")
    #     mainBot.stop()
    #
    # def step():
    #     mainBot.forward(10)
    #
    # setup(20)

b = TrashBot()
b.run(60)