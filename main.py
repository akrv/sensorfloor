from flask import Flask, render_template, jsonify, request, flash, redirect, url_for, session
from werkzeug.utils import secure_filename

import os, json
app = Flask(__name__)

import socket
import netifaces as ni
import ow
(ow.init('localhost:4304'))
node_list = ow.Sensor('/').sensorList()

from pprint import pprint
from config import strip_path_inorder, NODE_NOT_FOUND, address_finder

from wire1_wrapper import find_nodeObj, put_all_pins_to_zero, read_state_byte, read_data, power_reset, turn_on,toggle_rs422_comms


string_list = ['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15']

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
        ip = ni.ifaddresses('wlan0')[ni.AF_INET][0]['addr']
    return ip

# TODO needs to be changed for production
UPLOAD_FOLDER = os.path.dirname(os.path.realpath(__file__))+'/flash'
ALLOWED_EXTENSIONS = set(['hex'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def hex_file_processing(request):

    # check if the post request has the file part
    if 'file' not in request.files:
        print('No file part')
        return('error','No file part')
    file = request.files['file']
    if file.filename == '':
        print('No file selected for uploading')
        return('error','No file selected for uploading')
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        print('File successfully uploaded')
        return('OK','File successfully uploaded')
    else:
        print('Allowed file type HEX')
        return('error','Allowed file type HEX')
    return None

def flashing_hex_file(file=None,device=None):
    if device:
        pass
    else:
        pass

@app.route("/<device_name>",methods=['GET','POST'])
def device_specific(device_name):
    print(device_name)
    if request.method == 'POST':
        if request.files['file']:
            [success, message] = hex_file_processing(request)
            # everything went well
            session['message'] = message
            return redirect(url_for('hello', message=message))
        # request didnt have file
        return redirect(url_for('hello'), message="No file found")
    # GET is not allowed in this method at this moment
    return render_template('index.html', hostname=socket.gethostname(), ipaddress=get_ipaddress(),
                           strip_path_inorder=strip_path_inorder[1:], message="GET not allowed")

@app.route("/",methods=['GET','POST'])
def hello():
    if request.method == 'POST':
        if request.files['file']:
            [success, message] = hex_file_processing(request)
            # todo start a thread to flash all devices one by one
            flashing_hex_file()
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
    # address finder will be started
    returned_from_address_finder = address_finder()
    return jsonify(returned_from_address_finder)

if __name__ == '__main__':
    strip_path_inorder = []

    # read the stored file which is a json with a list of items
    with open(os.path.dirname(os.path.realpath(__file__))+'/addr_finder/node_order.json') as json_file:
        strip_path_inorder = json.load(json_file)
    json_file.close()

    app.secret_key = "secret_key"
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.run(debug=True,host='0.0.0.0')
