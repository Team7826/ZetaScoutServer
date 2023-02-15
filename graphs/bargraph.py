import tkinter

from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure

class BarGraph:
    def __init__(self, dataset: dict, title="Bar graph"):
        root = tkinter.Tk()
        root.wm_title(title)

        fig = Figure()
        ax = fig.add_subplot()
        ax.bar(list(dataset.keys()), list(dataset.values()))

        canvas = FigureCanvasTkAgg(fig, master=root)  # A tk.DrawingArea.
        canvas.draw()

        toolbar = NavigationToolbar2Tk(canvas, root, pack_toolbar=False)
        toolbar.update()

        toolbar.pack(side=tkinter.BOTTOM, fill=tkinter.X)
        canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True)

    def run(self):
        tkinter.mainloop()

if __name__ == "__main__":
    graph = BarGraph({"Eleven": 11, "Ten": 10, "Four": 4}, "Totally Real Dataset")
    graph.run()