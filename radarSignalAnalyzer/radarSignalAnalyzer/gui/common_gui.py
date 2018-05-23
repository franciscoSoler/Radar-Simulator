from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore
import os
import enum
import sndhdr


def is_audio(filename):
    return sndhdr.whathdr(filename) is not None


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


class Icons(enum.Enum):
    PLAY = 'play.png'
    PAUSE = 'pause.png'
    STOP = 'stop.png'
    REWIND = 'rewind.png'
    AREWIND = 'autoRewind.png'
    BROWSE = 'browse.png'
    INCVOL = 'increaseVolume.png'
    DECVOL = 'decreaseVolume.png'


class CommonGUI():

    def __init__(self):
        self._icon_size = 30
        self._real_time = False
        self.__freq_max = 800
        self._controller = None
        self._running = False
        self._icons_path = os.path.join(os.path.dirname(__file__), 'icons')

    def _add_icon_to_button(self, button, icon_path):
        button.setIcon(QtGui.QIcon(icon_path))
        button.setIconSize(QtCore.QSize(self._icon_size, self._icon_size))

    def _browse_file(self, title, path):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(self, title, path,
                                                             "All Files (*);;Python Files (*.py)", options=options)
        return file_name

    @QtCore.pyqtSlot(bool)
    def _update_execution_status(self, status):
        self._running = status

    @staticmethod
    def _get_button_validator(textbox, regex):
        regex = QtCore.QRegExp(regex)
        validator = QtGui.QRegExpValidator(regex, textbox)
        textbox.setValidator(validator)
        return validator