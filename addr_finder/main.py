import ow
from time import sleep, time
import json
from pprint import pprint
(ow.init('localhost:4304'))
node_list = ow.Sensor('/').sensorList()
import os

from subprocess import Popen, PIPE

import serial
nodes_inorder = {}

def run_jelmer():
    process = Popen(['python', '/home/pi/Documents/sensorfloor/cc2538-bsl/cc2538-bsl.py'], stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    process.wait()
    # print(stdout, stderr)
    try:

        address = stderr.split('\n')[-2].split("Address: ")[-1]

        if len(address.split(":")) == 8:
            return address
        else:
            return "EE:EE:EE:EE:EE:EE:EE:EE" # better printouts
    except:
        return "EE:EE:EE:EE:EE:EE:EE:EE" # better printouts

def read_data(sensor_path):
    id = None
    ponce = False
    ser = serial.Serial('/dev/ttyUSB0', baudrate=115200, timeout=1)
    start_time = time()
    while time() - start_time < 1:
        rcvdData = ser.readline().decode('ascii')
        if rcvdData:
            #verify its the logging line
            if "Log Count Led" in rcvdData:
                #print(sensor_path+": ID: "+rcvdData.split(";")[-2]+" Count: "+rcvdData.split(";")[-1])
                id = int(rcvdData.split(";")[-2])
                if ponce:
                    print(sensor_path + ": ID: " + rcvdData.split(";")[-2] + " Count: " + rcvdData.split(";")[-1])
                    ponce = False
            #print(rcvdData)
    ser.close()
    if id:
        return (id,sensor_path)
    else:
        return (0,sensor_path)


def set_blm(sensor):
    # sensor.PIO_BYTE = b'10011100'
    # print(sensor.sensed_BYTE)
    # sensor.PIO_1 = "1"
    # sensor.PIO_3 = "0"
    #
    # # getting comms ready
    # sensor.PIO_7 = "1"
    # sensor.PIO_6 = "0"
    # # usually dont care
    # sensor.PIO_5 = "0"
    # # MUX_EN
    # sensor.PIO_4 = "1"
    #
    # # RST held low
    # sensor.PIO_3 = "1"
    #
    # # set BL_PIN high
    # sensor.PIO_2 = "1"
    #
    # # set power to high
    # sensor.PIO_1 = "1"
    #
    # # change comms channel to BL pins
    # sensor.PIO_0 = "0"

    sensor.PIO_BYTE = "147"
    sleep(0.01)
    sensor.PIO_BYTE = "159"
    sleep(0.1) # wait until chip boots to BL mode
    sensor.PIO_BYTE = "150"

def get_all_name(node_list):
    list_of_nodes=[]
    for sensor in node_list:
        if sensor.type == "DS2408":
            list_of_nodes.append(sensor._path)
    return list_of_nodes

def set_all_0():
    # zero with comms turned off. so it is 64 and not 0 itself.
    # here every node is set to 0
    for sensor in node_list:
        if sensor.type == "DS2408":
            # print(sensor)
            sensor.PIO_BYTE = "64"  # lsb is PIO0 msb is PIO7
            # sleep(.3)
            # print(sensor.sensed_BYTE)
            # sleep(3)

def set_to_0(node):
    # zero with comms turned off. so it is 64 and not 0 itself.
    for sensor in node_list:
        if sensor._path == node:
            sensor.PIO_BYTE = "64"  # lsb is PIO0 msb is PIO7
            #sleep(.3)

def read_all():
    for sensor in node_list:
        if sensor.type == "DS2408":
            print(sensor._path, sensor.sensed_BYTE)

def addr_find():
    node_list = ow.Sensor('/').sensorList()
    list_of_nodes = get_all_name(node_list)
    if len(list_of_nodes) == 15:
        nodes_inorder_list = range(0,16)
        for sensor in node_list:
            if sensor.type == "DS2408":
                # if sensor._path in excluded_sensors:
                #     print("skipping already found sensor %", sensor._path)
                # else:
                # print(sensor._path)
                sensor.PIO_BYTE = "147"  # lsb is PIO0 msb is PIO7
                ## read data
                (id,sensor_path) = read_data(sensor._path)
                sensor.PIO_BYTE = "64"  # lsb is PIO0 msb is PIO7

                # check bootloader
                set_blm(sensor)
                # get IEEE address
                ieee_addr = run_jelmer()
                sensor.PIO_BYTE = "64"  # lsb is PIO0 msb is PIO7
                # this is an ordered list with 0 is 0 and the rest is populated
                nodes_inorder_list[id] = {
                                        "wire1" : sensor._path,
                                        "IEEE"  : ieee_addr,
                                        "id"    : id
                                      }
                pprint(nodes_inorder_list)

        (json.dumps(nodes_inorder, sort_keys=True))  # probably this helps in sorting the nodes in order

        # path will work with production as well.
        with open(os.path.dirname(os.path.realpath(__file__)) + '/node_order.json', 'w') as outfile:
            json.dump(nodes_inorder_list, outfile)
        return ('ok',nodes_inorder_list)

    else:
        return ('error','not all devices are seen on the wire1 bus')
if __name__ == '__main__':
    # populate the list
    list_of_nodes = get_all_name()
    if len(list_of_nodes) == 15:
        # set all nodes to 64
        set_all_0()
        # read_all()
        # test_run_table()
        nodes_inorder = addr_find()

        for node in nodes_inorder:
            pprint(node)
        print("ID 0 means the device ID was not found\nIEEE address is EE:EE:... there is problems with bootloader mode.")
    else:
        print("Only %d/15 1wire nodes are seen, fix this" % (len(list_of_nodes)) )