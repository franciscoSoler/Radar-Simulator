#!/usr/bin/python3.4

from PyQt5 import QtWidgets
from PyQt5 import QtCore

import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
import controller


class RadarUI(QtWidgets.QWidget):

    def __init__(self):
        super(RadarUI, self).__init__()
        self.__init_ui()
        # self.__controller = None

    def __init_ui(self):
        remove_clutter = QtWidgets.QPushButton('Remove Clutter', self)
        restore_clutter = QtWidgets.QPushButton('Restore Clutter', self)

        remove_clutter.clicked.connect(self.remove_clutter)
        restore_clutter.clicked.connect(self.restore_clutter)

        buttons_layout = QtWidgets.QHBoxLayout()
        buttons_layout.addWidget(remove_clutter)
        buttons_layout.addWidget(restore_clutter)

        figure = Figure()
        self.__controller = controller.Controller(figure)
        self.__controller.update.connect(self.__update_label)

        ax = figure.add_subplot(212)
        self.__line, = ax.plot(range(10))

        self.__canvas = FigureCanvasQTAgg(figure)
        self.__canvas.show()

        self.__name_label = QtWidgets.QLabel("asdf")

        # main layout
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addStretch(1)
        main_layout.addWidget(self.__canvas)
        main_layout.addWidget(self.__name_label)
        main_layout.addLayout(buttons_layout)

        self.setLayout(main_layout)

    def remove_clutter(self):
        # todo
        x, y = self.__line.get_data()
        self.__line.set_ydata(y - 0.2 * x)
        self.__canvas.draw()

    def restore_clutter(self):
        # todo
        x, y = self.__line.get_data()
        self.__line.set_ydata(y + 0.2 * x)
        self.__canvas.draw()

    def run(self):
        self.__controller.run2()

    @QtCore.pyqtSlot(np.ndarray)
    def __update_label(self, value):
        self.__name_label.setText(str(value))
