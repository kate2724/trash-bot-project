from ev3dev2.motor import OUTPUT_A, OUTPUT_B, OUTPUT_C, OUTPUT_D
from ev3dev2.sensor import INPUT_1, INPUT_2, INPUT_3, INPUT_4
from ev3dev2.display import Display
from ev3dev2.sensor import Sensor
from ev3dev2.port import LegoPort
from SturdyBotHW3Starter import SturdyBot
import time

from enum import Enum, unique

class TrashBot:
    def __init__(self):
        config = {'left-motor':OUTPUT_C, 'right-motor': OUTPUT_B, "medium-motor":OUTPUT_D, "color-sensor":INPUT_1,
                  "gyro-sensor":INPUT_3, "ultra-sensor":INPUT_4}
        self.mainBot = SturdyBot('mainBot', config)
        self.pixy = Sensor(INPUT_2)
        self.state, self.foundTrash, self.sensorResult, self.halt = (None for i in range(4))
        self.originalAngle = None
        # pixy cam is 320 by 200, and it measures coordinates starting from (0, 0) in the top left.
        self.CAM_RES_X, self.CAM_RES_Y = 320, 200
        g_x, g_y = self.CAM_RES_X/2, 170  # TODO: these grabber constants are completely arbitrary. The mapping values below are based on these as well
        self.GRABBER_CENTROID = (g_x, g_y)
        self.GRABBER_DIMS = (100, 20)
        self.grabber_hmap = linearMap(min_in=-g_x, max_in=g_x, min_out=-5, max_out=5)
        self.grabber_vmap = linearMap(min_in=-(self.CAM_RES_Y - g_y), max_in=self.CAM_RES_Y - g_y, min_out=-2.5, max_out=2.5, inverse=True)
        self.dumpster_hmap = linearMap(min_in=-self.CAM_RES_X/2, max_in=self.CAM_RES_X/2, min_out=-2, max_out=2)
        self.PIXY_TRASH_MODE = "SIG1"
        self.PIXY_DUMPSTER_MODE = "SIG2"

    ##########################
    ##### DRIVER METHODS #####
    ##########################

    def run(s, time_limit):
        s.initialize()
        startTime = time.time()
        elapsedTime = 0.0
        while elapsedTime < time_limit and not s.halt:
            s.sensorResult = s.sense()
            print(str(s.sensorResult.seesTrash))
            s.cleanUpStep()
            elapsedTime = time.time() - startTime
            if s.mainBot.bttn.backspace:
                s.halt = True
        print("trash objects found:", len(s.foundTrash))
        s.mainBot.stop()

    def initialize(self):
        self.state = State.SEARCHING_FOR_TRASH
        self.pixy.mode = self.PIXY_TRASH_MODE
        self.foundTrash = []
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
            if x > 0 or y > 0 and not color in s.foundTrash:
                # I'm assuming here that pixy will report x, y == 0, 0 if no object is found
                # TODO: check this assumption
                # TODO: add heuristic to refuse to add trash objects whose on-screen area is too small
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

        # searches for the dumpster
        dumpsterX = -1
        if s.pixy.mode == s.PIXY_DUMPSTER_MODE:
            dumpsterX = s.pixy.value(1)
        foundDumpster = dumpsterX > 0

        return SensorReading(seesTrash, withinGrabber, tuple(trashList), foundDumpster, dumpsterX)

    def cleanUpStep(s):
        if s.state is State.SEARCHING_FOR_TRASH:
            s.searchForTrash()
        elif s.state is State.GRABBING_TRASH:
            s.grabTrash()
        elif s.state is State.SEARCHING_FOR_DUMPSTER:
            s.searchForDumspter()
        elif s.state is State.TRANSPORTING_TRASH:
            s.transportTrash()
        elif s.state is State.RELEASING_TRASH:
            s.releaseTrash()

    #########################
    ##### STATE METHODS #####
    #########################

    def searchForTrash(s):
        if s.sensorResult.seesTrash:
            if s.sensorResult.withinGrabber:
                s.state = State.GRABBING_TRASH
                s.grabTrash()
            else:
                s.fineTunePosition()
        else:
            s.wander()

    def grabTrash(s):
        s.mainBot.forward(0)  # equivalent to stopping
        s.mainBot.pointerTurnBy(-100, speed=20)
        s.state = State.SEARCHING_FOR_DUMPSTER
        s.originalAngle = s.mainBot.readGyroAngle()
        s.pixy.mode = s.PIXY_DUMPSTER_MODE

    def searchForDumspter(s):
        currentAngle = s.mainBot.readGyroAngle()
        if abs(s.originalAngle - currentAngle) > 359 or s.sensorResult.foundDumpster:
            s.state = State.TRANSPORTING_TRASH
        else:
            s.mainBot.turnRight(4)

    def transportTrash(s):
        floorReflectance = s.mainBot.readReflect()
        reachedDumpster = floorReflectance > 20
        if reachedDumpster:
            s.state = State.RELEASING_TRASH
            s.releaseTrash()
        else:
            if s.sensorResult.foundDumpster:
                s.goToDumpster()
            else:
                s.wander()

    def releaseTrash(s):
        s.mainBot.pointerTurnBy(100, speed=20)
        s.foundTrash.append("blue")  # ideally this would be determined dynamically
        s.state = State.SEARCHING_FOR_TRASH
        s.pixy.mode = s.PIXY_TRASH_MODE

    ##########################
    ##### HELPER METHODS #####
    ##########################

    def wander(s):
        d = s.mainBot.readDistance()
        print("distance:", d)
        if d < 60:
            s.mainBot.turnLeft(10, runTime=1)
            leftDistance = s.mainBot.readDistance()
            s.mainBot.turnRight(10, runTime=2)
            rightDistance = s.mainBot.readDistance()

            if leftDistance > rightDistance:
                s.mainBot.turnLeft(10, runTime=2)
        else:
            s.mainBot.forward(10)

    def fineTunePosition(s):
        # this method will only be called when the trash isn't already within the grabber's claw
        # it should also only be called when there is definitely a trash object (trashList not empty)
        trash = s.sensorResult.trashList[0]
        grabber_x, grabber_y = s.GRABBER_CENTROID

        horizontal_diff = (trash.x - grabber_x)  # this is negative when the bot needs to turn left
        vertical_diff = (trash.y - grabber_y)  # this is negative when the bot needs to drive forward
        horizontal_impulse = s.grabber_hmap(horizontal_diff)  # maps negatives to negatives
        vertical_impulse = s.grabber_vmap(vertical_diff) + 2.5  # maps negatives to positives

        # if the left motor < power than right motor, then bot turns left.
        # so, if horizontal_impulse is negative, these equations give left_speed < right_speed
        left_speed = vertical_impulse + horizontal_impulse
        right_speed = vertical_impulse - horizontal_impulse

        s.mainBot.curve(left_speed, right_speed)

        # want to minimize abs(trash.x - grabber_x) (and y).
        # can minimize x's by turning left or right
        # can minimize y's by driving forward or back
        # should slow down as it approaches the correct position
        # should tend towards overshooting?

        # fine-tuning is not its own state, to account for the possibility that the ball
        #  gets knocked/jostled out of the robot's field of view during the approach.
        #  this shouldn't happen often, but not using a state for this adds a little resilience

    def goToDumpster(s):
        # TODO center dumpster location in camera, move forwards until reach dumpster, recentering as necessary
        horizontal_diff = (s.sensorResult.dumpsterX - s.CAM_RES_X/2)
        horizontal_impulse = s.dumpster_hmap(horizontal_diff)
        forward_impulse = 10  # should always drive forward while returning to the dumpster

        left_speed = forward_impulse + horizontal_impulse
        right_speed = forward_impulse - horizontal_impulse
        s.mainBot.curve(left_speed, right_speed)

### End class

##########################
##### HELPER CLASSES #####
##########################


@unique
class State(Enum):
    SEARCHING_FOR_TRASH = "searching for trash"
    GRABBING_TRASH = "grabbing trash"
    SEARCHING_FOR_DUMPSTER = "searching for dumpster"
    TRANSPORTING_TRASH = "transporting trash"
    RELEASING_TRASH = "releasing trash"


class SensorReading:
    def __init__(self, seesTrash, withinGrabber, trashList, foundDumpster, dumpsterX):
        self.seesTrash = seesTrash
        self.withinGrabber = withinGrabber
        self.trashList = trashList
        self.foundDumpster = foundDumpster
        self.dumpsterX = dumpsterX


class TrashObject:
    def __init__(self, color, x, y):
        self.color = color
        self.x = x
        self.y = y

############################
##### HELPER FUNCTIONS #####
############################


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
    def lin_map(x):
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
    return lin_map

##########################
##### EXECUTING CODE #####
##########################

b = TrashBot()
b.run(60)
