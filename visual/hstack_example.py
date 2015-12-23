import numpy as np
import matplotlib.animation as animation

import tkinter
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


def data_gen(t=0):
    cnt = 0
    while cnt < 1000:
        cnt += 1
        t += 0.1
        yield t, np.sin(2*np.pi*t) * np.exp(-t/10.)


def init():
    ax.set_ylim(-1.1, 1.1)
    ax.set_xlim(0, 10)
    # del xdata[:]
    # del ydata[:]
    line.set_data(xdata, ydata)
    return line,

root = tkinter.Tk()
# frame = tkinter.Frame(root)
# fig, ax = plt.subplots()
fig = Figure()
ax = fig.add_subplot(211)
line, = ax.plot([], [], lw=2)
# ax.grid()
# xdata, ydata = [], []
xdata, ydata = list(range(11)), np.zeros(11)


def run(data):
    # update the data
    t, y = data
    # xdata.append(t)
    # ydata.append(y)
    # ydata = np.hstack((ydata[1:], y))
    xmin, xmax = ax.get_xlim()
    temp_data = np.hstack((ydata[1:], y))
    for i in range(len(ydata)):
        ydata[i] = temp_data[i]
    '''
    if t >= xmax:
        ax.set_xlim(xmin, 2*xmax)
        ax.figure.canvas.draw()
    '''
    line.set_data(xdata, ydata)
    return line,


label = tkinter.Label(root, text="this is a label").pack()


class App:
    def __init__(self, master, figure):
        # Create a container
        frame = tkinter.Frame(master)
        # Create 2 buttons
        self.button_left = tkinter.Button(frame, text="< Decrease Slope",
                                          command=self.decrease)
        self.button_left.pack(side="left")
        self.button_right = tkinter.Button(frame, text="Increase Slope >",
                                           command=self.increase)
        self.button_right.pack(side="left")

        # fig = Figure()
        ax = figure.add_subplot(212)
        self.line, = ax.plot(range(10))

        self.canvas = FigureCanvasTkAgg(figure, master=master)
        self.canvas.show()
        self.canvas.get_tk_widget().pack(side='top', fill='both', expand=1)
        frame.pack()

    def decrease(self):
        x, y = self.line.get_data()
        self.line.set_ydata(y - 0.2 * x)
        self.canvas.draw()

    def increase(self):
        x, y = self.line.get_data()
        self.line.set_ydata(y + 0.2 * x)
        self.canvas.draw()

app = App(root, fig)

'''
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.show()
canvas.get_tk_widget().grid(column=0, row=1)
'''

ani = animation.FuncAnimation(fig, run, data_gen, blit=False, interval=10,
                              repeat=False, init_func=init)
root.mainloop()
