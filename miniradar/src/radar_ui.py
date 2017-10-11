#!/usr/bin/python3

from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
import controller
import common
import sys
from functools import partial


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


class RadarMainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super(RadarMainWindow, self).__init__()
        self.__radar_ui = RadarUI()
        self.__init_ui()

    def __init_ui(self):

        self.resize(600, 500)
        self.__center()

        self.setWindowTitle('Radar Measurements')
        self.setWindowIcon(QtGui.QIcon('icon.jpg'))

        # self.__create_menu()
        self.__create_toolbar()

        # main layout
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addWidget(self.__radar_ui)

        central_widget = QtWidgets.QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        self.show()
        self.__radar_ui.run()

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

class RadarUI(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super(RadarUI, self).__init__()

        self.__measure_phase = False
        self.__real_time = False
        self.__freq_max = 800
        self.__controller = controller.Controller(self.__freq_max, real_time=self.__real_time)

        self.__vsup = 0.4
        self.__vinf = 0

        self.__max_freq_amplitude = 0.5
        self.__x_sign_data = self.__controller.get_signal_range()
        self.__x_freq_data = self.__controller.get_frequency_range()
        self.__img_lims = (0, common.Spectrogram_length, 0, self.__controller.get_disance_from_freq(self.__x_freq_data[-1]))
        self.__spectrogram_data = np.zeros((self.__controller.freq_length, common.Spectrogram_length))
        self.__figure = plt.figure(figsize=(25,20))

        self.__init_ui()

    def __set_distance(self, distance, validator):
        if validator.validate(distance.text(), 0)[0] == QtGui.QValidator.Acceptable:
            self.__controller.set_distance_from_gui(float(distance.text()))

    def __remove_distance(self, distance_textbox):
        distance_textbox.setText("")
        self.__controller.remove_distance()

    def __set_volume(self, volume, validator):
        if validator.validate(volume.text(), 0)[0] == QtGui.QValidator.Acceptable:
            self.__controller.set_volume(float(volume.text()))

    def __reset_volume(self, volume_textbox):
        volume_textbox.setText("")
        self.__controller.reset_volume()

    def __init_ui(self):
        self.__controller.update_data.connect(self.__update_data_label)

        remove_clutter = QtWidgets.QPushButton('Remove Clutter', self)
        restore_clutter = QtWidgets.QPushButton('Restore Clutter', self)

        remove_clutter.clicked.connect(self.__controller.remove_clutter)
        restore_clutter.clicked.connect(self.__controller.restore_clutter)

        distance_textbox = QtWidgets.QLineEdit(self)
        regex = QtCore.QRegExp("\d+\.?\d*")
        distance_validator = QtGui.QRegExpValidator(regex, distance_textbox)
        distance_textbox.setValidator(distance_validator)

        self.__used_dist_to_tg_label = QtWidgets.QLabel("Dist to target [m]: 0")
        set_distance = QtWidgets.QPushButton('Set Distance', self)
        remove_distance = QtWidgets.QPushButton('Remove Distance', self)

        volume_textbox = QtWidgets.QLineEdit(self)
        regex = QtCore.QRegExp("\d+\.?\d*")
        volume_validator = QtGui.QRegExpValidator(regex, volume_textbox)
        volume_textbox.setValidator(volume_validator)

        self.__used_volume_label = QtWidgets.QLabel('Volume [veces]: 1')
        set_volume = QtWidgets.QPushButton('Set Volume', self)
        reset_volume = QtWidgets.QPushButton('Reset Volume', self)

        reset_statistics = QtWidgets.QPushButton('Reset Statitistics', self)
        self.__rewind_audio = QtWidgets.QPushButton('Rewind Audio', self)
        auto_rewind = QtWidgets.QPushButton('Auto Rewind', self)
        auto_rewind.setCheckable(True)

        set_distance.clicked.connect(partial(self.__set_distance, distance_textbox, distance_validator))
        remove_distance.clicked.connect(partial(self.__remove_distance, distance_textbox))
        set_volume.clicked.connect(partial(self.__set_volume, volume_textbox, volume_validator))
        reset_volume.clicked.connect(partial(self.__reset_volume, volume_textbox))
        reset_statistics.clicked.connect(self.__controller.reset_statistics)
        auto_rewind.clicked[bool].connect(self.__rewind)
        self.__rewind_audio.clicked.connect(self.__controller.rewind_audio)
        if self.__real_time:
            auto_rewind.hide()
            self.__rewind_audio.hide()

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

        used_layout = QtWidgets.QHBoxLayout()
        used_layout.addWidget(self.__used_dist_to_tg_label)
        used_layout.addWidget(VLine())
        used_layout.addWidget(self.__used_volume_label)
        used_layout.addStretch(1)

        distance_layout = QtWidgets.QHBoxLayout()
        distance_layout.addWidget(distance_textbox)
        distance_layout.addWidget(set_distance)
        distance_layout.addWidget(remove_distance)
        distance_layout.addWidget(volume_textbox)
        distance_layout.addWidget(set_volume)
        distance_layout.addWidget(reset_volume)
        distance_layout.addWidget(reset_statistics)
        distance_layout.addWidget(auto_rewind)
        distance_layout.addWidget(self.__rewind_audio)
        distance_layout.addStretch(1)

        title_layout = QtWidgets.QHBoxLayout()
        title_layout.addWidget(QtWidgets.QLabel("Medium Properties"))
        title_layout.addWidget(VLine())
        title_layout.addWidget(QtWidgets.QLabel("Target Properties"))
        title_layout.addWidget(VLine())
        title_layout.addWidget(QtWidgets.QLabel("Receiving Properties"))

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
        main_layout.addLayout(distance_layout)
        # main_layout.addWidget(self.__used_dist_to_tg_label)
        # main_layout.addWidget(self.__used_volume_label)
        main_layout.addLayout(used_layout)
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

    def __rewind(self, pressed):
        source = self.sender()
        if pressed:
            self.__rewind_audio.hide()
            self.__controller.set_auto_rewind(True)
        else:
            self.__rewind_audio.show()
            self.__controller.set_auto_rewind(False)

    def __update_figures(self, data):
        # update the data
        signal, freq, phase = data

        self.__sign_line.set_ydata(signal)

        if self.__measure_phase:
            self.__freq_line.set_ydata(np.hstack((self.__freq_line.get_ydata()[1:], phase)))
        else:
            self.__freq_line.set_ydata(freq)
        self.__spectrogram_data = np.hstack((self.__spectrogram_data[:, 1:], np.transpose([freq])))
        self.__image.set_array(self.__spectrogram_data)

    def __init(self):
        ax_sign = self.__figure.add_subplot(311)
        ax_sign.set_ylim(-1, 1) # TODO change this range
        ax_sign.set_ylabel('Voltage')
        ax_sign.set_xlabel('Time')
        ax_sign.grid()

        self.__sign_line, = ax_sign.plot(self.__x_sign_data, np.zeros(self.__controller.signal_length))


        ax_freq = self.__figure.add_subplot(312)

        if self.__measure_phase:
            ax_freq.set_ylim(-180, 180)
            ax_freq.set_ylabel('Phase')
            ax_freq.set_xlabel('Freq')
            self.__freq_line, = ax_freq.plot(np.arange(common.Spectrogram_length), np.zeros(common.Spectrogram_length))
        else:
            ax_freq.set_ylim(self.__vinf, self.__max_freq_amplitude)
            ax_freq.set_ylabel('Gain')
            self.__freq_line, = ax_freq.plot(self.__x_freq_data, np.zeros(self.__controller.freq_length))
        ax_freq.grid()

        ax_spectr = self.__figure.add_subplot(313)
        ax_spectr.set_xlabel('Pulse Number')
        ax_spectr.set_ylabel('Distance')
        ax_spectr.grid(color='white')

        self.__image = ax_spectr.imshow(self.__spectrogram_data, aspect='auto', origin='lower',
                                             interpolation=None, animated=True, vmin=self.__vinf,
                                             vmax=self.__vsup, extent=self.__img_lims)
        self.__figure.colorbar(self.__image)

    @QtCore.pyqtSlot(float, list, float, list, list, float, float, float, float)
    def __update_data_label(self, freq_to_tg, calc_dist_to_tg, d_dist, gain, phase, gain_to_tg, phase_to_tg, used_dist_to_tg, volume):
        self.__freq_to_tg_label.setText("Frequency to target [Hz]: " + str(freq_to_tg))
        self.__dist_to_tg_label.setText("Distance to target [m]: {} \u00B1 {}".format(*calc_dist_to_tg))
        self.__delta_dist_to_tg_label.setText("Delta dist to target [m]: " + str(d_dist))
        self.__rx_gain_label.setText("Target's Gain [dB]: {} \u00B1 {}".format(*gain))
        self.__rx_phase_label.setText(u"Target's Phase [deg]: {} \u00B1 {}".format(*phase))
        self.__gain_to_tg_label.setText("Medium's Gain [dB]: " + str(gain_to_tg))
        self.__phase_to_tg_label.setText("Medium's Phase [deg]: " + str(phase_to_tg))
        self.__used_dist_to_tg_label.setText("Dist to target [m]: " + str(used_dist_to_tg))
        self.__used_volume_label.setText('Volume [veces]: ' + str(volume))


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    radar = RadarMainWindow()

    sys.exit(app.exec_())
