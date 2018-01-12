from PyQt5 import QtWidgets
import sys

import radarSignalAnalyzer.gui.radar_main_window as mainWindow


def main():
    app = QtWidgets.QApplication(sys.argv)
    radar = mainWindow.RadarMainWindow()

    sys.exit(app.exec_())
