import serial
import struct
import time

ser = serial.Serial( port='/dev/ttyACM0', baudrate=115200)

while(1):
    ser.reset_input_buffer()

    #do the interrupt here

    #calculate the length
    if ser.read(2) == '[[':
        print "Correct beginning of RX"
    else:
        print "ERROR parsing RX"

    buffer_length = struct.unpack('<H', ser.read(2))
    buffer_length = buffer_length[0]
    print buffer_length

    buffer = ser.read(buffer_length*9*2)
    print len(buffer)
    data = struct.unpack('<' + str(buffer_length*9) + 'H', buffer)
    print data

    rest = ser.readline()
    print len(rest)
    print rest
    if (rest == ']]\n'):
        print 'Correct buffer end'
    else:
        print 'Error in bufer end'