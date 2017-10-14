from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore

import gui.common_gui as common_gui
import gui.radar_ui as radar_ui
import gui.properties_gui as properties
import gui.signal_properties_gui as signal_properties
import gui.volume_properties_gui as volume_properties
import gui.measuring_properties_gui as measuring_properties
import gui.plot_properties_gui as plot_properties
import src.controller as controller


class RadarMainWindow(QtWidgets.QMainWindow, common_gui.CommonGUI):

    def __init__(self):
        super(RadarMainWindow, self).__init__()
        self.__freq_max = 800
        self._controller = controller.Controller(self.__freq_max, real_time=self._real_time)

        self.__radar_ui = radar_ui.RadarUI(self._controller)
        self.__properties = properties.PropertiesGUI()
        self.__signal_properties = signal_properties.SignalPropertiesGUI(self._controller)
        self.__volume_properties = volume_properties.VolumePropertiesGUI(self._controller)
        self.__measuring_properties = measuring_properties.MeasuringPropertiesGUI(self._controller)
        self.__plot_properties = plot_properties.PlotPropertiesGUI(self._controller)

        self.__init_ui()

    def __init_ui(self):
        self._controller.update_data.connect(self.__update_data_label)

        self.setWindowTitle('Radar Measurements')
        self.setWindowIcon(QtGui.QIcon('icon.jpg'))

        # self.__create_menu()
        self.__create_toolbar()

        right_layout = QtWidgets.QVBoxLayout()
        right_layout.addWidget(self.__signal_properties)
        right_layout.addWidget(self.__volume_properties)
        right_layout.addWidget(self.__measuring_properties)
        right_layout.addWidget(self.__plot_properties)

        left_layout = QtWidgets.QVBoxLayout()
        left_layout.addWidget(self.__properties)
        left_layout.addWidget(self.__radar_ui)

        # main layout
        main_layout = QtWidgets.QHBoxLayout()
        main_layout.addLayout(left_layout)
        main_layout.addLayout(right_layout)

        central_widget = QtWidgets.QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        self.showMaximized()
        ani = self.__radar_ui.run()

        self.__signal_properties.animation = ani

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

    @QtCore.pyqtSlot(float, list, float, list, list, float, float, float, float)
    def __update_data_label(self, freq_to_tg, calc_dist_to_tg, d_dist, gain, phase, gain_to_tg, phase_to_tg, used_dist_to_tg, volume):
        self.__radar_ui.update_data_label(freq_to_tg, calc_dist_to_tg, d_dist, gain, phase, gain_to_tg, phase_to_tg, used_dist_to_tg, volume)
        self.__volume_properties.update_volume(volume)
        self.__measuring_properties.update_distance(used_dist_to_tg)
        self.__properties.update_measurements(freq_to_tg, calc_dist_to_tg, d_dist, gain, phase, gain_to_tg, phase_to_tg)
