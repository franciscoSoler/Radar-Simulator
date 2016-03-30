#!/usr/bin/python3.4

from PyQt5 import QtWidgets
from PyQt5 import QtCore

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
import controller
import common

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
        self.__controller = controller.Controller()
        # TODO fix this 4096
        self.__spectrogram_data = np.zeros((4096, common.Spectrogram_length))
        self.__figure = plt.figure()

        self.__init_ui()

    def __init_ui(self):
        self.__controller.update_data.connect(self.__update_data_label)

        remove_clutter = QtWidgets.QPushButton('Remove Clutter', self)
        restore_clutter = QtWidgets.QPushButton('Restore Clutter', self)

        remove_clutter.clicked.connect(self.__controller.remove_clutter)
        restore_clutter.clicked.connect(self.__controller.restore_clutter)

        buttons_layout = QtWidgets.QHBoxLayout()
        buttons_layout.addWidget(remove_clutter)
        buttons_layout.addWidget(restore_clutter)

        self.__canvas = FigureCanvasQTAgg(self.__figure)
        self.__canvas.show()

        self.__freq_to_tg_label = QtWidgets.QLabel("Frequency to target: 0")
        self.__dist_to_tg_label = QtWidgets.QLabel("Distance to target: 0")
        self.__delta_dist_to_tg_label = QtWidgets.QLabel("Delta Dist to target: 0")
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
        medium_layout.addWidget(self.__delta_dist_to_tg_label)

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
        main_layout.addLayout(buttons_layout)

        self.setLayout(main_layout)
        self.show()

    def run(self):
        self.__ani = animation.FuncAnimation(self.__figure, self.__update_figures, self.__controller.run,
                                             blit=False, interval=50, repeat=False,
                                             init_func=self.__init)

    def __update_figures(self, data):
        # update the data
        freq, max_freq = data
        self.__spectrogram_data = np.hstack((self.__spectrogram_data[:, 1:], np.transpose([freq])))

        # TODO remove the random
        self.__line.set_data(self.__xdata, freq[:len(self.__xdata)] + np.random.rand(len(self.__xdata)))
        self.__ax_spectr.imshow(self.__spectrogram_data, aspect='auto', origin='lower')

    def __init(self):
        ax_freq = self.__figure.add_subplot(211)
        ax_freq.set_ylim(-1.1, 1.1)
        ax_freq.set_xlim(0, 10)

        self.__line, = ax_freq.plot([], [], lw=2)
        # TODO remove the 1024
        self.__xdata = list(range(1024))

        self.__ax_spectr = self.__figure.add_subplot(212)
        image = self.__ax_spectr.imshow(self.__spectrogram_data, aspect='auto', origin='lower')
        self.__figure.colorbar(image)

        self.__line.set_data(self.__xdata, np.zeros(1024))
        return self.__line,

    @QtCore.pyqtSlot(float, float, float, float, float, float, float)
    def __update_data_label(self, freq_to_tg, dist_to_tg, d_dist, gain, phase, gain_to_tg, phase_to_tg):
        self.__freq_to_tg_label.setText("Frequency to target: " + str(freq_to_tg))
        self.__dist_to_tg_label.setText("Distance to target: " + str(dist_to_tg))
        self.__delta_dist_to_tg_label.setText("Delta dist to target: " + str(d_dist))
        self.__rx_gain_label.setText("Received gain: " + str(gain))
        self.__rx_phase_label.setText("Received phase: " + str(phase))
        self.__gain_to_tg_label.setText("Gain of target: " + str(gain_to_tg))
        self.__phase_to_tg_label.setText("Phase of target: " + str(phase_to_tg))


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    radar = RadarUI()
    radar.run()
    sys.exit(app.exec_())
