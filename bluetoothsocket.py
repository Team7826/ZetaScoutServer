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
        
        self.active = self.sock != None
        
        self.scouting_end_callback = None
        
        self.recieved_scout_data = None

        self.update_thread = threading.Thread(target=self._update)
        self.update_thread.start()
    
    def set_scouting_end_callback(self, callback):
        self.scouting_end_callback = callback
    
    def build_widget(self, master, window):
        self.devicewidget = devicewidget.DeviceWidget(master, window, self.device_name, self.sock, self.port, self.address)
        return self.devicewidget
    
    def _update(self):
        while self.active:
            print("Receiving data...")
            data = self.recieve_data()
            print(data)
            if data:
                if data == btstatuscodes.GET_FIELDS:
                    self.send_field_data()
                elif data == btstatuscodes.READY_SCOUT:
                    self.status = btstatuscodes.READY_SCOUT
                elif data == btstatuscodes.FINISHED_SCOUTING:
                    self.recieved_scout_data = self.receive_until(btstatuscodes.END_RESPONSE)
                    print(self.recieved_scout_data)
                    self.send_data("")
                    self.scouting_end_callback(self.recieved_scout_data)
        
    def recieve_data(self):
        return bluetoothmanager.recvall(self.sock).decode()

    def receive_until(self, end):
        data = ""
        while True:
            data += self.recieve_data()
            print(data)
            if data.endswith(end):
                return data.rstrip(end)
    
    def send_data(self, data):
        self.sock.send((str(data) + btstatuscodes.END_RESPONSE).encode())
    
    def send_field_data(self):
        self.send_data(fields.fields)
    
    def close(self):
        self.send_data(btstatuscodes.CLOSE_APPLICATION)
        if self.sock: self.sock.close()
        self.active = False