import serial
import os
import json
import ow
import argparse

if __name__ == '__main__':
    # args
    parser = argparse.ArgumentParser()
    parser.add_argument('--turn-on', dest='powered', action='store_true')
    parser.add_argument('--turn-off', dest='powered', action='store_false')
    parser.set_defaults(powered=False)

    try:
        args = parser.parse_args()
    except:
        print('args provided are wrong')
        exit()

    if args.powered:
        print('turning all nodes on, communication off')
    else:
        print('turning all node off')

    # get the wire1 lib setup to talk the devices
    (ow.init('localhost:4304'))
    node_list = ow.Sensor('/').sensorList()

    # turn on and put them in a not communicating mode
    for sensor in node_list:
        if sensor.type == "DS2408":
            if args.powered:
                sensor.PIO_BYTE = "64"  # turn off
                sensor.PIO_BYTE = "147"  # turn on with comms
                sensor.PIO_7 = "0"  # turn off RX & TX
                sensor.PIO_6 = "1"
            else:
                sensor.PIO_BYTE = "64"  # turn off
                sensor.PIO_7 = "0"  # turn off RX & TX
                sensor.PIO_6 = "1"