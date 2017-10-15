from PyQt5 import QtWidgets
from PyQt5 import QtCore

import os
import gui.common_gui as common_gui
from functools import partial


class ClutterPropertiesGUI(QtWidgets.QGroupBox, common_gui.CommonGUI):

    pause_execution = QtCore.pyqtSignal(bool)

    def __init__(self, controller, parent=None):
        super(ClutterPropertiesGUI, self).__init__()
        self._controller = controller
        self.__play = None
        self.__external_clutter_label = None
        self.__external_clutter_label_text = 'Ext Clutter: '

        self.__init_ui()

    def __init_ui(self):
        self.__external_clutter_label = QtWidgets.QLabel(self.__external_clutter_label_text)

        remove_clutter = QtWidgets.QPushButton('Remove Clutter', self)
        remove_clutter.setCheckable(True)
        remove_clutter.clicked.connect(self.__remove_clutter)

        external_clutter = QtWidgets.QPushButton('', self)
        self._add_icon_to_button(external_clutter, 'gui/icons/browse.png')
        external_clutter.setCheckable(True)
        external_clutter.setMaximumWidth(55)
        external_clutter.clicked.connect(partial(self.__select_external_clutter, remove_clutter))

        buttons_layout = QtWidgets.QHBoxLayout()
        buttons_layout.addWidget(remove_clutter)
        buttons_layout.addWidget(external_clutter)

        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addLayout(buttons_layout)
        main_layout.addWidget(self.__external_clutter_label)

        self.setTitle("Clutter Properties")
        self.setStyleSheet("QGroupBox {border: 2px solid gray; border-radius: 9px; margin-top: 0.5em} QGroupBox:title {subcontrol-origin: margin; subcontrol-position: top center; padding-left: 10px; padding-right: 10px}")
        self.setLayout(main_layout)

    def __remove_clutter(self, pressed):
        if not self._running:
            self.sender().setChecked(False)
            return

        self._controller.reset_statistics()
        if pressed:
            self._controller.remove_clutter()
        else:
            self._controller.restore_clutter()

    def __select_external_clutter(self, rem_clutter, pressed):
        source = self.sender()
        if not self._running:
            source.setChecked(False)
            return

        if pressed:
            self.pause_execution.emit(True)
            file_name = self._browse_file("Open Clutter Data", "measurements/cornerReflector/Clutter")
            self.pause_execution.emit(False)

            if not file_name:
                source.setChecked(False)
            else:
                self._controller.use_external_clutter(file_name)
                self.__external_clutter_label.setText(self.__external_clutter_label_text + os.path.basename(file_name))
                rem_clutter.setChecked(False)
                self._controller.restore_clutter()
        else:
            self._controller.stop_using_external_clutter()
            self._controller.restore_clutter()
            self.__external_clutter_label.setText(self.__external_clutter_label_text)
            rem_clutter.setChecked(False)
