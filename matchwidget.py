import customtkinter

class MatchWidget(customtkinter.CTkFrame):
    def __init__(self, master, window, match_number, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        
        self.font = customtkinter.CTkFont(size=20)
        
        self.matchNumber = customtkinter.CTkLabel(self, text="MATCH " + str(match_number), font=self.font)
        self.matchNumber.grid(row=0, column=0)