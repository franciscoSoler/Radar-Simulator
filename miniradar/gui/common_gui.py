from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore
import src.controller as controller


class CommonGUI():

    def __init__(self):
        self._icon_size = 30
        self._real_time = False
        self.__freq_max = 800
        self._controller = None #controller.Controller(self.__freq_max, real_time=self._real_time)
        self._ani = None

    def _add_icon_to_button(self, button, icon_path):
        button.setIcon(QtGui.QIcon(icon_path))
        button.setIconSize(QtCore.QSize(self._icon_size, self._icon_size))

    def _set_animation(self, ani):
        self._ani = ani

    def _browse_file(self, title, path):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(self, title, path,
                                                             "All Files (*);;Python Files (*.py)", options=options)
        return file_name

    @staticmethod
    def _get_button_validator(textbox, regex):
        regex = QtCore.QRegExp(regex)
        validator = QtGui.QRegExpValidator(regex, textbox)
        textbox.setValidator(validator)
        return validator