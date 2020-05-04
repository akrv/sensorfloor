'''Testing firmware with USB
This script will connect to a test kit to t test the firmware via USB.
Data is organised in the stream as next:
- first 2 bytes (2 char) are '[[' this represent the start of a buffer flush from the kit
- next 2 byte (uint_17) encodes number of reading being flushed 
- next bytes are the readings. Lenght varies depending on the number of readings being flushed,
  the kit flushes in each measurment 9 reading of IMU then RSSI
- end of the stream are ']]' just to make sure everything was read and parsed correctly

data is organised in the stream as next:
'''
import serial
import struct
import time

ser = serial.Serial( port='/dev/ttyACM0', baudrate=921600)

while(1):
    ser.reset_input_buffer()
    ser.reset_input_buffer()

    #do the interrupt here or press the buttons of the dev kit

    print '__________________________________________________'

    #calculate the length
    tx_start = ser.read(2)
    if tx_start == '[[':
        print "Correct beginning of RX"
    else:
        print "ERROR parsing RX"

    buffer_length = struct.unpack('<H', ser.read(2))
    buffer_length = buffer_length[0]
    print 'buffer length: ' + str(buffer_length)

    imu_data = list()
    rssi_data = list()
    for readings in range(buffer_length):
        buffer = ser.read(9*2)
        data = struct.unpack('<' + str(9) + 'H', buffer)
        imu_data.append(data)
        buffer = ser.read(1)
        data = struct.unpack('<' + str(1) + 'b', buffer)
        rssi_data.append(data)
    print 'imu data:'
    print imu_data
    print 'RSSI data:'
    print rssi_data

    rest = ser.readline()
    if (rest == ']]\n'):
        print 'Correct buffer end'
    else:
        print 'Error in bufer end'
