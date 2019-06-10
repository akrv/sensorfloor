import ow

(ow.init('localhost:4304'))
node_list = ow.Sensor('/').sensorList()
from config import strip_path_inorder
from config import NODE_NOT_COMPATIBLE, NODE_NOT_FOUND, RS422_NOT_ALL_AT_ONCE
from time import sleep, time
import serial


def find_nodeObj(node):
    if isinstance(node, int):
        # returns node object
        for node_ow in ow.Sensor('/').sensorList():
            # loop through the sensor list
            if node_ow._path == strip_path_inorder[node - 1]:
                # compare path with path in a ordered list
                # node-1 is the list index starting from 0 whereas node int will start from 1
                return strip_path_inorder[node - 1]
    elif isinstance(node, str):
        for node_ow in ow.Sensor('/').sensorList():
            if node_ow._path == node:
                return node_ow
    elif isinstance(node, ow.Sensor):
        return node
    return NODE_NOT_FOUND


def put_all_pins_to_zero(node=None):
    # return 0 nothing done
    # return 1 specific node done
    # return 2 all node done
    if node:
        nodeObj = find_nodeObj(node)
        if nodeObj == NODE_NOT_FOUND:
            return (('error',NODE_NOT_FOUND))
        if nodeObj.type == "DS2408":
            nodeObj.PIO_BYTE = str(int(b'00000000'[::-1], 2))
        else:
            return (("error", NODE_NOT_COMPATIBLE))
        return 1
    else:
        # set all the pins to zero for all nodes
        for nodeObj in node_list:
            if nodeObj.type == "DS2408":
                nodeObj.PIO_BYTE = str(int(b'00000000'[::-1], 2))
        return 2
    return 0


def turn_on(node=None):
    # return 0 nothing done
    # return 1 specific node done
    # return 2 all node done
    if node:
        # check if node is passed into this function
        nodeObj = find_nodeObj(node=node)
        if nodeObj == NODE_NOT_FOUND:
            return (('error',NODE_NOT_FOUND))
        # setting the node to be powered but not communicating in RS422
        if nodeObj.type == "DS2408":
            nodeObj.PIO_BYTE = str(int(b'11001010'[::-1], 2))
        else:
            return (("error", NODE_NOT_COMPATIBLE))
        return 1
    else:
        # if node is none, then do it for all the nodes
        for nodeObj in node_list:
            # setting the node to be powered but not communicating in RS422
            if nodeObj.type == "DS2408":
                nodeObj.PIO_BYTE = str(int(b'11001010'[::-1], 2))
        return 2
    return 0


def toggle_rs422_comms(comms_on, node):
    if node:
        nodeObj = find_nodeObj(node)
        if nodeObj == NODE_NOT_FOUND:
            return (('error',NODE_NOT_FOUND))
        if comms_on:
            # turn on RS422 comms
            if nodeObj.type == "DS2408":
                node.PIO_4 = "1"  # mux en
                node.PIO_6 = "0"  # DE
                node.PIO_7 = "1"  # !RE
        else:
            # turn off RS422 comms
            if nodeObj.type == "DS2408":
                node.PIO_6 = "1"  # DE
                node.PIO_7 = "0"  # !RE
    else:
        return ('error', RS422_NOT_ALL_AT_ONCE)


def power_reset(node=None):
    # return 0 nothing done
    # return 1 specific node done
    # return 2 all node done
    if node:
        # check if node is passed into this function
        nodeObj = find_nodeObj(node=node)
        if nodeObj == NODE_NOT_FOUND:
            return (('error',NODE_NOT_FOUND))
        nodeObj.PIO_1 = "0"
        sleep(0.1)
        nodeObj.PIO_1 = "1"
        return 1
    else:
        # do it for all nodes
        for nodeObj in ow.Sensor('/').sensorList():
            nodeObj.PIO_1 = "0"
            sleep(0.1)
            nodeObj.PIO_1 = "1"
        return 2
    return 0


def read_state_byte(node=None):
    if node:
        nodeObj = find_nodeObj(node=node)
        if nodeObj == NODE_NOT_FOUND:
            return (('error',NODE_NOT_FOUND))
        if nodeObj.type == "DS2408":
            return nodeObj.sensed_BYTE
        else:
            return ("error", NODE_NOT_COMPATIBLE)
    else:
        # if there is no nodes given, returns a list of (node path,sensed_BYTE) as tuple
        for node in ow.Sensor('/').sensorList():
            list_of_sensed_bytes = []
            if node.type == "DS2408":
                list_of_sensed_bytes.append((node._path, node.sensed_BYTE))
        return list_of_sensed_bytes


def read_data(messages=[]):
    ser = serial.Serial('/dev/ttyUSB0', baudrate=115200, timeout=1)
    timestamp = time() + 10.0
    # print(ser,time(),timestamp)
    while time() < timestamp:
        # print(time())
        rcvdData = ser.readline().decode('ascii')
        if rcvdData:
            print(rcvdData)
            messages.append(rcvdData)
    print(ser.close())  # close the serial port at every access
