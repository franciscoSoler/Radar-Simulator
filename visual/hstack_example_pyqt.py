import sys
import numpy as np
import matplotlib.animation as animation

from PyQt5 import QtWidgets
from PyQt5 import QtGui
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
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


root = QtWidgets.QVBoxLayout()
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

    line.set_data(xdata, ydata)
    return line,


class App(QtWidgets.QMainWindow):
    def __init__(self, master, figure):
        super().__init__()
        self.__init_ui()
        # Create a container
        # frame = QtWidgets.QFrame(master)
        # Create 2 buttons
        button_left = QtWidgets.QPushButton('< Decrease Slope', self)
        button_right = QtWidgets.QPushButton('Increase Slope >', self)

        button_left.clicked.connect(self.decrease)
        button_right.clicked.connect(self.increase)

        buttons_layout = QtWidgets.QHBoxLayout()
        buttons_layout.addWidget(button_left)
        buttons_layout.addWidget(button_right)

        ax = figure.add_subplot(212)
        self.line, = ax.plot(range(10))

        self.__canvas = FigureCanvasQTAgg(figure)
        self.__canvas.show()
        master.addWidget(self.__canvas)
        master.addLayout(buttons_layout)

        central_widget = QtWidgets.QWidget()
        central_widget.setLayout(master)
        self.setCentralWidget(central_widget)

        self.show()

    def decrease(self):
        x, y = self.line.get_data()
        self.line.set_ydata(y - 0.2 * x)
        self.__canvas.draw()

    def increase(self):
        x, y = self.line.get_data()
        self.line.set_ydata(y + 0.2 * x)
        self.__canvas.draw()

    def __init_ui(self):

        self.resize(600, 500)
        self.__center()

        self.setWindowTitle('test')

        # self.__create_menu()
        self.__create_toolbar()

    def __create_menu(self):
        exit_action = QtWidgets.QAction(QtGui.QIcon('icon.jpg'), '&Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.setStatusTip('Exit application')
        exit_action.triggered.connect(QtWidgets.qApp.quit)

        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu('&File')
        file_menu.addAction(exit_action)

    def __create_toolbar(self):
        exit_action = QtWidgets.QAction(QtGui.QIcon('icon.jpg'), 'Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(QtWidgets.qApp.quit)

        self.toolbar = self.addToolBar('Exit')
        self.toolbar.addAction(exit_action)

    def __center(self):
        qr = self.frameGeometry()
        cp = QtWidgets.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

app1 = QtWidgets.QApplication(sys.argv)
app = App(root, fig)


ani = animation.FuncAnimation(fig, run, data_gen, blit=False, interval=10,
                              repeat=False, init_func=init)

sys.exit(app1.exec_())

