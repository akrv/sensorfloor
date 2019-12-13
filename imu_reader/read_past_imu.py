import serial
from time import sleep, time
import os, json
from subprocess import Popen, PIPE
import ow, json
import paho.mqtt.client as paho
from pprint import pprint
import struct


def reader_worker(strip_id, strip_path_inorder, node_list, serial_handler, mqtt_connection_info):
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
            sensor.PIO_BYTE = "64"  # turn off
            sleep(0.1)
            sensor.PIO_BYTE = "147"  # turn on with comms

            sensor.PIO_7 = "0"  # turn off RX & TX
            sensor.PIO_6 = "1"

    rs422_latency = []
    parsing_latency = []
    publish_latency = []
    switching_latency = []
    interrupt_latency = []
    count = 0
    while continously_run:
        data_received = []
        count += 1
        for sensor in node_list:

            loop_start_time = time()
            # if sensor.type == "DS2408" and sensor._path == '/29.EF992F000000':
            if sensor.type == "DS2408":
                node_id = str(1 + strip_path_inorder.index(sensor._path))
                # construct topic for publishing
                mqtt_publish_topic = 'imu_reader' + "/" + strip_id + "/" + node_id

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
                # calculate the length
                if serial_handler.read(2) == '[[':
                    # print("Correct beginning of RX")
                    # read dat  a from serial port
                    buffer_length = struct.unpack('<H', serial_handler.read(2))
                    buffer_length = buffer_length[0]
                    buffer = serial_handler.read(buffer_length * 9 * 2)
                    data = struct.unpack('<' + str(buffer_length * 9) + 'H', buffer)
                    serial_handler.reset_input_buffer()
                    # rest = serial_handler.readline()
                    # if (rest == ']]\n'):
                    #     # print(data)
                    #     pass
                    # else:
                    #     print('Error in buffer end')
                else:
                    print("ERROR parsing RX")
                rs422_latency.append(time() - read_start_time)

                parsing_start_time = time()
                reading_to_publish = []
                current_reading = {}

                # data prototype
                # [{a:[x,y,z],m:[],},..]
                for reading in range(0, len(data), 9):

                    current_reading['a'] = [(i * 1.0) / (32768 / 2) for i in data[reading:reading + 3]]
                    current_reading['m'] = data[reading + 3:reading + 6]
                    current_reading['g'] = [(i * 1.0) / (65536 / 500) for i in data[reading + 6:reading + 9]]
                    reading_to_publish.append(current_reading)

                parsing_latency.append(time() - parsing_start_time)

                publish_start_time = time()
                # format data to be published with metadata
                data_to_publish = {'strip_id': strip_id,
                                   'node_id': node_id,
                                   'data': reading_to_publish,
                                   'timestamp': time()
                                   }
                ret = client1.publish(mqtt_publish_topic, json.dumps(data_to_publish))  # publish
                publish_latency.append(time() - publish_start_time)
                # print(reading_to_publish)
                switching2 = time()
                # turn off RS422 after read
                sensor.PIO_7 = "0"
                sensor.PIO_6 = "1"
                switching_latency.append(switching_start_time + (time() - switching2))
        # pprint(data_received)
        # print("rcvd stats: ", len(reading_to_publish))

        latency_info = {'publish': sum(publish_latency) / len(publish_latency),
                        'interrupt': sum(interrupt_latency) / len(interrupt_latency),
                        'parsing': sum(parsing_latency) / len(parsing_latency),
                        'switching': sum(switching_latency) / len(switching_latency),
                        'rs422': sum(rs422_latency) / len(rs422_latency),
                        'rcvd_stats': len(reading_to_publish)
                        }

        pprint(latency_info)
        ret = client1.publish('imu_reader/' + strip_id + '/latency', json.dumps(latency_info))  # publish


def getMAC(interface='eth0'):
    # Return the MAC address of the specified interface
    try:
        str = open('/sys/class/net/%s/address' % interface).read()
    except:
        str = "00:00:00:00:00:00"
    return str[0:17]


if __name__ == '__main__':
    broker = "129.217.152.1"
    port = 8883

    # get the wire1 lib setup to talk the devices
    (ow.init('localhost:4304'))
    node_list = ow.Sensor('/').sensorList()

    continously_run = True

    # serial port to talk through rs422
    ser = serial.Serial('/dev/ttyUSB0', baudrate=115200, timeout=1)
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
