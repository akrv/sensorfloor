import ow
from time import sleep, time
import json
from pprint import pprint
(ow.init('localhost:4304'))
node_list = ow.Sensor('/').sensorList()
import statistics
import serial
from pprint import pprint
ser = serial.Serial('/dev/ttyUSB0', baudrate = 115200, timeout=1)

avg_time =[]
data_list = []
def set_turn_on():
    # zero with comms turned off. so it is 64 and not 0 itself.
    # here every node is set to 0
    for sensor in node_list:
        if sensor.type == "DS2408":
            sensor.PIO_BYTE = "64"  # power reset them all
            sensor.PIO_BYTE = "83"  # power the  device but turn off comms channel

def turn_on_device_for_comms(node):
    node.PIO_BYTE = "147"
    while 1:

        rcvdData = ser.readline()

        if "Log Count Led" in rcvdData:
            # print(rcvdData)
            break
    node.PIO_BYTE = "83"
    return rcvdData

def calc_time():
    for sensor in node_list:
        if sensor.type == "DS2408":
            timestamp1 = time()
            data_from_line = turn_on_device_for_comms(sensor)
            timestamp2 = time()
            avg_time.append(timestamp2-timestamp1)
            # id = int(data_from_line.split(";")[-2])
            # count = int(data_from_line.split(";")[-1])
            data_list.append(data_from_line)

if __name__ == "__main__":
    set_turn_on()
    for i in range(100):
        calc_time()
    print (statistics.mean(avg_time),statistics.median(avg_time),statistics.stdev(avg_time))
    # pprint(data_list)