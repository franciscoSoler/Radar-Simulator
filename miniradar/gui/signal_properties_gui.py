from PyQt5 import QtWidgets
from PyQt5 import QtCore

import os
import gui.common_gui as common_gui


class SignalPropertiesGUI(QtWidgets.QGroupBox, common_gui.CommonGUI):
    start_running = QtCore.pyqtSignal()
    stop_running = QtCore.pyqtSignal()
    pause_execution = QtCore.pyqtSignal(bool)

    def __init__(self, controller, parent=None):
        super(SignalPropertiesGUI, self).__init__()
        self._controller = controller
        self.__play = None
        self.__audio_label = None
        self.__audio_label_text = 'Audio: '
        self.__init_ui()

    def __init_ui(self):
        self.__audio_label = QtWidgets.QLabel(self.__audio_label_text)

        browse_or_stop = QtWidgets.QPushButton('', self)
        self._add_icon_to_button(browse_or_stop, 'gui/icons/browse.png')
        browse_or_stop.setCheckable(True)
        browse_or_stop.clicked.connect(self.__browse_or_stop_signal)

        rewind_audio = QtWidgets.QPushButton('', self)
        self._add_icon_to_button(rewind_audio, 'gui/icons/rewind.png')
        rewind_audio.clicked.connect(self._controller.rewind_audio)

        self.__play = QtWidgets.QPushButton('', self)
        self._add_icon_to_button(self.__play, 'gui/icons/play.png')
        self.__play.setCheckable(True)
        self.__play.clicked.connect(self.__play_audio)

        auto_rewind = QtWidgets.QPushButton('', self)
        self._add_icon_to_button(auto_rewind, 'gui/icons/autoRewind.png')
        auto_rewind.setCheckable(True)
        auto_rewind.clicked[bool].connect(self.__loop)

        intermediate_layout = QtWidgets.QHBoxLayout()
        intermediate_layout.addWidget(browse_or_stop)
        intermediate_layout.addWidget(rewind_audio)
        intermediate_layout.addWidget(self.__play)
        intermediate_layout.addWidget(auto_rewind)

        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addLayout(intermediate_layout)
        main_layout.addWidget(self.__audio_label)

        self.setTitle("Signal Properties")
        self.setStyleSheet("QGroupBox {border: 2px solid gray; border-radius: 9px; margin-top: 0.5em} QGroupBox:title {subcontrol-origin: margin; subcontrol-position: top center; padding-left: 10px; padding-right: 10px}")
        self.setLayout(main_layout)

    def __play_audio(self, pressed):
        source = self.sender()
        if not self._running:
            source.setChecked(False)
            return

        if pressed:
            self._add_icon_to_button(source, 'gui/icons/pause.png')
            self.pause_execution.emit(False)
        else:
            self._add_icon_to_button(source, 'gui/icons/play.png')
            self.pause_execution.emit(True)

    def __loop(self, pressed):
        self._controller.set_auto_rewind(True if pressed else False)

    def __browse_or_stop_signal(self, pressed):
        source = self.sender()
        if pressed:
            file_name = self._browse_file("Open Signal Data", "measurements/cornerReflector/Signal")
            if not file_name:
                source.setChecked(False)
            else:
                self._add_icon_to_button(source, 'gui/icons/stop.png')
                self._controller.use_external_signal(file_name)
                self.__audio_label.setText(self.__audio_label_text + os.path.basename(file_name))
                self.start_running.emit()
                self.pause_execution.emit(False)

                self._add_icon_to_button(source, 'gui/icons/pause.png')
                self.__play.setChecked(True)

        else:
            # TODO: I need to stop everything
            self._add_icon_to_button(source, 'gui/icons/browse.png')
            self.__audio_label.setText(self.__audio_label_text)
            self.stop_running.emit()
