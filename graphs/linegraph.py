import tkinter

from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure

import numpy as np
import random

class LineGraph:
    def __init__(self, datasets: dict, title="Line Graph", xlabel="Team", ylabel="Points", yheight=100, trend_line=True):
        root = tkinter.Tk()
        root.wm_title(title)

        fig = Figure()
        ax = fig.add_subplot()
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)

        ax.set_yticks(datasets[list(datasets.keys())[0]])

        print("DATA: " + str(datasets))

        ax.set_xlim(0, len(datasets[list(datasets.keys())[0]])-1)
        ax.set_ylim(0, yheight)

        canvas = FigureCanvasTkAgg(fig, master=root)  # A tk.DrawingArea.
        canvas.draw()

        # pack_toolbar=False will make it easier to use a layout manager later on.
        toolbar = NavigationToolbar2Tk(canvas, root, pack_toolbar=False)
        toolbar.update()

        canvas.mpl_connect(
            "key_press_event", lambda event: print(f"you pressed {event.key}"))
        canvas.mpl_connect("key_press_event", key_press_handler)

        keys = list(datasets.keys())

        lines = {}

        for i in range(0, len(keys)):
            data = datasets[keys[i]]
            data_range = range(0, len(data))
            if len(data_range) < 2:
                data_range = [0, 1]
                trend_line = False
            line, = ax.plot(1, 1)
            line.set_data(data_range, data)

            lines[keys[i]] = line

            if trend_line:

                bestfit, = ax.plot(1, 1, "--")
                bestfit.set_color(line.get_color())

                x_avg = np.average(data_range).tolist()
                print("Data fo avg:" + str(data_range))
                y_avg = np.average(data).tolist()

                x_avg_subtracted = [data_range[i]-x_avg for i in data_range]
                y_avg_subtracted = [data[i] - y_avg for i in data_range]

                rise = 0
                for x in range(0, len(x_avg_subtracted)):
                    rise += x_avg_subtracted[x] * y_avg_subtracted[x]
                run = 0
                for x in range(0, len(x_avg_subtracted)):
                    run += x_avg_subtracted[x] * x_avg_subtracted[x]

                slope = rise/run

                b = (slope*x_avg+(-y_avg))/-1 # y = mx+b but better

                bestfit.set_data(data_range, [slope*i + b for i in data_range])

                lines[keys[i] + " Trend"] = bestfit


            # required to update canvas and attached toolbar!
            fig.legend(lines.values(), lines.keys())
            canvas.draw()

        toolbar.pack(side=tkinter.BOTTOM, fill=tkinter.X)
        canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True)

    def run(self):
        tkinter.mainloop()

if __name__ == "__main__":
    count = 37
    line = LineGraph({"7826": [random.randint(0, 37) for _ in range(0, count)]}, yheight=36)
    line.run()