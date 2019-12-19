import urllib.request
import json

from fabric.api import *



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

for hosts in RPi_IPs:
    env.hosts.append(hosts['ip_addr'])

env.user = "pi"
env.password = "raspberry"

# some stats to printout
success_list = []
error_list = []
env.reject_unknown_hosts = False
def r():
    run('mkdir /home/pi/sensorfloor/flash')

@parallel
def deploy():
    with cd('~/sensorfloor'):
        run('git pull')
        run('sudo cp -rf sensorfloor /var/www/')

@parallel
def webui():
    try:
        with cd('~/sensorfloor'):
            run('git pull')
            run('pip install -r requirements.txt')
        with cd('~/'):
            run('sudo cp sensorfloor/sensorfloor.conf /etc/sites-available')

            run('sudo cp -rf sensorfloor /var/www/')

            run('sudo a2ensite sensorfloor.conf')
            run('sudo systemctl reload apache2')
        success_list.append(env.host)
    except:
        error_list.append(env.host)
    print(error_list)


@parallel
def reboot():
    run('sudo reboot now')

# /Users/akrv/Documents/dev/sensorfloor/imu_app/imu_ti_workspace/imu_data_interrupt/Release/imu_data_interrupt.bin
def flash():
    env.hosts=[]
    # send a post request to port 5000

    url = "http://129.217.152.54"
    payload = {'device':1,
               'file':open('/Users/akrv/Documents/dev/sensorfloor/imu_app/imu_ti_workspace/imu_data_interrupt/Release/imu_data_interrupt.bin', 'wb')
               }
    response = requests.request("POST", url, data=payload)

    print(response.text)

# @parallel
# def setup():
#     # install apache2 and mod-wsgi
#     run('sudo apt-get update')
#     run('sudo apt-get install -y apache2 libapache2-mod-wsgi git libcairo2-dev libjpeg-dev libgif-dev')
#
#     # disable default conf
#     run('sudo a2dissite 000-default.conf')
#
#     with cd('~/'):
#         run('sudo rm -rf sensorfloor')
#         # git clone
#         run('git clone --recurse-submodules http://github.com/akrv/sensorfloor')
#         # copy conf and the rest of the folder
#         run('sudo cp sensorfloor/sensorfloor.conf /etc/apache2/sites-available')
#
#         # copy to www folder the source code
#         run('sudo cp -rf sensorfloor /var/www/')
#     with cd('~/sensorfloor'):
#         run('pip install -r requirements.txt')
#     # enable site
#     run('sudo a2ensite sensorfloor.conf')
#     run('sudo systemctl reload apache2')
