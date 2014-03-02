# Wrapper class for the BrickPi() structure provided with the installation.
#
# Copyright (c) 2014 Charles Weir.  Shared under the MIT Licence.

from Motor import Motor
from Sensor import Sensor
import BrickPi as BP
from Scheduler import Scheduler

class BrickPiWrapper(Scheduler):
    '''
    This extends the Scheduler with functionality specific to the BrickPi

    The constructor takes a map giving the sensor type connected to each port: 1 through 5.
        E.g. BrickPiWrapper( {'1': Sensor.TYPE_SENSOR_ULTRASONIC_CONT} )

    Motors and sensors are identified by their port names: motors are A to D; sensors 1 to 5.
    '''
    def __init__(self, portTypes = {} ):
        Scheduler.__init__(self)
        self.motors = { 'A': Motor(BP.PORT_A, self), 'B': Motor(BP.PORT_B, self), 'C': Motor(BP.PORT_C, self), 'D': Motor(BP.PORT_D, self) }
        self.sensors = { '1': Sensor( BP.PORT_1 ), '2': Sensor( BP.PORT_2 ), '3': Sensor( BP.PORT_3 ), '4': Sensor( BP.PORT_4 ) }
        BP.BrickPiSetup()  # setup the serial port for communication

        for port in portTypes:
            portNum = Sensor.portNumFromId(port)
            BP.BrickPi.SensorType[portNum] = portTypes[port]
        BP.BrickPiSetupSensors()       #Send the properties of sensors to BrickPi

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
            BP.BrickPi.MotorEnable[motor.port] = int(motor.enabled())
            BP.BrickPi.MotorSpeed[motor.port] = motor.power()

        # Updates sensor readings, motor locations, and motor power settings.
        # Takes about 6ms.
        BP.BrickPiUpdateValues()

        for motor in self.motors.values():
            position = BP.BrickPi.Encoder[motor.port]
            if not isinstance( position, ( int, long ) ):  # For mac
                position = 0
            motor.updatePosition( position )

        for sensor in self.sensors.values():
            value = BP.BrickPi.Sensor[sensor.port]
            if not isinstance( value, ( int, long ) ):  # For mac
                value = 0
            sensor.updateValue( value )


    def updaterCoroutine(self):
        # Coroutine to call the update function.
        while True:
            self.update()
            yield


