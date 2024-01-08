import customtkinter
from bluetoothsocket import BluetoothSocket
from pairabledevicewidget import PairableDeviceWidget
import bluetoothmanager
import threader
import fields
import btstatuscodes

class BTPairDialog:
    
    def __init__(self, window):
        self.app = customtkinter.CTk()
        self.app.geometry("450x350")
        self.app.title("Pair New Device...")
        self.window = window
        
        self.sockets = []
        
        self.status = customtkinter.CTkLabel(self.app, text="Make sure that ZetaScout is open and on the pairing screen before continuing")
        self.status.pack(anchor="s")
        
        self.searchButton = customtkinter.CTkButton(self.app, text="Search", command=lambda: threader.run_as_thread(self.find_devices, self.found_devices, lambda: self.show_status("Searching...")))
        self.searchButton.pack(anchor="n")
        
        self.deviceList = customtkinter.CTkScrollableFrame(self.app)
        self.deviceList.pack(anchor="s")
        
        self.pairButton = customtkinter.CTkButton(self.app, text="Pair", command=lambda: self.app.after(0, self.complete_pair))
        self.pairButton.pack(anchor="s")
    
    
    def show_status(self, status, is_error=False):
        self.status.configure(text=status, text_color=("red" if is_error else "white"))
        
    def find_devices(self):
        return bluetoothmanager.scan()
        
    def pair_devices(self):
        addresses = []
        buttons = self.deviceList.winfo_children()
        for button in buttons:
            if button.devicePairCheck.get():
                addresses.append((button.service, button.deviceName.cget("text")))
        
        sockets = []
        for address, device_name in addresses:
            sock = bluetoothmanager.connect_service(address)
            sockets.append((sock, device_name, address["port"], address["host"]))
        
        return sockets
    
    def found_devices(self, devices):
        threader.run_as_thread(lambda: bluetoothmanager.filter_zetascout(devices), self.refresh_devices, lambda: self.show_status("Filtering out non-ZetaScout devices..."))
    
    def refresh_devices(self, devices):
        for child in self.deviceList.winfo_children():
            child.destroy()
        
        for device in devices.keys():
            deviceWidget = PairableDeviceWidget(self.deviceList, self, device, devices[device])
            deviceWidget.pack(anchor="n")
        
        self.show_status("Select devices to pair to.")

    def pairing(self):
        pass
    
    def complete_pair(self):
        self.sockets = self.pair_devices()
        self._close()
    
    def _close(self):
        self.app.quit()
        self.app.destroy()
        
    def show(self):
        self.app.mainloop()
        return self.sockets
        

if __name__ == "__main__":
    d = BTPairDialog()
    print(d.show())