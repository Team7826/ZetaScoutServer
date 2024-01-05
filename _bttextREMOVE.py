# simple inquiry example
import bluetoothmanager

nearby_devices = bluetoothmanager.discover_devices(lookup_names=True)

address = None
devices = {}
for addr, name in nearby_devices:
    print(name, addr)
    devices[name] = addr
    if name == "Vivo XI":
        address = addr

#address = devices[input(">")]

print(address)

services = bluetoothmanager.find_service(None, None, address)

if len(services) > 0:
    print("Found {} services on {}.".format(len(services), address))
else:
    print("No services found.")

service = None

for svc in services:
    if "C51F17B3-C044-4FE5-A62A-789A3BC92E1C" in svc["service-classes"]:
        service = svc
        break

if service is None:
    print("ZetaScout service no present")

sock = bluetoothmanager.BluetoothSocket(bluetoothmanager.RFCOMM)
sock.connect((service["host"], service["port"]))

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

print("Connected. Type something...")
while True:
    print(recvall(sock).decode())
    sock.send("Elijah eats infants END_RESPONSE".encode())

sock.close()