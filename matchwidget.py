import customtkinter

class MatchWidget(customtkinter.CTkFrame):
    def __init__(self, master, window, match_number, select_match_callback, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.font = customtkinter.CTkFont(size=20)

        self.matchNumber = customtkinter.CTkLabel(self, text="MATCH " + str(match_number), font=self.font)
        self.matchNumber.grid(row=0, column=0)

        self.matchSelect = customtkinter.CTkButton(self, text="Scout", command=lambda: select_match_callback(match_number-1), font=self.font)
        self.matchSelect.grid(row=0, column=1)