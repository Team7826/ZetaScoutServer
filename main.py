import copy as np
import json
import os
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
        self.window.configure(bg=self.COLOR_SCHEME["background"])
        self.window.geometry("1200x600")
        self.window.rowconfigure(0, weight=1)
        self.window.columnconfigure(1, weight=2)
        self.window.columnconfigure(2, weight=0)

        self.comparing = tk.StringVar()
        self.comparable = {}

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
        
        # operation output log
        self.output_header = tk.Label(self.data_load_pane, font=("Arial", 12), bg=self.COLOR_SCHEME["background"], fg=self.COLOR_SCHEME["foreground"], text="Output")
        self.output_header.grid(row=3, column=0, columnspan=2, sticky="ew")
        
        self.output_text = tk.Text(self.data_load_pane, font=("Arial", 10), bg=self.COLOR_SCHEME["background"], fg=self.COLOR_SCHEME["foreground"], height=5, width=9, border=0, borderwidth=0)
        self.output_text.grid(row=4, column=0, columnspan=2, sticky="ew")
        self.output_text.insert(tk.END, "Perform an operation to get output.\n")
        self.output_text.config(state=tk.DISABLED)

        self.clear_data_button = tk.Button(self.data_load_pane, bg=self.COLOR_SCHEME["background-secondary"], fg=self.COLOR_SCHEME["foreground"], text="!!! Delete Comp Data !!!", border=0, borderwidth=0, command=self.reset_comp)
        self.clear_data_button.grid(row=5, column=0, columnspan=2)
    

        # Team Pane
        self.teams_pane = tk.Listbox(self.left_pane, fg="#FFFFFF", bg=self.COLOR_SCHEME["background-secondary"], borderwidth=0, border=0)
        self.teams_pane.grid(row=1, column=0, sticky="nsew")
        #self.teams_pane.grid_columnconfigure(0, weight=1)
        self.teams_pane_scroll = tk.Scrollbar(self.teams_pane, bg=self.COLOR_SCHEME["foreground"], border=0)
        self.teams_pane_scroll.pack(side="right", fill="y")

        self.teams_pane_scroll.config(command=self.teams_pane.yview)
        self.teams_pane.config(yscrollcommand=self.teams_pane_scroll.set)
        self.teams_pane.bind("<<ListboxSelect>>", self.show_team)

        # Right Pane
        self.right_pane = tk.PanedWindow(self.window, bg=self.COLOR_SCHEME["background"], width=300)
        self.right_pane.grid(row=0, column=3, sticky="nse")

        self.compare_header = tk.Label(self.right_pane, bg=self.COLOR_SCHEME["background"], fg=self.COLOR_SCHEME["foreground"], text="Compare")
        self.compare_header.grid(column=0, row=0, sticky="new")

        self.comparing_teams_list = tk.Listbox(self.right_pane, bg=self.COLOR_SCHEME["background-secondary"], fg=self.COLOR_SCHEME["foreground"], borderwidth=0, border=0)
        self.comparing_teams_list.grid(column=0, row=1, sticky="sew")

        self.compare_button_container = tk.PanedWindow(self.right_pane, bg=self.COLOR_SCHEME["background"], borderwidth=0, border=0)
        self.compare_button_container.grid(column=0, row=2, sticky="sew")

        self.compare_button_container.columnconfigure(0, weight=1)

        self.compare_add_button = tk.Button(self.compare_button_container, bg=self.COLOR_SCHEME["background-secondary"], fg=self.COLOR_SCHEME["foreground"], text="Add Team", borderwidth=0, border=0, command=self.add_team_to_comparer)
        self.compare_add_button.grid(column=0, row=0, sticky="nsw")
        self.compare_rem_button = tk.Button(self.compare_button_container, bg=self.COLOR_SCHEME["background-secondary"], fg=self.COLOR_SCHEME["foreground"], text="Remove Team", borderwidth=0, border=0, command=self.remove_team_from_comparer)
        self.compare_rem_button.grid(column=1, row=0, sticky="nse")

        self.compare_team_pane = tk.PanedWindow(self.right_pane, bg=self.COLOR_SCHEME["background-secondary"], borderwidth=0, border=0)
        self.compare_team_pane.grid(column=0, row=3)

        self.compare_team_label = tk.Label(self.compare_team_pane, font=("Arial", 12), bg=self.COLOR_SCHEME["background"], fg=self.COLOR_SCHEME["foreground"], text="Team #")
        self.compare_team_label.grid(column=0, row=0, sticky="nsew")

        self.compare_team_in = tk.Entry(self.compare_team_pane, bg=self.COLOR_SCHEME["background-secondary"], fg=self.COLOR_SCHEME["foreground"], border=0, borderwidth=0, validate="all", validatecommand=(self.window.register(lambda p: str.isdigit(p) or p==""), "%P"))
        self.compare_team_in.grid(column=1, row=0, sticky="nsew")

        self.compare_button = tk.Button(self.right_pane, bg=self.COLOR_SCHEME["background-secondary"], fg=self.COLOR_SCHEME["foreground"], text="Compare", borderwidth=0, border=0, command=self.compare)
        self.compare_button.grid(row=5, column=0, sticky="nsew")

        # Middle Pane
        self.mid_pane_canvas= tk.Canvas(self.window, bg=self.COLOR_SCHEME["background-secondary"], border=0, borderwidth=0)
        

        self.mid_pane = tk.Frame(self.mid_pane_canvas, width=600, bg=self.COLOR_SCHEME["background"], border=0, borderwidth=0)
        #self.mid_pane.grid(column=0, row=0, sticky="nsw")

        self.mid_pane_scroller = tk.Scrollbar(self.window, orient='vertical', bg=self.COLOR_SCHEME["foreground"], command=self.mid_pane_canvas.yview)
        self.mid_pane_canvas.configure(yscrollcommand=self.mid_pane_scroller.set)

        

        self.mid_pane.columnconfigure(0, weight=1)

        self.mid_pane_frame = self.mid_pane_canvas.create_window((1, 1), window=self.mid_pane, anchor=tk.CENTER)

        self.mid_pane.bind("<Configure>", self.OnFrameConfigure)
        self.mid_pane_canvas.bind('<Configure>', self.FrameWidth)

        self.selected_team_header = tk.Label(self.mid_pane, font=("Arial", 24), bg=self.COLOR_SCHEME["background"], fg=self.COLOR_SCHEME["foreground"], text="No Team Selected")
        self.selected_team_header.grid(row=0, column=0, sticky="ew")

        self.add_team_point("total_point_avg", "Average Contributed Points")

        self.add_team_point("cone-top", "Average Cones On Top (Auton)", 0)
        self.add_team_point("cone-mid", "Average Cones On Middle (Auton)", 0)
        self.add_team_point("cone-bot", "Average Cones On Bottom (Auton)", 0)

        self.add_team_point("cube-top", "Average Cubes On Top (Auton)", 0)
        self.add_team_point("cube-mid", "Average Cubes On Middle (Auton)", 0)
        self.add_team_point("cube-bot", "Average Cubes On Bottom (Auton)", 0)
        
        self.add_team_point("cone-top", "Average Cones On Top (Teleop)", 1)
        self.add_team_point("cone-mid", "Average Cones On Middle (Teleop)", 1)
        self.add_team_point("cone-bot", "Average Cones On Bottom (Teleop)", 1)

        self.add_team_point("cube-top", "Average Cubes On Top (Teleop)", 1)
        self.add_team_point("cube-mid", "Average Cubes On Middle (Teleop)", 1)
        self.add_team_point("cube-bot", "Average Cubes On Bottom (Teleop)", 1)

        self.add_team_point("bal-eng", "Engaged Balances (Auton)", 0)
        self.add_team_point("bal-eng", "Engaged Balances (Teleop)", 1)

        self.add_team_point("bal", "Balances (Auton)", 0)
        self.add_team_point("bal", "Balances (Teleop)", 1)

        self.add_team_point("bal-fail", "Failed Balances", 2)

        self.add_team_point("got-park", "Usually Gets Parking Bonus", 2)
        self.add_team_point("got-mob", "Usually Gets Mobility Bonus", 2)

        self.add_team_point("links", "Average Links", 2)
        self.add_team_point("rat-driving", "Average Driving Rating", 2)
        self.add_team_point("rat-defense", "Average Defense Rating", 2)
        self.add_team_point("fouls", "Average Fouls", 2)

        self.team_notes_container = tk.Listbox(self.mid_pane, fg="#FFFFFF", bg=self.COLOR_SCHEME["background-secondary"], border=0, borderwidth=0)
        self.team_notes_container.grid(column=0, sticky="nsew")

        self.load_teams_into_selector()

        self.compare_categories = tk.OptionMenu(self.right_pane, self.comparing, *self.comparable.keys())
        self.compare_categories.grid(row=4, column=0, sticky="nsew")
    
    def compare(self):
        comparing_nice_name = self.comparing.get()
        if comparing_nice_name.strip() == "":
            return
        comparing = self.comparable[comparing_nice_name]
        print("Comparing: " + comparing + " - AKA - " + comparing_nice_name)

        graphing_data = {}

        for team in self.comparing_teams_list.get(0, tk.END):
            print(team)
            graphing_data[team] = self.graph(comparing, True, team)
        
        LineGraph(graphing_data, "Comparing teams: " + comparing_nice_name)
    
    def add_team_to_comparer(self):
        text = self.compare_team_in.get()
        print(text)
        if text.strip() == "":
            return
        if text in self.comparing_teams_list.get(0, tk.END):
            return
        self.comparing_teams_list.insert(tk.END, text)
        self.compare_team_in.delete(0, tk.END)
    
    def remove_team_from_comparer(self):
        for i in self.comparing_teams_list.curselection():
            print(self.comparing_teams_list.get(i))
            self.comparing_teams_list.delete(i)
    
    def FrameWidth(self, event):
        canvas_width = event.width
        self.mid_pane_canvas.itemconfig(self.mid_pane_frame, width = canvas_width)

    def OnFrameConfigure(self, event):
        self.mid_pane_canvas.configure(scrollregion=self.mid_pane_canvas.bbox("all"))

    
    # Adds a graphable data point to the team page
    # Point type is the category (0 - Auton, 1 - Teleop, 2 - O M N I P R E S E N T)
    def add_team_point(self, point_name, point_label, point_type=-1, row=None):
        if not row: row = len(list(self.loaded_team_data.keys()))+1

        suffix = ""
        if point_type == 0:
            suffix = ".auton"
        elif point_type == 1:
            suffix = ".teleop"
        self.loaded_team_data[point_name + suffix] = [None, None, None, None, point_type]
        point = self.loaded_team_data[point_name + suffix]

        self.comparable[point_label] = point_name + suffix


        point[0] = tk.PanedWindow(self.mid_pane, bg=self.COLOR_SCHEME["background"], height=50)
        point[0].grid(row=row, column=0, sticky="nsew")
        point[0].columnconfigure(0, weight=1)

        point[1] = tk.Label(point[0], bg=self.COLOR_SCHEME["background"], fg=self.COLOR_SCHEME["foreground"], text=point_label)
        point[1].grid(row=0, column=0, sticky="nsw")

        point[2] = tk.Label(point[0], bg=self.COLOR_SCHEME["background"], fg=self.COLOR_SCHEME["foreground"], text="-")
        point[2].grid(row=0, column=1, sticky="ns")

        point[3] = tk.Button(point[0], bg=self.COLOR_SCHEME["background"], fg=self.COLOR_SCHEME["foreground"], text="Graph", border=0, borderwidth=0, command=lambda: self.graph(point_name + suffix))
        point[3].grid(row=0, column=2, padx=30, sticky="nsew")

    def graph(self, data, just_return=False, selected_team=None):
        if not selected_team: selected_team = self.selected_team

        
        if data == "total_point_avg":
            if (selected_team in self.data.keys()):
                data = self.data[selected_team]
                processed_data = []
                for match in list(data.keys()):
                    processed_data.append(self.process_points(data[match]))
                if just_return:
                    return processed_data
                graph = LineGraph({selected_team: processed_data}, "Average Points for " + selected_team)
                graph.run()
        
        else:
            data_type = data
            if (selected_team in self.data.keys()):
                data = self.data[selected_team]
                data_category = self.loaded_team_data[data_type][4] # Which category it is, auton, teleop, or other
                processed_data = []
                for match in list(data.keys()):
                    processed_data.append(int(data[match][str(data_category)][data_type.split(".")[0]]))
                
                if just_return:
                    return processed_data
                graph = LineGraph({selected_team: processed_data}, data_type + " - " + selected_team)
                graph.run()
    
    def process_points(self, match_data):
        # Auton: 0, Teleop: 1, Other: 2
        if not "0" in list(match_data.keys()):
            return 0
        points = 0
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
        try:
            #print(int(event.widget.get(event.widget.curselection()[0]).split()[0]))
            team = event.widget.get(event.widget.curselection()[0]).split()[0] # gets the selected team in the list
            self.mid_pane.event_generate("<Configure>")
            self.mid_pane_canvas.yview_moveto(0)
            self.mid_pane_canvas.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
            self.mid_pane_scroller.grid(column=2, row=0, sticky="nse")
        except IndexError as e:
            print("Error: " + str(e))
            return
        self.selected_team = team
        self.selected_team_header.config(text="Team #" + str(team))

        matches = self.data[team] # The matches of the team

        avgpnts = 0

        data_points = list(self.loaded_team_data.keys())
        processed_data_points = {}

        for point in data_points:
            if point != "total_point_avg":
                processed_data_points[point] = 0

        notes = []

        for match in list(matches.keys()): # Iterating over the match numbers
            match_data = matches[match] # Getting the match data
            if len(list(match_data.keys())) != 0:

                avgpnts += self.process_points(match_data) # processes the points

                for point in processed_data_points.keys():
                    point_category = self.loaded_team_data[point][4]
                    processed_data_points[point] += int(match_data[str(point_category)][point.split(".")[0]])

                notes.append(match_data["2"]["notes"])
        
        match_count = len(list(matches.keys()))
        avgpnts /= match_count
        
        for point in processed_data_points.keys():
            processed_data_points[point] /= match_count

        self.team_notes_container.delete(0, tk.END)

        i = 0
        for note in notes:
            i += 1
            self.team_notes_container.insert(tk.END, "Match #" + str(i) + ": " + note)

        self.loaded_team_data["total_point_avg"][2].config(text=avgpnts)

        for point in processed_data_points.keys():
            self.loaded_team_data[point][2].config(text=processed_data_points[point])
        self.reload_team_scrollbar(None)



    def reload_team_scrollbar(self, e):
        if e:
            print(e.width)
            #self.mid_pane.configure(width=e.width)
        self.mid_pane_canvas.configure(scrollregion=self.mid_pane_canvas.bbox("all"))

    def load_teams_into_selector(self):
        teams = list(self.data.keys())
        teams = sorted(teams)
        teamsavgpnts = {}
        #teams.sort()
        self.teams_pane.delete(0, tk.END)
        for i in range(0, len(teams)):
            team = teams[i]
            teamsavgpnts[team] = str(self.get_avg_pnts(team))

        sorted_teamsavgpnts = sorted([(float(value), key) for (key, value) in teamsavgpnts.items()], reverse = True)
        print(sorted_teamsavgpnts)
        for t in sorted_teamsavgpnts:
            self.teams_pane.insert(tk.END, t[1] + " - " + str(t[0]))
        

    def get_avg_pnts(self, t):
        # ap: avgpnts, t = team
        ap = 0

        matches = self.data[t] # The matches of the team
        for match in list(matches.keys()): # Iterating over the match numbers
            match_data = matches[match] # Getting the match data
            if len(list(match_data.keys())) != 0:
                ap += self.process_points(match_data) # processes the points

        match_count = len(list(matches.keys()))
        ap /= match_count

        return ap

    def get_match(self):
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
                    self.data[team][match] = None
                self.data[team][match] = data[team]
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
    
    def reset_comp(self):
        with open("data.json", "w+") as data:
            data.write("{}")
            self.teams_pane.delete(0, tk.END)
            self.data = {}
            self.load_teams_into_selector()

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    ui = UI()
    ui.run()