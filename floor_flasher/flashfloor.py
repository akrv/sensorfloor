import os, requests, sys, json
import asyncio

from floor_flasher.fabfile import RPi_IPs

if len(sys.argv) > 1:
    if sys.argv[1] == 'check':
        check = True
    else:
        filename = sys.argv[1]
else:
    print('Please provide absolute path file name as arg to flash')
    print('check will check if all services are up')


def send_flash_req(RPi_IPs, filename, devices=0):
    if filename:
        for ips in RPi_IPs:
            url = "http://" + ips['ip_addr']
            payload = {'device': devices}
            headers = {'content-type': "multipart/form-data;"}
            response = requests.request("POST", url, data=payload, files={'file': open(filename, 'rb')},
                                        headers=headers)
            if response.status_code == 200:
                print('success: ', ips['ip_addr'])
            else:
                print('failed: ', ips['ip_addr'])
    else:
        print('Please provide absolute path file name as arg')


def check_all_services(RPi_IPs):
    for ips in RPi_IPs:
        url = "http://" + ips['ip_addr']
        response = requests.request("GET", url)
        if response.status_code == 200:
            print('success: ', ips['ip_addr'])
        else:
            print('failed: ', ips['ip_addr'])


if check:
    check_all_services(RPi_IPs)
else:
    send_flash_req(RPi_IPs, filename)
