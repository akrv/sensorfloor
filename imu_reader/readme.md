**How to start data mesaurement**
using the FLW-NUC or the robot nuc in the hall


  `cd ~/sensorfloor`<br />
is where the repo is available <br />

**Collecting Vicon data:** <br />
start vicon data after starting ros core and roslaunch vicon_bridge
cd ~/sensorfloor/imu_reader<br />
python listener.py <br />
this will create a vicon_data.txt file with line delimited json objects which contain a reading with timestamp from the local machine.<br />

**Collecting imu data**<br />
cd ~/sensorfloor/imu_reader
python live_plotter.py<br />
this will create a file test_data.txt with json per reading per node timestampped at the RPi<br />
it will only start to populate after the next step.

**starting imu data**<br />
cd ~/sensorfloor/floor_flasher<br />
fab imuread<br />
this fab recipe will block the terminal and this need to be alive to run the programs on all the RPi hosts.

**Latency measurements for looping through the strip**<br/>
  3.8s latency with 7Hz sample rate <br />
  {'interrupt': 0.09613079603026513,<br/>
 'parsing': 0.000125336809223201,<br/>
 'publish': 0.001433641732144518,<br/>
 'rs422': 0.006461214208278526,<br/>
 'switching': 0.1287158135654164}<br/>
