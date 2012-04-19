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
from netzob.Common.Token import Token
from lxml import etree

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+


#+---------------------------------------------------------------------------+
#| IRPDeviceIoControlMessageFactory:
#|     Factory dedicated to the manipulation of IRP IOCTL messages
#| ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~+
#+---------------------------------------------------------------------------+
class IRPDeviceIoControlMessageFactory():

    @staticmethod
    #+-----------------------------------------------------------------------+
    #| save
    #|     Generate the XML representation of a IRP IOCTL message
    #+-----------------------------------------------------------------------+
    def save(message, xmlMessages, namespace_project, namespace):
        root = etree.SubElement(xmlMessages, "{" + namespace + "}message")
        root.set("id", str(message.getID()))
        root.set("timestamp", str(message.getTimestamp()))
        root.set("{http://www.w3.org/2001/XMLSchema-instance}type", "netzob-common:IRPDeviceIoControlMessage")
        # data
        subData = etree.SubElement(root, "{" + namespace + "}data")
        subData.text = str(message.getData())
        # direction
        subDirection = etree.SubElement(root, "{" + namespace + "}direction")
        subDirection.text = message.getDirection()
        # major
        subMajor = etree.SubElement(root, "{" + namespace + "}major")
        subMajor.text = message.getMajor()
        # minor
        subMinor = etree.SubElement(root, "{" + namespace + "}minor")
        subMinor.text = str(message.getMinor())
        # requestMode
        subRequestMode = etree.SubElement(root, "{" + namespace + "}requestMode")
        subRequestMode.text = message.getRequestMode()
        # pid
        subPid = etree.SubElement(root, "{" + namespace + "}pid")
        subPid.text = str(message.getPID())
        # status
        subStatus = etree.SubElement(root, "{" + namespace + "}status")
        subStatus.text = str(message.getStatus())
        # information
        subInformation = etree.SubElement(root, "{" + namespace + "}information")
        subInformation.text = str(message.getInformation())
        # cancel
        subCancel = etree.SubElement(root, "{" + namespace + "}cancel")
        subCancel.text = TypeConvertor.bool2str(message.getCancel())
        # sizeIn
        subSizeIn = etree.SubElement(root, "{" + namespace + "}sizeIn")
        subSizeIn.text = str(message.getSizeIn())
        # sizeOut
        subSizeOut = etree.SubElement(root, "{" + namespace + "}sizeOut")
        subSizeOut.text = str(message.getSizeOut())
        # ioctl
        subIoctl = etree.SubElement(root, "{" + namespace + "}ioctl")
        subIoctl.text = str(message.getIOCTL())

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
    #+---------------------------------------------------------------------------+
    #| loadFromXML:
    #|     Function which parses an XML and extract from it
    #[    the definition of a IRP message
    #| @param rootElement: XML root of the IRP IOCTL message
    #| @return an instance of a IRPDeviceIoControlMessage
    #| @throw NameError if XML invalid
    #+---------------------------------------------------------------------------+
    def loadFromXML(rootElement, namespace, version):

        # Then we verify its an IPC Message
        if rootElement.get("{http://www.w3.org/2001/XMLSchema-instance}type", "abstract") != "netzob-common:IRPDeviceIoControlMessage":
            raise NameError("The parsed xml doesn't represent a IRP IOCTL message.")

        # Verifies the data field
        if rootElement.find("{" + namespace + "}data") == None or rootElement.find("{" + namespace + "}data").text == None or not rootElement.find("{" + namespace + "}data").text:
            raise NameError("The parsed message has no data specified")

        # Parse the data field and transform it into a byte array
        msg_data = bytearray(rootElement.find("{" + namespace + "}data").text)

        # Retrieve the id
        msg_id = rootElement.get("id")

        # Retrieve the timestamp
        msg_timestamp = int(rootElement.get("timestamp"))

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

        # Retrieves the ioctl
        msg_ioctl = int(rootElement.find("{" + namespace + "}ioctl").text)

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

        #print "FACTORY "+rootElement.find("{" + namespace + "}pattern").text+" give "+str(pattern[0])+";"+str([str(i) for i in pattern[1]])
        # TODO : verify this ! Circular imports in python !
        # WARNING : verify this ! Circular imports in python !
        from netzob.Common.Models.IRPDeviceIoControlMessage import IRPDeviceIoControlMessage

        result = IRPDeviceIoControlMessage(msg_id, msg_timestamp, msg_data, msg_direction, msg_major, msg_minor, msg_requestMode, msg_pid, msg_status, msg_information, msg_cancel, msg_sizeIn, msg_sizeOut, msg_ioctl, pattern)

        return result
