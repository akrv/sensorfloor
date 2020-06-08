import serial
# import pytty as serial
from time import sleep, time
import os, json
from subprocess import Popen, PIPE
import ow, json
import paho.mqtt.client as paho
from pprint import pprint
import struct

RPi_IPs = [
            {"column_num": 1, "ip_addr": "129.217.152.74", "mac_id": "b8:27:eb:41:99:a0", "hostname": "raspberrypi"},
            {"column_num": 2, "ip_addr": "129.217.152.111", "mac_id": "b8:27:eb:c0:fd:6a", "hostname": "raspberrypi"},
            {"column_num": 3, "ip_addr": "129.217.152.79", "mac_id": "b8:27:eb:18:92:c7", "hostname": "raspberrypi"},
            {"column_num": 4, "ip_addr": "129.217.152.54", "mac_id": "b8:27:eb:53:f2:33", "hostname": "raspberrypi"},
            {"column_num": 5, "ip_addr": "129.217.152.86", "mac_id": "b8:27:eb:e7:6f:dc", "hostname": "raspberrypi"},
            # {"column_num": 6, "ip_addr": "129.217.152.110", "mac_id": "b8:27:eb:9b:69:9a", "hostname": "raspberrypi"},
            {"column_num": 6, "ip_addr": "129.217.152.89", "mac_id": "b8:27:eb:38:4b:07", "hostname": "raspberrypi"},
            {"column_num": 7, "ip_addr": "129.217.152.84", "mac_id": "b8:27:eb:1b:cf:26", "hostname": "raspberrypi"},
            {"column_num": 8, "ip_addr": "129.217.152.119", "mac_id": "b8:27:eb:6d:0e:53", "hostname": "raspberrypi"},
            {"column_num": 9, "ip_addr": "129.217.152.77", "mac_id": "b8:27:eb:b7:a3:b7", "hostname": "raspberrypi"},
            {"column_num": 10, "ip_addr": "129.217.152.118", "mac_id": "b8:27:eb:be:dc:32", "hostname": "raspberrypi"},
            {"column_num": 11, "ip_addr": "129.217.152.69", "mac_id": "b8:27:eb:ff:a4:48", "hostname": "raspberrypi"},
            {"column_num": 12, "ip_addr": "129.217.152.59", "mac_id": "b8:27:eb:a9:7d:4d", "hostname": "raspberrypi"},
            {"column_num": 13, "ip_addr": "129.217.152.85", "mac_id": "b8:27:eb:c4:f8:c7", "hostname": "raspberrypi"},
            {"column_num": 14, "ip_addr": "129.217.152.48", "mac_id": "b8:27:eb:e4:43:6d", "hostname": "raspberrypi"},
            {"column_num": 15, "ip_addr": "129.217.152.63", "mac_id": "b8:27:eb:98:69:6e", "hostname": "raspberrypi"},
            {"column_num": 16, "ip_addr": "129.217.152.50", "mac_id": "b8:27:eb:75:c7:a2", "hostname": "raspberrypi"},
            {"column_num": 17, "ip_addr": "129.217.152.37", "mac_id": "b8:27:eb:09:3d:77", "hostname": "raspberrypi"},
            {"column_num": 18, "ip_addr": "129.217.152.60", "mac_id": "b8:27:eb:05:d8:4d", "hostname": "raspberrypi"},
            {"column_num": 19, "ip_addr": "129.217.152.64", "mac_id": "b8:27:eb:36:da:22", "hostname": "raspberrypi"},
            {"column_num": 20, "ip_addr": "129.217.152.62", "mac_id": "b8:27:eb:f5:5d:04", "hostname": "raspberrypi"},
            {"column_num": 21, "ip_addr": "129.217.152.51", "mac_id": "b8:27:eb:88:8d:56", "hostname": "raspberrypi"},
            {"column_num": 22, "ip_addr": "129.217.152.87", "mac_id": "b8:27:eb:00:be:93", "hostname": "raspberrypi"},
            {"column_num": 23, "ip_addr": "129.217.152.33", "mac_id": "b8:27:eb:c0:10:ae", "hostname": "raspberrypi"},
            ]


