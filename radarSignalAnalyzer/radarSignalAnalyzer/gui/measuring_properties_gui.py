from PyQt5 import QtWidgets
from PyQt5 import QtGui
import gui.common_gui as common_gui
from functools import partial


class MeasuringPropertiesGUI(QtWidgets.QGroupBox, common_gui.CommonGUI):

    def __init__(self, controller, parent=None):
        super(MeasuringPropertiesGUI, self).__init__()
        self._controller = controller
        self.__distance_label = None
        self.__distance_label_text = 'Distance to target [m]: '

        self.__init_ui()

    def __init_ui(self):
        zero_label = '0'
        self.__distance_label = QtWidgets.QLabel(self.__distance_label_text + zero_label)

        reset_statistics = QtWidgets.QPushButton('Reset Statitistics', self)
        reset_statistics.clicked.connect(self._controller.reset_statistics)

        distance_textbox = QtWidgets.QLineEdit(self)
        distance_textbox.setMinimumWidth(55)
        distance_validator = self._get_button_validator(distance_textbox, "\d+\.?\d*")

        set_distance = QtWidgets.QPushButton('Set Distance', self)
        set_distance.clicked.connect(partial(self.__set_distance, distance_textbox, distance_validator))

        remove_distance = QtWidgets.QPushButton('Remove Distance', self)
        remove_distance.clicked.connect(partial(self.__remove_distance, distance_textbox))

        intermediate_layout = QtWidgets.QHBoxLayout()
        intermediate_layout.addWidget(distance_textbox)
        intermediate_layout.addWidget(set_distance)
        intermediate_layout.addWidget(remove_distance)

        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addWidget(reset_statistics)
        main_layout.addLayout(intermediate_layout)
        main_layout.addWidget(self.__distance_label)

        self.setTitle("Measurement Properties")
        self.setStyleSheet("QGroupBox {border: 2px solid gray; border-radius: 9px; margin-top: 0.5em} QGroupBox:title {subcontrol-origin: margin; subcontrol-position: top center; padding-left: 10px; padding-right: 10px}")
        self.setLayout(main_layout)

    def __set_distance(self, distance, validator):
        if validator.validate(distance.text(), 0)[0] == QtGui.QValidator.Acceptable:
            self._controller.set_distance_from_gui(float(distance.text()))

    def __remove_distance(self, distance_textbox):
        distance_textbox.setText("")
        self._controller.remove_distance()

    def update_distance(self, distance):
        self.__distance_label.setText(self.__distance_label_text + str(distance))
