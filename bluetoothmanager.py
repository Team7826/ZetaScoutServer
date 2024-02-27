import bluetooth
import time

def scan(is_zetascout=True):

    nearby_devices = bluetooth.discover_devices(lookup_names=True)

    print(nearby_devices)

    devices = {}

    for addr, name in nearby_devices:

        devices[name] = addr

    return devices

def filter_zetascout(devices):
    filtered = {}

    for device in devices.keys():
        services = bluetooth.find_service(None, None, devices[device])
        for service in services:
            if "C51F17B3-C044-4FE5-A62A-789A3BC92E1C" in service["service-classes"]:
                filtered[device] = service
                break
    return filtered

def connect_service(service):
    sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    sock.connect((service["host"], service["port"]))
    return sock

def recvall(sock):
    BUFF_SIZE = 4096 # 4 KiB
    data = b''
    while True:
        part = sock.recv(BUFF_SIZE)
        data += part
        if len(part) < BUFF_SIZE:
            # either 0 or end of data
            break
    return data