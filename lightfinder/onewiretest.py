import ow
from time import sleep
from config import sensor_path as excluded_sensors

(ow.init('localhost:4304'))
node_list = ow.Sensor('/').sensorList()
from subprocess import call

list_of_nodes = []


def run_jelmer():
    return call(['/home/pi/Documents/lightfinder/cc2538-bsl/cc2538-bsl.py'], shell=True)


def set_blm(sensor):
    # sensor.PIO_BYTE = b'10011100'
    # print(sensor.sensed_BYTE)
    # sensor.PIO_1 = "1"
    # sensor.PIO_3 = "0"

    # getting comms ready
    sensor.PIO_7 = "1"
    sensor.PIO_6 = "0"
    # usually dont care
    sensor.PIO_5 = "0"
    # MUX_EN
    sensor.PIO_4 = "1"

    # RST held low
    sensor.PIO_3 = "1"

    # set BL_PIN high
    sensor.PIO_2 = "1"

    # set power to high
    sensor.PIO_1 = "1"

    if (sensor.sensed_BYTE) != 105:
        sensor.PIO_BYTE = "150"


def get_all_name():
    for sensor in node_list:
        if sensor.type == "DS2408":
            list_of_nodes.append(sensor._path)


def set_all_0():
    for sensor in node_list:
        if sensor.type == "DS2408":
            # print(sensor)
            sensor.PIO_BYTE = "64"  # lsb is PIO0 msb is PIO7
            sleep(.3)
            # print(sensor.sensed_BYTE)
            # sleep(3)
    # # sensor on desk: /29.CF992F000000 - DS2408


def set_to_0(node):
    for sensor in node_list:
        if sensor._path == node:
            sensor.PIO_BYTE = "64"  # lsb is PIO0 msb is PIO7
            sleep(.3)


def read_all():
    for sensor in node_list:
        if sensor.type == "DS2408":
            print(sensor._path, sensor.sensed_BYTE)

def light_finder():
    for sensor in node_list:
        if sensor.type == "DS2408":
            if sensor._path in excluded_sensors:
                print("skipping already found sensor %", sensor._path)
            else:
                print(sensor._path)
                sensor.PIO_BYTE = "66"  # lsb is PIO0 msb is PIO7
                sleep(3)
                sensor.PIO_BYTE = "64"  # lsb is PIO0 msb is PIO7


def test_run_table():
    for sensor in node_list:
        if sensor.type == "DS2408":
            if "/29.DF992F000000" == sensor._path:
                set_blm(sensor)
                term_res = run_jelmer()
                if term_res and sensor.sensed_BYTE == "105":
                    term_res = run_jelmer()
                    print(sensor._path, sensor.sensed_BYTE, term_res)
                else:
                    print("successful")
                set_to_0(sensor._path)
                print(sensor._path, sensor.sensed_BYTE, term_res)

            # if sensor.sensed_BYTE == 105:
            #     run_jelmer()
            # else:
            #     sensor.PIO_BYTE = b'00000000'
            #     print(sensor.sensed_BYTE)
            #     sensor.PIO_BYTE = b'10011100'
            #     sensor.PIO_BYTE = b'10010110'
            #     print(sensor.sensed_BYTE)
            #     if sensor.sensed_BYTE == 105:
            #         run_jelmer()
            #
            #


if __name__ == '__main__':
    # populate the list
    get_all_name()
    # set all nodes to 64
    set_all_0()
    # read_all()
    # test_run_table()
    light_finder()
