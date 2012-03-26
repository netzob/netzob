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


#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+
from lxml.etree import ElementTree
from netzob.Common.Type.TypeConvertor import TypeConvertor
from lxml import etree
import datetime

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+


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

    @staticmethod
    #+-----------------------------------------------------------------------+
    #| saveInXML
    #|     Generate the XML representation of a file message
    #| @return a string which include the xml definition of the file msg
    #+-----------------------------------------------------------------------+
    def save(message, xmlMessages, namespace_project, namespace_common):
        root = etree.SubElement(xmlMessages, "{" + namespace_common + "}message")
        root.set("id", str(message.getID()))
        root.set("timestamp", str(message.getTimestamp()))
        root.set("{http://www.w3.org/2001/XMLSchema-instance}type", "netzob-common:FileMessage")
        # data
        subData = etree.SubElement(root, "{" + namespace_common + "}data")
        subData.text = str(message.getData())
        # line number
        subLineNumber = etree.SubElement(root, "{" + namespace_common + "}lineNumber")
        subLineNumber.text = str(message.getLineNumber())
        # filename
        subFilename = etree.SubElement(root, "{" + namespace_common + "}filename")
        subFilename.text = message.getFilename()
        # creationDate
        subCreationDate = etree.SubElement(root, "{" + namespace_common + "}creationDate")
        subCreationDate.text = TypeConvertor.pythonDatetime2XSDDatetime(message.getCreationDate())
        # creationDate
        subModificationDate = etree.SubElement(root, "{" + namespace_common + "}modificationDate")
        subModificationDate.text = TypeConvertor.pythonDatetime2XSDDatetime(message.getModificationDate())

        # owner
        subOwner = etree.SubElement(root, "{" + namespace_common + "}owner")
        subOwner.text = message.getOwner()
        # size
        subSize = etree.SubElement(root, "{" + namespace_common + "}size")
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
    def loadFromXML(rootElement, namespace, version):

        # Then we verify its an IPC Message
        if rootElement.get("{http://www.w3.org/2001/XMLSchema-instance}type", "abstract") != "netzob-common:FileMessage":
            raise NameError("The parsed xml doesn't represent a File message.")

        # Verifies the data field
        if rootElement.find("{" + namespace + "}data") == None or not rootElement.find("{" + namespace + "}data").text:
            raise NameError("The parsed message has no data specified")

        # Parse the data field and transform it into a byte array
        msg_data = bytearray(rootElement.find("{" + namespace + "}data").text)

        # Retrieve the id
        msg_id = rootElement.get("id")

        # Retrieve the timestamp
        msg_timestamp = int(rootElement.get("timestamp"))

        # Retrieves the lineNumber (default -1)
        msg_lineNumber = int(rootElement.find("{" + namespace + "}lineNumber").text)

        # Retrieves the filename
        msg_filename = rootElement.find("{" + namespace + "}filename").text

        # Retrieves the creation date
        msg_creationDate = TypeConvertor.xsdDatetime2PythonDatetime(rootElement.find("{" + namespace + "}creationDate").text)

        # Retrieves the modification date
        if rootElement.find("{" + namespace + "}modificationDate").text != None:
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

        result = FileMessage(msg_id, msg_timestamp, msg_data, msg_filename, msg_creationDate, msg_modificationDate, msg_owner, msg_size, msg_lineNumber)

        return result
