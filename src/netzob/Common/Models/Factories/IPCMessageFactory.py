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
import uuid

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+
from lxml.etree import ElementTree
from lxml import etree

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+


#+---------------------------------------------------------------------------+
#| IPCMessageFactory:
#|     Factory dedicated to the manipulation of IPC messages
#| ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~+
#| XML Definition:
#| <message type="IPC" id="">
#|     <category></category>
#|     <key></key>
#|     <name></name>
#|     <type></type>
#|     <direction></direction>
#|     <timestamp></timestamp>
#|     <data></data>
#| </message>
#+---------------------------------------------------------------------------+
class IPCMessageFactory(object):

    XML_SCHEMA_TYPE = "netzob-common:IPCMessage"

    @staticmethod
    #+-----------------------------------------------------------------------+
    #| save
    #|     Generate the XML representation of an IPC message
    #+-----------------------------------------------------------------------+
    def save(message, xmlMessage, namespace_project, namespace):

        xmlMessage.set("{http://www.w3.org/2001/XMLSchema-instance}type", IPCMessageFactory.XML_SCHEMA_TYPE)

        # Add message properties
        IPCMessageFactory.addPropertiesToElement(xmlMessage, message, namespace)

    @staticmethod
    def addPropertiesToElement(xmlMessage, message, namespace):
        # category
        subCategory = etree.SubElement(xmlMessage, "{" + namespace + "}category")
        subCategory.text = str(message.getCategory())
        # key
        subKey = etree.SubElement(xmlMessage, "{" + namespace + "}key")
        subKey.text = str(message.getKey())
        # type
        subType = etree.SubElement(xmlMessage, "{" + namespace + "}type")
        subType.text = str(message.getType())
        # direction
        subDirection = etree.SubElement(xmlMessage, "{" + namespace + "}direction")
        subDirection.text = str(message.getDirection())

    @staticmethod
    #+---------------------------------------------------------------------------+
    #| loadFromXML:
    #|     Function which parses an XML and extract from it
    #[    the definition of an IPC message
    #| @param rootElement: XML root of the IPC message
    #| @return an instance of a n IPC Message
    #| @throw NameError if XML invalid
    #+---------------------------------------------------------------------------+
    def loadFromXML(rootElement, namespace, version):
        # Then we verify its an IPC Message
        if rootElement.get("{http://www.w3.org/2001/XMLSchema-instance}type", "abstract") != "netzob-common:IPCMessage":
            raise NameError("The parsed xml doesn't represent an IPC message.")

        # Verifies the data field
        if rootElement.find("{" + namespace + "}data") is None or not rootElement.find("{" + namespace + "}data").text:
            raise NameError("The parsed message has no data specified")

        # Parse the data field and transform it into a byte array
        msg_data = bytearray(rootElement.find("{" + namespace + "}data").text)

        # Retrieve the id
        msg_id = str(rootElement.get("id"))

        # Retrieve the timestamp
        msg_timestamp = int(rootElement.get("timestamp"))

        # Retrieves the category
        msg_category = rootElement.find("{" + namespace + "}category").text

        # Retrieves the key
        msg_key = rootElement.find("{" + namespace + "}key").text

        # Retrieves the type
        msg_type = rootElement.find("{" + namespace + "}type").text

        # Retrieves the direction
        msg_direction = rootElement.find("{" + namespace + "}direction").text

        # TODO : verify this ! Circular imports in python !
        # WARNING : verify this ! Circular imports in python !
        from netzob.Common.Models.IPCMessage import IPCMessage

        result = IPCMessage(msg_id, msg_timestamp, msg_data, msg_category, msg_key, msg_direction)

        return result
