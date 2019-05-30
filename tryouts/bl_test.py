# serial port is controlled by Jelmer at this moment
import ow
from time import sleep
(ow.init('localhost:4304'))
sensorlist = ow.Sensor('/').sensorList()

# turn off all the boards
for sensor in sensorlist:
    if sensor.type == "DS2408":
        print(sensor)
        sensor.PIO_BYTE = b'00000000' # lsb is PIO0 msb is PIO7
        sensor.PIO_BYTE = b'01000000'  # lsb is PIO0 msb is PIO7
        print(sensor.sensed_BYTE)

# put this board into bootloader mode
for sensor in sensorlist:
    if sensor.type == "DS2408" and sensor == "/29.CF992F000000 - DS2408":
        sensor.PIO_5 = 0
        sensor.PIO_5 = 0
        # hit the pin that needs to be high



# try to run the jelmer and printout all the output


# turn the pin down
