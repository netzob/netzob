# -*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|          01001110 01100101 01110100 01111010 01101111 01100010            |
#|                                                                           |
#|               Netzob : Inferring communication protocols                  |
#+---------------------------------------------------------------------------+
#| Copyright (C) 2011 Georges Bossert and Frédéric Guihéry                   |
#| This program is free software: you can redistribute it and/or modify      |
#| it under the terms of the GNU General Public License as published by      |
#| the Free Software Foundation, either version 3 of the License, or         |
#| (at your option) any later version.                                       |
#|                                                                           |
#| This program is distributed in the hope that it will be useful,           |
#| but WITHOUT ANY WARRANTY; without even the implied warranty of            |
#| MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the              |
#| GNU General Public License for more details.                              |
#|                                                                           |
#| You should have received a copy of the GNU General Public License         |
#| along with this program. If not, see <http://www.gnu.org/licenses/>.      |
#+---------------------------------------------------------------------------+
#| @url      : http://www.netzob.org                                         |
#| @contact  : contact@netzob.org                                            |
#| @sponsors : Amossys, http://www.amossys.fr                                |
#|             Supélec, http://www.rennes.supelec.fr/ren/rd/cidre/           |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Standard library imports
#+---------------------------------------------------------------------------+
import logging
import os
from lxml.etree import ElementTree
from lxml import etree
from gettext import gettext as _

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common import Project
from netzob.Common.Workspace import Workspace
from netzob.Common.Models.Factories.AbstractMessageFactory import AbstractMessageFactory
from netzob.Import.AbstractImporter import AbstractImporter


class XMLImporter(AbstractImporter):
    """Model of XML importer plugin"""

    def __init__(self, netzob):
        super(XMLImporter, self).__init__("XML IMPORT", netzob)
        self.log = logging.getLogger('netzob.Import.XMLImport.py')
        self.filesToBeImported = []

    def setSourceFiles(self, filePathList):
        self.filesToBeImported = filePathList

    def readMessages(self):
        self.messages = []
        for filePath in self.filesToBeImported:
            self._readMessagesFromFile(filePath)

    def _readMessagesFromFile(self, filePath):
        from netzob.Common.ResourcesConfiguration import ResourcesConfiguration
        xmlSchemaPath = os.path.join(ResourcesConfiguration.getStaticResources(), "xsds/0.1/common.xsd")
        # If we find a version which validates the XML, we parse with the associated function
        if not Workspace.isSchemaValidateXML(xmlSchemaPath, filePath):
            logging.error("The specified XML file {0} is not valid "
                          "according to the XSD ({1}).".format(filePath, xmlSchemaPath))
        else:
            logging.debug("XML file valid according to the XSD schema")

            # Parse the XML Document as 0.1 version
            tree = ElementTree()
            tree.parse(filePath)
            xmlFile = tree.getroot()

            for xmlMessage in xmlFile.findall("{" + Project.COMMON_NAMESPACE + "}message"):
                message = AbstractMessageFactory.loadFromXML(xmlMessage, Project.COMMON_NAMESPACE, "0.1")
                logging.debug("XML String data: " + message.getStringData())
                self.messages.append(message)
