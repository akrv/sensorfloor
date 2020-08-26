#!/usr/bin/python3
"""
This is an example code for TU Dortmund summer-school-2020 Hackathon.

The example shows how the robot can be controlled using the APIs to complete
the whole task.

The competitiors needs only to write the make_prediction function to call their
machine learning trained model. The function should return the position of
the robot as (x,y) cooridnates. The example has a simple path planning
algortihm that can drive the robot around the arena to reach all the waypoints
specified for each team.

All robot frames specified in this code and the whole competition are according
to ROS (robot operating system) standards [for more info check ROS REP 105]
"""

import requests
import json
import time
import numpy as np
import pandas as pd


###############################################################################
###############################################################################
SERVER = "http://s17.phynetlab.com/"

# This is a secret key that will be given to each team to get access to
# control the robot during the second task.
ALLOWED_SECRET = '5ebe2294ecd0e0f08eab7690d2a6ee69'

# Specify the waypoint provided to each team (5 points)
WAY_POINTS = np.array([[18,5], [8,7], [10,5], [5,4], [9,9]]) # Team 1 waypoints
###############################################################################
###############################################################################

class RobotController:
    def __init__(self):
        self.url_drive = SERVER + ALLOWED_SECRET  +'/robot/action'

    def go_forward(self,x):
        """
        This function will drive the robot forward relative to its current
        position and orientation.
        """
        payload = { 'action': 'forward', 'value': str(x) }
        return requests.post(self.url_drive, json=payload)

    def turn(self,theta):
        """
        This function will turn the robot around its center.
        Signs of turn directions are according to ROS standards.
        Z-axis points up, positive turn rotation are counter-clockwise and
        negative turn direction is clockwise.

        theta should be specified in angles.
        """
        payload = { 'action': 'turn', 'value': str(theta) }
        return requests.post(self.url_drive, json=payload)

    def go_to_relative(self,x,y):
        """
        This function will drive the robot to an (x,y) position relative to
        the current robot position but with the orientation of the origin frame.
        So, the robot will move to an (x,y) position relative to its position
        but as if it was oriented as the origin frame. Also the robot will
        orient itself as the origin frame when it reaches the goal point.

        This is function is used witin this example to drive the robot between
        cells (hence waypoints).
        """
        payload = { 'action': 'go_to_relative', 'x': str(x) , 'y': str(y)}
        return requests.post(self.url_drive, json=payload)

    def localize(self):
        """
        This function should return where the robot is currently is.

        Competitors should fill the code in the make_predictions() function to
        return the current location in (x,y) cooridnates then convet_to_cell
        will convert this value to a cell number.
        """
        # wait 5 seconds
        # floor data is 5 seconds delayed
        # stay still for 5 second then read localization value
        time.sleep(5)

        # read current values from the floor and return predicted robot position
        predict_vicon =  make_predictions()

        # convert the position to a cell number
        predict_cell = self.convert_to_cell(predict_vicon)

        return predict_cell

    def make_predictions(self):
        """
        This function should be written by the competitors to call their
        machine learning model and return (x,y) cooridnates of the robot position
        """
        # read the current values from the APIs
        url_data = SERVER +  ALLOWED_SECRET + "/current_values"
        response = requests.request("GET", url_data, headers=headers, data=payload)
        frame = pd.read_json(response.text.encode('utf8'))

        # TODO call the machine learning model and predict values here
        raise NotImplementedError()

    def convert_to_cell(self, predict_vicon):
        '''
        This function takes a measurement in origin frame (x,y), convert it
        to a cell number and return it as (strip_id, node_id)
        '''
        def translate(value, leftMin, leftMax, rightMin, rightMax):
            # Figure out how 'wide' each range is
            leftSpan = leftMax - leftMin
            rightSpan = rightMax - rightMin

            # Convert the left range into a 0-1 range (float)
            valueScaled = float(value - leftMin) / float(leftSpan)

            # Convert the 0-1 range into a value in the right range.
            return rightMin + (valueScaled * rightSpan)

        predict_cell = np.array([0,0])
        predict_cell[0] = predict_vicon[0] + 11.185
        predict_cell[1] = translate(predict_vicon[1], -15+7.575, 7.575, 15, 0)
        predict_cell = np.round(predict_cell)

        return predict_cell

    def path_planner(self, goal):
        """
        This function will drive the robot to a relative position in (x,y)
        coordinates.

        No need to explicitly write a path planner. Calling "go_to_relative"
        API will use the robot Planner to drive the robot to the desired point.

        Other APIs ("forward" and "turn") can give more control over the robot
        bevahiour. It's up to the competitors to decide it they want to use
        these APIs and how to use it as the "go_to_relative" API should be
        enough to finish the whole taks in an easy way.
        """
        self.go_to_relative(goal[0], goal[1])


if __name__ == '__main__':

    robot = RobotController()

    # Iterate over waypoints and keep looping until the robot gets a feedback
    # that each waypoint was successfully reached.
    for way_point in WAY_POINTS:
        relative_pos = np.array([0,0])
        way_point = way_point.flatten()

        # get the robot position from the latest data and the trained model
        current_cell = robot.localize().flatten()

        abs_distance = np.abs(way_point - current_cell)

        if   current_cell[0] >= way_point[0] and current_cell[1] >= way_point[1] : # north-west quarter
            relative_pos[0] = -abs_distance[0]
            relative_pos[1] =  abs_distance[1]
        elif current_cell[0] <= way_point[0] and current_cell[1] >= way_point[1] : # north-east quarter
            relative_pos[0] =  abs_distance[0]
            relative_pos[1] =  abs_distance[1]
        elif current_cell[0] <= way_point[0] and current_cell[1] <= way_point[1] : # south-east quarter
            relative_pos[0] =  abs_distance[0]
            relative_pos[1] = -abs_distance[1]
        elif current_cell[0] >= way_point[0] and current_cell[1] <= way_point[1] : # south-west quarter
            relative_pos[0] = -abs_distance[0]
            relative_pos[1] = -abs_distance[1]
        robot.go_to_relative(relative_pos[0], relative_pos[1])

        print("waypoint reached")