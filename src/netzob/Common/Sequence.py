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

#+---------------------------------------------------------------------------+
#| Local imports
#+---------------------------------------------------------------------------+
from netzob.Common.Order import Order


#+---------------------------------------------------------------------------+
#| Sequence:
#|     Class definition of a sequence of "simili"-abstracted message
#+---------------------------------------------------------------------------+
class Sequence(object):

    #+-----------------------------------------------------------------------+
    #| Constructor
    #+-----------------------------------------------------------------------+
    def __init__(self, id, name, description):
        self.id = id
        self.name = name
        self.description = description
        self.orders = []

    def addOrder(self, order):
        self.orders.append(order)

    def addMessage(self, message, orderNumber):
        # We retrieve the order (if it exists)
        order = self.getOrderByValue(orderNumber)
        # if it doesn't exist we create it
        if order == None:
            order = Order(orderNumber)
            self.orders.append(order)
        order.addMessage(message)

    def getOrderByValue(self, value):
        for order in self.orders:
            if order.getValue() == value:
                return order
        return None

    def getSortedOrders(self):
        return sorted(self.orders, key=lambda Order: Order.value)

    def save(self, root, namespace):
        xmlSequence = etree.SubElement(root, "{" + namespace + "}sequence")
        xmlSequence.set("id", str(self.getID()))
        xmlSequence.set("name", str(self.getName()))

        if self.getDescription() != None:
            xmlSequence.set("description", str(self.getDescription()))

        for order in self.getSortedOrders():
            order.save(xmlSequence, namespace)

    #+----------------------------------------------
    #| GETTERS
    #+----------------------------------------------
    def getID(self):
        return self.id

    def getName(self):
        return self.name

    def getDescription(self):
        return self.description

    def setID(self, id):
        self.id = id

    def setName(self, name):
        self.name = name

    def setDescription(self, description):
        self.description = description

    @staticmethod
    def loadFromXML(xmlRoot, vocabulary, namespace, version):
        if version == "0.1":
            sequence_ID = xmlRoot.get("id")
            sequence_name = xmlRoot.get("name")
            sequence_description = xmlRoot.get("description")

            sequence = Sequence(sequence_ID, sequence_name, sequence_description)

            for xmlOrder in xmlRoot.findall("{" + namespace + "}order"):
                order = Order.loadFromXML(xmlOrder, vocabulary, namespace, version)
                sequence.addOrder(order)

            return sequence

        return None
