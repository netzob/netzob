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
from netzob.Common.Models.Factories.L2NetworkMessageFactory import L2NetworkMessageFactory


class L3NetworkMessageFactory(object):
    """Factory dedicated to the manipulation of network messages"""

    XML_SCHEMA_TYPE = "netzob-common:L3NetworkMessage"

    @staticmethod
    def save(message, xmlMessage, namespace_project, namespace):
        """Generate the XML representation of a Network message"""
        xmlMessage.set("{http://www.w3.org/2001/XMLSchema-instance}type", L3NetworkMessageFactory.XML_SCHEMA_TYPE)

        # Add network message properties
        L2NetworkMessageFactory.addL2PropertiesToElement(xmlMessage, message, namespace)
        L3NetworkMessageFactory.addL3PropertiesToElement(xmlMessage, message, namespace)

    @staticmethod
    def addL3PropertiesToElement(root, message, namespace):
        subL3Protocol = etree.SubElement(root, "{" + namespace + "}l3Protocol")
        subL3Protocol.text = message.getL3Protocol()
        subL3SourceAddress = etree.SubElement(root, "{" + namespace + "}l3SourceAddress")
        subL3SourceAddress.text = message.getL3SourceAddress()
        subL3DestinationAddress = etree.SubElement(root, "{" + namespace + "}l3DestinationAddress")
        subL3DestinationAddress.text = message.getL3DestinationAddress()

    @staticmethod
    def loadFromXML(rootElement, namespace, version, id, timestamp, data):
        """Function which parses an XML and extract from it
           the definition of a network message
           @param rootElement: XML root of the network message
           @return an instance of a NetworkMessage
           @raise NameError if XML invalid"""

        if rootElement.get("{http://www.w3.org/2001/XMLSchema-instance}type", "abstract") != L3NetworkMessageFactory.XML_SCHEMA_TYPE:
            raise NameError("The parsed xml doesn't represent a Network message.")

        # Retrieve layer 2 properties
        (l2Protocol, l2SourceAddress, l2DestinationAddress) = L2NetworkMessageFactory.loadL2Properties(rootElement, namespace)
        #Retrieve layer 3 properties
        (l3Protocol, l3SourceAddress, l3DestinationAddress) = L3NetworkMessageFactory.loadL3Properties(rootElement, namespace)

        # IMPORTANT : Avoid circular import
        from netzob.Common.Models.L3NetworkMessage import L3NetworkMessage
        message = L3NetworkMessage(id, timestamp, data, l2Protocol, l2SourceAddress, l2DestinationAddress, l3Protocol, l3SourceAddress, l3DestinationAddress)

        return message

    @staticmethod
    def loadL3Properties(rootElement, namespace):
        l3Protocol = rootElement.find("{" + namespace + "}l3Protocol").text
        l3SourceAddress = rootElement.find("{" + namespace + "}l3SourceAddress").text
        l3DestinationAddress = rootElement.find("{" + namespace + "}l3DestinationAddress").text
        return (l3Protocol, l3SourceAddress, l3DestinationAddress)
