#!/usr/bin/env python
import rospy
from std_msgs.msg import String
import geometry_msgs.msg
import json
from time import time

topic = '/vicon/aerobie/aerobie'


def callback(data):
    global topic
    j_msg = {
        'object': topic,
        'translation': [data.transform.translation.x, data.transform.translation.y, data.transform.translation.z],
        'rotation': [data.transform.rotation.x, data.transform.rotation.y, data.transform.rotation.z],
        'time': time()
    }
    with open("vicon_data.txt", "a+") as test_data:
        test_data.write(json.dumps(j_msg) + '\n')
    test_data.close()


def listener():
    global topic
    rospy.init_node('listener', anonymous=True)
    rospy.Subscriber(topic, geometry_msgs.msg.TransformStamped, callback)
    rospy.spin()

if __name__ == '__main__':
    listener()
