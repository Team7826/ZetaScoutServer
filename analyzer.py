import customtkinter
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from numpy import arange, polyfit, sqrt, linalg

from scoutingdataitem import ScoutingDataItem
import dictutil

def spawn_analyzer(title, data):
    print(title, data)
    spawn_advanced_analyzer([{"title": title, "data": data}])

def spawn_advanced_analyzer(config):
    analyzer = Analyzer(config)
    analyzer.run()

CYCLE_COLORS = ("red", "orange", "yellow", "green", "blue", "purple")

DEFAULT_ANALYSIS_CONFIG = {
    "plot_line_of_best_fit": False,
    "calculate_standard_deviation": False
}

class Analyzer:
    def __init__(self, config):
        self.app = customtkinter.CTk()
        self.app.geometry("500x500")
        self.app.title("Analyzer")

        self.config = config

        self.stat_font = customtkinter.CTkFont(size=20)

        self.controlPane = customtkinter.CTkFrame(self.app)
        #self.controlPane.pack(fill="x")

        self.stat_pane = customtkinter.CTkFrame(self.app)


        self.create_plots()

        self.stat_pane.pack()


    def create_plots(self):
        #size = (len(self.data), max(self.data))
        # the figure that will contain the plot
        fig = Figure(dpi = 100)

        # adding the subplot
        data_plot = fig.add_subplot()

        max_width = 1
        max_height = 1

        i = 0
        for plot in self.config:

            # plotting the graph
            title = get_from_dict_or(plot, "title", "Graph " + str(i))
            data = get_from_dict_or(plot, "data", [])

            color = get_from_dict_or(plot, "color", CYCLE_COLORS[i % len(CYCLE_COLORS)])

            data_plot.plot(data, label=title, color=color)

            analysis_config = get_from_dict_or(plot, "analysis", DEFAULT_ANALYSIS_CONFIG)

            if analysis_config["plot_line_of_best_fit"]:
                x, b, m = calculate_best_fit(data)
                data_plot.plot(x, b*x+m, label="Line of Best Fit", scalex=False, scaley=False, color=color, linestyle="dashed")

            if analysis_config["calculate_standard_deviation"]:
                customtkinter.CTkLabel(self.stat_pane, font=self.stat_font, text=title + " SD: " + str(calculate_standard_deviation(data))).pack()

            i += 1

        fig.legend()

        # creating the Tkinter canvas
        # containing the Matplotlib figure
        canvas = FigureCanvasTkAgg(fig,
                                master = self.app)
        canvas.draw()

        # placing the canvas on the Tkinter window
        canvas.get_tk_widget().pack()

        # creating the Matplotlib toolbar
        toolbar = NavigationToolbar2Tk(canvas,
                                    self.app)
        toolbar.update()

        # placing the toolbar on the Tkinter window
        canvas.get_tk_widget().pack()

    def run(self):
        self.app.mainloop()

def get_from_dict_or(dict, value, default):
    if not value in dict.keys():
        return default
    return dict[value]

def calculate_mean(data: list):
    return sum(data) / len(data)

def calculate_standard_deviation(data: list):
    mean = calculate_mean(data)
    deviations = data.copy()
    for i in range(0, len(deviations)):
        deviations[i] -= mean
        deviations[i] **= 2

    deviation_sum = sum(deviations)
    variance = deviation_sum/len(deviations)

    return round(sqrt(variance), 1)

def calculate_best_fit(data: list):
    try:
        # Fit with polyfit
        data_x = arange(len(data))
        b, m = polyfit(data_x, data, 1)
    except linalg.LinAlgError as e:
        return [0, 0, 0]

    return data_x, b, m

