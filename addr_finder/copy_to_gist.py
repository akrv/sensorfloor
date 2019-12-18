#!/usr/bin/python

# usage python gist.py ./gist.py [GitHub Username] [GitHub Password]
import os, requests, sys, json

def getMAC(interface='eth0'):
    # Return the MAC address of the specified interface
    try:
        str = open('/sys/class/net/%s/address' % interface).read()
    except:
        str = "00:00:00:00:00:00"
    return str[0:17]


username=sys.argv[1]
password=sys.argv[2]
filename = getMAC()
content=open('node_order.json', 'r').read()
r = requests.post('https://api.github.com/gists',json.dumps({'files':{filename:{"content":content}}}),auth=requests.auth.HTTPBasicAuth(username, password))
print(r.json()['html_url'])