# -*- coding: utf-8 -*-
import re, os, time, struct
import ow

(ow.init('localhost:4304'))
from time import sleep


def readOutput(slave):
    try:
        with open("/sys/bus/w1/devices/%s/output" % slave, "rb") as f:
            data = f.read(1)
        # logger.info("ro: %s" % (ord(data)))
        return bytearray(data)[0]
    except IOError:
        return -1


def writeOutput(slave, value):
    # logger.info("wo: %s" % (value))
    try:
        with open("/sys/bus/w1/devices/%s/output" % slave, "wb") as f:
            f.write(bytearray([value]))
    except IOError:
        # logger.info("wo: exception")
        pass


def readState(slave):
    try:
        with open("/sys/bus/w1/devices/%s/state" % slave, "rb") as f:
            data = f.read(1)
        # logger.info("rs: %s" % (ord(data)))
        return ord(data)
    except IOError:
        return -1


# define pathes to 1-wire sensor

sensor_path1 = ['29-0000002f9946',
                '29-0000002f998f',
                '29-0000002f99d4',
                '29-0000002f99ef',
                '29-0000002f994f',
                '29-0000002f99a5',
                '29-0000002f99dc',
                '29-0000002f9a0f',
                '29-0000002f9984',
                '29-0000002f99cc',
                '29-0000002f99df',
                '29-0000002f9a27',
                '29-0000002f998c',
                '29-0000002f99cf',
                '29-0000002f99e4',
                ]
# sensor_path = ['/29.24FF2F000000', '/29.A4EB2F000000', '/29.A4CF2F000000', '/29.B4EB2F000000', '/29.740A30000000', '/29.F2FE2F000000', '/29.AAF12F000000', '/29.9EEB2F000000', '/29.01E42F000000', '/29.A1FE2F000000', '/29.A9FC2F000000', '/29.35EB2F000000', '/29.5D0530000000', '/29.5FFC2F000000']
sensor_path = ow.Sensor('/').sensorList()

# for slave in sensor_path:
#     # print(readOutput(slave))
#     # print("State")
#
#     #writeOutput(64,slave), slave
#     #print(readState(slave),slave)


for sensor in sensor_path:
    if sensor.type == "DS2408":
        sensor.PIO_BYTE = "64"  # lsb is PIO0 msb is PIO7


for sensor in sensor_path:
    print (sensor._path)
    if sensor._path == '/29.47FC2F000000':
    # if sensor.type == "DS2408":

        # normal operation with Comms On
        # sleep(1)

        # sensor.out_of_testmode = "0"
        # sleep(.1)
        # sensor.out_of_testmode = "1"
        # sleep(.1)
        # sensor.PIO_BYTE = "64"
        # sleep(.1)
        # sensor.PIO_BYTE = "147"


        # # set node bootloader mode
        sensor.PIO_BYTE = "159"
        sleep(.1)  # wait until chip boots to BL mode
        sensor.PIO_BYTE = "150"
        sleep(.1)

        # Interrupt to read IMU
        # while 1:
        #     sensor.PIO_2 = "1"
        #     # sleep(1)
        #     sensor.PIO_2 = "0"
        #     # sleep(1)
        #     sensor.PIO_2 = "1"
        #     sleep(5)

