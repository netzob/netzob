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
from gettext import gettext as _
import logging
from lxml.etree import ElementTree
from lxml import etree
import uuid

#+---------------------------------------------------------------------------+
#| Local Imports
#+---------------------------------------------------------------------------+
from netzob.Common.Property import Property
from netzob.Common.Type.Format import Format
from netzob.Common.Type.TypeConvertor import TypeConvertor
from netzob.Common.ProjectConfiguration import ProjectConfiguration


#+---------------------------------------------------------------------------+
#| Session:
#|     Class definition of a session of messages
#+---------------------------------------------------------------------------+
class Session(object):

    #+-----------------------------------------------------------------------+
    #| Constructor
    #+-----------------------------------------------------------------------+
    def __init__(self, id, name, project, description):
        self.id = id
        self.name = name
        self.project = project
        self.description = description
        self.messages = []

        # Interpretation attributes
        if self.project is not None:
            self.format = self.project.getConfiguration().getVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_GLOBAL_FORMAT)
            self.unitSize = self.project.getConfiguration().getVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_GLOBAL_UNITSIZE)
            self.sign = self.project.getConfiguration().getVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_GLOBAL_SIGN)
            self.endianess = self.project.getConfiguration().getVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_GLOBAL_ENDIANESS)
        else:
            self.format = None
            self.unitSize = None
            self.sign = None
            self.endianess = None

    def addMessage(self, message):
        self.messages.append(message)

    def getID(self):
        return self.id

    def getName(self):
        return self.name

    def getDescription(self):
        return self.description

    def getMessages(self):
        return self.messages

    def getFormat(self):
        return self.format

    def getUnitSize(self):
        return self.unitSize

    def getSign(self):
        return self.sign

    def getEndianess(self):
        return self.endianess

    def setFormat(self, aFormat):
        self.format = aFormat

    def setUnitSize(self, unitSize):
        self.unitSize = unitSize

    def setSign(self, sign):
        self.sign = sign

    def setEndianess(self, endianess):
        self.endianess = endianess

    def setID(self, id):
        self.id = id

    def setName(self, name):
        self.name = name

    def setDescription(self, description):
        self.description = description

    def save(self, root, namespace_main, namespace_common):
        xmlSession = etree.SubElement(root, "{" + namespace_common + "}session")
        xmlSession.set("id", str(self.getID()))
        if self.getName() is not None:
            xmlSession.set("name", str(self.getName()))
        if self.getDescription() is not None:
            xmlSession.set("description", str(self.getDescription()))

        if self.getFormat() is not None:
            xmlSessionFormat = etree.SubElement(xmlSession, "{" + namespace_common + "}format")
            xmlSessionFormat.text = str(self.getFormat())

        if self.getUnitSize() is not None:
            xmlSessionUnitSize = etree.SubElement(xmlSession, "{" + namespace_common + "}unitsize")
            xmlSessionUnitSize.text = str(self.getUnitSize())

        if self.getSign() is not None:
            xmlSessionSign = etree.SubElement(xmlSession, "{" + namespace_common + "}sign")
            xmlSessionSign.text = str(self.getSign())

        if self.getEndianess() is not None:
            xmlSessionEndianess = etree.SubElement(xmlSession, "{" + namespace_common + "}endianess")
            xmlSessionEndianess.text = str(self.getEndianess())

        xmlMessagesRef = etree.SubElement(xmlSession, "{" + namespace_common + "}messages-ref")
        for message in self.getMessages():
            xmlMessage = etree.SubElement(xmlMessagesRef, "{" + namespace_common + "}message-ref")
            xmlMessage.set("id", str(message.getID()))

    def getProperties(self):
        properties = []
        prop = Property('name', Format.STRING, self.getName())
        prop.setIsEditable(True)
        properties.append(prop)

        properties.append(Property('messages', Format.DECIMAL, len(self.getMessages())))
        minMsgSize = None
        maxMsgSize = 0
        avgMsgSize = 0
        if len(self.getMessages()) > 0:
            for m in self.getMessages():
                s = len(m.getData()) * 2
                if minMsgSize is None or s < minMsgSize:
                    minMsgSize = s
                if maxMsgSize is None or s > maxMsgSize:
                    maxMsgSize = s
                avgMsgSize += s
            avgMsgSize = avgMsgSize / len(self.getMessages())
        properties.append(Property('avg msg size (bytes)', Format.DECIMAL, avgMsgSize))
        properties.append(Property('min msg size (bytes)', Format.DECIMAL, minMsgSize))
        properties.append(Property('max msg size (bytes)', Format.DECIMAL, maxMsgSize))

        return properties

    #+----------------------------------------------
    #| Static methods
    #+----------------------------------------------
    @staticmethod
    def loadFromXML(xmlRoot, namespace_main, namespace_common, version, project, poolOfMessages):
        if version == "0.1":
            id = str(xmlRoot.get("id"))
            name = xmlRoot.get("name")
            description = xmlRoot.get("description")

            session = Session(id, name, project, description)

            if xmlRoot.find("{" + namespace_common + "}format") is not None:
                session_format = xmlRoot.find("{" + namespace_common + "}format").text
                session.setFormat(session_format)

            if xmlRoot.find("{" + namespace_common + "}unitsize") is not None:
                session_unitsize = xmlRoot.find("{" + namespace_common + "}unitsize").text
                session.setUnitSize(session_unitsize)

            if xmlRoot.find("{" + namespace_common + "}sign") is not None:
                session_sign = xmlRoot.find("{" + namespace_common + "}sign").text
                session.setSign(session_sign)

            if xmlRoot.find("{" + namespace_common + "}endianess") is not None:
                session_endianess = xmlRoot.find("{" + namespace_common + "}endianess").text
                session.setEndianess(session_endianess)

            if xmlRoot.find("{" + namespace_common + "}messages-ref") is not None:
                xmlMessages = xmlRoot.find("{" + namespace_common + "}messages-ref")
                for xmlMessage in xmlMessages.findall("{" + namespace_common + "}message-ref"):
                    id = xmlMessage.get("id")
                    message = poolOfMessages.getMessageByID(id)
                    if message is not None:
                        message.setSession(session)
                        session.addMessage(message)
            return session
        return None
