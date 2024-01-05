import tkinter
import customtkinter

class PairableDeviceWidget(customtkinter.CTkFrame):
    def __init__(self, master, window, device_name, service, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        
        self.font = customtkinter.CTkFont(size=20)
        
        self.devicePairCheck = customtkinter.CTkCheckBox(self, text="Pair")
        self.devicePairCheck.grid(row=0, column=0)
        
        self.deviceName = customtkinter.CTkLabel(self, text=str(device_name), font=self.font)
        self.deviceName.grid(row=0, column=1)
        
        self.service = service