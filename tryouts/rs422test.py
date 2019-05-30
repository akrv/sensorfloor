import serial
ser = serial.Serial('/dev/ttyUSB0', baudrate = 115200, timeout=1)

while 1:
    rcvdData= ser.readline().decode('ascii')
    if rcvdData:
        print(rcvdData)
