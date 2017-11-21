from PyQt5 import QtWidgets
from PyQt5 import QtCore

import numpy as np
import matplotlib
import matplotlib.lines as lines
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
import src.common as common
import gui.common_gui as common_gui


class RadarUI(QtWidgets.QWidget, common_gui.CommonGUI):

    update_execution_status = QtCore.pyqtSignal(bool)

    def __init__(self, controller):
        super(RadarUI, self).__init__()
        self.__ani = None
        self.__measure_phase = True
        # self._real_time = False
        # self.__freq_max = 800
        self._controller = controller

        self.__vsup = 0.4
        self.__vinf = 0

        self.__max_freq_amplitude = 0.5

        self.__x_sign_data = None
        self.__x_freq_data = None
        self.__img_lims = None
        self.__spectrogram_data = None

        matplotlib.rcParams.update({'font.size': 17})
        self.__figure = plt.figure(figsize=(25,20))

        self.__animation_paused = True
        self.__phase_line = None
        self.__freq_line = None
        self.__second_plot_line = None

        self.__init_ui()
        plt.tight_layout(pad=4, h_pad=4)

    def __init_ui(self):
        ax_sign = self.__figure.add_subplot(311)
        self.__initialize_voltage_plot(ax_sign)

        ax_two = self.__figure.add_subplot(312)
        if self.__measure_phase:
            self.__initialize_phase_plot(ax_two)
        else:
            self.__initialize_fft_plot(ax_two)

        ax_spectr = self.__figure.add_subplot(313)
        self.__initialize_spec_plot(ax_spectr)

        self.__image = ax_spectr.imshow([[0,0],[0,0]], aspect='auto', origin='lower',
                                             interpolation=None, animated=True, vmin=self.__vinf,
                                             vmax=self.__vsup, extent=self.__img_lims)
        self.__figure.colorbar(self.__image)

        self.__canvas = FigureCanvasQTAgg(self.__figure)
        self.__canvas.show()

        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addWidget(self.__canvas)

        self.setLayout(main_layout)

    def __init_plot_data(self):
        self.__x_sign_data = self._controller.get_signal_range()
        self.__x_freq_data = self._controller.get_frequency_range()
        self.__img_lims = (0, common.Spectrogram_length, 0, self._controller.get_disance_from_freq(self.__x_freq_data[-1]))
        self.__spectrogram_data = np.zeros((self._controller.freq_length, common.Spectrogram_length))

        self.__phase_line = lines.Line2D(np.arange(common.Spectrogram_length), np.zeros(common.Spectrogram_length))
        self.__freq_line = lines.Line2D(self.__x_freq_data, np.zeros(self._controller.freq_length))

        [ax_one, ax_two, ax_three, ax_four] = self.__figure.axes
        self.__clean_figures()

        self.__initialize_voltage_plot(ax_one)
        self.__sign_line, = ax_one.plot(self.__x_sign_data, np.zeros(self._controller.signal_length))

        if self.__measure_phase:
            self.__initialize_phase_plot(ax_two)
            self.__second_plot_line, = ax_two.plot(np.arange(common.Spectrogram_length), np.zeros(common.Spectrogram_length))
        else:
            self.__initialize_fft_plot(ax_two)
            self.__second_plot_line, = ax_two.plot(self.__x_freq_data, np.zeros(self._controller.freq_length))

        self.__initialize_spec_plot(ax_three)
        self.__image = ax_three.imshow(self.__spectrogram_data, aspect='auto', origin='lower',
                                             interpolation=None, animated=True, vmin=self.__vinf,
                                             vmax=self.__vsup, extent=self.__img_lims)

    def __update_figures(self, data):
        signal, freq, phase = data

        self.__sign_line.set_ydata(signal)

        if self.__measure_phase:
            self.__second_plot_line.set_ydata(np.hstack((self.__second_plot_line.get_ydata()[1:], phase)))
        else:
            self.__second_plot_line.set_ydata(freq)

        print(self._controller.freq_length, len(freq))
        self.__spectrogram_data = np.hstack((self.__spectrogram_data[:, 1:], np.transpose([freq])))
        self.__image.set_array(self.__spectrogram_data)

    def __initialize_voltage_plot(self, ax=None):
        ax_sign = self.__figure.axes[0] if ax is None else ax
        ax_sign.set_ylim(-1, 1)
        ax_sign.set_ylabel('Voltage')
        ax_sign.set_xlabel('Time')
        ax_sign.grid(True)

    def __initialize_fft_plot(self, ax=None):
        ax_freq = self.__figure.axes[1] if ax is None else ax
        ax_freq.set_ylim(self.__vinf, self.__max_freq_amplitude)
        ax_freq.set_ylabel('Gain')
        ax_freq.grid(True)
        return ax_freq

    def __initialize_phase_plot(self, ax=None):
        ax_phase = self.__figure.axes[1] if ax is None else ax
        ax_phase.set_ylim(-180, 180)
        ax_phase.set_ylabel('Phase')
        ax_phase.set_xlabel('Freq')
        ax_phase.grid(True)
        return ax_phase

    def __initialize_spec_plot(self, ax=None):
        ax_spectr = self.__figure.axes[2] if ax is None else ax
        ax_spectr.set_xlabel('Pulse Number')
        ax_spectr.set_ylabel('Distance')
        ax_spectr.grid(color='white')

    def __clean_figures(self):
        [ax_one, ax_two, ax_three, _] = self.__figure.axes
        ax_one.cla()
        ax_two.cla()
        ax_three.cla()

        ax_one.grid(True)
        ax_two.grid(True)
        ax_three.grid(color="white")

    @QtCore.pyqtSlot()
    def run(self):
        self.__ani = animation.FuncAnimation(self.__figure, self.__update_figures, self._controller.run,
                                             blit=False, interval=50, repeat=True,
                                             init_func=self.__init_plot_data)
        self._running = True
        self.update_execution_status.emit(True)
        self.__figure.canvas.draw()

    @QtCore.pyqtSlot()
    def stop(self):
        self.pause_execution(False)
        self.__ani.repeat = False
        self._running = False
        self.update_execution_status.emit(False)

    @QtCore.pyqtSlot(bool)
    def pause_execution(self, pause):
        if self.__animation_paused and not pause:
            self.__animation_paused = False
            self.__ani.event_source.start()

        elif not self.__animation_paused and pause:
            self.__animation_paused = True
            self.__ani.event_source.stop()

    def plot_phase(self):
        self.__measure_phase = True

        ax_phase = self.__initialize_phase_plot()

        if self._running:
            self.__second_plot_line.set_data(self.__phase_line.get_data())
            ax_phase.relim()
            ax_phase.autoscale_view()
        else:
            self.__figure.canvas.draw()

    def plot_fft(self):
        self.__measure_phase = False

        ax_freq = self.__initialize_fft_plot()

        if self._running:
            self.__second_plot_line.set_data(self.__freq_line.get_data())
            ax_freq.relim()
            ax_freq.autoscale_view()
        else:
            self.__figure.canvas.draw()
