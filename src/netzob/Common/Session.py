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
from lxml.etree import ElementTree
from lxml import etree

#+---------------------------------------------------------------------------+
#| Local Imports
#+---------------------------------------------------------------------------+


#+---------------------------------------------------------------------------+
#| Session:
#|     Class definition of a session of messages
#+---------------------------------------------------------------------------+
class Session(object):

    #+-----------------------------------------------------------------------+
    #| Constructor
    #+-----------------------------------------------------------------------+
    def __init__(self, id, name, description):
        self.id = id
        self.name = name
        self.description = description
        self.messages = []

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

    def setID(self, id):
        self.id = id

    def setName(self, name):
        self.name = name

    def setDescription(self, description):
        self.description = description

    def save(self, root, namespace_main, namespace_common):
        xmlSession = etree.SubElement(root, "{" + namespace_common + "}session")
        xmlSession.set("id", str(self.getID()))
        if self.getName() != None:
            xmlSession.set("name", str(self.getName()))
        if self.getDescription() != None:
            xmlSession.set("description", str(self.getDescription()))

        xmlMessagesRef = etree.SubElement(xmlSession, "{" + namespace_common + "}messages-ref")
        for message in self.getMessages():
            xmlMessage = etree.SubElement(xmlMessagesRef, "{" + namespace_common + "}message-ref")
            xmlMessage.set("id", str(message.getID()))

    #+----------------------------------------------
    #| Static methods
    #+----------------------------------------------
    @staticmethod
    def loadFromXML(xmlRoot, namespace_main, namespace_common, version, poolOfMessages):
        if version == "0.1":
            id = xmlRoot.get("id")
            name = xmlRoot.get("name")
            description = xmlRoot.get("description")

            session = Session(id, name, description)

            if xmlRoot.find("{" + namespace_common + "}messages-ref") != None:
                xmlMessages = xmlRoot.find("{" + namespace_common + "}messages-ref")
                for xmlMessage in xmlMessages.findall("{" + namespace_common + "}message-ref"):
                    id = xmlMessage.get("id")
                    message = poolOfMessages.getMessageByID(id)
                    if message != None:
                        message.setSession(session)
                        session.addMessage(message)
            return session
        return None
