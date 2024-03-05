import btstatuscodes
import fields
import bluetoothmanager
import threading
import devicewidget
import dictutil
import json

class BluetoothSocket:
    NULL_DATA_RECV_COUNT_THRESHOLD = 5
    def __init__(self, sock, device_name, port, address, device_widget = None):
        self.sock = sock

        self.status = ""

        self.devicewidget = device_widget

        self.device_name = device_name
        self.port = port
        self.address = address

        self.active = self.sock != None

        self.scouting_end_callback = None

        self.recieved_scout_data = None

        self.team_scouting = None
        self.match_scouting = None

        self.null_data_recv_count = 0 # Increments when we receive nothing

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
                    print("Sending data...")
                    self.send_field_data()
                elif data == btstatuscodes.READY_SCOUT:
                    self.status = btstatuscodes.READY_SCOUT
                elif data == btstatuscodes.FINISHED_SCOUTING:
                    self.recieved_scout_data = self.receive_until(btstatuscodes.END_RESPONSE)
                    print(self.recieved_scout_data)
                    self.recieved_scout_data = dictutil.calculate_nested_dict_percentages(json.loads(self.recieved_scout_data))
                    self.send_data("")
                    self.scouting_end_callback(self.team_scouting, self.match_scouting, self.recieved_scout_data)
            else:
                self.null_data_recv_count += 1
                if self.null_data_recv_count > self.NULL_DATA_RECV_COUNT_THRESHOLD:
                    self.active = False

        print(self.devicewidget.window.sockets)
        self.devicewidget.window.sockets.remove(self)

        try:
            self.sock.close()
        except: pass

        self.devicewidget.socket = None
        self.devicewidget.update_button()

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
        print("Sending data on socket: " + str(data))
        self.sock.send((str(data) + btstatuscodes.END_RESPONSE).encode())
        print("Sent.")

    def send_field_data(self):
        self.send_data(fields.fields)

    def close(self):
        self.send_data(btstatuscodes.CLOSE_APPLICATION)
        if self.sock: self.sock.close()
        self.active = False