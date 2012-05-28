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
#| Global Imports
#+---------------------------------------------------------------------------+
import logging
import bz2
import uuid
from lxml.etree import ElementTree
from lxml import etree
from base64 import *
import dateutil.parser
import time

#+---------------------------------------------------------------------------+
#| Local Imports
#+---------------------------------------------------------------------------+
from netzob.Import.ThirdParties.AbstractThirdPartyImporter import AbstractThirdPartyImporter
from netzob.Common.Models.NetworkMessage import NetworkMessage
from netzob.Common.Type.TypeConvertor import TypeConvertor


#+---------------------------------------------------------------------------+
#| AbstractThirdPartyImporter:
#|     Abstract class for third parties
#+---------------------------------------------------------------------------+
class OSpy(AbstractThirdPartyImporter):

    def __init__(self):
        AbstractThirdPartyImporter.__init__(self, "netzob.Import.ThirdParties.OSpy", "OSpy")

    def parse(self, paths):
        result = []
        for path in paths:
            pathResult = self.parsePath(path)
            if pathResult != None:
                result.extend(pathResult)
        return result

    def parsePath(self, path):
        logging.debug("Parse file from {0}".format(path))

        # Uncompress the file
        xmlData = self.uncompressFile(path)
        if xmlData == None or len(xmlData) == 0:
            logging.warning("No data have been extracted from the provided file.")
            return None

        # Parse the XML file
        messages = self.extractMessagesFromXML(xmlData)

        return messages

    def extractMessagesFromXML(self, xmlData):
        messages = []

        logging.debug("Load the XML structure in memory")
        xmlRoot = etree.fromstring(xmlData)

        if xmlRoot == None:
            logging.warning("Error while loading the XML.")
            return None
        listOfFunctions = []
        for xmlMessage in xmlRoot.findall("Messages"):
            message = self.extractMessageFromXML(xmlMessage)
            if message != None:
                if message.getProtocol() == "EncryptMessage" or message.getProtocol() == "DecryptMessage":
                    messages.append(message)
                if not message.getProtocol() in listOfFunctions:
                    listOfFunctions.append(message.getProtocol())

        return messages

    def extractMessageFromXML(self, rootElement):
        if rootElement == None:
            return None
#        <Messages>
#            <Index>647</Index>
#            <Timestamp>2012-05-22T08:58:42.0708262+02:00</Timestamp>
#            <ProcessName>EuroFortune.exe</ProcessName>
#            <ProcessId>1004</ProcessId>
#            <ThreadId>3448</ThreadId>
#            <FunctionName>SecureReceive</FunctionName>
#            <Backtrace>wininet.dll::0x71236f77
#        wininet.dll::0x712185c7
#        wininet.dll::0x71224dfb
#        RASAPI32.dll::0x6dfc280b
#        ntdll.dll::0x77eeb338
#        ntdll.dll::0x77eeb309
#        ntdll.dll::0x77f1b26c</Backtrace>
#            <ReturnAddress>1898147703</ReturnAddress>
#            <CallerModuleName>wininet.dll</CallerModuleName>
#            <ResourceId>11581</ResourceId>
#            <MsgType>1</MsgType>
#            <Direction>1</Direction>
#            <LocalAddress>10.0.2.15</LocalAddress>
#            <LocalPort>49843</LocalPort>
#            <PeerAddress>200.124.131.116</PeerAddress>
#            <PeerPort>443</PeerPort>
#            <Data>SFRUUC8xLjEgMjAwIE9LDQpEYXRlOiBUdWUsIDIyIE1heSAyMDEyIDA2OjU4OjExIEdNVA0KU2VydmVyOiBBcGFjaGUNCkNvbnRlbnQtRW5jb2Rpbmc6IGd6aXANClZhcnk6IEFjY2VwdC1FbmNvZGluZw0KQ29udGVudC1MZW5ndGg6IDUwDQpLZWVwLUFsaXZlOiB0aW1lb3V0PTE1LCBtYXg9OTkxDQpDb25uZWN0aW9uOiBLZWVwLUFsaXZlDQpDb250ZW50LVR5cGU6IHRleHQvaHRtbA0KDQofiwgAAAAAAAADqlYqLkksSVWyMtBRSixLzMxJTMoB8gxrAQAAAP//AwAQWBTTGQAAAA==</Data>
#          </Messages>
        id = uuid.uuid4()

        msg_timestamp = None
        msg_data = None
        msg_ipLocal = None
        msg_ipPeer = None
        msg_portLocal = 0
        msg_portPeer = 0
        msg_protocol = None
        data = None

        # Retrieves the timestamp
        if rootElement.find("Timestamp") != None:
            msg_timestamp = rootElement.find("Timestamp").text
            date = dateutil.parser.parse(msg_timestamp)
            timestamp = int(time.mktime(date.timetuple()))

        # Retrieves the data of the message
        if rootElement.find("Data") != None:
            msg_data = rootElement.find("Data").text
            data = b64decode(msg_data).encode('hex')

        # Retrieves the local address
        if rootElement.find("LocalAddress") != None:
            msg_ipLocal = rootElement.find("LocalAddress").text

        # Retrieves the peer address
        if rootElement.find("PeerAddress") != None:
            msg_ipPeer = rootElement.find("PeerAddress").text

        # Retrieves the local port
        if rootElement.find("LocalPort") != None:
            msg_portLocal = rootElement.find("LocalPort").text

        # Retrieves the peer port
        if rootElement.find("PeerPort") != None:
            msg_portPeer = rootElement.find("PeerPort").text

        if rootElement.find("FunctionName") != None:
            msg_protocol = rootElement.find("FunctionName").text

        ip_destination = msg_ipPeer
        l4_destination_port = msg_portPeer
        ip_source = msg_ipLocal
        l4_source_port = msg_portLocal

        if rootElement.find("Direction") != None:
            msg_direction = rootElement.find("Direction").text
            if msg_direction == 2:
                ip_source = msg_ipPeer
                l4_source_port = msg_portPeer
                ip_destination = msg_ipLocal
                l4_destination_port = msg_portLocal

        if data != None:
            message = NetworkMessage(id, timestamp, data, ip_source, ip_destination, msg_protocol, l4_source_port, l4_destination_port)
            return message

    def uncompressFile(self, path):
        logging.debug("Uncompress the provided File.")
        file = open(path, "rb")
        compresseddata = file.read()
        file.close()

        # FUncompress the content of file
        data = bz2.decompress(compresseddata)

        return data
