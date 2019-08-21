from flask import Flask, render_template, jsonify, request, flash, redirect
import os
app = Flask(__name__)

import socket
import netifaces as ni



import ow
(ow.init('localhost:4304'))
node_list = ow.Sensor('/').sensorList()

from pprint import pprint
from config import strip_path_inorder, NODE_NOT_FOUND

from wire1_wrapper import find_nodeObj, put_all_pins_to_zero, read_state_byte, read_data, power_reset, turn_on,toggle_rs422_comms


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


ALLOWED_EXTENSIONS = set(['hex'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/",methods=['GET','POST'])
def hello():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No file selected for uploading')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            flash('File successfully uploaded')
            return redirect('/')
        else:
            flash('Allowed file types are txt, pdf, png, jpg, jpeg, gif')
            return redirect(request.url)

    return render_template('index.html', hostname=socket.gethostname(), ipaddress= get_ipaddress(), strip_path_inorder=strip_path_inorder)

@app.route('/node_inorder')
def node_inorder():
    # returns a list of nodes in order as physically installed in the strip starting with the one closest to the RPi
    return jsonify(strip_path_inorder)

if __name__ == '__main__':
    app.secret_key = "secret_key"
    app.run(debug=True,host='0.0.0.0')
