import enum

import radarSignalAnalyzer.src.utils.xml_manager as xmlManager


class ConfTags(enum.Enum):
    F0 = 'centralFrecuency'
    BW = 'bandwidth'
    TXPW = 'txPower'
    RXPW = 'rxPower'
    DIST = 'distance'
    DELAY = 'antennaDelay'
    RFL = 'rfLosses'
    CABL = 'cableLosses'
    LNAG = 'lnaGain'
    MIXG = 'mixerGain'
    LPFG = 'lpfGain'
    R2MG = 'radarToMicGain'
    RXLN = 'rxLength'
    CABLN = 'cableLength'
    PROP = 'propagationVel'
    MINFREQ = 'minFreqToMeasure'


class ConfigFileManager(xmlManager.XmlManager):
    
    def __init__(self, config_file=None):
        super(ConfigFileManager, self).__init__(config_file)

    def check_existence(self, parameter):
        """
        Check the presence of a parameter in the parameter file.

        :param parameter: ConfigType parameter to check its presence.
        :returns: True when the parameter is present and False otherwise
        """
        return True if self._find_in_xml(parameter.value) else False

    def get_parameter(self, parameter):
        """
        Obtain the configuration of a certain parameter.

        :param parameter: ConfigType parameter to check its presence.
        :returns: The configuration of the parameter or None when the parameter doesn't exist.
        """
        if self._find_in_xml(parameter.value, namespace='') is None:
            raise Exception('the element {} does not exist'.format(parameter.value))

        return float(self._find_in_xml(parameter.value, namespace='').text)

    def parameters(self):
        """
        Obtain the configuration of every parameter.

        :returns: A list containing every parameter.
        """
        return [child.text for child in self._xml]
