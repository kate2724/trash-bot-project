
from ev3dev2.motor import MediumMotor, LargeMotor, MotorSet, MoveTank, MoveSteering
from ev3dev2.motor import OUTPUT_A, OUTPUT_B, OUTPUT_C, OUTPUT_D
from ev3dev2.sensor import INPUT_1, INPUT_2, INPUT_3, INPUT_4
from ev3dev2.sensor.lego import TouchSensor, UltrasonicSensor, GyroSensor, ColorSensor
from ev3dev2.button import Button
from ev3dev2.sound import Sound
import time


class SturdyBot(object):
    """The class to create a manager for robot"""

    # ---------------------------------------------------------------------------
    # Constants for the configDict
    LEFT_MOTOR = 'left-motor'
    RIGHT_MOTOR = 'right-motor'
    MEDIUM_MOTOR = 'medium-motor'
    LEFT_TOUCH = 'left-touch'
    RIGHT_TOUCH = 'right-touch'
    ULTRA_SENSOR = 'ultra-sensor'
    COLOR_SENSOR = 'color-sensor'
    GYRO_SENSOR = 'gyro-sensor'

    # ---------------------------------------------------------------------------
    # The default config that the program will use if no config is given
    DEFAULT_CONFIG = {ULTRA_SENSOR: INPUT_2, LEFT_TOUCH: INPUT_4,
                      COLOR_SENSOR: INPUT_3, RIGHT_TOUCH: INPUT_1,
                      LEFT_MOTOR: OUTPUT_C, RIGHT_MOTOR: OUTPUT_B,
                      MEDIUM_MOTOR: OUTPUT_D}

    # ---------------------------------------------------------------------------

    def __init__(self, name, configDict=None):
        """ Take the configuration of the robot and set up the robot
        If no configuration is given, then the robot will not set up motors
        or sensors, and the robot will fail
        """
        # super(SturdyBot, self).__init__()
        self.name = name
        self.bttn = Button()
        self.snd = Sound()

        self.tankMover = None
        self.steerMover = None
        self.mediumMotor = None
        self.leftTouch = None
        self.rightTouch = None
        self.ultraSensor = None
        self.colorSensor = None
        self.gyroSensor = None

        if configDict is None:
            configDict = self.DEFAULT_CONFIG
        # Call the method to set up the setup sensors and motors
        self.setupSensorsMotors(configDict)
        assert (self.LEFT_MOTOR in configDict) and (self.RIGHT_MOTOR in configDict)
        leftPort = configDict[self.LEFT_MOTOR]
        rightPort = configDict[self.RIGHT_MOTOR]
        self.tankMover = MoveTank(leftPort, rightPort)
        self.steerMover = MoveSteering(leftPort, rightPort)


    def setupSensorsMotors(self, configDict):
        """Method to set up all the sensors and motors based on the input configuration"""
        for item in configDict:
            port = configDict[item]
            if (item == self.LEFT_MOTOR) or (item == self.RIGHT_MOTOR):
                pass
            elif item == self.MEDIUM_MOTOR:
                self.mediumMotor = MediumMotor(port)
                self.mediumMotor.stop_action = "brake"
            elif item == self.LEFT_TOUCH:
                self.leftTouch = TouchSensor(port)
            elif item == self.RIGHT_TOUCH:
                self.rightTouch = TouchSensor(port)
            elif item == self.ULTRA_SENSOR:
                self.ultraSensor = UltrasonicSensor(port)
            elif item == self.GYRO_SENSOR:
                self.gyroSensor = GyroSensor(port)
            elif item == self.COLOR_SENSOR:
                self.colorSensor = ColorSensor(port)
            else:
                print("Error while setting the item: " + item)

    def steerMove(self, speed, heading, runTime=None):
        if (runTime is None):
            self.steerMover.on(heading, speed)
        else:
            self.steerMover.on_for_seconds(heading, speed, runTime)

    def readReflect(self):
        """read and report the reflectance value for the color sensor"""
        return self.colorSensor.reflected_light_intensity

    def readAmbient(self):
        """read and report the ambient light value for the color sensor"""
        return self.colorSensor.ambient_light_intensity

    def readColor(self):
        """read and report the color value (0 through 7, or the color strings)"""
        return self.colorSensor.color_name

    def readRGBColor(self):
        """read and report the RGB color value for the color sensor, returning it as a tuple with three numbers in it"""
        return self.colorSensor.rgb

    def readDistance(self):
        if self.ultraSensor == None:
            print("Warning: ultraSensor not connected")
        else:
            return self.ultraSensor.distance_centimeters

    def readGyroAngle(self, bounds=False):
        """If `bounds` is False, then the gyro angle is reported as-is. If `bounds` is true,
        then the gyro angle is restricted to the range 0-359, and will be converted to that
        range with modulo arithmetic."""
        if self.gyroSensor == None:
            print("Warning: gyroSensor not connected")
        else:
            if(bounds):
                return self.gyroSensor.angle % 360
            else:
                return self.gyroSensor.angle

    def readTouch(self):
        """Reports the value of both touch sensors, OR just one if only one is connected, OR
        prints an alert and returns nothing if neither is connected."""
        if self.leftTouch is not None and self.rightTouch is not None:
            return self.leftTouch.is_pressed, self.rightTouch.is_pressed
        elif self.leftTouch is not None:
            return self.leftTouch.is_pressed, None
        elif self.rightTouch is not None:
            return None, self.rightTouch.is_pressed
        else:
            print("Warning, no touch sensor connected")
            return None, None

    def calibrateWhite(self):
        """Calls the underlying calibrate_white method, which adjusts reported RGB colors
        so that they max out at the given color."""
        if self.colorSensor is not None:
            self.colorSensor.calibrate_white()
        else:
            print("Warning, no color sensor connected")
            return None

    def forward(self, speed, runTime=None):
        """Make the robot move forward with the given speed. If there is no given time,
        the robot would move forerver"""
        assert -100.0 <= speed <= 100.0
        assert self.tankMover is not None
        if runTime is None:
            self.tankMover.on(speed, speed)
        else:
            self.tankMover.on_for_seconds(speed, speed, runTime)


    def backward(self, speed, runTime=None):
        """Make the robot to move backward with the given speed"""
        # This method will call the forward method with a negative speed
        assert -100.0 <= speed <= 100.0
        assert self.tankMover is not None
        self.forward(-speed, runTime)

    def turnLeft(self, speed, runTime=None):
        """Make the robot to turn left in place with the given speed.
                If there is no given time, the robot keeps turning forever"""
        assert -100.0 <= speed <= 100.0
        assert self.tankMover is not None
        if runTime is None:
            self.tankMover.on(-speed, speed)
        else:
            self.tankMover.on_for_seconds(-speed, speed, runTime)


    def turnRight(self, speed, runTime=None):
        """Make the robot to turn right in place with the given speed.
                If there is no given time, the robot keeps turning forever"""
        assert -100.0 <= speed <= 100.0
        assert self.tankMover is not None
        if runTime is None:
            self.tankMover.on(speed, -speed)
        else:
            self.tankMover.on_for_seconds(speed, -speed, runTime)


    def stop(self):
        """Turns off the motors."""
        assert self.tankMover is not None
        self.tankMover.off()
        # Stop the medium motor as well
        if self.mediumMotor is not None:
            self.mediumMotor.stop()

    def curve(self, leftSpeed, rightSpeed, runTime=None):
        """Given speeds for left and right motors, runs the motors to make the robot travel in a curve."""
        assert self.tankMover is not None
        assert -100.0 <= leftSpeed <= 100.0
        assert -100.0 <= rightSpeed <= 100.0
        if runTime is None:
            self.tankMover.on(leftSpeed, rightSpeed)
        else:
            self.tankMover.on_for_seconds(leftSpeed, rightSpeed, runTime)


    def zeroPointer(self):
        """Turns the medium motor/pointer to the zero angle position. """
        self.mediumMotor.on_to_position(30, 0)


    def pointerTurn(self, speed=50.0, runTime=None):
        """Turns the medium moter counter-clockwise at the given speed, stopping
        after some time if a time is specified. If negative speed is input, then
        movement is clockwise."""
        assert -100.0 <= speed <= 100.0
        if runTime is None:
            self.mediumMotor.on(speed)
        else:
            self.mediumMotor.on_for_seconds(speed, runTime)


    def pointerTurnBy(self, angle, speed=50.0):
        """Given an angle, turn counter-clockwise by that many degrees (negative
        values cause clockwise turn. Speed input is optional."""
        assert -100.0 <= speed <= 100.0
        self.mediumMotor.on_for_degrees(angle, speed)


    def pointerTurnTo(self, angle):
        """Turns to the specified angle"""
        assert 0 <= angle <= 360
        self.mediumMotor.on_to_position(30.0, angle)


# Sample of how to use this
if __name__ == "__main__":
    touchyRobot = SturdyBot('Touchy')
    print("Setup done")
    for i in range(5):
        touchValues = touchyRobot.readTouch()
        print("Touch values:", touchValues)
        touchyRobot.forward(25.0, 2.0)
        touchyRobot.curve(50.0, 75.0, 1.0)
        touchyRobot.stop()

