import serial
import struct
from time import time

ser = serial.Serial('/dev/ttyUSB0', baudrate=921600, timeout=1)
while 1:
    try:
        curr = time()
        rcvdData = ser.read(size=4)
        if rcvdData:
            ser.reset_input_buffer()
        print(rcvdData,len(rcvdData))
        print(struct.unpack('<H', rcvdData[2:]))
        # print(len(rcvdData), len(rcvdData) / 2)
        print(time() - curr)
    except Exception as e:
        print(e)
        print(time() - curr)
    # rcvdData = ser.read(size=1)