#!/usr/bin/python3

import os, requests, sys, json
import asyncio
import argparse

from fabfile import RPi_IPs

def send_flash_req(ip_addr, filename, devices=0):
    if filename:
        url = "http://" + ip_addr
        payload = {'device': devices}
        headers = {}
        files = [('file', open(filename, 'rb'))]
        response = requests.request("POST", url, headers=headers, data=payload, files=files)
        if response.status_code == 200:
            return (['success: ', ip_addr])
        else:
            return (['failed: ', ip_addr])
    else:
        return (['error', 'Please provide absolute path file name as arg'])


def flash_coroutine(RPi_IPs, filename):
    for RPi in RPi_IPs:
        print("working: ",RPi['ip_addr'])
        result = send_flash_req(RPi['ip_addr'], filename)


def check_all_services(RPi_IPs):
    for ips in RPi_IPs:
        url = "http://" + ips['ip_addr']
        response = requests.request("GET", url)
        if response.status_code == 200:
            print('success: ', ips['ip_addr'])
        else:
            print('failed: ', ips['ip_addr'])

if __name__ == '__main__':
    # args
    parser = argparse.ArgumentParser()
    parser.add_argument('--firmware-path', type=str)

    parser.add_argument('--check', dest='check', action='store_true')
    parser.set_defaults(check=False)

    parser.add_argument('--flash-all', dest='flash_all', action='store_true')
    parser.add_argument('--flash-one-node', dest='flash_all', action='store_false')
    parser.set_defaults(flash_all=False)

    parser.add_argument('--strip-id', type=int)
    parser.add_argument('--node-id', type=int)

    try:
        args = parser.parse_args()
    except:
        print('args provided are wrong')
        exit()

    if args.check:
        print('Check all services')
        check_all_services(RPi_IPs)
        exit()

    if args.firmware_path is None:
        print('Please provide absolute path file name as arg to flash')
        exit()

    if args.flash_all:
        print('Flashing the whole floor')
        flash_coroutine(RPi_IPs, args.firmware_path)
    else:
        print('Flashing node strip_id:', args.strip_id, 'node_id:', args.node_id)
        send_flash_req(RPi_IPs[args.strip_id-1]['ip_addr'], args.firmware_path, devices=args.node_id)