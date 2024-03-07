import json
from bluetoothsocket import BluetoothSocket
from btpairdialog import BTPairDialog
import btstatuscodes
import config
import comp
import customtkinter
from devicewidget import DeviceWidget
import tba
import competitiondialog
import matchwidget
import bluetoothmanager
import fields
import devices
import scouted
import dictutil
import analyzer
from PIL import Image, ImageTk
from _tkinter import TclError

customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("dark-blue")

class Window:
    def __init__(self):
        self.app = customtkinter.CTk()
        def set_maximized():
            try:
                self.app.state('zoomed')
            except TclError as e: pass

        self.app.after(0, set_maximized)
        self.app.title("ZetaScout")
        icon = Image.open("zetascout.ico")
        photo = ImageTk.PhotoImage(icon)
        self.app.wm_iconphoto(True, photo)

        self.tba = None # To be initialized later
        self.sockets = []
        self.old_devices = {}
        self.current_match = -1 # -1 means no match
        self.match_currently_scouting = -1 # Still, -1 means no match
        self.scouting = []

        self.points_autonomous = []
        self.points_teleop = []
        self.points_total = []

        self.compiled_team_data = {}

        self.add_widgets()

        self.app.rowconfigure(0, weight=1)
        self.app.grid_columnconfigure(1, weight=2)

        if "matches" in scouted.scouted.keys():
            last_match = len(scouted.scouted["matches"])
            self.current_match = last_match - 1
        else:
            scouted.scouted["matches"] = []

        self.refresh_tba_status()
        self.refresh_comp_status()
        self.refresh_old_device_list()
        self.refresh_match_status()

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

        self.startMatch = customtkinter.CTkButton(deviceFrame, text="Start match -", font=subheaderFont)
        self.startMatch.grid(row=3, column=0, sticky="EW")

        deviceStatus = customtkinter.CTkFrame(deviceFrame)
        deviceStatus.grid(row=4, column=0, sticky="EW")



        ### END DEVICE FRAME

        ### DATA FRAME
        dataFrame = customtkinter.CTkFrame(self.app, corner_radius=8)
        dataFrame.grid(row=0, column=1, padx=10, pady=10, sticky="NSEW")
        dataFrame.grid_columnconfigure(0, weight=1)
        dataFrame.grid_rowconfigure(1, weight=1)

        selectedTeamFrame = customtkinter.CTkFrame(dataFrame, corner_radius=0)
        selectedTeamFrame.grid(row=0, column=0, sticky="EW")

        selectedTeamFrame.grid_columnconfigure(1, weight=1)

        self.teamSelector = customtkinter.CTkOptionMenu(selectedTeamFrame, values=["-"], command=lambda e: self.select_team())
        self.teamSelector.grid(row=0, column=0)

        self.teamName = customtkinter.CTkLabel(selectedTeamFrame, text="SCOUTED DATA", font=subheaderFont)
        self.teamName.grid(row=0, column=1)

        # Team data section
        teamDataFrame = customtkinter.CTkFrame(dataFrame, corner_radius=0)
        teamDataFrame.grid(row=1, column=0, sticky="NSEW")

        teamDataFrame.grid_columnconfigure(0, weight=1)
        teamDataFrame.grid_rowconfigure(1, weight=1)

        averagesFrame = customtkinter.CTkFrame(teamDataFrame)
        averagesFrame.grid(row=0, column=0, sticky="NEW")

        averagesFrame.grid_columnconfigure(0, weight=1)
        averagesFrame.grid_columnconfigure(1, weight=1)
        averagesFrame.grid_columnconfigure(2, weight=1)

        averagePointsHeader = customtkinter.CTkLabel(averagesFrame, text="Average Points", font=subheaderFont)
        averagePointsHeader.grid(row=0, column=0)

        self.averagePoints = customtkinter.CTkLabel(averagesFrame, text="-", font=headerFont)
        self.averagePoints.grid(row=1, column=0)

        averagePointsAnalyze = customtkinter.CTkButton(averagesFrame, text="Analyze", font=headerFont, command=lambda: analyzer.spawn_analyzer("Average Points", self.points_total))
        averagePointsAnalyze.grid(row=2, column=0)

        averagePointsAutonomousHeader = customtkinter.CTkLabel(averagesFrame, text="Autonomous", font=subheaderFont)
        averagePointsAutonomousHeader.grid(row=0, column=1)

        self.averagePointsAutonomous = customtkinter.CTkLabel(averagesFrame, text="-", font=headerFont)
        self.averagePointsAutonomous.grid(row=1, column=1)

        averagePointsAutonomousAnalyze = customtkinter.CTkButton(averagesFrame, text="Analyze", font=headerFont, command=lambda: analyzer.spawn_analyzer("Average Points Autonomous", self.points_autonomous))
        averagePointsAutonomousAnalyze.grid(row=2, column=1)

        averagePointsTeleopHeader = customtkinter.CTkLabel(averagesFrame, text="Teleop", font=subheaderFont)
        averagePointsTeleopHeader.grid(row=0, column=2)

        self.averagePointsTeleop = customtkinter.CTkLabel(averagesFrame, text="-", font=headerFont)
        self.averagePointsTeleop.grid(row=1, column=2)

        averagePointsTeleopAnalyze = customtkinter.CTkButton(averagesFrame, text="Analyze", font=headerFont, command=lambda: analyzer.spawn_analyzer("Average Points Teleop", self.points_teleop))
        averagePointsTeleopAnalyze.grid(row=2, column=2)

        self.averagePointsFrame = customtkinter.CTkScrollableFrame(teamDataFrame)
        self.averagePointsFrame.grid(row=1, column=0, sticky="NSEW")

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

        self.analyzerBuilder = customtkinter.CTkButton(matchFrame, text="Advanced Analyzer", command=lambda: analyzer.spawn_analyzer_creator(self.compiled_team_data))
        self.analyzerBuilder.grid(row=5, column=0)

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



    def refresh_team_data(self):
        self.compiled_team_data = dictutil.compile_team_data(scouted.scouted["matches"])
        print(self.compiled_team_data)
        self.teamSelector.configure(values=self.compiled_team_data.keys())

    def select_competition(self):
        if self.tba is not None:
            print("Waiting...")
            data, matches_raw = competitiondialog.CompetitionDialog(self.tba).show()
            print(matches_raw)
            print("Processing matches...")
            matches = []
            matches_raw = sorted(matches_raw, key=lambda d: d["match_number"])
            for match in matches_raw:
                if match["comp_level"] != "qm": continue
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
            self.refresh_match_status()

    def refresh_match_status(self):
        if not comp.comp["matches"]:
            self.matchNumber.configure("Match #-")
            self.startMatch.configure(text="Start match -")
        if len(scouted.scouted.keys()) == 0:
            scouted.scouted["matches"] = []
        self.matchNumber.configure(text="Match #" + str(self.current_match + 1))

        if self.match_currently_scouting == -1:
            self.startMatch.configure(text="Start match " + str(self.current_match + 2), command=self.start_next_match)
        else:
            self.startMatch.configure(text="Force end match", command=self.end_scouting_match)

        self.refresh_team_data()

    def start_next_match(self):
        self.select_match(self.current_match + 1)

    def socket_end_scouting_match(self, competitor, match, data):
        print(self.scouting)
        self.scouting.remove(competitor)
        print("Got data for " + competitor + " in " + str(match) + ": " + str(data))

        while len(scouted.scouted["matches"]) < match+1:
            scouted.scouted["matches"].append({})

        scouted.scouted["matches"][match][competitor] = data

        if len(self.scouting) == 0:
            print("No more teams to scout!")
            self.end_scouting_match()

        scouted.save()

    def end_scouting_match(self):
        print("Done")
        self.match_currently_scouting = -1
        self.refresh_match_status()

    def pair_device(self):
        sockets = BTPairDialog(self).show()
        for socket, device_name, port, address in sockets:
            devices.devices["paired"][device_name] = [address, port]
            socket = self.create_socket(socket, device_name, port, address, None)
            devicewidget = socket.build_widget(self.deviceList, self)
            devicewidget.pack(anchor="n")
        devices.save()

    def create_socket(self, socket, device_name, port, address, device_widget):
        socket = BluetoothSocket(socket, device_name, port, address, device_widget)
        self.sockets.append(socket)
        return socket

    def refresh_old_device_list(self):
        if len(self.old_devices.keys()) == 0:
            for device in devices.devices["paired"].keys():
                device_data = devices.devices["paired"][device]
                widget = DeviceWidget(self.deviceList, self, device, None, device_data[1], device_data[0])
                widget.pack(anchor="n")
                self.old_devices[device] = widget

    def refresh_comp_status(self):
        print("Configuring...")
        if comp.comp.get("name", None) is None: return
        self.competitionName.configure(text=comp.comp["name"])
        self.competitionSelect.configure(text="Change")

        for child in self.matchList.winfo_children():
            child.destroy()

        i = 1
        for match in comp.comp["matches"]:
            matchWidget = matchwidget.MatchWidget(self.matchList, self, i, self.select_match)
            matchWidget.grid(row=i-1, column=0)
            i += 1
        print("Done")

    def select_match(self, match):
        self.current_match = match
        self.match_currently_scouting = self.current_match
        self.scouting = []
        competitors_raw = comp.comp["matches"][self.current_match]
        competitors = competitors_raw[0] + competitors_raw[1]

        if len(scouted.scouted["matches"]) > self.current_match:
            for competitor in scouted.scouted["matches"][self.current_match].keys():
                try: competitors.remove(competitor)
                except ValueError: pass
        i = 0
        for socket in self.sockets:
            if socket.status == btstatuscodes.READY_SCOUT:

                try: competitor = competitors[i]
                except IndexError: break

                socket.team_scouting = competitor
                socket.match_scouting = self.current_match
                socket.set_scouting_end_callback(lambda competitor, match, data: self.socket_end_scouting_match(competitor, match, data))
                socket.send_data(("B" if i < 3 else "R") + competitor)
                self.scouting.append(competitor)
                i += 1

        self.refresh_match_status()

    def select_team(self):

        for child in self.averagePointsFrame.winfo_children():
            child.destroy()

        team = self.teamSelector.get()
        team_data = self.compiled_team_data[team]
        print(team)
        print(self.compiled_team_data[team])
        self.points_autonomous, self.points_teleop, self.points_total = dictutil.calculate_points(team_data)
        average_autonomous, average_teleop, average_total = dictutil.calculate_point_averages(self.points_autonomous, self.points_teleop, self.points_total)

        self.averagePoints.configure(text=average_total)
        self.averagePointsAutonomous.configure(text=average_autonomous)
        self.averagePointsTeleop.configure(text=average_teleop)

        average_elements = dictutil.recursively_average_all_values(team_data)

        dictutil.recursively_generate_match_data_frame(self.averagePointsFrame, average_elements,
                                                       headerFont = customtkinter.CTkFont(size=30),
                                                       titleFont = customtkinter.CTkFont(size=25),
                                                       numberFont = customtkinter.CTkFont(size=25))

    def run(self):
        self.app.mainloop()

if __name__ == "__main__":
    window = Window()
    window.run()
    print("Closing sockets...")
    for socket in window.sockets:
        socket.close()