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
        self.pixy.mode = 'SIG1'
        self.initialize()
        self.state, self.foundTrash, self.remainingTrash, self.sensorResult, self.halt = (None for i in range(5))
        # pixy cam is 320 by 200, and it measures coordinates starting from (0, 0) in the top left.
        self.GRABBER_CENTROID = (160, 170)
        self.GRABBER_DIMS = (100, 20) # TODO: these grabber constants are completely arbitrary

    def initialize(self):
        self.state = "looking for trash"
        self.foundTrash = []
        self.remainingTrash = ['blue']
        self.sensorResult = None
        self.halt = False  # emergency stop

    def sense(self):
        trashList = []

        # do thing. should fill with 'TrashObject' objects

        seesTrash = len(trashList) > 0

        # checks if any of the discovered trash objects are within the grabber's grasp
        withinGrabber = None
        if seesTrash:
            for trash in trashList:
                if withinRect(self.GRABBER_CENTROID, self.GRABBER_DIMS, trash.x, trash,y):
                    withinGrabber = True
        if withinGrabber is None:
            withinGrabber = False


        # read for dumpster

        dumpsterX = -1


        foundDumpster = dumpsterX >= 0

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
            if("""trash within range"""):
                s.state = "grabbing trash"
                s.grabTrash()
            else:
                s.fineTunePosition()
        else:
            s.wander()

    def wander(s):
        if s.mainBot.readDistance()<30:
            s.mainBot.turnLeft(10)
            leftDistance = s.mainBot.readDistance()
            s.mainBot.turnRight(10)
            s.mainBot.turnRight(10)
            rightDistance = s.mainBot.readDistance

            if(leftDistance > rightDistance):
                s.mainBot.turnLeft(10)
                s.mainBot.turnLeft(10)
        else:
            s.mainBot.forward(10)

    def transportTrash(s):
        s.pixy.mode = 'SIG2'
        floorReflectance = s.mainBot.readReflect()
        if floorReflectance>20:
            s.state == "releasing trash"




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