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
import numpy as np

ser = serial.Serial( port='/dev/ttyACM0', baudrate=921600)

while(1):
    ser.reset_input_buffer()
    ser.reset_input_buffer()

    #do the interrupt here or press the buttons of the dev kit

    print '__________________________________________________'
    np.set_printoptions(formatter={'float': lambda x: "{0:0.3f}".format(x)})

    #calculate the length
    tx_start = ser.read(2)
    if tx_start == '[[':
        print "Correct beginning of RX"
    else:
        print "ERROR parsing RX"

    buffer_length = struct.unpack('<H', ser.read(2))
    buffer_length = buffer_length[0]
    print 'buffer length: ' + str(buffer_length)

    imu_acc_data = list()
    imu_gyr_data = list()
    imu_mag_data = list()
    imu_mag_data_raw = list()
    rssi_data = list()
    for readings in range(buffer_length):
        buffer = ser.read(9*2)
        buffer = struct.unpack('<' + str(9) + 'h', buffer)
        # Acc
        data = np.array(buffer[0:3], dtype=np.float)
        data = (data* 1.0) / (32768 / 2)
        imu_acc_data.append(data)
        # Gyr
        data = np.array(buffer[3:6], dtype=np.float)
        data = (data* 1.0) / (65536 / 500)
        imu_gyr_data.append(data)
        # Mag
        data = np.array([buffer[6:9]], dtype=np.float)
        data *=0.15
        imu_mag_data.append(data)
        # RSSI
        buffer = ser.read(1)
        data = struct.unpack('<' + str(1) + 'b', buffer)
        rssi_data.append(data)

    print 'Acc data:'
    print imu_acc_data
    print 'Gyr data:'
    print imu_gyr_data
    print 'Mag data:'
    print imu_mag_data
    print 'RSSI data:'
    print rssi_data

    rest = ser.readline()
    if (rest == ']]\n'):
        print 'Correct buffer end'
    else:
        print 'Error in bufer end'
