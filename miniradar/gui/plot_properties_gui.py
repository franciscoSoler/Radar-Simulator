from PyQt5 import QtWidgets
import os
import gui.common_gui as common_gui


class PlotPropertiesGUI(QtWidgets.QGroupBox, common_gui.CommonGUI):

    def __init__(self, controller, parent=None):
        super(PlotPropertiesGUI, self).__init__()
        self._controller = controller
        self.__plot_phase_name = 'Plot Phase'
        self.__plot_fft_name = 'Plot FFT'
        self.__init_ui()

    def __init_ui(self):
        plot_phase = QtWidgets.QRadioButton(self.__plot_phase_name)
        plot_phase.setChecked(True)
        plot_phase.toggled.connect(lambda: self.btnstate(plot_phase))
          
        plot_fft = QtWidgets.QRadioButton(self.__plot_fft_name)
        plot_fft.toggled.connect(lambda: self.btnstate(plot_fft))

        main_layout = QtWidgets.QHBoxLayout()
        main_layout.addWidget(plot_phase)
        main_layout.addWidget(plot_fft)

        self.setTitle("Plot Properties")
        self.setStyleSheet("QGroupBox {border: 2px solid gray; border-radius: 9px; margin-top: 0.5em} QGroupBox:title {subcontrol-origin: margin; subcontrol-position: top center; padding-left: 10px; padding-right: 10px}")
        self.setLayout(main_layout)

    def btnstate(self, b):
    
        if b.text() == self.__plot_phase_name and b.isChecked() == True:
            # Plot phase
            print (b.text()+" is selected")
            
        if b.text() == self.__plot_fft_name and b.isChecked() == True:
            # plot FFT
            print (b.text()+" is selected")
