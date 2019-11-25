#!/usr/bin/env python3

import paho.mqtt.client as mqtt
import matplotlib.pyplot as plt
#import DataPlot and RealtimePlot from the file plot_data.py
from plot_data import DataPlot, RealtimePlot


fig, axes = plt.subplots()
plt.title('Data from TTN console')

data = DataPlot()
dataPlotting= RealtimePlot(axes)

count=0

import json

# This is the Subscriber

def on_connect(client, userdata, flags, rc):
  print("Connected with result code "+str(rc))
  for node in range(15):
    client.subscribe("imu_reader/dev/"+str(node+1))

def on_message(client, userdata, msg):
  if msg.payload.decode():
      # print(msg.payload)
      j_msg = json.loads(msg.payload.decode('utf-8'))
      print(j_msg)
      accel_x = j_msg['accel'][0]
      accel_y = j_msg['accel'][1]
      accel_z = j_msg['accel'][2]
      # if j_msg['node']==1:

      # plot data
      global count
      count += 1
      data.add(count, accel_x, accel_y,accel_z)
      dataPlotting.plot(data)
      plt.pause(0.001)





# set paho.mqtt callback
client = mqtt.Client()
client.connect("129.217.152.1",8883,60)
client.on_connect = on_connect
client.on_message = on_message

try:
    client.loop_forever()
except KeyboardInterrupt:
    print('disconnect')
    client.disconnect()