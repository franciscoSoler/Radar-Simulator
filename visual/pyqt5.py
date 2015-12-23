#!/usr/bin/python3.4

import sys
from PyQt5 import QtGui
from PyQt5 import QtWidgets
import radar_ui


class AppUI(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        self.__radar_ui = radar_ui.RadarUI()
        self.__init_ui()

    def __init_ui(self):

        self.resize(600, 500)
        self.__center()

        self.setWindowTitle('Radar Measurements')
        self.setWindowIcon(QtGui.QIcon('icon.jpg'))

        # self.__create_menu()
        self.__create_toolbar()

        # main layout
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addWidget(self.__radar_ui)

        central_widget = QtWidgets.QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        self.show()
        self.__radar_ui.run()

    def __create_menu(self):
        exit_action = QtWidgets.QAction(QtGui.QIcon('icon.jpg'), '&Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.setStatusTip('Exit application')
        exit_action.triggered.connect(QtWidgets.qApp.quit)

        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu('&File')
        file_menu.addAction(exit_action)

    def __create_toolbar(self):
        exit_action = QtWidgets.QAction(QtGui.QIcon('icon.jpg'), 'Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(QtWidgets.qApp.quit)

        self.toolbar = self.addToolBar('Exit')
        self.toolbar.addAction(exit_action)

    def __center(self):
        qr = self.frameGeometry()
        cp = QtWidgets.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    radar = AppUI()

    sys.exit(app.exec_())
