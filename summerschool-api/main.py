from flask import Flask, request
import redis, json
from flask import jsonify
import paho.mqtt.client as mqttClient
import sys
from scipy.spatial.transform import Rotation as Rot
import json


#######################################################################################
# TODO determine which robot is used during the hackathon

ROBOT_ID = "rb1_base_c"

#######################################################################################


"""
MQTT Settings
"""
broker_address= "gopher.phynetlab.com"
port = 8883
Connected = False

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        global Connected
        Connected = True

def on_message(client, userdata, message):
        #print 'on_message'
	return

def exit_handler():
    client.disconnect()
    sys.exit()

client = mqttClient.Client()
client.on_connect= on_connect                          # attach function to callback
client.on_message= on_message                          # attach function to callback
client.connect(broker_address, port=port)              # connect to broker
client.loop_start()                                    # start the loop
client.subscribe("/robotnik/#", 0) # Topics with wild card and a robotnik namespace 

'''
#######################################################################################
'''
status = -1
status_received = False

app = Flask(__name__)


allowed_secrets = []
f = open("allowed_secret.txt", "r")
for i in range(10):
    allowed_secrets.append(f.readline()[:-1]) # to remove the trailing \n

RPi_IPs = [
            {"column_num": 1, "ip_addr": "129.217.152.74", "mac_id": "b8:27:eb:41:99:a0", "hostname": "raspberrypi"},
            {"column_num": 2, "ip_addr": "129.217.152.111", "mac_id": "b8:27:eb:c0:fd:6a", "hostname": "raspberrypi"},
            {"column_num": 3, "ip_addr": "129.217.152.79", "mac_id": "b8:27:eb:18:92:c7", "hostname": "raspberrypi"},
            {"column_num": 4, "ip_addr": "129.217.152.54", "mac_id": "b8:27:eb:53:f2:33", "hostname": "raspberrypi"},
            {"column_num": 5, "ip_addr": "129.217.152.86", "mac_id": "b8:27:eb:e7:6f:dc", "hostname": "raspberrypi"},
            # {"column_num": 6, "ip_addr": "129.217.152.110", "mac_id": "b8:27:eb:9b:69:9a", "hostname": "raspberrypi"},
            {"column_num": 6, "ip_addr": "129.217.152.89", "mac_id": "b8:27:eb:38:4b:07", "hostname": "raspberrypi"},
            {"column_num": 7, "ip_addr": "129.217.152.84", "mac_id": "b8:27:eb:1b:cf:26", "hostname": "raspberrypi"},
            {"column_num": 8, "ip_addr": "129.217.152.119", "mac_id": "b8:27:eb:6d:0e:53", "hostname": "raspberrypi"},
            {"column_num": 9, "ip_addr": "129.217.152.77", "mac_id": "b8:27:eb:b7:a3:b7", "hostname": "raspberrypi"},
            {"column_num": 10, "ip_addr": "129.217.152.118", "mac_id": "b8:27:eb:be:dc:32", "hostname": "raspberrypi"},
            {"column_num": 11, "ip_addr": "129.217.152.69", "mac_id": "b8:27:eb:ff:a4:48", "hostname": "raspberrypi"},
            {"column_num": 12, "ip_addr": "129.217.152.59", "mac_id": "b8:27:eb:a9:7d:4d", "hostname": "raspberrypi"},
            {"column_num": 13, "ip_addr": "129.217.152.85", "mac_id": "b8:27:eb:c4:f8:c7", "hostname": "raspberrypi"},
            {"column_num": 14, "ip_addr": "129.217.152.48", "mac_id": "b8:27:eb:e4:43:6d", "hostname": "raspberrypi"},
            {"column_num": 15, "ip_addr": "129.217.152.63", "mac_id": "b8:27:eb:98:69:6e", "hostname": "raspberrypi"},
            {"column_num": 16, "ip_addr": "129.217.152.50", "mac_id": "b8:27:eb:75:c7:a2", "hostname": "raspberrypi"},
            {"column_num": 17, "ip_addr": "129.217.152.37", "mac_id": "b8:27:eb:09:3d:77", "hostname": "raspberrypi"},
            {"column_num": 18, "ip_addr": "129.217.152.60", "mac_id": "b8:27:eb:05:d8:4d", "hostname": "raspberrypi"},
            {"column_num": 19, "ip_addr": "129.217.152.64", "mac_id": "b8:27:eb:36:da:22", "hostname": "raspberrypi"},
            {"column_num": 20, "ip_addr": "129.217.152.62", "mac_id": "b8:27:eb:f5:5d:04", "hostname": "raspberrypi"},
            {"column_num": 21, "ip_addr": "129.217.152.51", "mac_id": "b8:27:eb:88:8d:56", "hostname": "raspberrypi"},
            {"column_num": 22, "ip_addr": "129.217.152.87", "mac_id": "b8:27:eb:00:be:93", "hostname": "raspberrypi"},
            {"column_num": 23, "ip_addr": "129.217.152.33", "mac_id": "b8:27:eb:c0:10:ae", "hostname": "raspberrypi"},
            ]
