import json

devices = {}

with open("devices.json", "r") as devices_file:
    devices = json.loads(devices_file.read())

def save():
    with open("devices.json", "w") as devices_file:
        devices_file.write(json.dumps(devices))