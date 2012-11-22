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

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+


#+---------------------------------------------------------------------------+
#| IRPMessageFactory:
#|     Factory dedicated to the manipulation of IRP messages
#| ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~+
#+---------------------------------------------------------------------------+
class IRPMessageFactory(object):

    XML_SCHEMA_TYPE = "netzob-common:IRPMessage"

    @staticmethod
    #+-----------------------------------------------------------------------+
    #| save
    #|     Generate the XML representation of a IRP message
    #+-----------------------------------------------------------------------+
    def save(message, xmlMessage, namespace_project, namespace):

        xmlMessage.set("{http://www.w3.org/2001/XMLSchema-instance}type", IRPMessageFactory.XML_SCHEMA_TYPE)

        # Add message properties
        IRPMessageFactory.addPropertiesToElement(xmlMessage, message, namespace)

    @staticmethod
    def addPropertiesToElement(xmlMessage, message, namespace):
        # direction
        subDirection = etree.SubElement(xmlMessage, "{" + namespace + "}direction")
        subDirection.text = message.getDirection()
        # major
        subMajor = etree.SubElement(xmlMessage, "{" + namespace + "}major")
        subMajor.text = message.getMajor()
        # minor
        subMinor = etree.SubElement(xmlMessage, "{" + namespace + "}minor")
        subMinor.text = str(message.getMinor())
        # requestMode
        subRequestMode = etree.SubElement(xmlMessage, "{" + namespace + "}requestMode")
        subRequestMode.text = message.getRequestMode()
        # pid
        subPid = etree.SubElement(xmlMessage, "{" + namespace + "}pid")
        subPid.text = str(message.getPID())
        # status
        subStatus = etree.SubElement(xmlMessage, "{" + namespace + "}status")
        subStatus.text = str(message.getStatus())
        # information
        subInformation = etree.SubElement(xmlMessage, "{" + namespace + "}information")
        subInformation.text = str(message.getInformation())
        # cancel
        subCancel = etree.SubElement(xmlMessage, "{" + namespace + "}cancel")
        subCancel.text = TypeConvertor.bool2str(message.getCancel())
        # sizeIn
        subSizeIn = etree.SubElement(xmlMessage, "{" + namespace + "}sizeIn")
        subSizeIn.text = str(message.getSizeIn())
        # sizeOut
        subSizeOut = etree.SubElement(xmlMessage, "{" + namespace + "}sizeOut")
        subSizeOut.text = str(message.getSizeOut())

    @staticmethod
    #+---------------------------------------------------------------------------+
    #| loadFromXML:
    #|     Function which parses an XML and extract from it
    #[    the definition of a IRP message
    #| @param rootElement: XML root of the IRP message
    #| @return an instance of a IRPMessage
    #| @throw NameError if XML invalid
    #+---------------------------------------------------------------------------+
    def loadFromXML(rootElement, namespace, version, id, timestamp, data):

        # Then we verify its an IPC Message
        if rootElement.get("{http://www.w3.org/2001/XMLSchema-instance}type", "abstract") != IRPMessageFactory.XML_SCHEMA_TYPE:
            raise NameError("The parsed xml doesn't represent a IRP message.")

        # Retrieve properties
        (msg_direction, msg_major, msg_minor, msg_requestMode, msg_pid, msg_status, msg_information, msg_cancel, msg_sizeIn, msg_sizeOut) = IRPMessageFactory.loadProperties(rootElement, namespace)

        # TODO : verify this ! Circular imports in python !
        # WARNING : verify this ! Circular imports in python !
        from netzob.Common.Models.IRPMessage import IRPMessage

        result = IRPMessage(id, timestamp, data, "IRP", msg_direction, msg_major, msg_minor, msg_requestMode, msg_pid, msg_status, msg_information, msg_cancel, msg_sizeIn, msg_sizeOut)

        return result

    @staticmethod
    def loadProperties(rootElement, namespace):
        # Retrieves the direction
        msg_direction = rootElement.find("{" + namespace + "}direction").text

        # Retrieves the major
        msg_major = rootElement.find("{" + namespace + "}major").text

        # Retrieves the minor
        msg_minor = int(rootElement.find("{" + namespace + "}minor").text)

        # Retrieves the requestMode
        msg_requestMode = rootElement.find("{" + namespace + "}requestMode").text

        # Retrieves the pid
        msg_pid = int(rootElement.find("{" + namespace + "}pid").text)

        # Retrieves the status
        msg_status = int(rootElement.find("{" + namespace + "}status").text)

        # Retrieves the information
        msg_information = long(rootElement.find("{" + namespace + "}information").text)

        # Retrieves the cancel
        msg_cancel = TypeConvertor.str2bool(rootElement.find("{" + namespace + "}cancel").text)

        # Retrieves the sizeIn
        msg_sizeIn = int(rootElement.find("{" + namespace + "}sizeIn").text)

        # Retrieves the sizeOut
        msg_sizeOut = int(rootElement.find("{" + namespace + "}sizeOut").text)

        return (msg_direction, msg_major, msg_minor, msg_requestMode, msg_pid, msg_status, msg_information, msg_cancel, msg_sizeIn, msg_sizeOut)
