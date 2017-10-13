#!/usr/bin/python3
from PyQt5 import QtWidgets
import gui.radar_ui as mainWindow
import sys


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    radar = mainWindow.RadarMainWindow()

    sys.exit(app.exec_())
