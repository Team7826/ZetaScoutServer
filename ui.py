import copy as np
import json
import tkinter as tk
from reader import get_data, remove_data
from graphs.linegraph import LineGraph

class UI:
    COLOR_SCHEME = { # we should make this customiazble
        "background": "#181818",
        "background-secondary": "#212121",
        "foreground": "#ffffff",
        "foreground-secondary": "#aaaaaa"
    }

    def __init__(self):
        self.data = {}

        self.selected_team = None

        self.loaded_team_data = {}

        try:
            with open("data.json", "r") as data_file:
                self.data = json.loads(data_file.read())
        except json.JSONDecodeError as e:
            print("Read error")
            self.data = {}        

        self.window = tk.Tk()
        self.window.geometry("1200x600")
        self.window.rowconfigure(0, weight=1)
        self.window.columnconfigure(1, weight=1)
        self.add_widgets()

        
    
    def add_widgets(self):

        # Left Pane
        self.left_pane_width = 300
        self.left_pane = tk.PanedWindow(self.window, bg=self.COLOR_SCHEME["background"], width=self.left_pane_width)
        self.left_pane.grid(row=0, column=0, sticky="nsw")
        self.left_pane.rowconfigure(1, weight=1)
        self.left_pane.columnconfigure(0, weight=1)
        self.left_pane.columnconfigure(1, weight=2)

        # Data Load Pane
        self.data_load_pane = tk.PanedWindow(self.left_pane, bg=self.COLOR_SCHEME["background"], width=self.left_pane_width)
        self.data_load_pane.grid(row=0, column=0, sticky="nsew")

        # load data title
        self.data_load_header = tk.Label(self.data_load_pane, font=("Arial", 18), bg=self.COLOR_SCHEME["background"], fg=self.COLOR_SCHEME["foreground"], text="Load Data")
        self.data_load_header.grid(row=0, column=0, columnspan=2, sticky="ew")

        # match # label / input box
        self.match_no_label = tk.Label(self.data_load_pane, font=("Arial", 12), bg=self.COLOR_SCHEME["background"], fg=self.COLOR_SCHEME["foreground"], text="Match #")
        self.match_no_selector = tk.Entry(self.data_load_pane, bg=self.COLOR_SCHEME["background-secondary"], fg=self.COLOR_SCHEME["foreground"], border=0, borderwidth=0, validate="all", validatecommand=(self.window.register(lambda p: str.isdigit(p) or p==""), "%P"))
        self.match_no_selector.insert(tk.END, 1)

        self.match_no_label.grid(row=1, column=0, sticky="nsw")
        self.match_no_selector.grid(row=1, column=1, sticky="nse")

        # match load + clear buttons
        self.match_load_button = tk.Button(self.data_load_pane, bg=self.COLOR_SCHEME["background-secondary"], fg=self.COLOR_SCHEME["foreground"], text="Load From Device", border=0, borderwidth=0, command=self.load_data)
        self.match_load_button.grid(row=2, column=0, pady=10, padx=10)
        self.clear_device_button = tk.Button(self.data_load_pane, bg=self.COLOR_SCHEME["background-secondary"], fg=self.COLOR_SCHEME["foreground"], text="Clear From Device", border=0, borderwidth=0, command=self.rm_data)
        self.clear_device_button.grid(row=2, column=1, pady=10, padx=10)
        
        # operation output???
        self.output_header = tk.Label(self.data_load_pane, font=("Arial", 12), bg=self.COLOR_SCHEME["background"], fg=self.COLOR_SCHEME["foreground"], text="Output")
        self.output_header.grid(row=3, column=0, columnspan=2, sticky="ew")
        
        self.output_text = tk.Text(self.data_load_pane, font=("Arial", 10), bg=self.COLOR_SCHEME["background"], fg=self.COLOR_SCHEME["foreground"], height=5, width=9, border=0, borderwidth=0)
        self.output_text.grid(row=4, column=0, columnspan=2, sticky="ew")
        self.output_text.insert(tk.END, "Perform an operation to get output.\n")
        self.output_text.config(state=tk.DISABLED)
    

        # Team Pane
        self.teams_pane = tk.Listbox(self.left_pane, fg="#FFFFFF", bg=self.COLOR_SCHEME["background-secondary"])
        self.teams_pane.grid(row=1, column=0, sticky="nsew")
        #self.teams_pane.grid_columnconfigure(0, weight=1)
        self.teams_pane_scroll = tk.Scrollbar(self.teams_pane, bg=self.COLOR_SCHEME["foreground"], border=0)
        self.teams_pane_scroll.pack(side="right", fill="y")

        self.teams_pane_scroll.config(command=self.teams_pane.yview)
        self.teams_pane.config(yscrollcommand=self.teams_pane_scroll.set)
        self.teams_pane.bind("<<ListboxSelect>>", self.show_team)

        # Right Pane
        self.right_pane = tk.PanedWindow(self.window, bg=self.COLOR_SCHEME["background"], width=300)
        self.right_pane.grid(row=0, column=2, sticky="nse")

        # Middle Pane
        self.mid_pane = tk.PanedWindow(self.window, bg=self.COLOR_SCHEME["background-secondary"])
        self.mid_pane.grid(row=0, column=1, sticky="nsew")

        self.mid_pane.columnconfigure(0, weight=1)

        self.selected_team_header = tk.Label(self.mid_pane, font=("Arial", 24), bg=self.COLOR_SCHEME["background-secondary"], fg=self.COLOR_SCHEME["foreground"], text="No Team Selected")
        self.selected_team_header.grid(row=0, column=0)

        self.add_team_point("total_point_avg", "Average Contributed Points")
        self.add_team_point("total_foul_avg", "Average Fouls")

        self.load_teams_into_selector()
    
    # Adds a graphable data point to the team page
    def add_team_point(self, point_name, point_label, row=None):
        if not row: row = len(list(self.loaded_team_data.keys()))+1
        self.loaded_team_data[point_name] = [None, None, None, None]
        point = self.loaded_team_data[point_name]


        point[0] = tk.PanedWindow(self.mid_pane, bg=self.COLOR_SCHEME["background"], height=50)
        point[0].grid(row=row, column=0, sticky="new")

        point[1] = tk.Label(point[0], bg=self.COLOR_SCHEME["background"], fg=self.COLOR_SCHEME["foreground"], text=point_label)
        point[1].grid(row=0, column=0, sticky="nsw")

        point[2] = tk.Label(point[0], bg=self.COLOR_SCHEME["background"], fg=self.COLOR_SCHEME["foreground"], text="-")
        point[2].grid(row=0, column=1, sticky="ns")

        point[3] = tk.Button(point[0], bg=self.COLOR_SCHEME["background"], fg=self.COLOR_SCHEME["foreground"], text="Graph", border=0, borderwidth=0, command=lambda: self.graph(point_name))
        point[3].grid(row=0, column=2, padx=30, sticky="nsew")

    def graph(self, data):
        print(data)
        if data == "total_point_avg":
            data = self.data[self.selected_team]
            processed_data = []
            for match in list(data.keys()):
                processed_data.append(self.process_points(data[match][0]))
            print(processed_data)
            graph = LineGraph({self.selected_team: processed_data}, "Average Points for " + self.selected_team)
            graph.run()
    
    def process_points(self, match_data):
        # Auton: 0, Teleop: 1, Other: 2
        if not "0" in list(match_data.keys()):
            return 0
        points = 0
        print(match_data)
        if match_data["2"]["got-mob"]: points+=3

        points += int(match_data["0"]["cone-top"])*6
        points += int(match_data["0"]["cone-mid"])*4
        points += int(match_data["0"]["cone-bot"])*3

        points += int(match_data["1"]["cone-top"])*5
        points += int(match_data["1"]["cone-mid"])*3
        points += int(match_data["1"]["cone-bot"])*2

        points += int(match_data["2"]["links"])*5

        points += int(match_data["0"]["bal"])*8
        points += int(match_data["1"]["bal"])*6
        points += int(match_data["0"]["bal-eng"])*12
        points += int(match_data["1"]["bal-eng"])*10

        if match_data["2"]["got-park"]: points+=2

        points -= int(match_data["2"]["fouls"])*5

        return points
    
    def show_team(self, event):
        team = event.widget.get(event.widget.curselection()[0]) # gets the selected team in the list
        self.selected_team = team
        self.selected_team_header.config(text="Team #" + str(team))

        matches = self.data[team] # The matches of the team

        avgpnts = 0
        avgfouls = 0

        for match in list(matches.keys()): # Iterating over the match numbers
            match_data = matches[match][0] # Getting the match data
            print(match_data)
            if len(list(match_data.keys())) != 0:

                avgpnts += self.process_points(match_data) # processes the points
                avgfouls += int(match_data["2"]["fouls"])
        
        avgpnts = avgpnts/len(list(matches.keys()))
        avgfouls = avgfouls/len(list(matches.keys()))

        self.loaded_team_data["total_point_avg"][2].config(text=avgpnts)
        self.loaded_team_data["total_foul_avg"][2].config(text=avgfouls)
    
    def load_teams_into_selector(self):
        teams = list(self.data.keys())
        teams.sort()
        for i in range(0, len(teams)):
            team = teams[i]
            self.teams_pane.insert(tk.END, team)

    def get_match(self):
        print(self.match_no_selector.get())
        return self.match_no_selector.get()
    
    def output_to_device_log(self, data, auto_newline=True):
        self.output_text.config(state=tk.NORMAL)
        self.output_text.insert(tk.END, str(data) + ("\n" if auto_newline else ""))
        self.output_text.config(state=tk.DISABLED)
        self.output_text.see(tk.END)
    
    def load_data(self):
        
        try:
            data = get_data()
            teams = list(data.keys())
            added_teams = list(self.data.keys())
            match = self.get_match()
            for team in teams:
                if not team in added_teams:
                    self.data[team] = {}
                if not match in self.data[team]:
                    self.data[team][match] = []
                self.data[team][match].append(data[team])
            print("Data: " + str(self.data))
            self.save_json_db()
            self.output_to_device_log("Loaded successfully!")
            self.load_teams_into_selector()
        except Exception as e:
            self.output_to_device_log(e.with_traceback(None))
    def rm_data(self):
        remove_data()

    def save_json_db(self):
        with open("data.json", "w+") as data_file:
            data_file.write(json.dumps(self.data))

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    ui = UI()
    ui.run()