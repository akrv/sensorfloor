# -*- coding: utf-8 -*-
import re, os, time, struct

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
sensor_path = ['/29.CF992F000000',  # closest to the RPi
               '/29.84992F000000',
               '/29.8C992F000000',
               '/29.0F9A2F000000',
               '/29.DF992F000000',
               '/29.DC992F000000',
               '/29.CC992F000000',
               '/29.E4992F000000',
               '/29.D4992F000000',
               '/29.8F992F000000',
               '/29.279A2F000000',
               '/29.A5992F000000',
               '/29.46992F000000',
               '/29.4F992F000000',
               '/29.EF992F000000'   # farthest to the RPi
               ]

for slave in sensor_path:
    # print(readOutput(slave))
    # print("State")

    writeOutput(64,slave), slave
    print(readState(slave),slave)

