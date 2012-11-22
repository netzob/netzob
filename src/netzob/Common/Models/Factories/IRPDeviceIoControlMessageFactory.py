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
import uuid

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+
from lxml.etree import ElementTree
from netzob.Common.Type.TypeConvertor import TypeConvertor
from netzob.Common.Token import Token
from lxml import etree
from netzob.Common.Models.Factories.IRPMessageFactory import IRPMessageFactory

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+


#+---------------------------------------------------------------------------+
#| IRPDeviceIoControlMessageFactory:
#|     Factory dedicated to the manipulation of IRP IOCTL messages
#| ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~+
#+---------------------------------------------------------------------------+
class IRPDeviceIoControlMessageFactory(object):

    XML_SCHEMA_TYPE = "netzob-common:IRPDeviceIoControlMessage"

    @staticmethod
    #+-----------------------------------------------------------------------+
    #| save
    #|     Generate the XML representation of a IRP IOCTL message
    #+-----------------------------------------------------------------------+
    def save(message, xmlMessage, namespace_project, namespace):

        xmlMessage.set("{http://www.w3.org/2001/XMLSchema-instance}type", IRPDeviceIoControlMessageFactory.XML_SCHEMA_TYPE)

        IRPMessageFactory.addPropertiesToElement(xmlMessage, message, namespace)

        # ioctl
        subIoctl = etree.SubElement(xmlMessage, "{" + namespace + "}ioctl")
        subIoctl.text = str(message.getIOCTL())

    @staticmethod
    #+---------------------------------------------------------------------------+
    #| loadFromXML:
    #|     Function which parses an XML and extract from it
    #[    the definition of a IRP message
    #| @param rootElement: XML root of the IRP IOCTL message
    #| @return an instance of a IRPDeviceIoControlMessage
    #| @throw NameError if XML invalid
    #+---------------------------------------------------------------------------+
    def loadFromXML(rootElement, namespace, version, id, timestamp, data):

        # Then we verify its an IPC Message
        if rootElement.get("{http://www.w3.org/2001/XMLSchema-instance}type", "abstract") != IRPDeviceIoControlMessageFactory.XML_SCHEMA_TYPE:
            raise NameError("The parsed xml doesn't represent a IRP IOCTL message.")

        # Retrieve properties from normal IRP
        (msg_direction, msg_major, msg_minor, msg_requestMode, msg_pid, msg_status, msg_information, msg_cancel, msg_sizeIn, msg_sizeOut) = IRPMessageFactory.loadProperties(rootElement, namespace)

        # Retrieves the ioctl
        msg_ioctl = int(rootElement.find("{" + namespace + "}ioctl").text)

        # TODO : verify this ! Circular imports in python !
        # WARNING : verify this ! Circular imports in python !
        from netzob.Common.Models.IRPDeviceIoControlMessage import IRPDeviceIoControlMessage

        result = IRPDeviceIoControlMessage(id, timestamp, data, msg_direction, msg_major, msg_minor, msg_requestMode, msg_pid, msg_status, msg_information, msg_cancel, msg_sizeIn, msg_sizeOut, msg_ioctl)

        return result
