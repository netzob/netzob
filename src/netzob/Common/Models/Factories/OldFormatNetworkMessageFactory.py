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
from lxml import etree

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.Token import Token
from netzob.Common.Models.L4NetworkMessage import L4NetworkMessage


class OldFormatNetworkMessageFactory(object):
    """Factory dedicated to the manipulation of network messages"""

    @staticmethod
    def save(message, xmlMessages, namespace_project, namespace):
        """Generate the XML representation of a Network message"""
        root = etree.SubElement(xmlMessages, "{" + namespace + "}message")
        root.set("id", str(message.getID()))
        root.set("timestamp", str(message.getTimestamp()))
        root.set("{http://www.w3.org/2001/XMLSchema-instance}type", "netzob-common:NetworkMessage")
        # data
        subData = etree.SubElement(root, "{" + namespace + "}data")
        subData.text = str(message.getData())
        # ipSource
        subIpSource = etree.SubElement(root, "{" + namespace + "}ip_source")
        subIpSource.text = message.getIPSource()
        # ipTarget
        subIpTarget = etree.SubElement(root, "{" + namespace + "}ip_destination")
        subIpTarget.text = message.getIPDestination()
        # protocol
        subProtocol = etree.SubElement(root, "{" + namespace + "}protocol")
        subProtocol.text = message.getProtocol()
        # l4 source port
        subL4SourcePort = etree.SubElement(root, "{" + namespace + "}l4_source_port")
        subL4SourcePort.text = str(message.getL4SourcePort())
        # l4 target port
        subL4TargetPort = etree.SubElement(root, "{" + namespace + "}l4_destination_port")
        subL4TargetPort.text = str(message.getL4DestinationPort())
        #pattern
        subPattern = etree.SubElement(root, "{" + namespace + "}pattern")
        subsubDirection = etree.SubElement(subPattern, "{" + namespace + "}direction")
        subsubDirection.text = str(message.getPattern()[0])
        for t in message.getPattern()[1]:
            subsubToken = etree.SubElement(subPattern, "{" + namespace + "}token")
            subsubToken.set("format", t.getFormat())
            subsubToken.set("length", str(t.getLength()))
            subsubToken.set("type", t.getType())
            subsubToken.set("value", t.getValue().encode("base-64"))
        return etree.tostring(root)

    @staticmethod
    def loadFromXML(rootElement, namespace, version):
        """Function which parses an XML and extract from it
           the definition of a network message
           @param rootElement: XML root of the network message
           @return an instance of a NetworkMessage
           @raise NameError if XML invalid"""

        # Then we verify its an IPC Message
        if rootElement.get("{http://www.w3.org/2001/XMLSchema-instance}type", "abstract") != "netzob-common:NetworkMessage":
            raise NameError("The parsed xml doesn't represent a Network message.")

        # Verifies the data field
        if rootElement.find("{" + namespace + "}data") is None or rootElement.find("{" + namespace + "}data").text is None or not rootElement.find("{" + namespace + "}data").text:
            raise NameError("The parsed message has no data specified")

        # Parse the data field and transform it into a byte array
        msg_data = bytearray(rootElement.find("{" + namespace + "}data").text)

        # Retrieve the id
        msg_id = str(rootElement.get("id"))

        # Retrieve the timestamp
        msg_timestamp = int(rootElement.get("timestamp"))

        # Retrieves the ip source
        msg_ipSource = rootElement.find("{" + namespace + "}ip_source").text

        # Retrieves the ip target
        msg_ipDestination = rootElement.find("{" + namespace + "}ip_destination").text

        # Retrieves the protocol
        msg_protocol = rootElement.find("{" + namespace + "}protocol").text

        # Retrieves the l4 source port
        msg_l4SourcePort = rootElement.find("{" + namespace + "}l4_source_port").text

        # Retrieves the l4 target port (default 0)
        msg_l4TargetPort = rootElement.find("{" + namespace + "}l4_destination_port").text

        #Retrieve pattern
        pattern = []
        try:
            patTemp = rootElement.find("{" + namespace + "}pattern")
            pattern.append(patTemp.find("{" + namespace + "}direction").text)
            tokens = patTemp.findall("{" + namespace + "}token")
            #print "find "+str(tokens)
            tokenList = []
            for t in tokens:
                t_format = t.get("format")
                t_length = t.get("length")
                t_type = t.get("type")
                t_value = t.get("value").decode("base-64")
                tokenList.append(Token(t_format, t_length, t_type, t_value))
            pattern.append(tokenList)
        except:
            pattern = []

        result = L4NetworkMessage(msg_id, msg_timestamp, msg_data,
                                  None, None, None,  # Layer 2 Information
                                  "IP", msg_ipSource, msg_ipDestination,
                                  msg_protocol, msg_l4SourcePort, msg_l4TargetPort,
                                  pattern)

        return result
