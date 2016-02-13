#!/usr/bin/python3.4

from PyQt5 import QtWidgets
from PyQt5 import QtCore

import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
import controller

import sys


def HLine():
    toto = QtWidgets.QFrame()
    toto.setFrameShape(QtWidgets.QFrame.HLine)
    toto.setFrameShadow(QtWidgets.QFrame.Sunken)
    return toto


def VLine():
    toto = QtWidgets.QFrame()
    toto.setFrameShape(QtWidgets.QFrame.VLine)
    toto.setFrameShadow(QtWidgets.QFrame.Sunken)
    return toto


class RadarUI(QtWidgets.QWidget):

    def __init__(self):
        super(RadarUI, self).__init__()
        self.__controller = None
        self.__init_ui()

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
        self.__freq_to_tg_label = QtWidgets.QLabel("Frequency to target: 0")
        self.__dist_to_tg_label = QtWidgets.QLabel("Distance to target: 0")
        self.__rx_gain_label = QtWidgets.QLabel("Received gain: 0")
        self.__rx_phase_label = QtWidgets.QLabel("Received phase: 0")
        self.__gain_to_tg_label = QtWidgets.QLabel("Gain to target: 0")
        self.__phase_to_tg_label = QtWidgets.QLabel("Phase to target: 0")


        title_layout = QtWidgets.QHBoxLayout()
        title_layout.addWidget(QtWidgets.QLabel("Medium Properties"))
        title_layout.addWidget(VLine())
        title_layout.addWidget(QtWidgets.QLabel("Target Properties"))
        title_layout.addWidget(VLine())
        title_layout.addWidget(QtWidgets.QLabel("Receive Properties"))

        medium_layout = QtWidgets.QVBoxLayout()
        medium_layout.addWidget(self.__freq_to_tg_label)
        medium_layout.addWidget(self.__dist_to_tg_label)
        
        target_layout = QtWidgets.QVBoxLayout()
        target_layout.addWidget(self.__rx_gain_label)
        target_layout.addWidget(self.__rx_phase_label)
        
        receive_layout = QtWidgets.QVBoxLayout()
        receive_layout.addWidget(self.__gain_to_tg_label)
        receive_layout.addWidget(self.__phase_to_tg_label)
        
        # label layout
        label_layout = QtWidgets.QHBoxLayout()
        label_layout.addLayout(medium_layout)
        label_layout.addWidget(VLine())
        label_layout.addLayout(target_layout)
        label_layout.addWidget(VLine())
        label_layout.addLayout(receive_layout)

        # main layout
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addStretch(1)
        main_layout.addLayout(title_layout)
        main_layout.addWidget(HLine())
        main_layout.addLayout(label_layout)
        main_layout.addWidget(HLine())
        main_layout.addWidget(self.__canvas)
        main_layout.addWidget(HLine())
        main_layout.addWidget(self.__name_label)
        main_layout.addWidget(HLine())
        main_layout.addLayout(buttons_layout)

        self.setLayout(main_layout)
        self.show()

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

    @QtCore.pyqtSlot(float)
    def __update_frequency(self, value):
        self.__freq_to_tg_label.setText("Frequency to target: " + str(value))

    @QtCore.pyqtSlot(float)
    def __update_distance(self, value):
        self.__dist_to_tg_label.setText("Distance to target: " + str(value))

    @QtCore.pyqtSlot(float)
    def __update_rx_gain(self, value):
        self.__rx_gain_label.setText("Received gain: " + str(value))

    @QtCore.pyqtSlot(float)
    def __update_rx_phase(self, value):
        self.__rx_phase_label.setText("Received phase: " + str(value))

    @QtCore.pyqtSlot(float)
    def __update_tg_gain(self, value):
        self.__gain_to_tg_label.setText("Gain of target: " + str(value))
    
    @QtCore.pyqtSlot(float)
    def __update_tg_phase(self, value):
        self.__phase_to_tg_label.setText("Phase of target: " + str(value))


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    radar = RadarUI()
    radar.run()
    sys.exit(app.exec_())