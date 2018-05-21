__author__ = 'Francisco Soler'

import os
import time
from lxml import etree
import xml.etree.cElementTree as Et
from xml.dom import minidom

Xmlns_path = '{http://www.w3.org/2001/XMLSchema-instance}'


class XmlManager:

    def __init__(self, xmlfile=None):
        Et.register_namespace('', Xmlns_path)
        self._xml = None
        self._path_to_xml = None

        if xmlfile is not None:
            self.load(xmlfile)

    def load(self, path):
        """
        Load an xml file from a file.

        :param path: path indicating the file's location.
        """
        if not os.path.isfile(path):
            message = 'Error: The xml was not found, path to search: ' + path
            raise IOError(message)

        self._xml = Et.parse(path)
        self._path_to_xml = os.path.abspath(path)

    def save(self, save_path=None):
        """
        Save the xml file to file.

        :param save_path: path indicating where the file has to be saved (default None).
        :raises IOError: This exception is raised when the xml to save is empty.
        """
        if self._xml is None:
            raise IOError("There's nothing to save")

        path = self._path_to_xml if save_path is None else save_path

        with open(path, 'w') as f:
            rough_string = Et.tostring(self._xml, 'utf-8')
            par = etree.XMLParser(remove_blank_text=True)
            elem = etree.XML(rough_string, parser=par)
            parsed = minidom.parseString(etree.tostring(elem))
            f.write(parsed.toprettyxml(indent="  "))

    def _find_in_xml(self, pattern, element=None, namespace=Xmlns_path):
        """
        Finds the first element that matchs the pattern.

        :param pattern: pattern to search into the xml.
        :param element: elemnt used to search (default None).
        :param namespace: namespace used to search (default http://www.w3.org/2001/XMLSchema-instance).
        :returns: The searched element or None when it is not found.
        """
        el = self._xml if element is None else element
        return el.find('.//' + namespace + pattern)

    def get_content(self, pattern, namespace=Xmlns_path):
        """
        Obtain the text of a certain tag.

        :param pattern: A pattern of the tag to be searched.
        :param namespace: The namespace of the tag (default http://www.w3.org/2001/XMLSchema-instance).
        :returns: A string with the content of the searched tag.
        :raises Exception: When the element does not exist.
        """
        if self._find_in_xml(pattern, namespace=namespace) is None:
            raise Exception('the element {} with namespace {} does not exist'.format(pattern, namespace))

        return self._find_in_xml(pattern, namespace=namespace).text

    @staticmethod
    def _create_element(tag, text="", attr={}, namespace=Xmlns_path):
        """Create an element filled with attributes and text.

        :param tag: string representing the element's tag.
        :param text: string representing the element's text.
        :param attr: a dictionary with each key as an attribute name and value as the attribute's content.
        :param namespace: The namespace of the tag (default http://www.w3.org/2001/XMLSchema-instance).
        :returns: The created element.
        """
        element = Et.Element('.//' + namespace + tag, attr)
        element.text = text
        return element
