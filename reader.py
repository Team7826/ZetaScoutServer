from ppadb.client import Client as AdbClient
import os
import json

os.system("./adb start-server")

def connect():
    client = AdbClient(host="127.0.0.1", port=5037) # Default is "127.0.0.1" and 5037

    devices = client.devices()

    if len(devices) == 0:
        print('No devices')
        raise Exception("no device connected")

    device = devices[0]

    print(f'Connected to {device}')

    return device, client

def get_data():
    device, client = connect()

    data = device.shell('cat /storage/emulated/0/Documents/zetascout.json')
    data = json.loads(data)
    return data

def remove_data():
    device, client = connect()

    device.shell('rm /storage/emulated/0/Documents/zetascout.json')

if __name__ == '__main__':
    print(get_data())
    