# open as many dbs as required for every strip
for ip in RPi_IPs:
    if ip["column_num"] <= 15:
        ip['redis_handler']= redis.Redis(host='129.217.152.1', port=6379, db=ip["column_num"])
    else:
        # who is going to stop me from making shitty decisions, just me. but hey i built the whole stack and it was working
        # you are reading this comment because this was a bad decision to start with
        # you sure want to check redis_pusher.py
        ip['redis_handler']= redis.Redis(host='129.217.152.1', port=6380, db=ip["column_num"]-15)
        # -15 to not exceed the max 16 dbs and there are two instances of redis exposed in two different ports

redis_generated_frame = redis.Redis(host='129.217.152.1', port=6380, db=9) # db 9 is from danny's frame generator code

@app.route('/<allowed_secret>/current_values',methods=['GET'])
def send_current_values(allowed_secret):
    # if allowed_secret in allowed_secrets:
    #     current_values = []
    #     for ip in RPi_IPs:
    #         for key in (ip["redis_handler"].keys()):
    #             value_json = json.loads(ip["redis_handler"].get(key).decode("utf-8"))
    #             current_values.append(value_json)
    # else:
    #     current_values = {"error": "your key is not authenticated"}
    #
    # return jsonify(current_values)

    if allowed_secret in allowed_secrets:
        value_json = json.loads(redis_generated_frame.get('frame').decode("utf-8"))
        return jsonify(value_json)

def parse_status_data(client, userdata, message):
        try:
            status_msg = json.loads(message.payload)
        except:
            print('Json Message not correctly Formatted!')
            return
        global status
        status = status_msg['status']
        status_received = True
        #status_msg['command_id'] # Maybe be used!


def do_action(requested_json):
    # TODO: Message Throttling
    # all action related logic is performed here
    msg = {
        "robot_id": ROBOT_ID,\
        "command_id": "",\
        "pose": {\
        "position": {\
        "x": 0,\
        "y": 0,\
        "z": 0\
        },\
        "orientation": {\
        "x": 0,\
        "y": 0,\
        "z": 0,\
        "w": 1\
        }},\
        "action": "drive",\
        "cart_id": "KLT_7_neu",\
        "station_id": "AS_5_neu",\
        "bound_mode": "inbound", \
        "cancellation_stamp": 0 \
        }
    if requested_json["action"] == "forward":
        # call a function and return safe value from current location
        #position = {"x":int(requested_json["value"]), "y":0, "z":0}
        #msg = {"robot_id":ROBOT_ID, "action":"drive","position":position}
        msg['pose']['position']['x'] = float(requested_json["value"])

        #msg.command_id = data.command_id # Maybe be used!
        # value cannot be more than 10. sent value is in meters
        # value can be float
        # anything less than 10cm is error
        client.publish('/robotnik/mqtt_ros_command',json.dumps(msg,indent=4))
        global status
        while(status==1): pass # status 1 (as in ROS move_base server) then goal is active and can be executed

        # TODO check status
        return_values = {"status": "goal sent"}
        #if status == 3:
        #    return_values = {"status": "goal reached"}
        #elif status == 4:
        #    return_values = {"status": "goal failed"}
        # TODO check if this will crash the robot
    elif requested_json["action"] == "turn":
        # value cannot be float
        # value can only be a multiple of 5
        if abs(int(requested_json["value"])) >= 10 and int(requested_json["value"]) % 5 == 0:
            # check if this will crash the robot
            r = Rot.from_euler('z', int(requested_json["value"]), degrees=True)
            r = r.as_quat()
            orientation = {"x":r[0], "y":r[1], "z":r[2], "w":r[3]}
            msg['pose']['orientation'] = orientation
            return_values = {"status": "turn value published to robot"}
            client.publish('/robotnik/mqtt_ros_command',json.dumps(msg,indent=4))
            return_values = {"status": "goal sent"}
        else:
            return_values = {"error": "not a valid turn value"}  
    else:
        return_values = {"error": "requested action is not valid"}
    return return_values

@app.route('/<allowed_secret>/robot/action',methods=['POST'])
def move_robot_forward(allowed_secret):
    # only the request is authenticated
    if allowed_secret in allowed_secrets:
        requested_json=request.get_json()
        return_values = do_action(requested_json=request.get_json())
    else:
        return_values = {"error": "your key is not authenticated"}
    return jsonify(return_values)

client.message_callback_add("/robotnik/mqtt_ros_info", parse_status_data) # commands received from user ex: pick, place, etc

# running the server
app.run(debug = True, host= "0.0.0.0") # to allow for debugging and auto-reload


