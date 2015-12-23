import matplotlib.animation as animation
from PyQt5 import QtCore
import numpy as np


def data_gen(t=0):
    cnt = 0
    while cnt < 1000:
        cnt += 1
        t += 0.1
        yield t, np.sin(2*np.pi*t) * np.exp(-t/10.)


class Controller(QtCore.QObject):

    update = QtCore.pyqtSignal(np.ndarray)

    def __init__(self, figure):
        super().__init__()
        self.figure = figure
        self.ax = figure.add_subplot(211)
        self.line, = self.ax.plot([], [], lw=2)
        self.xdata, self.ydata = list(range(11)), np.zeros(11)
        self.__ani = None

    def run2(self):
        self.__ani = animation.FuncAnimation(self.figure, self.run, data_gen, blit=False, interval=10,
                                      repeat=False, init_func=self.init)

    def init(self):
        self.ax.set_ylim(-1.1, 1.1)
        self.ax.set_xlim(0, 10)
        # del xdata[:]
        # del ydata[:]
        self.line.set_data(self.xdata, self.ydata)
        return self.line,

    def run(self, data):
        # update the data
        t, y = data
        # xdata.append(t)
        # ydata.append(y)
        # ydata = np.hstack((ydata[1:], y))
        xmin, xmax = self.ax.get_xlim()
        temp_data = np.hstack((self.ydata[1:], y))
        for i in range(len(self.ydata)):
            self.ydata[i] = temp_data[i]

        self.line.set_data(self.xdata, self.ydata)
        self.update.emit(temp_data)
        return self.line,