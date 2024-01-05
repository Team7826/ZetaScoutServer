import bluetooth

def scan(is_zetascout=True):

    nearby_devices = bluetooth.discover_devices(lookup_names=True)

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