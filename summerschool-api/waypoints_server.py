#!/usr/bin/python2
import json
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import euclidean_distances
import paho.mqtt.client as mqttClient

import rospy
from std_msgs.msg import String
import geometry_msgs.msg

w1 = (18,5)
w2 = (18,9)
w3 = (14,7)
w4 = (10,5)
w5 = (9,9)
w6 = (8,7)
w7 = (5,4)
w8 = (4,6)

##############################################################################
##############################################################################
# Define which team is being evaluated
#waypoints = [w1, w6, w4, w7, w5] # Team 1 waypoints
#waypoints = [w1, w6, w5, w7, w4] # Team 2 waypoints
#waypoints = [w2, w6, w4, w7, w8] # Team 3 waypoints
#waypoints = [w8, w3, w4, w7, w5] # Team 4 waypoints
#waypoints = [w8, w3, w5, w7, w6] # Team 5 waypoints


# Define robot being used
ros_vicon_topic = '/vicon/rb1_base_c/rb1_base_c'
##############################################################################

feedback_msg = {"waypoints_reached": 0}

# setup floor cells center coordinates - cells are 1 meter square around each node
grid = pd.read_csv("vicon_node_positions.csv")
vicon_positions = np.vstack((grid.vicon_x, grid.vicon_y)).transpose()


##############################################################################
##############################################################################
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
##############################################################################


def vicon_callback(data):

    if (feedback_msg['waypoints_reached'] < 5):
        waypoint_to_check = waypoints[feedback_msg['waypoints_reached']]

        ## check if next waypoint is reached
        robot_position = [[data.transform.translation.x, data.transform.translation.y]]
        # check euclidean distance to all points
        distances = euclidean_distances(robot_position, vicon_positions)
        # robot is at cell with least euclidean distance
        index_least = np.argmin(distances)
        robot_cell = (int(grid.strip_id[index_least]), int(grid.node_id[index_least]))
        # check if robot cell equals waypoint 
        if robot_cell == waypoint_to_check:
            feedback_msg['waypoints_reached'] += 1
    
    ## publish waypoints_feedback to mqtt topic
    client.publish('/waypoints_feedback',json.dumps(feedback_msg,indent=4))


def main():
    rospy.init_node('summerschool_waypoint_checker', anonymous=True)
    rospy.Subscriber(ros_vicon_topic, geometry_msgs.msg.TransformStamped, vicon_callback)
    rospy.spin()

if __name__ == '__main__':
    main()
