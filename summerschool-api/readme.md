### How to start the server with local

use python3

`pip3 install -r requirements.txt`

`python3 main.py`

### API Documentation

### How to control the robot?

The robot is a ROS based, mobile robot that is tracked using Vicon motion tracking system. We have abstracted the mobility functions to a simple web based REST API that allows you to control the robot from anywhere in the world.

As it is mentioned, the API is simple and you have three possible actions. 

### Forward:
The robot can move forward taking an argument which is a number interpreted by the server as meters. This is passed onto the robot and the robot will move.

### Turn: 
Since the robot can turn freely in any direction, you are also provided with the ability to turn the robot with the action turn robot. The number here is interpreted by the server in angles. 


For a complex motion planner, you can use these two basic kinematic abstractions to move the robot wherever you desire inside the hall. Since the robot is localised using a Vicon Motion Capturing system, the meter distances are tracked precisely but there is an allowable margin for error due to the physical dynamics of the robots’ motors and its interaction with the floor.

### go_to_relative
If you wish to only move the robot around without talking into consideration the orientation of the robot, we have created a third action, where you can tell the robot to move in meters relative to its current position.

### Data: current_values
The sensor floor real-time data is available through the API as well. It is generated almost every 6 seconds and it is already the pre-processed data that you can directly use in your machine learning model.

All of this API is documented in postman and you can easily switch to your target language to develop your navigation stack using the sensor floor real-time data.

https://documenter.getpostman.com/view/1411058/T1LV7i4v

### Sample code:
We have made it easier for you to program the sensor floor based navigation stack using localisation and motion planning of the robot using a simple python code. You are not limited to our creativity and you are free to choose to implement the solution however you wish to in any language you prefer. We chose the web based REST API interface especially to allow for this flexibility. The link to the sample code is available below and all of the updated comments are in the file.

https://github.com/akrv/sensorfloor/blob/master/summerschool-api/competition_example.py
