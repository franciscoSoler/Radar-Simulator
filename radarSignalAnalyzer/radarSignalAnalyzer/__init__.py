from PyQt5 import QtWidgets
import sys
import logging
import logging.handlers

import radarSignalAnalyzer.gui.radar_main_window as mainWindow


def main():
    logging.basicConfig(format=' %(asctime)s %(name)s: %(message)s', level=logging.INFO)
    logging.getLogger().addHandler(logging.handlers.SysLogHandler(address='/dev/log'))
    logger = logging.getLogger(__name__)

    app = QtWidgets.QApplication(sys.argv)
    try:
        logger.info('Execution started')

        radar = mainWindow.RadarMainWindow()
        s = app.exec_()
    except Exception:
        logger.exception('An exception was raised:')

    finally:
        logger.info('Execution ended with exit code %d', s)
        logging.shutdown()
        sys.exit(s)
