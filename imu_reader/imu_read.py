import serial
from time import sleep, time
import os, json
from subprocess import Popen, PIPE
import ow
import paho.mqtt.client as paho
broker="129.217.152.1"
port=8883

def reader_worker(strip_id,strip_path_inorder):
    while continously_run:
        for sensor in node_list:
            if sensor.type == "DS2408":
                sensor.PIO_BYTE = "64"
                sensor.PIO_BYTE = "147"
                sensor.PIO_7 = "0"
                sensor.PIO_6 = "1"
        start_time = time()
        for sensor in node_list:
            if sensor.type == "DS2408":

                # construct topic for publishing
                mqtt_publish_topic = 'imu_reader'+"/"+strip_id+"/"+str(1+strip_path_inorder.index(sensor._path))

                # set all devices PIO 6 and 7 RX and TX off.
                # turn on RS422 before read
                sensor.PIO_7 = "1"
                sensor.PIO_6 = "0"

                # sending this give 1 as value
                # print(sensor.sensed_2)

                # send interrupt
                sensor.PIO_2 = "1"
                sensor.PIO_2 = "0"
                sensor.PIO_2 = "1"
                all_read = True
                data_received = []
                while all_read:
                    rcvdData = ser.readline()
                    if rcvdData:
                        data_received.append(rcvdData)
                    if len(data_received)==2:
                        all_read = False
                # print(mqtt_publish_topic,data_received)
                ret = client1.publish(mqtt_publish_topic,str(data_received))  # publish

                # turn off RS422 after read
                sensor.PIO_7 = "0"
                sensor.PIO_6 = "1"
        # print(time()-start_time)
        ret = client1.publish('imu_reader/latency', str(time()-start_time))  # publish
if __name__ == '__main__':

    # get the wire1 lib setup to talk the devices
    (ow.init('localhost:4304'))
    node_list = ow.Sensor('/').sensorList()

    continously_run = True

    # serial port to talk through rs422
    ser = serial.Serial('/dev/ttyUSB0', baudrate=115200, timeout=1)

    # mqtt publish
    client1 = paho.Client("raspi-dev")  # create client
    client1.connect(broker, port)  # establish connection

    # read json file from file system
    # next version should read from mongodb (when?)
    with open(os.path.dirname(os.path.realpath(__file__))+'/../addr_finder/node_order.json') as json_file:
        strip_path_inorder = json.load(json_file)
    json_file.close()
    returned_from_address_finder = strip_path_inorder
    # an ordered list with index == position on strip
    strip_path_inorder = [node_name['wire1'] for node_name in strip_path_inorder]

    reader_worker(strip_id='dev', strip_path_inorder=strip_path_inorder)