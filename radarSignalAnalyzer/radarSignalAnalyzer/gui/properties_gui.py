from PyQt5 import QtWidgets

import radarSignalAnalyzer.gui.common_gui as common_gui



class PropertiesGUI(QtWidgets.QGroupBox, common_gui.CommonGUI):

    def __init__(self, parent=None):
        super(PropertiesGUI, self).__init__()
        
        self.__freq_to_tg_label = None
        self.__dist_to_tg_label = None
        self.__delta_dist_to_tg_label = None
        self.__rx_gain_label = None
        self.__rx_phase_label = None
        self.__gain_to_tg_label = None
        self.__phase_to_tg_label = None

        self.__freq_to_tg_label_text = 'Frequency to target [Hz]:'
        self.__dist_to_tg_label_text = 'Distance to target [m]:'
        self.__delta_dist_to_tg_label_text = 'Delta Dist to target [m]:'
        self.__rx_gain_label_text = "Target's Gain [dB]: "
        self.__rx_phase_label_text = "Target's Phase [deg]: "
        self.__gain_to_tg_label_text = "Medium's Gain [dB]: "
        self.__phase_to_tg_label_text = "Medium's Phase [deg]: "
        
        self.__init_ui()

    def __init_ui(self):
        zero_text = '0'
        self.__freq_to_tg_label = QtWidgets.QLabel(self.__freq_to_tg_label_text + zero_text)
        self.__dist_to_tg_label = QtWidgets.QLabel(self.__dist_to_tg_label_text + zero_text)
        self.__delta_dist_to_tg_label = QtWidgets.QLabel(self.__delta_dist_to_tg_label_text + zero_text)
        self.__rx_gain_label = QtWidgets.QLabel(self.__rx_gain_label_text + zero_text)
        self.__rx_phase_label = QtWidgets.QLabel(self.__rx_phase_label_text + zero_text)
        self.__gain_to_tg_label = QtWidgets.QLabel(self.__gain_to_tg_label_text + zero_text)
        self.__phase_to_tg_label = QtWidgets.QLabel(self.__phase_to_tg_label_text + zero_text)

        title_layout = QtWidgets.QHBoxLayout()
        title_layout.addWidget(QtWidgets.QLabel("Medium Properties"))
        title_layout.addWidget(common_gui.VLine())
        title_layout.addWidget(QtWidgets.QLabel("Target Properties"))
        title_layout.addWidget(common_gui.VLine())
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

        label_layout = QtWidgets.QHBoxLayout()
        label_layout.addLayout(medium_layout)
        label_layout.addWidget(common_gui.VLine())
        label_layout.addLayout(target_layout)
        label_layout.addWidget(common_gui.VLine())
        label_layout.addLayout(receive_layout)

        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addLayout(title_layout)
        main_layout.addWidget(common_gui.HLine())
        main_layout.addLayout(label_layout)

        self.setTitle("Measurements")
        self.setStyleSheet("QGroupBox {border: 2px solid gray; border-radius: 9px; margin-top: 0.5em} QGroupBox:title {subcontrol-origin: margin; subcontrol-position: top center; padding-left: 10px; padding-right: 10px}")
        self.setLayout(main_layout)

    def update_measurements(self, freq_to_tg, calc_dist_to_tg, d_dist, gain, phase, gain_to_tg, phase_to_tg):
        self.__freq_to_tg_label.setText(self.__freq_to_tg_label_text + str(freq_to_tg))
        self.__dist_to_tg_label.setText(self.__dist_to_tg_label_text + "{} \u00B1 {}".format(*calc_dist_to_tg))
        self.__delta_dist_to_tg_label.setText(self.__delta_dist_to_tg_label_text + str(d_dist))
        self.__rx_gain_label.setText(self.__rx_gain_label_text + "{} \u00B1 {}".format(*gain))
        self.__rx_phase_label.setText(self.__rx_phase_label_text + "{} \u00B1 {}".format(*phase))
        self.__gain_to_tg_label.setText(self.__gain_to_tg_label_text + str(gain_to_tg))
        self.__phase_to_tg_label.setText(self.__phase_to_tg_label_text + str(phase_to_tg))
