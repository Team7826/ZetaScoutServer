import tkinter
import customtkinter
import devices
import bluetoothmanager
from PIL import Image

class DeviceWidget(customtkinter.CTkFrame):
    def __init__(self, master, window, device_name="Unknown device", socket=None, port=None, address=None, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        
        self.font = customtkinter.CTkFont(size=20)
        
        self.thumbnail = customtkinter.CTkImage(Image.open("zs device.png"), size=(500/10, 677/10))
        self.thumbnail_label = customtkinter.CTkLabel(self, image=self.thumbnail, text="")
        self.thumbnail_label.grid(row=0, column=0)
        
        self.deviceName = customtkinter.CTkLabel(self, text=str(device_name), font=self.font)
        self.deviceName.grid(row=0, column=1)
        
        self.actionButton = customtkinter.CTkButton(self, text="...", font=self.font)
        self.actionButton.grid(row=1, column=1)
        
        self.socket = socket
        self.port = port
        self.address = address
        self.window = window
        
        self.update_button()
    
    def update_button(self):
        self.actionButton.configure(text="Disconnect" if self.socket else "Reconnect", command=self.disconnect if self.socket else self.connect)
    
    def connect(self):
        service_list = bluetoothmanager.filter_zetascout({self.deviceName.cget("text"): self.address})
        try:
            service = service_list[self.deviceName.cget("text")]
        except KeyError:
            return
        self.socket = bluetoothmanager.connect_service(service)
        self.window.create_socket(self.socket, self.deviceName.cget("text"), self.port, self.address)
        self.update_button()
    
    def disconnect(self):
        self.socket.close()
        del devices.devices["paired"][self.deviceName.cget("text")]
        self.destroy()