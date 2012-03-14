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
from netzob.Common.Session import Session


#+---------------------------------------------------------------------------+
#| ImportedTrace:
#|     Class definition of an imported trace registered in a workspace
#+---------------------------------------------------------------------------+
class ImportedTrace(object):

    #+-----------------------------------------------------------------------+
    #| Constructor
    #+-----------------------------------------------------------------------+
    def __init__(self, id, date, type, description, name):
        self.id = id
        self.date = date
        self.type = type
        self.description = description
        self.name = name
        self.messages = []
        self.sessions = []

    def save(self, root, namespace_workspace, namespace_common, pathOfTraces):
        xmlTrace = etree.SubElement(root, "{" + namespace_workspace + "}trace")
        xmlTrace.set("date", str(TypeConvertor.pythonDatetime2XSDDatetime(self.getDate())))
        xmlTrace.set("type", str(self.getType()))
        xmlTrace.set("description", str(self.getDescription()))
        xmlTrace.set("name", str(self.getName()))
        xmlTrace.set("id", str(self.getID()))

        # Creation of the XML File (in buffer)
        # Compress it using gzip and save the .gz
        tracesFile = os.path.join(pathOfTraces, str(self.getID()) + ".gz")
        logging.info("Save the trace " + str(self.getID()) + " in " + tracesFile)

        # Register the namespace (2 way depending on the version)
        try:
            etree.register_namespace('netzob-common', namespace_common)
        except AttributeError:
            etree._namespace_map[namespace_common] = 'netzob-common'

        # Save the messages
        root = etree.Element("{" + namespace_workspace + "}trace")
        root.set("id", str(self.getID()))
        xmlMessages = etree.SubElement(root, "{" + namespace_workspace + "}messages")
        for message in self.getMessages():
            AbstractMessageFactory.save(message, xmlMessages, namespace_workspace, namespace_common)

        # Save the sessions
        xmlSessions = etree.SubElement(root, "{" + namespace_workspace + "}sessions")
        for session in self.getSessions():
            session.save(xmlSessions, namespace_workspace, namespace_common)

        tree = ElementTree(root)
        contentOfFile = str(etree.tostring(tree.getroot()))

        # if outputfile already exists we delete it
        if os.path.isfile(tracesFile):
            logging.debug("The compressed version (" + tracesFile + ") of the file already exists, we replace it with the new one")
            os.remove(tracesFile)

        # Compress and write the file
        gzipFile = gzip.open(tracesFile, 'wb')
        gzipFile.write(contentOfFile)
        gzipFile.close()

    def addSession(self, session):
        self.sessions.append(session)

    def addMessage(self, message):
        self.messages.append(message)

    def getID(self):
        return self.id

    def getDate(self):
        return self.date

    def getType(self):
        return self.type

    def getDescription(self):
        return self.description

    def getName(self):
        return self.name

    def getSessions(self):
        return self.sessions

    def getMessages(self):
        return self.messages

    def getMessageByID(self, id):
        for message in self.messages:
            if message.getID() == id:
                return message
        return None

    def setID(self, id):
        self.id = id

    def setDate(self, date):
        self.date = date

    def setType(self, type):
        self.type = type

    def setDescription(self, description):
        self.description = description

    def setName(self, name):
        self.name = name

    #+----------------------------------------------
    #| Static methods
    #+----------------------------------------------
    @staticmethod
    def loadTrace(xmlRoot, namespace_workspace, namespace_common, version, pathOfTraces):

        if version == "0.1":
            date = TypeConvertor.xsdDatetime2PythonDatetime(str(xmlRoot.get("date")))
            type = xmlRoot.get("type")
            description = xmlRoot.get("description", "")
            id = xmlRoot.get("id")
            name = xmlRoot.get("name")

            importedTrace = ImportedTrace(id, date, type, description, name)
            tracesFile = os.path.join(pathOfTraces, str(id) + ".gz")
            if not os.path.isfile(tracesFile):
                logging.warn("The trace file " + str(tracesFile) + " is referenced but doesn't exist.")
            else:
                gzipFile = gzip.open(tracesFile, 'rb')
                xml_content = gzipFile.read()
                gzipFile.close()

                tree = etree.parse(StringIO(xml_content))
                xmlRoot = tree.getroot()

                # We retrieve the pool of messages
                if xmlRoot.find("{" + namespace_workspace + "}messages") != None:
                    xmlMessages = xmlRoot.find("{" + namespace_workspace + "}messages")
                    for xmlMessage in xmlMessages.findall("{" + namespace_common + "}message"):
                        message = AbstractMessageFactory.loadFromXML(xmlMessage, namespace_common, version)
                        if message != None:
                            importedTrace.addMessage(message)

                # We retrieve the sessions
                if xmlRoot.find("{" + namespace_workspace + "}sessions") != None:
                    xmlSessions = xmlRoot.find("{" + namespace_workspace + "}sessions")
                    for xmlSession in xmlSessions.findall("{" + namespace_common + "}session"):
                        session = Session.loadFromXML(xmlSession, namespace_workspace, namespace_common, version, importedTrace)
                        if session != None:
                            importedTrace.addSession(session)
            return importedTrace
        return None
