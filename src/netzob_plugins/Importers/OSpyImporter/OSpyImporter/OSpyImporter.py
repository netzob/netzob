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
import logging
import bz2
import uuid
import time
import dateutil.parser
from lxml import etree
from base64 import b64decode

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Import.AbstractImporter import AbstractImporter
from netzob.Common.Models.L4NetworkMessage import L4NetworkMessage


class OSpyImporter(AbstractImporter):

    def __init__(self, netzob):
        super(OSpyImporter, self).__init__("OSPY IMPORT", netzob)
        self.log = logging.getLogger(__name__)
        self.filesToBeImported = []

    def setSourceFiles(self, filePathList):
        self.filesToBeImported = filePathList

    def readMessages(self):
        self.messages = []
        for filePath in self.filesToBeImported:
            currentFileMessageList = self._parseOSpyXMLFile(filePath)
            self.messages.extend(currentFileMessageList)

    def _parseOSpyXMLFile(self, filePath):
        xmlFileContents = self._readBZ2CompressedFile(filePath)
        self.log.debug("Loading XML structure in memory")
        xmlRoot = etree.fromstring(xmlFileContents)
        if xmlRoot is None:
            self.log.error("Error while loading XML structure in memory")
            return None
        # Parse all found messages in the XML structure
        messageList = []
        functionList = []
        for xmlMessage in xmlRoot.findall("Messages"):
            message = self._parseMessage(xmlMessage)
            if message is not None:  # and (message.getL4Protocol() == "EncryptMessage" or message.getL4Protocol() == "DecryptMessage"):
                messageList.append(message)
                if not message.getL4Protocol() in functionList:
                    functionList.append(message.getL4Protocol())
        return messageList

    def _parseMessage(self, rootElement):
        mUuid = str(uuid.uuid4())
        mTimestamp = None
        mData = None
        localAddress = None
        peerAddress = None
        localPort = 0
        peerPort = 0
        l4Protocol = None

        # Retrieves the timestamp
        if rootElement.find("Timestamp") is not None:
            mTimestamp = rootElement.find("Timestamp").text
            date = dateutil.parser.parse(mTimestamp)
            mTimestamp = int(time.mktime(date.timetuple()))

        # Retrieves the data of the message
        if rootElement.find("Data") is not None:
            mData = rootElement.find("Data").text
            mData = b64decode(mData).encode('hex')

        # Retrieves the local address
        if rootElement.find("LocalAddress") is not None:
            localAddress = rootElement.find("LocalAddress").text

        # Retrieves the peer address
        if rootElement.find("PeerAddress") is not None:
            peerAddress = rootElement.find("PeerAddress").text

        # Retrieves the local port
        if rootElement.find("LocalPort") is not None:
            localPort = rootElement.find("LocalPort").text

        # Retrieves the peer port
        if rootElement.find("PeerPort") is not None:
            peerPort = rootElement.find("PeerPort").text

        if rootElement.find("FunctionName") is not None:
            l4Protocol = rootElement.find("FunctionName").text

        # Set source and destination port and address
        # according to message direction
        l3SourceAddress = localAddress
        l3DestinationAddress = peerAddress
        l4SourcePort = localPort
        l4DestinationPort = peerPort
        if rootElement.find("Direction") is not None:
            msg_direction = rootElement.find("Direction").text
            if msg_direction == 2:
                l3SourceAddress = peerAddress
                l3DestinationAddress = localAddress
                l4SourcePort = peerPort
                l4DestinationPort = localPort

        # Create message
        if mData is not None:
            message = L4NetworkMessage(mUuid, mTimestamp, mData,
                                       None, None, None,
                                       "IP", l3SourceAddress, l3DestinationAddress,
                                       l4Protocol, l4SourcePort, l4DestinationPort)
            return message

    def _readBZ2CompressedFile(self, filePath):
        self.log.debug("Decompressing file: {0}".format(filePath))
        with open(filePath, "rb") as fileObj:
            compressedData = fileObj.read()
            data = bz2.decompress(compressedData)
            return data
