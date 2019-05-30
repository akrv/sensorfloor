# Lightfinder

This python package is used to find the order of the 1wire nodes on the strip.

The config.py on this folder will be edited everytime you find the sensor.

The node that is closest to the power line is the first list item and the last list item will be the node farthest in the strip.

## How to use lightfinder


 - Clone the sensorfloor repo
	 -	`git clone https://github.com/akrv/sensorfloor/tree/master/lightfinder`
 - Flash each of nodes with
   [blink-hello.hex](https://github.com/akrv/sensorfloor/blob/master/lightfinder/blink-hello.hex). This firmware will flash the light every second on the sensortag.
 - Navigate to lightfinder folder
	 - `cd sensorfloor/lightfinder`
 - run the main.py file 
	 - `python main.py`
 - every time a node is activated, the sensortag will start to blink. Blinking happens for three seconds and the sensortag is turned off and the next one on the 1wire bus is turned on
 - if the node you are inspecting is blinking, then press `ctrl+c` to stop the program and copy the path printed in the terminal and paste it into the `config.py`  file. 
 - A finished fully tested strip will have the list populated as below. 
	 - `sensor_path = ['/29.EF992F000000', '/29.4F992F000000', '/29.46992F000000', '/29.A5992F000000', '/29.279A2F000000', '/29.8F992F000000', '/29.D4992F000000', '/29.E4992F000000', '/29.CC992F000000', '/29.DC992F000000', '/29.DF992F000000', '/29.0F9A2F000000', '/29.8C992F000000', '/29.84992F000000', '/29.CF992F000000']
`
 - everytime a new list item is added, this node will be skipped for consequent testing.
 - Config file will be also used in the deployed software, make sure you copy the config file into the respective RPi.
