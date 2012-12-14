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

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+
from lxml.etree import ElementTree
from lxml import etree

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.Models.Factories.FileMessageFactory import FileMessageFactory
from netzob.Common.Models.Factories.OldFormatNetworkMessageFactory import OldFormatNetworkMessageFactory
from netzob.Common.Models.Factories.L2NetworkMessageFactory import L2NetworkMessageFactory
from netzob.Common.Models.Factories.L3NetworkMessageFactory import L3NetworkMessageFactory
from netzob.Common.Models.Factories.L4NetworkMessageFactory import L4NetworkMessageFactory
from netzob.Common.Models.Factories.IPCMessageFactory import IPCMessageFactory
from netzob.Common.Models.Factories.IRPMessageFactory import IRPMessageFactory
from netzob.Common.Models.Factories.IRPDeviceIoControlMessageFactory import IRPDeviceIoControlMessageFactory
from netzob.Common.Models.Factories.RawMessageFactory import RawMessageFactory


class AbstractMessageFactory(object):
    """Factory dedicated to the manipulation of file messages"""

    @staticmethod
    def save(message, root, namespace_project, namespace_common):
        """Generate an XML representation of a message"""

        # Create the initial xml tree
        xmlMessage = etree.SubElement(root, "{" + namespace_common + "}message")
        xmlMessage.set("id", str(message.getID()))
        xmlMessage.set("timestamp", str(message.getTimestamp()))

        # Add the data
        subData = etree.SubElement(xmlMessage, "{" + namespace_common + "}data")
        subData.text = str(message.getData())

        # Depending of the type, we add its proper meta-datas
        if message.getType() == "File":
            FileMessageFactory.save(message, xmlMessage, namespace_project, namespace_common)
        elif message.getType() == "L2Network":
            L2NetworkMessageFactory.save(message, xmlMessage, namespace_project, namespace_common)
        elif message.getType() == "L3Network":
            L3NetworkMessageFactory.save(message, xmlMessage, namespace_project, namespace_common)
        elif message.getType() == "L4Network":
            L4NetworkMessageFactory.save(message, xmlMessage, namespace_project, namespace_common)
        elif message.getType() == "IPC":
            IPCMessageFactory.save(message, xmlMessage, namespace_project, namespace_common)
        elif message.getType() == "IRP":
            IRPMessageFactory.save(message, xmlMessage, namespace_project, namespace_common)
        elif message.getType() == "IRPDeviceIoControl":
            IRPDeviceIoControlMessageFactory.save(message, xmlMessage, namespace_project, namespace_common)
        elif message.getType() == "RAW":
            RawMessageFactory.save(message, xmlMessage, namespace_project, namespace_common)
        else:
            raise NameError('''There is no factory which would support
            the generation of an xml representation of the message : ''' + str(message))

        return etree.tostring(xmlMessage)

    @staticmethod
    def loadFromXML(rootElement, namespace, version):
        """loadFromXML:
           Function which parses an XML and extract from it
           the definition of a file message
           @param rootElement: XML root of the file message
           @return an instance of a message
           @throw NameError if XML invalid"""

        # Computes which type is it
        if rootElement.get("{http://www.w3.org/2001/XMLSchema-instance}type", "abstract") == "abstract":
            raise NameError("The parsed xml doesn't represent a valid type message.")

        # Parse common attributes (id, timestamp, data)
        # Parse the data field and transform it into a byte array
        if rootElement.find("{" + namespace + "}data") is None or not rootElement.find("{" + namespace + "}data").text:
            raise NameError("The parsed message has no data specified")
        data = bytearray(rootElement.find("{" + namespace + "}data").text)
        id = str(rootElement.get("id"))
        timestamp = float(rootElement.get("timestamp"))

        if rootElement.get("{http://www.w3.org/2001/XMLSchema-instance}type", "abstract") == FileMessageFactory.XML_SCHEMA_TYPE:
            return FileMessageFactory.loadFromXML(rootElement, namespace, version, id, timestamp, data)

#        # Preserve compatibility with former traces
#        elif rootElement.get("{http://www.w3.org/2001/XMLSchema-instance}type", "abstract") == "netzob-common:NetworkMessage":
#            return OldFormatNetworkMessageFactory.loadFromXML(rootElement, namespace, version)

        elif rootElement.get("{http://www.w3.org/2001/XMLSchema-instance}type", "abstract") == L2NetworkMessageFactory.XML_SCHEMA_TYPE:
            return L2NetworkMessageFactory.loadFromXML(rootElement, namespace, version, id, timestamp, data)

        elif rootElement.get("{http://www.w3.org/2001/XMLSchema-instance}type", "abstract") == L3NetworkMessageFactory.XML_SCHEMA_TYPE:
            return L3NetworkMessageFactory.loadFromXML(rootElement, namespace, version, id, timestamp, data)

        elif rootElement.get("{http://www.w3.org/2001/XMLSchema-instance}type", "abstract") == L4NetworkMessageFactory.XML_SCHEMA_TYPE:
            return L4NetworkMessageFactory.loadFromXML(rootElement, namespace, version, id, timestamp, data)

        elif rootElement.get("{http://www.w3.org/2001/XMLSchema-instance}type", "abstract") == IPCMessageFactory.XML_SCHEMA_TYPE:
            return IPCMessageFactory.loadFromXML(rootElement, namespace, version, id, timestamp, data)

        elif rootElement.get("{http://www.w3.org/2001/XMLSchema-instance}type", "abstract") == IRPMessageFactory.XML_SCHEMA_TYPE:
            return IRPMessageFactory.loadFromXML(rootElement, namespace, version, id, timestamp, data)

        elif rootElement.get("{http://www.w3.org/2001/XMLSchema-instance}type", "abstract") == IRPDeviceIoControlMessageFactory.XML_SCHEMA_TYPE:
            return IRPDeviceIoControlMessageFactory.loadFromXML(rootElement, namespace, version, id, timestamp, data)

        elif rootElement.get("{http://www.w3.org/2001/XMLSchema-instance}type", "abstract") == RawMessageFactory.XML_SCHEMA_TYPE:
            return RawMessageFactory.loadFromXML(rootElement, namespace, version, id, timestamp, data)
        else:
            raise NameError("The parsed xml doesn't represent a valid type message.")
            return None
