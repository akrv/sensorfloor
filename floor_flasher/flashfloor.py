import os, requests, sys, json, argparse

import aiohttp, asyncio

from aiohttp import ClientSession

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
        print("working: ", RPi['ip_addr'])
        result = send_flash_req(RPi['ip_addr'], filename)


def check_all_services(RPi_IPs):
    for ips in RPi_IPs:
        url = "http://" + ips['ip_addr']
        response = requests.request("GET", url)
        if response.status_code == 200:
            print('success: ', ips['ip_addr'])
        else:
            print('failed: ', ips['ip_addr'])


async def fetch(url, session):
    async with session.get(url) as response:
        response_text = await response.text()
        response_status = response.status
        return (response_status, response_text)


async def post_firmware(url, session, firmwarepath):
    payload = {
        'device': "0",
        'file': open(firmwarepath, 'rb')
    }
    async with session.post(url, data=payload) as response:
        response_text = await response.text()
        response_status = response.status
        return (response_status, response_text)


async def run(type="check", RPi_IPs=RPi_IPs, firmware=None):
    # by default check to disable accidental flash all.
    tasks = []
    if type == "check":
        # Fetch all responses within one Client session,
        # keep connection alive for all requests.
        async with ClientSession() as session:
            for RPI in RPi_IPs:
                url = "http://" + RPI['ip_addr']
                task = asyncio.ensure_future(fetch(url, session))
                tasks.append(task)

            responses = await asyncio.gather(*tasks)
            # you now have all response bodies in this variable
            for i in responses:
                print(i[0])

    elif type == "flashall":
        # flash all concurrently but sending the requests one after the other right after the other
        # keep connection alive for all requests.
        async with ClientSession() as session:
            for RPI in RPi_IPs:
                url = "http://" + RPI['ip_addr']
                task = asyncio.ensure_future(post_firmware(url, session, firmware))
                tasks.append(task)

            responses = await asyncio.gather(*tasks)
            # you now have all response bodies in this variable
            for i in responses:
                print(i)


if __name__ == '__main__':

    print("args")

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
        print(args)
    except:
        print('args provided are wrong')
        # exit()

    if args.check:
        print('Check all services')
        loop = asyncio.get_event_loop()
        future = asyncio.ensure_future(run("check"))
        loop.run_until_complete(future)
        # exit()

    if args.firmware_path is None:
        print('Please provide absolute path file name as arg to flash')
        # exit()brew update && brew upgrade && brew install openssl

    if args.flash_all:
        print('Flashing the whole floor')
        loop = asyncio.get_event_loop()
        future = asyncio.ensure_future(run(type="flashall", RPi_IPs=RPi_IPs, firmware=args.firmware_path))
        loop.run_until_complete(future)
    elif args.strip_id:
        print('Flashing node strip_id:', args.strip_id, 'node_id:', args.node_id)
        send_flash_req(RPi_IPs[args.strip_id - 1]['ip_addr'], args.firmware_path, devices=args.node_id)
    else:
        print("print arg options")
