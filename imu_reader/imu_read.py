import serial
from time import sleep, time
import os, json
from subprocess import Popen, PIPE
import ow, json
import paho.mqtt.client as paho
from pprint import pprint

def reader_worker(strip_id,strip_path_inorder,node_list,serial_handler, mqtt_connection_info):
    # strip id is important for constructing the topic
    # strip_path_inorder is a ordered list of wire1 ID as owfs path
    # node_list is the object created by owfs lib for list of wire1 devices
    # serial handler when this function is used from another thread which has access
    # mqtt connection info is a list with broker and port

    client1 = paho.Client("raspi-dev")  # create client
    client1.connect(mqtt_connection_info[0], mqtt_connection_info[1])  # establish connection

    # turn on and put them in a not communicating mode
    for sensor in node_list:
        if sensor.type == "DS2408":
            sensor.PIO_BYTE = "64"      # turn off
            sensor.PIO_BYTE = "147"     # turn on with comms
            sensor.PIO_7 = "0"          # turn off RX & TX
            sensor.PIO_6 = "1"
    rs422_latency = parsing_latency = publish_latency = switching_latency = interrupt_latency =[]
    while continously_run:
        for sensor in node_list:
            loop_start_time = time()
            # if sensor.type == "DS2408" and sensor._path == '/29.EF992F000000':
            if sensor.type == "DS2408":
                node_id = str(1+strip_path_inorder.index(sensor._path))
                # construct topic for publishing
                mqtt_publish_topic = 'imu_reader'+"/"+strip_id+"/"+node_id

                switching_start_time = time()
                # set all devices PIO 6 and 7 RX and TX off.
                # turn on RS422 before read
                sensor.PIO_7 = "1"
                sensor.PIO_6 = "0"
                switching_start_time = (time()-switching_start_time)

                interrupt_start_time = time()
                # send interrupt
                sensor.PIO_2 = "1"
                sensor.PIO_2 = "0"
                sensor.PIO_2 = "1"
                interrupt_latency.append(time()-interrupt_start_time)

                read_start_time = time()
                all_read = True
                data_received = []
                while all_read:
                    rcvdData = serial_handler.readline()
                    if rcvdData:
                        data_received.append(rcvdData)
                    if len(data_received)==2:
                        rs422_latency.append(time() - read_start_time)
                        all_read = False

                # print(mqtt_publish_topic,data_received)

                parsing_start_time =  time()
                # IMU data parsing
                try:
                    accel = data_received[0].split(',')[1:4]
                except:
                    accel = [0, 0, 0]

                try:
                    gyro = data_received[1].split(',')[1:4]
                except:
                    gyro = [0, 0, 0]
                try:
                    mag = data_received[1].split(',')[5:8]
                except:
                    mag = [0,0,0]

                for i in range(3):
                    # gyro: value = (data * 1.0) / (65536 / 500)
                    try:
                        gyro[i] = (int(gyro[i])*1.0)/(65536 / 500)
                    except:
                        gyro = [0, 0, 0]
                    # accel: 2G
                    # v = (rawData * 1.0) / (32768/2);
                    try:
                        accel[i] = (int(accel[i])*1.0)/((32768/2))
                    except:
                        accel = [0, 0, 0]
                parsing_latency.append(time() - parsing_start_time)
                # mag: reading is already processed

                publish_start_time = time()
                data_to_publish = {
                                    'node': int(node_id),
                                    'strip': (strip_id),
                                    'accel':    accel,
                                    'gyro':     gyro,
                                    'mag':      mag
                                    }

                ret = client1.publish(mqtt_publish_topic,json.dumps(data_to_publish))  # publish
                publish_latency.append(time()-publish_start_time)

                switching2 = time()
                # turn off RS422 after read
                sensor.PIO_7 = "0"
                sensor.PIO_6 = "1"
                switching_latency.append(switching_start_time+(time()-switching2))

        latency_info = {'publish':      sum(publish_latency)/len(publish_latency),
                        'interrupt':    sum(interrupt_latency)/len(interrupt_latency),
                        'parsing':      sum(parsing_latency)/len(parsing_latency),
                        'switching':    sum(switching_latency)/len(switching_latency),
                        'rs422':        sum(rs422_latency)/len(rs422_latency)
                        }

        pprint(latency_info)
        # ret = client1.publish('imu_reader/'+strip_id+'/latency', json.dumps(latency_info))  # publish
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