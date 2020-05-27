import serial
import os
import json
import ow
import argparse

if __name__ == '__main__':
    # get the wire1 lib setup to talk the devices
    ow.init('localhost:4304')
    node_list = ow.Sensor('/').sensorList()

    # serial port to talk through rs422
    ser = serial.Serial('/dev/ttyUSB0', baudrate=115200, timeout=1)
    ser.reset_input_buffer()

    with open(os.path.dirname(os.path.realpath(__file__)) + '/../addr_finder/node_order.json') as json_file:
        strip_path_inorder = json.load(json_file)
    json_file.close()
    strip_path_inorder = [node_name['wire1'] for node_name in strip_path_inorder]

    # rn on and put them in a not communicating mode
    for sensor in node_list:
        if sensor.type == "DS2408":
            sensor.PIO_7 = "0"  # turn off RX & TX
            sensor.PIO_6 = "1"

    f = open("data.txt", "w")
    for sensor in strip_path_inorder:
        sensor = ow.Sensor(str(sensor))
        if sensor.type == "DS2408":
            # turn on RS422
            sensor.PIO_7 = "1"
            sensor.PIO_6 = "0"

            for i in range(5):
                line = ser.readline()
            f.write(line)

            # turn off RS422
            sensor.PIO_7 = "0"
            sensor.PIO_6 = "1"
    f.close()