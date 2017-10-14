from PyQt5 import QtWidgets
import os
import gui.common_gui as common_gui


class ClutterPropertiesGUI(QtWidgets.QGroupBox, common_gui.CommonGUI):

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
        remove_clutter.clicked.connect(self._controller.remove_clutter)

        restore_clutter = QtWidgets.QPushButton('Restore Clutter', self)
        restore_clutter.clicked.connect(self._controller.restore_clutter)

        external_clutter = QtWidgets.QPushButton('', self)
        self._add_icon_to_button(external_clutter, 'gui/icons/browse.png')
        external_clutter.setCheckable(True)
        external_clutter.clicked.connect(self.__select_external_clutter)

        buttons_layout = QtWidgets.QHBoxLayout()
        buttons_layout.addWidget(remove_clutter)
        buttons_layout.addWidget(restore_clutter)
        buttons_layout.addWidget(external_clutter)

        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addLayout(buttons_layout)
        main_layout.addWidget(self.__external_clutter_label)

        self.setTitle("Clutter Properties")
        self.setStyleSheet("QGroupBox {border: 2px solid gray; border-radius: 9px; margin-top: 0.5em} QGroupBox:title {subcontrol-origin: margin; subcontrol-position: top center; padding-left: 10px; padding-right: 10px}")
        self.setLayout(main_layout)

    def __select_external_clutter(self, pressed):
        source = self.sender()
        if pressed:
            self._ani.event_source.stop()

            file_name = self._browse_file("Open Clutter Data", "measurements/cornerReflector/Clutter")

            self._ani.event_source.start()

            if not file_name:
                source.setChecked(False)
            else:
                # Here I need to call the method giving the external Clutter path
                self.__external_clutter_label.setText(self.__external_clutter_label_text + os.path.basename(file_name))
        else:
            self.__external_clutter_label.setText(self.__external_clutter_label_text)
