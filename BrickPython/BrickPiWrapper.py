# Wrapper class for the BrickPi() structure provided with the installation.
#
# Copyright (c) 2014 Charles Weir.  Shared under the MIT Licence.

from Motor import Motor
from Sensor import Sensor
from BrickPi import *
from Scheduler import Scheduler


class BrickPiWrapper(Scheduler):
    '''
    This extends the Scheduler with functionality specific to the BrickPi

    The constructor takes a map giving the sensor type connected to each port: PORT_1 through PORT_4.
        E.g. BrickPiWrapper( {PORT_1: TYPE_SENSOR_ULTRASONIC_CONT} )

    Motors and sensors are identified by their port names: motors are A to D; sensors 1 to 5.
    '''
    def __init__(self, portTypes = [] ):
        Scheduler.__init__(self)
        self.motors = { 'A': Motor(PORT_A, self), 'B': Motor(PORT_B, self), 'C': Motor(PORT_C, self), 'D': Motor(PORT_D, self) }
        self.sensors = { '1': Sensor( PORT_1 ), '2': Sensor( PORT_2 ), '3': Sensor( PORT_3 ), '4': Sensor( PORT_4 ) }
        BrickPiSetup()  # setup the serial port for communication

        for port in portTypes:
            BrickPi.SensorType[port] = portTypes[port]
        BrickPiSetupSensors()       #Send the properties of sensors to BrickPi

        self.setUpdateCoroutine( self.updaterCoroutine() )

    def motor( self, which ):
        '''Answers the corresponding motor, e.g. motor('A')
        '''
        return self.motors[which]

    def sensor( self, which ):
        '''Answers the corresponding sensor, e.g. sensor('1')
        '''
        return self.sensors[which]

    def update(self):
        # Communicates with the BrickPi processor, sending current motor settings, and receiving sensor values.
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
        # Coroutine to call the update function.
        while True:
            self.update()
            yield


