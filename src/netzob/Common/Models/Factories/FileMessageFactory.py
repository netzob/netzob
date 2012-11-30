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
import datetime

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.Type.TypeConvertor import TypeConvertor


#+---------------------------------------------------------------------------+
#| FileMessageFactory:
#|     Factory dedicated to the manipulation of file messages
#| ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~+
#| XML Definition
#| <message type="file" id="" timestamp="">
#|     <data></data>
#|     <lineNumber></lineNumber>
#|     <filename></filename>
#|     <creationDate></creationDate>
#|     <modificationDate></modificationDate>
#|     <owner></owner>
#|     <size></size>
#|     <data></data>
#| </message>
#+---------------------------------------------------------------------------+
class FileMessageFactory():

    XML_SCHEMA_TYPE = "netzob-common:FileMessage"

    @staticmethod
    #+-----------------------------------------------------------------------+
    #| saveInXML
    #|     Generate the XML representation of a file message
    #| @return a string which include the xml definition of the file msg
    #+-----------------------------------------------------------------------+
    def save(message, xmlMessage, namespace_project, namespace_common):
        xmlMessage.set("{http://www.w3.org/2001/XMLSchema-instance}type", FileMessageFactory.XML_SCHEMA_TYPE)

        # line number
        subLineNumber = etree.SubElement(xmlMessage, "{" + namespace_common + "}lineNumber")
        subLineNumber.text = str(message.getLineNumber())
        # filename
        subFilename = etree.SubElement(xmlMessage, "{" + namespace_common + "}filename")
        subFilename.text = message.getFilename().decode('utf-8')
        # creationDate
        subCreationDate = etree.SubElement(xmlMessage, "{" + namespace_common + "}creationDate")
        subCreationDate.text = TypeConvertor.pythonDatetime2XSDDatetime(message.getCreationDate())
        # creationDate
        subModificationDate = etree.SubElement(xmlMessage, "{" + namespace_common + "}modificationDate")
        subModificationDate.text = TypeConvertor.pythonDatetime2XSDDatetime(message.getModificationDate())

        # owner
        subOwner = etree.SubElement(xmlMessage, "{" + namespace_common + "}owner")
        subOwner.text = message.getOwner()
        # size
        subSize = etree.SubElement(xmlMessage, "{" + namespace_common + "}size")
        subSize.text = str(message.getSize())

    @staticmethod
    #+---------------------------------------------------------------------------+
    #| loadFromXML:
    #|     Function which parses an XML and extract from it
    #[    the definition of a file message
    #| @param rootElement: XML root of the file message
    #| @return an instance of a FipSource (default 0.0.0.0)ileMessage
    #| @throw NameError if XML invalid
    #+---------------------------------------------------------------------------+
    def loadFromXML(rootElement, namespace, version, id, timestamp, data):

        # Retrieves the lineNumber (default -1)
        msg_lineNumber = int(rootElement.find("{" + namespace + "}lineNumber").text)

        # Retrieves the filename
        msg_filename = rootElement.find("{" + namespace + "}filename").text

        # Retrieves the creation date
        msg_creationDate = TypeConvertor.xsdDatetime2PythonDatetime(rootElement.find("{" + namespace + "}creationDate").text)

        # Retrieves the modification date
        if rootElement.find("{" + namespace + "}modificationDate").text is not None:
            msg_modificationDate = TypeConvertor.xsdDatetime2PythonDatetime(rootElement.find("{" + namespace + "}modificationDate").text)
        else:
            msg_modificationDate = msg_creationDate

        # Retrieves the owner
        msg_owner = rootElement.find("{" + namespace + "}owner").text

        # Retrieves the size
        msg_size = int(rootElement.find("{" + namespace + "}size").text)

        # TODO : verify this ! Circular imports in python !
        # WARNING : verify this ! Circular imports in python !
        from netzob.Common.Models.FileMessage import FileMessage
        result = FileMessage(id, timestamp, data, msg_filename, msg_creationDate, msg_modificationDate, msg_owner, msg_size, msg_lineNumber)

        return result
