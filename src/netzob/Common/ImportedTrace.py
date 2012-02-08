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
import gzip
import os.path
from lxml.etree import ElementTree
from lxml import etree
from StringIO import StringIO

#+---------------------------------------------------------------------------+
#| Local Imports
#+---------------------------------------------------------------------------+
from netzob.Common.Type.TypeConvertor import TypeConvertor
from netzob.Common.Models.Factories.AbstractMessageFactory import AbstractMessageFactory

#+---------------------------------------------------------------------------+
#| ImportedTrace :
#|     Class definition of an imported trace registered in a workspace
#+---------------------------------------------------------------------------+
class ImportedTrace(object):

    #+-----------------------------------------------------------------------+
    #| Constructor
    #+-----------------------------------------------------------------------+
    def __init__(self, importID, date, dataType, description, projectName):
        self.importID = importID
        self.date = date
        self.dataType = dataType
        self.description = description
        self.projectName = projectName
        self.messages = []


    def save(self, root, namespace_workspace, namespace_common, pathOfTraces):
        xmlSymbol = etree.SubElement(root, "{" + namespace_workspace + "}trace")
        xmlSymbol.set("date", str(TypeConvertor.pythonDatetime2XSDDatetime(self.getDate())))
        xmlSymbol.set("type", str(self.getDataType()))
        xmlSymbol.set("description", str(self.getDescription()))
        xmlSymbol.set("projectName", str(self.getProjectName()))
        xmlSymbol.set("importID", str(self.getImportID()))

        # Creation of the XML File (in buffer)
        # Compress it using gzip and save the tar.gz
        tracesFile = os.path.join(pathOfTraces, str(self.getImportID()) + ".gz")
        logging.info("Save the config file of the trace " + str(self.getImportID()) + " in " + tracesFile)

        # Register the namespace (2 way depending of the version)
        try :
            etree.register_namespace('netzob-common', namespace_common)
        except AttributeError :
            etree._namespace_map[namespace_common] = 'netzob-common'

        # Save the messages
        root = etree.Element("{" + namespace_workspace + "}trace")
        root.set("id", str(self.getImportID()))
        xmlMessages = etree.SubElement(root, "{" + namespace_common + "}messages")
        for message in self.getMessages() :
            AbstractMessageFactory.save(message, xmlMessages, namespace_workspace, namespace_common)

        tree = ElementTree(root)
        contentOfFile = str(etree.tostring(tree.getroot()))

        # if outputfile already exists we delete it
        if os.path.isfile(tracesFile) :
            logging.debug("The compressed version (" + tracesFile + ") of the file already exists, we replace it with the new one")
            os.remove(tracesFile)

        # Compress and write the file
        gzipFile = gzip.open(tracesFile, 'wb')
        gzipFile.write(contentOfFile)
        gzipFile.close()




    def addMessage(self, message):
        self.messages.append(message)

    def getImportID(self):
        return self.importID
    def getDate(self):
        return self.date
    def getDataType(self):
        return self.dataType
    def getDescription(self):
        return self.description
    def getProjectName(self):
        return self.projectName
    def getMessages(self):
        return self.messages

    def setImportID(self, importID):
        self.importID = importID
    def setDate(self, date):
        self.date = date
    def setDataType(self, dataType):
        self.dataType = dataType
    def setDescription(self, description):
        self.description = description
    def setProjectName(self, projectName):
        self.projectName = projectName



    #+----------------------------------------------
    #| Static methods
    #+----------------------------------------------
    @staticmethod
    def loadSymbol(xmlRoot, namespace, namespace_common, version, pathOfTraces):

        if version == "0.1" :
            date = TypeConvertor.xsdDatetime2PythonDatetime(str(xmlRoot.get("date")))
            dataType = xmlRoot.get("type")
            description = xmlRoot.get("description", "")
            importID = xmlRoot.get("importID")
            projectName = xmlRoot.get("projectName")

            importedTrace = ImportedTrace(importID, date, dataType, description, projectName)
            tracesFile = os.path.join(pathOfTraces, str(importID) + ".gz")
            if not os.path.isfile(tracesFile) :
                logging.warn("The trace file " + str(tracesFile) + " is referenced but doesn't exist.")
            else :
                gzipFile = gzip.open(tracesFile, 'rb')
                xml_content = gzipFile.read()
                gzipFile.close()

                # We parse the xml content and fetch messages
                tree = etree.parse(StringIO(xml_content))
                xmlRoot = tree.getroot()

                if xmlRoot.find("{" + namespace_common + "}messages") != None :
                    xmlMessages = xmlRoot.find("{" + namespace_common + "}messages")
                    for xmlMessage in xmlMessages.findall("{" + namespace_common + "}message") :
                        message = AbstractMessageFactory.loadFromXML(xmlMessage, namespace_common, version)
                        if message != None :
                            importedTrace.addMessage(message)

            return importedTrace
        return None



