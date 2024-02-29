import tkinter
import customtkinter

class ScoutingDataItem(customtkinter.CTkFrame):
    def __init__(self, master, data_name, team, data_value_method, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.font = customtkinter.CTkFont(size=20)

        self.dataName = customtkinter.CTkLabel(self, text=str(team) + ": " + str(data_name), font=self.font)
        self.dataName.grid(row=0, column=0)

        self.makeLineOfbestFit = customtkinter.BooleanVar(self, False)
        self.calculateStandardDeviation = customtkinter.BooleanVar(self, False) 

        self.lineOfBestFit = customtkinter.CTkCheckBox(self, text="Line of Best Fit", variable=self.makeLineOfbestFit)
        self.lineOfBestFit.grid(row=0, column=1)

        self.calculateStdDeviation  = customtkinter.CTkCheckBox(self, text="Calculate Standard Deviation", variable=self.calculateStandardDeviation)
        self.calculateStdDeviation.grid(row=0, column=2)

        self.data_name = data_name
        self.data_value_method = data_value_method
        self.team = team

    def get_data(self):
        return {
            "title": self.team + ": " + self.data_name,
            "data": self.data_value_method(self.team, self.data_name), 
            "analysis":
            {
                "plot_line_of_best_fit": self.makeLineOfbestFit.get(), 
                "calculate_standard_deviation": self.calculateStandardDeviation.get()
            }
        }