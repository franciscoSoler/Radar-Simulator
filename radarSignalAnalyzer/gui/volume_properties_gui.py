from PyQt5 import QtWidgets
from PyQt5 import QtGui
from functools import partial

import radarSignalAnalyzer.gui.common_gui as common_gui


class VolumePropertiesGUI(QtWidgets.QGroupBox, common_gui.CommonGUI):

    def __init__(self, controller, parent=None):
        super(VolumePropertiesGUI, self).__init__()
        self._controller = controller
        self.__volume_label = None
        self.__volume_label_text = 'Volume [dB]: '
        self.__volume = 0
        self.__init_ui()

    def __init_ui(self):
        self.__volume_label = QtWidgets.QLabel(self.__volume_label_text + str(self.__volume))

        volume_textbox = QtWidgets.QLineEdit(self)
        volume_validator = self._get_button_validator(volume_textbox, "\d+\.?\d*")

        set_volume = QtWidgets.QPushButton('Set Volume', self)
        set_volume.clicked.connect(partial(self.__set_volume, volume_textbox, volume_validator))
        
        reset_volume = QtWidgets.QPushButton('Reset Volume', self)
        reset_volume.clicked.connect(partial(self.__reset_volume, volume_textbox))

        increase_volume = QtWidgets.QPushButton('', self)
        self._add_icon_to_button(increase_volume, 'gui/icons/increaseVolume.png')
        increase_volume.clicked.connect(self.__increase_volume)
        
        decrease_volume = QtWidgets.QPushButton('', self)
        self._add_icon_to_button(decrease_volume, 'gui/icons/decreaseVolume.png')
        decrease_volume.clicked.connect(self.__decrease_volume)

        intermediate_layout = QtWidgets.QHBoxLayout()
        intermediate_layout.addWidget(volume_textbox)
        intermediate_layout.addWidget(set_volume)
        intermediate_layout.addWidget(reset_volume)

        volume_layout = QtWidgets.QHBoxLayout()
        volume_layout.addStretch(1)
        volume_layout.addWidget(increase_volume)
        volume_layout.addWidget(decrease_volume)
        volume_layout.addStretch(1)

        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addLayout(intermediate_layout)
        main_layout.addLayout(volume_layout)
        main_layout.addWidget(self.__volume_label)

        self.setTitle("Volume Properties")
        self.setStyleSheet("QGroupBox {border: 2px solid gray; border-radius: 9px; margin-top: 0.5em} QGroupBox:title {subcontrol-origin: margin; subcontrol-position: top center; padding-left: 10px; padding-right: 10px}")
        self.setLayout(main_layout)

    def __set_volume(self, volume, validator):
        if validator.validate(volume.text(), 0)[0] == QtGui.QValidator.Acceptable:
            self.__volume = float(volume.text())
            self.__volume_label.setText(self.__volume_label_text + volume.text())
            self._controller.set_volume(self.__volume)

    def __reset_volume(self, volume_textbox):
        volume_textbox.setText("")
        self.__volume = 0
        self.__volume_label.setText(self.__volume_label_text + str(self.__volume))
        self._controller.reset_volume()

    def __decrease_volume(self):
        self.__volume -= self._controller.decrease_volume()
        self.__volume_label.setText(self.__volume_label_text + str(self.__volume))

    def __increase_volume(self):
        self.__volume += self._controller.increase_volume()
        self.__volume_label.setText(self.__volume_label_text + str(self.__volume))
