from btpairdialog import BTPairDialog
import config
import comp
import customtkinter
import tba
import competitiondialog
import matchwidget

customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("dark-blue")

class Window:
    def __init__(self):
        self.app = customtkinter.CTk()
        self.app.geometry("800x400")
        self.app.title("ZetaScout")
        self.app.iconbitmap("zetascout.ico")
        
        self.tba = None # To be initialized later

        self.add_widgets()

        self.app.rowconfigure(0, weight=1)
        self.app.grid_columnconfigure(1, weight=2)
        
        self.refresh_tba_status()
        self.refresh_comp_status()

    def add_widgets(self) -> None:

        headerFont = customtkinter.CTkFont(size=40)
        subheaderFont = customtkinter.CTkFont(size=25)
        largeFont = customtkinter.CTkFont(size=14)

        ### DEVICE FRAME
        deviceFrame = customtkinter.CTkFrame(self.app, corner_radius=0)
        deviceFrame.grid(row=0, column=0, padx=0, pady=0, sticky="NSW")

        deviceHeader = customtkinter.CTkLabel(deviceFrame, text="DEVICES", font=headerFont)
        deviceHeader.grid(row=0, column=0, sticky="NEW")

        self.deviceList = customtkinter.CTkScrollableFrame(deviceFrame)
        self.deviceList.grid(row=1, column=0, sticky="NSEW", pady=10)
        deviceFrame.grid_rowconfigure(1, weight=1)

        addDevice = customtkinter.CTkButton(self.deviceList, text="+", command=self.pair_device)
        addDevice.pack(fill="x")

        self.matchNumber = customtkinter.CTkLabel(deviceFrame, text="Match #-", font=subheaderFont)
        self.matchNumber.grid(row=2, column=0, sticky="EW")

        deviceStatus = customtkinter.CTkFrame(deviceFrame)
        deviceStatus.grid(row=3, column=0, sticky="EW")
        deviceStatus.grid_columnconfigure(0, weight=1)

        self.deviceOperation = customtkinter.CTkLabel(deviceStatus, text="Idle", font=subheaderFont)
        self.deviceOperation.grid(row=0, column=0)

        self.operationProgress = customtkinter.CTkLabel(deviceStatus, text="--%", font=headerFont)
        self.operationProgress.grid(row=1, column=0)

        self.devicesLeft = customtkinter.CTkLabel(deviceStatus, text="- left", font=largeFont)
        self.devicesLeft.grid(row=0, column=1, sticky="NE")

        self.devicesQueued = customtkinter.CTkLabel(deviceStatus, text="- queued", font=largeFont)
        self.devicesQueued.grid(row=1, column=1, sticky="SE")

        self.operationProgressBar = customtkinter.CTkProgressBar(deviceFrame)
        self.operationProgressBar.grid(row=4, column=0, sticky="SEW")
        self.operationProgressBar.set(10)

        ### END DEVICE FRAME

        ### DATA FRAME
        dataFrame = customtkinter.CTkFrame(self.app, corner_radius=8)
        dataFrame.grid(row=0, column=1, padx=10, pady=10, sticky="NSEW")
        dataFrame.grid_columnconfigure(0, weight=1)
        
        selectedTeamFrame = customtkinter.CTkFrame(dataFrame)
        selectedTeamFrame.grid(row=0, column=0, sticky="EW")
        
        selectedTeamFrame.grid_columnconfigure(1, weight=1)
        
        self.teamSelector = customtkinter.CTkOptionMenu(selectedTeamFrame, values=["-"])
        self.teamSelector.grid(row=0, column=0)
        
        self.teamName = customtkinter.CTkLabel(selectedTeamFrame, text="-", font=subheaderFont)
        self.teamName.grid(row=0, column=1)

        ### END DATA FRAME

        ### MATCH FRAME
        
        matchFrame = customtkinter.CTkFrame(self.app, corner_radius=0)
        matchFrame.grid(row=0, column=2, padx=0, pady=0, sticky="NSE")
        
        matchFrame.grid_columnconfigure(0, weight=1)
        
        matchHeader = customtkinter.CTkLabel(matchFrame, text="COMPETITION", font=headerFont)
        matchHeader.grid(row=0, column=0)
        
        blueAllianceStatus = customtkinter.CTkFrame(matchFrame, corner_radius=0)
        blueAllianceStatus.grid(row=1, column=0, sticky="EW")
        blueAllianceStatus.grid_columnconfigure(0, weight=1)
        
        self.blueAllianceLabel = customtkinter.CTkLabel(blueAllianceStatus, text="TBA is -", font=largeFont)
        self.blueAllianceLabel.grid(row=0, column=0)
        
        self.blueAllianceButton = customtkinter.CTkButton(blueAllianceStatus, text="Set API Key", command=self.set_tba_api_key)
        self.blueAllianceButton.grid(row=0, column=1)
        
        competitionFrame = customtkinter.CTkFrame(matchFrame, corner_radius=0)
        competitionFrame.grid(row=2, column=0, sticky="EW")
        
        competitionFrame.grid_columnconfigure(0, weight=1)
        
        self.competitionName = customtkinter.CTkLabel(competitionFrame, text="No Competition", font=largeFont)
        self.competitionName.grid(row=0, column=0, sticky="EW")
        
        self.competitionSelect = customtkinter.CTkButton(competitionFrame, text="Select", command=self.select_competition)
        self.competitionSelect.grid(row=0, column=1, sticky="NSE")
        
        self.matchListLabel = customtkinter.CTkLabel(matchFrame, text="Matches", font=subheaderFont)
        self.matchListLabel.grid(row=3, column=0, sticky="EW")
        
        self.matchList = customtkinter.CTkScrollableFrame(matchFrame)
        self.matchList.grid(row=4, column=0)
        
        ### END MATCH FRAME
    
    def refresh_tba_status(self):
        if tba.get_has_key():
            self.blueAllianceLabel.configure(text="TBA is ready!")
            self.blueAllianceButton.configure(text="Change API Key")
            self.tba = tba.TBA()
        else:
            self.blueAllianceLabel.configure(text="TBA is not ready!")
            self.blueAllianceButton.configure(text="Set API Key")
    
    def set_tba_api_key(self):
        message = "Please paste your API key here:"
        valid = False
        while not valid:
            dialog = customtkinter.CTkInputDialog(text=message, title="API Key")
            result = dialog.get_input().strip()
            if result is None or result == "":
                return
            config.config["thebluealliance"]["apikey"] = result
            config.save()
            try:
                self.tba = tba.TBA()
                valid = True
            except tba.TBAKeyInvalidError:
                message = "That API key was invalid!"
        
        self.refresh_tba_status()
    
    def select_competition(self):
        if self.tba is not None:
            print("Waiting...")
            data, matches_raw = competitiondialog.CompetitionDialog(self.tba).show()
            print("Processing matches...")
            matches = []
            for match in matches_raw:
                matches.append(
                    (
                        match["alliances"]["blue"]["team_keys"],
                        match["alliances"]["red"]["team_keys"]
                    )
                )
            comp.comp["matches"] = matches
            comp.comp["name"] = data["event_code"]
            comp.save()
            print("Saved.")
            self.refresh_comp_status()
    
    def pair_device(self):
        sockets = BTPairDialog(self).show()
        print(sockets)
    
    def refresh_comp_status(self):
        print("Configuring...")
        if comp.comp.get("name", None) is None: return
        self.competitionName.configure(text=comp.comp["name"])
        self.competitionSelect.configure(text="Change")
        
        for child in self.matchList.winfo_children():
            child.destroy()
        
        i = 1
        for match in comp.comp["matches"]:
            matchWidget = matchwidget.MatchWidget(self.matchList, self, i)
            matchWidget.grid(row=i-1, column=0)
            i += 1
        print("Done")
        
    def run(self):
        self.app.mainloop()

if __name__ == "__main__":
    window = Window()
    window.run()