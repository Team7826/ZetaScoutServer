import btstatuscodes
import fields
import bluetoothmanager
import threading
import devicewidget

class BluetoothSocket:
    def __init__(self, sock, device_name, port, address):
        self.sock = sock
        
        self.status = ""
        
        self.devicewidget = None
        
        self.device_name = device_name
        self.port = port
        self.address = address

        self.update_thread = threading.Thread(target=self._update)
        self.update_thread.start()
    
    def build_widget(self, master, window):
        self.devicewidget = devicewidget.DeviceWidget(master, window, self.device_name, self.sock, self.port, self.address)
        return self.devicewidget
    
    def _update(self):
        while True:
            print("Receiving data...")
            data = self.recieve_data()
            print(data)
            if data:
                if data == btstatuscodes.GET_FIELDS:
                    self.send_field_data()
                elif data == btstatuscodes.READY_SCOUT:
                    self.status = btstatuscodes.READY_SCOUT
        
    def recieve_data(self):
        return bluetoothmanager.recvall(self.sock).decode()
    
    def send_field_data(self):
        self.sock.send((str(fields.fields) + btstatuscodes.END_RESPONSE).encode())