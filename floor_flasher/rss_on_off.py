#!/usr/bin/python2
import serial
import os
import json
import ow
import argparse

if __name__ == '__main__':
    # args
    parser = argparse.ArgumentParser()
    parser.add_argument('--node-id', type=int, default='')
    parser.add_argument('--rss-on', dest='rss_state', action='store_true')
    parser.add_argument('--rss-off', dest='rss_state', action='store_false')
    parser.set_defaults(rss_state=False)

    try:
        args = parser.parse_args()
    except:
        print('args provided are wrong')
        exit()

    # get the wire1 lib setup to talk the devices
    (ow.init('localhost:4304'))
    node_list = ow.Sensor('/').sensorList()

    # serial port to talk through rs422
    ser = serial.Serial('/dev/ttyUSB0', baudrate=115200, timeout=1)
    ser.reset_input_buffer()

    with open(os.path.dirname(os.path.realpath(__file__)) + '/../addr_finder/node_order.json') as json_file:
        strip_path_inorder = json.load(json_file)
    json_file.close()
    strip_path_inorder = [node_name['wire1'] for node_name in strip_path_inorder]

    # turn off all nodes communication
    for sensor in node_list:
        if sensor.type == "DS2408":
            sensor.PIO_7 = "0"  # turn off RX & TX
            sensor.PIO_6 = "1"

    # turn on RSS 422 for desired node
    sensor = strip_path_inorder[args.node_id-1]
    sensor = ow.Sensor(str(sensor))
    if sensor.type == "DS2408":
        if args.rss_state == True:
            # turn on RS422
            print('Turn on rss for sensor ID:' + str(args.node_id) + ' 1-wire: '+ str(sensor._path))
            sensor.PIO_7 = "1"
            sensor.PIO_6 = "0"
        else:
            # turn off RS422
            print('Turn off rss for sensor ID:' + str(args.node_id) + ' 1-wire: '+ str(sensor._path))
            sensor.PIO_7 = "0"
            sensor.PIO_6 = "1"
