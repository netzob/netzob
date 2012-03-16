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
import re
from lxml import etree
import uuid
import logging

#+---------------------------------------------------------------------------+
#| Local imports
#+---------------------------------------------------------------------------+


#+---------------------------------------------------------------------------+
#| Order:
#|     Class definition of an order in a sequence
#+---------------------------------------------------------------------------+
class Order(object):

    #+-----------------------------------------------------------------------+
    #| Constructor
    #+-----------------------------------------------------------------------+
    def __init__(self, value):
        self.value = value
        self.messages = []

    def addMessage(self, message):
        if not message in self.messages:
            self.messages.append(message)

    def removeMessage(self, message):
        if message in self.messages:
            self.messages.remove(message)
        else:
            logging.warn("Impossible to remove the message : it doesn't exist in order")

    def save(self, root, namespace):
        xmlOrder = etree.SubElement(root, "{" + namespace + "}order")
        xmlOrder.set("value", str(self.getValue()))
        for message in self.messages:
            xmlMessage = etree.SubElement(xmlOrder, "{" + namespace + "}msg-ref")
            xmlMessage.text = str(message.getID())

    #+----------------------------------------------
    #| GETTERS & SETTERS
    #+----------------------------------------------
    def getValue(self):
        return self.value

    def getMessages(self):
        return self.messages

    def setValue(self, value):
        self.value = value

    def setMesages(self, messages):
        self.messages = messages

    @staticmethod
    def loadFromXML(xmlRoot, vocabulary, namespace, version):
        if version == "0.1":
            order_value = int(xmlRoot.get("value"))

            order = Order(order_value)

            if xmlRoot.find("{" + namespace + "}msg-ref") != None:
                for xmlMsg in xmlRoot.findall("{" + namespace + "}msg-ref"):
                    msgID = str(xmlMsg.text)
                    msg = vocabulary.getMessageByID(msgID)
                    if msg == None:
                        logging.warn("Impossible to retrieve the message with ID " + str(msgID))
                    else:
                        order.addMessage(msg)

            return order

        return None
