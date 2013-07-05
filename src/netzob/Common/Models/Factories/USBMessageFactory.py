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


class USBMessageFactory(object):
    """Factory dedicated to the manipulation of USB messages"""

    XML_SCHEMA_TYPE = "netzob-common:USBMessage"

    @staticmethod
    def save(message, xmlMessage, namespace_project, namespace):
        """Generate the XML representation of a USB message"""
        xmlMessage.set("{http://www.w3.org/2001/XMLSchema-instance}type", USBMessageFactory.XML_SCHEMA_TYPE)

        subEndpointElements = etree.SubElement(xmlMessage, "{" + namespace + "}endpoint")

        # endpoint configuration
        endpointConfiguration = etree.SubElement(subEndpointElements, "{" + namespace_common + "}configuration")
        endpointConfiguration.text = str(message.getEndpointConfiguration())
        # endpoint interface
        endpointInterface = etree.SubElement(subEndpointElements, "{" + namespace_common + "}interface")
        endpointInterface.text = str(message.getEndpointInterface())
        # endpoint type
        endpointType = etree.SubElement(subEndpointElements, "{" + namespace_common + "}type")
        endpointType.text = str(message.getEndpointType())
        # endpoint dir
        endpointDir = etree.SubElement(subEndpointElements, "{" + namespace_common + "}dir")
        endpointDir.text = str(message.getEndpointDir())
        # endpoint number
        endpointNumber = etree.SubElement(subEndpointElements, "{" + namespace_common + "}number")
        endpointNumber.text = str(message.getEndpointNumber())

        # direction
        direction = etree.SubElement(xmlMessage, "{" + namespace_common + "}direction")
        direction.text = str(message.getDirection())
        # status
        status = etree.SubElement(xmlMessage, "{" + namespace_common + "}status")
        status.text = str(message.getStatus())
        # buffer length
        bufferLength = etree.SubElement(xmlMessage, "{" + namespace_common + "}buffer_length")
        bufferLength.text = str(message.getBufferLength())
        # actuel length
        actualLength = etree.SubElement(xmlMessage, "{" + namespace_common + "}actual_length")
        actualLength.text = str(message.getActualLength())

    @staticmethod
    def loadFromXML(rootElement, namespace, version, id, timestamp, data):
        """Function which parses an XML and extract from it
           the definition of a USB message
           @param rootElement: XML root of the USB message
           @return an instance of a USBMessage
           @raise NameError if XML invalid"""

        # endpoint
        if rootElement.find("{" + namespace + "}endpoint") is not None:
            endpointElement = rootElement.find("{" + namespace + "}endpoint")
        else:
            return None
        # endpoint configuration
        endpointConfiguration = str(endpointElement.find("{" + namespace + "}configuration").text)
        # endpoint interface
        endpointInterface = str(endpointElement.find("{" + namespace + "}interface").text)
        # endpoint type
        endpointType = str(endpointElement.find("{" + namespace + "}type").text)
        # endpoint dir
        endpointDir = str(endpointElement.find("{" + namespace + "}dir").text)
        # endpoint number
        endpointNumber = str(endpointElement.find("{" + namespace + "}number").text)

        # direction
        direction = str(rootElement.find("{" + namespace + "}direction").text)
        # status
        status = str(rootElement.find("{" + namespace + "}status").text)
        # direction
        bufferLength = str(rootElement.find("{" + namespace + "}buffer_length").text)
        # direction
        actualLength = str(rootElement.find("{" + namespace + "}actual_length").text)

        # TODO : verify this ! Circular imports in python !
        # WARNING : verify this ! Circular imports in python !
        from netzob.Common.Models.USBMessage import USBMessage
        message = USBMessage(id, timestamp, data, endpointConfiguration, endpointInterface, endpointType, endpointDir, endpointNumber, direction, status, bufferLength, actualLength)

        return message
