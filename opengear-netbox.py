#!/usr/bin/env python3

# Find API documentation here: https://ftp.opengear.com/download/documentation/api/cs/og-cs-rest-api-specification-latest.html

import pynetbox
import configparser
import requests
import argparse

config = configparser.ConfigParser()
config.read('config.ini')

parser = argparse.ArgumentParser(
    description='Update the ports on an Opengear serial console with information from Netbox')
parser.add_argument('--console', help='The hostname of the console')
args = parser.parse_args()

session = requests.Session()
session.verify = False
requests.packages.urllib3.disable_warnings()

CONSOLE = args.console
API_BASE_STRING = 'https://' + CONSOLE + '/api/v1.8/'

r = session.post(API_BASE_STRING + 'sessions', json={
    'username': config['opengear']['Username'],
    'password': config['opengear']['Password']
})

r.raise_for_status()
response = r.json()
opengear_token = response['session']

netbox = pynetbox.api(config['netbox']['URI'], config['netbox']['Token'])

ports = netbox.dcim.console_server_ports.filter(device=CONSOLE)
for port in ports:
    port_api_name = port['name'].replace(" ", "").lower()
    if port['connected_endpoints'] is not None and len(port['connected_endpoints']) > 0:
        device_name = port['connected_endpoints'][0]['device']['name']
        print(port_api_name + " connected device: " + device_name)
        port_speed = 115200
        if port.speed is not None:
            port_speed = port.speed.value
        new_serial_port = {
            "serialport": {
                "label": device_name,
                "modeSettings": {
                    "consoleServer": {
                        "ssh": {
                            "enabled": True,
                            "unauthenticated": False
                        },
                        "webShell": {
                            "enabled": True
                        },
                    }
                },
                "mode": "consoleServer",
                "hardwareSettings": {
                    "pinout": "X2",
                    "protocol": "RS232",
                    "uart": {
                        "parity": "none",
                        "baud": str(port_speed),
                        "stopBits": "1",
                        "dataBits": "8",
                        "flowControl": "none",
                        "dtrMode": "alwayson"
                    }
                },
                "logging": {
                    "priority": "Default",
                    "facility": "Default",
                    "level": "access"
                },
            },
        }
        r = session.patch(API_BASE_STRING + 'serialPorts/' + port_api_name, json=new_serial_port, headers={
            'Authorization': 'Token ' + opengear_token
        })
        r.raise_for_status()
        print(r.json())