class AnalyzerCreator:
    def __init__(self, team_data):
        self.app = customtkinter.CTk()
        self.app.geometry("1000x500")
        self.app.title("Analyzer Creator")

        self.app.grid_columnconfigure(0, weight=1)
        self.app.grid_rowconfigure(1, weight=1)

        self.team_data = team_data

        addButton = customtkinter.CTkButton(self.app, text="Add Datapoint", command=self.add_value)
        addButton.grid(row=0, column=0, sticky="EW")

        self.addedValues = customtkinter.CTkScrollableFrame(self.app)
        self.addedValues.grid(row=1, column=0, sticky="NSEW")

        doneButton = customtkinter.CTkButton(self.app, text="Finish & Create", command=self.exit)
        doneButton.grid(row=2, column=0, sticky="EW")

        self.datapoints = {}
        self.team_data_values = {}

    def add_value(self):
        popup = AnalyzerCreatorValuePopup(self.team_data)
        team, attribute, team_data_values = popup.run()

        self.team_data_values[team] = team_data_values
        self.team_data_values[team].update(dictutil.convert_list_of_dict_to_dict_with_list(self.team_data[team]))

        if team == "-" or attribute == "-":
            return

        widget = ScoutingDataItem(self.addedValues, attribute, team, self.get_team_data)
        widget.pack(fill="x")

    def get_team_data(self, team, path):
        return dictutil.retrieve_nested_value_from_path(self.team_data_values[team], path)
    
    def exit(self):
        self.datapoints = []
        for child in list(self.addedValues.children.values()):
            self.datapoints.append(child.get_data())
        
        print(self.datapoints)
        self.app.quit()
        self.app.destroy()


    def run(self):
        self.app.mainloop()

        spawn_advanced_analyzer(self.datapoints)

class AnalyzerCreatorValuePopup:
    def __init__(self, team_data):
        self.app = customtkinter.CTk()
        self.app.geometry("500x100")
        self.app.title("Add a value...")

        self.app.grid_columnconfigure(0, weight=1)
        self.app.grid_rowconfigure(2, weight=1)

        self.team_data = team_data

        self.team_data_values = {}

        self.teamDropdown = customtkinter.CTkComboBox(self.app, values=["-"] + list(team_data.keys()), command=self.select_team)
        self.teamDropdown.grid(row=0, column=0, sticky=["NEW"])

        self.dataPointDropdown = customtkinter.CTkComboBox(self.app, values=["-"])
        self.dataPointDropdown.grid(row=1, column=0, sticky=["NEW"])

        self.finishButton = customtkinter.CTkButton(self.app, command=self.exit, text="Finish & Add")
        self.finishButton.grid(row=2, column=0, sticky=["NSEW"])

    def select_team(self, team):
        self.team = team
        values = {}
        points_autonomous, points_teleop, points_total = dictutil.calculate_points(self.team_data[team])
        values.update({"Total Points": points_total, "Autonomous Points": points_autonomous, "Teleop Points": points_teleop})

        self.dataPointDropdown.configure(
            values=
            list(values.keys()) +
            dictutil.get_all_keys_as_paths(
                dictutil.convert_list_of_dict_to_dict_with_list(self.team_data[team])
                )
            )

        self.team_data_values = values

    def exit(self):
        self.team, self.attribute = self.teamDropdown.get(), self.dataPointDropdown.get()
        self.app.quit()
        self.app.destroy()

    def run(self):
        self.app.mainloop()
        return self.team, self.attribute, self.team_data_values

def spawn_analyzer_creator(team_data: dict):

    AnalyzerCreator(team_data).run()

if __name__ == "__main__":
    #spawn_analyzer("Garbage Data", [10, 1, 10, 1, 10, 1, 10, 1, 10, 1])
    import scouted
    import dictutil
    team_data = dictutil.compile_team_data(scouted.scouted["matches"])

    spawn_analyzer_creator(team_data)
    '''spawn_advanced_analyzer([
        {
            "title": "10062 Autonomous Points",
            "data": [4, 8, 4, 3, 2],
            "analysis": {
                "plot_line_of_best_fit": True,
                "calculate_standard_deviation": True
            }
        },
        {
            "title": "10062 Teleop Points",
            "data": [7, 5, 6, 3, 4],
            "analysis": {
                "plot_line_of_best_fit": True,
                "calculate_standard_deviation": True
            }
        }
    ])'''