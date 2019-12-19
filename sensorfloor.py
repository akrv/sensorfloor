from flask import Flask, render_template, jsonify, request, flash, redirect, url_for, session
from werkzeug.utils import secure_filename
import serial
import os, json
app = Flask(__name__)
from time import sleep
import socket
import netifaces as ni
from subprocess import Popen, PIPE
import ow
from pprint import pprint
(ow.init('localhost:4304'))
node_list = ow.Sensor('/').sensorList()

from pprint import pprint
from config import NODE_NOT_FOUND, address_finder

from wire1_wrapper import find_nodeObj, put_all_pins_to_zero, read_state_byte, read_data, power_reset, turn_on,toggle_rs422_comms

bootloader_path = os.path.dirname(os.path.realpath(__file__))+'/cc2538-bsl/cc2538-bsl.py'
string_list = ['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15']

strip_path_inorder = []

# read the stored file which is a json with a list of items
with open(os.path.dirname(os.path.realpath(__file__))+'/addr_finder/node_order.json') as json_file:
    strip_path_inorder = json.load(json_file)
json_file.close()
returned_from_address_finder = strip_path_inorder
strip_path_inorder = [node_name['wire1'] for node_name in strip_path_inorder]

# file upload params
# UPLOAD_FOLDER = os.path.dirname(os.path.realpath(__file__))+'/flash'
UPLOAD_FOLDER = '/home/pi/sensorfloor/flash'
ALLOWED_EXTENSIONS = set(['hex','bin'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def read_data_rs422(position, num_lines, event_pin=None):
    read_line = []
    ser = serial.Serial('/dev/ttyUSB0', baudrate=115200, timeout=1)

    if event_pin:
        # interrupt based
        toggle_rs422_comms()

    else:
        # line based
        # turn on position using 1 wire
        while 1:
            rcvdData = ser.readline().decode('ascii')
            if rcvdData:
                read_line.append(rcvdData)
            if len(read_line) == int(num_lines):
                ser.close()
                break

    return read_line

def toggle_pin_hw(position, pin_number):
    pass

def flashing_hex_file(filepath_to_flash=None,device_id=0):

    global returned_from_address_finder, strip_path_inorder
    node_list = ow.Sensor('/').sensorList()
    print(filepath_to_flash,device_id)
    if device_id == '0':
        stderr_concat = []
        # put all devices in the right state to flash
        for sensor in node_list:
            # set all devices PIO 6 and 7 RX and TX off.
            if sensor.type == "DS2408":
                sensor.PIO_7 = "0"
                sensor.PIO_6 = "1"
        # flash all devices
        for sensor in node_list:
            if sensor.type == "DS2408":
                sensor.PIO_BYTE = "147"
                sleep(0.01)
                sensor.PIO_BYTE = "159"
                sleep(0.1)  # wait until chip boots to BL mode
                sensor.PIO_BYTE = "150"
                process = Popen(['python', bootloader_path, '-e', '-w', '-v', filepath_to_flash], stdout=PIPE,
                                stderr=PIPE)
                stdout, stderr = process.communicate()
                process.wait()
                stderr_concat.append(stderr)
                print(stdout, stderr)
                # turn back to the right state
                # turn on and put it in a no communicate state.
                sensor.PIO_BYTE = "64"
                sensor.PIO_7 = "0"
                sensor.PIO_6 = "1"

        return ('OK',stderr_concat,device_id)
    else:
        device_id = int(device_id)
        # flash device with position number
        device_found = False
        for sensor_iter in returned_from_address_finder:

            if sensor_iter["id"] == device_id:
                sensor = sensor_iter["wire1"]
                device_found = True
                break

        if device_found:
            for sensor in node_list:
                # set all devices PIO 6 and 7 RX and TX off.
                if sensor.type == "DS2408":
                    sensor.PIO_7 = "0"
                    sensor.PIO_6 = "1"
            for sensor in node_list:
                if sensor.type == "DS2408" and sensor._path == strip_path_inorder[device_id-1]:
                    sensor.PIO_BYTE = "147"
                    sleep(0.01)
                    sensor.PIO_BYTE = "159"
                    sleep(0.1)  # wait until chip boots to BL mode
                    sensor.PIO_BYTE = "150"
                    process = Popen(['python', bootloader_path, '-e', '-w', '-v',filepath_to_flash], stdout=PIPE, stderr=PIPE)
                    stdout, stderr = process.communicate()
                    process.wait()
                    print(stdout, stderr)
                    # turn back to the right state
                    # turn on and put it in a no communicate state.
                    # reset power to reboot
                    sensor.PIO_BYTE = "64"
                    # set at running
                    sensor.PIO_BYTE = "147"
                    # stop communicating
                    sensor.PIO_7 = "0"
                    sensor.PIO_6 = "1"
                    return ('OK',stderr,device_id)
        else:
            return ('error','device not found in this strip')
def run_simple_test():
    messages = []
    put_all_pins_to_zero()
    # sleep(2)
    read_state_byte()
    # sleep(2)
    turn_on()
    # sleep(2)
    read_state_byte()
    # sleep(2)

    print(node_list)
    for node_ow in node_list:
        if node_ow.type == "DS2408":
            # goto a module

            # reset the module
            # power_reset(node=node_ow)

            # set the module for comms
            toggle_rs422_comms(comms_on=True,node=node_ow)
            # read data out
            read_data()
            toggle_rs422_comms(comms_on=False,node=node_ow)
    pprint(messages)

def get_ipaddress():
    ni.ifaddresses('eth0')
    try:
        ip = ni.ifaddresses('eth0')[ni.AF_INET][0]['addr']
    except KeyError:
        try:
            ip = ni.ifaddresses('wlan0')[ni.AF_INET][0]['addr']
        except:
            ip = "0.0.0.0"
    return ip


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def hex_file_processing(request):

    # check if the post request has the file part
    if 'file' not in request.files:
        print('No file part')
        return('error','No file part', None)

    file = request.files['file']

    if file.filename == '':
        print('No file selected for uploading')
        return('error','No file selected for uploading', None)

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_and_path = (os.path.join(app.config['UPLOAD_FOLDER'], filename))
        file.save(file_and_path)
        # print('File successfully uploaded')
        return('OK',
               'File successfully uploaded',
               file_and_path)

    else:
        print('Allowed file type HEX')
        return('error','Allowed file type HEX', None)
    return None

@app.route("/",methods=['GET','POST'])
def hello():
    if request.method == 'POST':

        if request.files['file']:
            [success, message, filepath_to_flash] = hex_file_processing(request)
            # todo start a thread to flash all devices one by one
            # print (request.form['device']) device to flash is available on this device
            flash_status = flashing_hex_file(filepath_to_flash=filepath_to_flash,device_id=request.form['device'])
            print(flash_status)
            message = flash_status[1]
            return render_template('index.html', hostname=socket.gethostname(), ipaddress= get_ipaddress(), strip_path_inorder=strip_path_inorder[1:], message=message)
        return render_template('index.html', hostname=socket.gethostname(), ipaddress= get_ipaddress(), strip_path_inorder=strip_path_inorder[1:], message="No file found")
    if request.method == 'GET':
        return render_template('index.html', hostname=socket.gethostname(), ipaddress= get_ipaddress(), strip_path_inorder=strip_path_inorder[1:])

@app.route('/node_inorder')
def node_inorder():
    # returns a list of nodes in order as physically installed in the strip starting with the one closest to the RPi
    return jsonify(strip_path_inorder)

@app.route('/addr_finder')
def addrs_finder():
    global returned_from_address_finder, bootloader_path
    # address finder will be started
    returned_from_address_finder = address_finder(force_find=False,bootloader_path=bootloader_path)
    return jsonify(returned_from_address_finder)

@app.route('/addresses')
def addresses():
    # address finder will be started
    return jsonify(returned_from_address_finder)

@app.route('/toggle/<position>/<pin_number>')
def toggle_pin_number(position,pin_number):
    # address finder will be started
    if 0 <= int(position) <= 15:
        if pin_number == 'DP12' or pin_number == 'DP11':
            toggle_pin_hw(int(position),pin_number)
            return jsonify({ 'status': 'ok', 'pin_number': pin_number, 'position': position})
        else:
            return jsonify({'status':'error', 'msg': 'ping to toggle is either 11 or 12'})
    else:
        return jsonify({'status':'error', 'msg': 'position should be between 0 and 15'})\

@app.route('/read/<position>/<event_pin>')
def read_lines(position,num_lines, event_pin=None):
    global read_lock
    if read_lock:
        read_lock = False
        # address finder will be started
        if 0 <= int(position) <= 15:
            if event_pin ==  None:
                read_line = read_data_rs422(position,num_lines,event_pin)
            else:
                read_line = read_data_rs422(position,num_lines)
            read_lock = True
            return jsonify(read_line)

        else:
            return jsonify({'status':'error', 'msg': 'position should be between 0 and 15'})
    else:
        return jsonify({'status': 'error', 'msg': 'someone else is reading, try using MQTT channels for multiple clients'})


if __name__ == '__main__':
    read_lock = True

    app.secret_key = "secret_key"

    app.run(debug=True,host='0.0.0.0')
