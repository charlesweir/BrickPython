
# Wrapper class for the BrickPi() structure provided with the installation.
from Motor import *
from Sensor import *
from BrickPi import *
from Scheduler import *


class BrickPiWrapper(Scheduler):
    # Takes map of port types, PORT_1 through PORT_4.
    #  E.g. BrickPiWrapper( {PORT_1: TYPE_SENSOR_ULTRASONIC_CONT} )

    global Motor, Sensor

    def __init__(self, portTypes = [] ):
        Scheduler.__init__(self)
        self.motors = { 'A': Motor(PORT_A, self), 'B': Motor(PORT_B, self), 'C': Motor(PORT_C, self), 'D': Motor(PORT_D, self) }
        self.sensors = { '1': Sensor( PORT_1 ), '2': Sensor( PORT_2 ), '3': Sensor( PORT_3 ), '4': Sensor( PORT_4 ) }
        BrickPiSetup()  # setup the serial port for sudo su communication

        for port in portTypes:
            BrickPi.SensorType[port] = portTypes[port]
        BrickPiSetupSensors()       #Send the properties of sensors to BrickPi

    def motor( self, which ):
        return self.motors[which]

    def sensor( self, which ):
        return self.sensors[which]

    def update(self):
        global BrickPi
        for motor in self.motors.values():
            BrickPi.MotorEnable[motor.port] = int(motor.enabled())
            BrickPi.MotorSpeed[motor.port] = motor.power()

        # Updates sensor readings, motor locations, and motor power settings.
        # Takes about 6ms.
        BrickPiUpdateValues()

        for motor in self.motors.values():
            position = BrickPi.Encoder[motor.port]
            if not isinstance( position, ( int, long ) ):  # For mac
                position = 0
            motor.updatePosition( position )

        for sensor in self.sensors.values():
            value = BrickPi.Sensor[sensor.port]
            if not isinstance( value, ( int, long ) ):  # For mac
                value = 0
            sensor.updateValue( value )


    def updaterCoroutine(self):
        while True:
            self.update()
            yield


