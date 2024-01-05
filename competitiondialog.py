import customtkinter

class CompetitionDialog:
    PLACEHOLDER_YEAR = "2023"
    PLACEHOLDER_EVENT = "Event Place..."
    
    def __init__(self, tba):
        self.tba = tba
        self.app = customtkinter.CTk()
        self.app.geometry("450x180")
        self.app.title("Select Competition...")
        
        self.data = None # To be set later
        self.matches = None # ^
        self.ready = False
        
        self.status = customtkinter.CTkLabel(self.app, text="Please fill in the information to find a match")
        self.status.pack(anchor="s")
        
        self.yearEntry = customtkinter.CTkEntry(self.app, placeholder_text=self.PLACEHOLDER_YEAR)
        self.yearEntry.pack(anchor="n")
        
        self.eventEntry = customtkinter.CTkEntry(self.app, placeholder_text=self.PLACEHOLDER_EVENT)
        self.eventEntry.pack(anchor="n")
        
        self.yearConfirm = customtkinter.CTkButton(self.app, text="Go", command=self.find_year)
        self.yearConfirm.pack(anchor="n")
        
        self.useButton = customtkinter.CTkButton(self.app, text="Use This Competition", command=lambda: self.show_status("You must find a competition first!", True))
        self.useButton.pack(anchor="n")
    
    def find_year(self):
        self.show_status("Searching...")
        year = self.yearEntry.get().strip()
        if year is "":
            year = self.PLACEHOLDER_YEAR
        
        event = self.eventEntry.get().strip()
        
        if event is "":
            self.show_status("Please fill in the event field with the event's name.", True)
            return
        
        events = self.tba.get_events(year, event)
        
        if events is None:
            self.show_status("Could not find that competition", True)
        else:
            matches = self.tba.get_matches(events["key"]).json()
            if len(matches) == 0:
                self.show_status("Found a competition in " + events["city"] + ", but it has not scheduled matches yet.", True)
            else:
                self.show_status("Competition found: " + events["city"] + ", " + events["state_prov"] + ", " + events["country"])
                self.data = events
                self.matches = matches
                self.useButton.configure(command=self._close)
    
    def show_status(self, status, is_error=False):
        self.status.configure(text=status, text_color=("red" if is_error else "white"))
    
    def _close(self):
        self.app.quit()
        self.app.destroy()
        
    def show(self):
        self.app.mainloop()
        return self.data, self.matches
        

if __name__ == "__main__":
    import tba
    d = CompetitionDialog(tba.TBA())
    print(d.show())