def reader_worker(strip_id, strip_path_inorder, node_list, serial_handler, mqtt_connection_info):
    # strip id is important for constructing the topic
    # strip_path_inorder is a ordered list of wire1 ID as owfs path
    # node_list is the object created by owfs lib for list of wire1 devices
    # serial handler when this function is used from another thread which has access
    # mqtt connection info is a list with broker and port

    client1 = paho.Client(strip_id[0])  # create client
    client1.connect(mqtt_connection_info[0], mqtt_connection_info[1])  # establish connection

    # turn on and put them in a not communicating mode
    for sensor in node_list:
        if sensor.type == "DS2408":
            sensor.PIO_BYTE = "64"  # turn off
            sensor.PIO_BYTE = "147"  # turn on with comms

            sensor.PIO_7 = "0"  # turn off RX & TX
            sensor.PIO_6 = "1"
    count = 0
    while continously_run:
        rs422_latency = []
        parsing_latency = []
        publish_latency = []
        switching_latency = []
        interrupt_latency = []
        data_received = []
        count += 1
        total_time = time()
        for sensor in node_list:
            # if sensor.type == "DS2408" and sensor._path == '/29.EF992F000000':
            if sensor.type == "DS2408":
                if sensor._path == "/29.BC992F000000" or sensor._path == "/29.47FC2F000000":
                    # sensor cannot be flashed.
                    data = [0,0,0,0,0,0,0,0,0]

                else:
                    node_id = str(1 + strip_path_inorder.index(sensor._path))

                    # construct topic for publishing
                    mqtt_publish_topic = 'imu_reader' + "/" + strip_id[0] + "/" + node_id
                    mqtt_publish_topic1 = 'imu_reader' + "/" + strip_id[1] + "/" + node_id

                    switching_start_time = time()
                    # set all devices PIO 6 and 7 RX and TX off.
                    # turn on RS422 before read
                    sensor.PIO_7 = "1"
                    sensor.PIO_6 = "0"
                    switching_start_time = (time() - switching_start_time)

                    # reset input buffer before sending an interrupt.
                    # serial_handler.reset_input_buffer()
                    serial_handler.reset_input_buffer()
                    interrupt_start_time = time()

                    # send interrupt

                    sensor.PIO_2 = "1"
                    sensor.PIO_2 = "0"
                    sensor.PIO_2 = "1"

                    interrupt_latency.append(time() - interrupt_start_time)

                    read_start_time = time()
                    try:
                        rcvdData = ser.read(size=4)
                        length_to_read = (struct.unpack('<H', rcvdData[2:]))[0]

                    except Exception as e:
                        print('dev_id: ',node_id, e)
                        continue
                    rs422_latency.append(time() - read_start_time)

                    parsing_start_time = time()
                # if its a not working sensor, then data is set to a list of 9 zeros
                parse = True
                if parse:
                    reading_to_publish = []

                    broken_node = False
                    for reading in range(length_to_read):
                        current_reading = {}
                        try:
                            # IMU
                            rcvdData = ser.read(size=9*2)
                            data = struct.unpack('<' + str(9) + 'h', rcvdData)
                            #current_reading['a'] = data[0:3]
                            #current_reading['g'] = data[3:6]
                            #current_reading['m'] = data[6:9]
                            current_reading['a'] = [(i * 1.0) / (32768 / 2) for i in data[0:3]]
                            current_reading['g'] = [(i * 1.0) / (65536 / 500) for i in data[3:6]]
                            current_reading['m'] = [i * 0.15 for i in data[6:9]]
                            # RSSI
                            rcvdData = ser.read(size=1)
                            data = struct.unpack('<' + str(1) + 'b', rcvdData)
                            current_reading['r'] = data
                            # publish the msg
                            reading_to_publish.append(current_reading)
                        except Exception as e:
                            print('broken node: ', sensor._path ,node_id, e)
                            broken_node = True
                            break
                    if broken_node is True:
                        continue
                    parsing_latency.append(time() - parsing_start_time)
                    publish_start_time = time()
                    # format data to be published with metadata
                    data_to_publish = {'strip_id': strip_id[0],
                                       'column_num': strip_id[1],
                                       'node_id': node_id,
                                       'data': reading_to_publish,
                                       'timestamp': time()
                                       }
                    ret = client1.publish(mqtt_publish_topic, json.dumps(data_to_publish))  # publish
                    ret = client1.publish(mqtt_publish_topic1, json.dumps(data_to_publish))  # publish
                    publish_latency.append(time() - publish_start_time)
                # print(reading_to_publish)
                switching2 = time()
                # turn off RS422 after read
                sensor.PIO_7 = "0"
                sensor.PIO_6 = "1"
                switching_latency.append(switching_start_time + (time() - switching2))
        latency_info = {
                        # 'publish': sum(publish_latency) / len(publish_latency),
                        'interrupt': sum(interrupt_latency) / len(interrupt_latency),
                        # 'parsing': sum(parsing_latency) / len(parsing_latency),
                        'switching': sum(switching_latency) / len(switching_latency),
                        'rs422': sum(rs422_latency) / len(rs422_latency),
                        }
        print(time() - total_time, 30 * '$')
        # pprint(latency_info)
        ret = client1.publish('imu_reader/' + strip_id + '/latency', json.dumps(latency_info))  # publish

def getMAC(interface='eth0'):
    # Return the MAC address of the specified interface
    try:
        str = open('/sys/class/net/%s/address' % interface).read()
        for ip in RPi_IPs:
            if ip["mac_id"] == str:
                column_num = ip["column_num"]
    except:
        str = "00:00:00:00:00:00"
        column_num = 0


    return [str[0:17],column_num]


if __name__ == '__main__':
    broker = "129.217.152.1"
    port = 8883

    # get the wire1 lib setup to talk the devices
    (ow.init('localhost:4304'))
    node_list = ow.Sensor('/').sensorList()

    continously_run = True

    # serial port to talk through rs422
    ser = serial.Serial('/dev/ttyUSB0', baudrate=921600, timeout=1)
    ser.reset_input_buffer()
    # read json file from file system
    # next version should read from mongodb (when?)
    with open(os.path.dirname(os.path.realpath(__file__)) + '/../addr_finder/node_order.json') as json_file:
        strip_path_inorder = json.load(json_file)
    json_file.close()
    returned_from_address_finder = strip_path_inorder
    # an ordered list with index == position on strip
    strip_path_inorder = [node_name['wire1'] for node_name in strip_path_inorder]
    print(getMAC())

    reader_worker(strip_id=getMAC(), strip_path_inorder=strip_path_inorder, node_list=node_list, serial_handler=ser,
                  mqtt_connection_info=[broker, port])
