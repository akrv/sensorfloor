import serial
from time import sleep, time
import os, json
from subprocess import Popen, PIPE
import ow
import paho.mqtt.client as paho

def reader_worker(strip_id,strip_path_inorder,node_list,serial_handler, mqtt_connection_info):
    # strip id is important for constructing the topic
    # strip_path_inorder is a ordered list of wire1 ID as owfs path
    # node_list is the object created by owfs lib for list of wire1 devices
    # serial handler when this function is used from another thread which has access
    # mqtt connection info is a list with broker and port

    client1 = paho.Client("raspi-dev")  # create client
    client1.connect(mqtt_connection_info[0], mqtt_connection_info[1])  # establish connection

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
                    rcvdData = serial_handler.readline()
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
        ret = client1.publish('imu_reader/'+strip_id+'/latency', str(time()-start_time))  # publish
if __name__ == '__main__':
    broker = "129.217.152.1"
    port = 8883

    # get the wire1 lib setup to talk the devices
    (ow.init('localhost:4304'))
    node_list = ow.Sensor('/').sensorList()

    continously_run = True

    # serial port to talk through rs422
    ser = serial.Serial('/dev/ttyUSB0', baudrate=115200, timeout=1)



    # read json file from file system
    # next version should read from mongodb (when?)
    with open(os.path.dirname(os.path.realpath(__file__))+'/../addr_finder/node_order.json') as json_file:
        strip_path_inorder = json.load(json_file)
    json_file.close()
    returned_from_address_finder = strip_path_inorder
    # an ordered list with index == position on strip
    strip_path_inorder = [node_name['wire1'] for node_name in strip_path_inorder]

    reader_worker(strip_id='dev', strip_path_inorder=strip_path_inorder,node_list=node_list,serial_handler=ser,mqtt_connection_info=[broker,port])