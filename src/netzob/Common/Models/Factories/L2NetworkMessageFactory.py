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
from lxml import etree
import uuid

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.Token import Token


class L2NetworkMessageFactory(object):
    """Factory dedicated to the manipulation of network messages"""

    XML_SCHEMA_TYPE = "netzob-common:L2NetworkMessage"

    @staticmethod
    def save(message, xmlMessage, namespace_project, namespace):
        """Generate the XML representation of a Network message"""
        xmlMessage.set("{http://www.w3.org/2001/XMLSchema-instance}type", L2NetworkMessageFactory.XML_SCHEMA_TYPE)
        # Add network message properties
        L2NetworkMessageFactory.addL2PropertiesToElement(xmlMessage, message, namespace)

    @staticmethod
    def addL2PropertiesToElement(root, message, namespace):
        subL2Protocol = etree.SubElement(root, "{" + namespace + "}l2Protocol")
        subL2Protocol.text = message.getL2Protocol()
        subL2SourceAddress = etree.SubElement(root, "{" + namespace + "}l2SourceAddress")
        subL2SourceAddress.text = message.getL2SourceAddress()
        subL2DestinationAddress = etree.SubElement(root, "{" + namespace + "}l2DestinationAddress")
        subL2DestinationAddress.text = message.getL2DestinationAddress()

    @staticmethod
    def loadFromXML(rootElement, namespace, version, id, timestamp, data):
        """Function which parses an XML and extract from it
           the definition of a network message
           @param rootElement: XML root of the network message
           @return an instance of a NetworkMessage
           @raise NameError if XML invalid"""

        if rootElement.get("{http://www.w3.org/2001/XMLSchema-instance}type", "abstract") != L2NetworkMessageFactory.XML_SCHEMA_TYPE:
            raise NameError("The parsed xml doesn't represent a Network message.")

        # Retrieve layer 2 properties
        (l2Protocol, l2SourceAddress, l2DestinationAddress) = L2NetworkMessageFactory.loadL2Properties(rootElement, namespace)

        # IMPORTANT : Avoid circular import
        from netzob.Common.Models.L2NetworkMessage import L2NetworkMessage
        message = L2NetworkMessage(id, timestamp, data, l2Protocol, l2SourceAddress, l2DestinationAddress)

        return message

    @staticmethod
    def loadL2Properties(rootElement, namespace):
        l2Protocol = rootElement.find("{" + namespace + "}l2Protocol").text
        l2SourceAddress = rootElement.find("{" + namespace + "}l2SourceAddress").text
        l2DestinationAddress = rootElement.find("{" + namespace + "}l2DestinationAddress").text
        return (l2Protocol, l2SourceAddress, l2DestinationAddress)
