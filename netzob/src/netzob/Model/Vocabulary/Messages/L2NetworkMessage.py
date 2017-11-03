# -*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|          01001110 01100101 01110100 01111010 01101111 01100010            |
#|                                                                           |
#|               Netzob : Inferring communication protocols                  |
#+---------------------------------------------------------------------------+
#| Copyright (C) 2011-2017 Georges Bossert and Frédéric Guihéry              |
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
#|             ANSSI,   https://www.ssi.gouv.fr                              |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Standard library imports
#+---------------------------------------------------------------------------+
import binascii
from lxml import etree
from lxml.etree import ElementTree
#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck
from netzob.Model.Vocabulary.Messages.RawMessage import RawMessage

class L2NetworkMessage(RawMessage):
    """Definition of a layer 2 network message.

    >>> msg = L2NetworkMessage(b"090002300202f000")
    >>> print(msg.data)
    b'090002300202f000'

    >>> msg = L2NetworkMessage(b"090002300202f000", date=1352293417.28, l2SourceAddress="00:02:7b:00:bf:33", l2DestinationAddress="00:02:3f:a8:bf:21")
    >>> print(msg.source)
    00:02:7b:00:bf:33
    >>> print(msg.destination)
    00:02:3f:a8:bf:21
    >>> print(msg)
    \033[0;32m[1352293417.28 \033[0;m\033[1;32m00:02:7b:00:bf:33\033[1;m\033[0;32m->\033[0;m\033[1;32m00:02:3f:a8:bf:21\033[1;m\033[0;32m]\033[0;m '090002300202f000'

    """

    def __init__(self,
                 data,
                 date=None,
                 l2Protocol=None,
                 l2SourceAddress=None,
                 l2DestinationAddress=None):
        super(L2NetworkMessage, self).__init__(
            data,
            date=date,
            source=l2SourceAddress,
            destination=l2DestinationAddress,
            messageType="Network")
        self.l2Protocol = str(l2Protocol)
        self.l2SourceAddress = str(l2SourceAddress)
        self.l2DestinationAddress = str(l2DestinationAddress)

    @property
    def l2Protocol(self):
        """The protocol of the second layer

        :type: str
        """
        return self.__l2Protocol

    @l2Protocol.setter
    @typeCheck(str)
    def l2Protocol(self, l2Protocol):
        self.__l2Protocol = l2Protocol

    @property
    def l2SourceAddress(self):
        """The source address of the second layer

        :type: str
        """
        return self.__l2SourceAddress

    @l2SourceAddress.setter
    @typeCheck(str)
    def l2SourceAddress(self, l2SourceAddress):
        self.__l2SourceAddress = l2SourceAddress

    @property
    def l2DestinationAddress(self):
        """The destination address of the second layer

        :type: str
        """
        return self.__l2DestinationAddress

    @l2DestinationAddress.setter
    @typeCheck(str)
    def l2DestinationAddress(self, l2DestinationAddress):
        self.__l2DestinationAddress = l2DestinationAddress

    def XMLProperties(currentMessage, xmlL2Message, symbol_namespace, common_namespace):
        if currentMessage.l2Protocol is not None:
            xmlL2Message.set("l2Protocol", str(currentMessage.l2Protocol))
        if currentMessage.l2SourceAddress is not None:
            xmlL2Message.set("l2SourceAddress", str(currentMessage.l2SourceAddress))
        if currentMessage.l2DestinationAddress is not None:
            xmlL2Message.set("l2DestinationAddress", str(currentMessage.l2DestinationAddress))

        # Save the Properties inherited from  RawMessage
        RawMessage.XMLProperties(currentMessage, xmlL2Message, symbol_namespace, common_namespace)

    def saveToXML(self, xmlRoot, symbol_namespace, common_namespace):
        xmlL2Message = etree.SubElement(xmlRoot, "{" + symbol_namespace + "}L2NetworkMessage")

        L2NetworkMessage.XMLProperties(self, xmlL2Message, symbol_namespace, common_namespace)

    @staticmethod
    def restoreFromXML(xmlroot, symbol_namespace, common_namespace, attributes):
        if xmlroot.get('l2Protocol') is not None:
            attributes['l2Protocol'] = str(xmlroot.get('l2Protocol'))
        else:
            attributes['l2Protocol'] = None

        if xmlroot.get('l2SourceAddress') is not None:
            attributes['l2SourceAddress'] = str(xmlroot.get('l2SourceAddress'))
        else:
            attributes['l2SourceAddress'] = None

        if xmlroot.get('l2DestinationAddress') is not None:
            attributes['l2DestinationAddress'] = str(xmlroot.get('l2DestinationAddress'))
        else:
            attributes['l2DestinationAddress'] = None

        RawMessage.restoreFromXML(xmlroot, symbol_namespace, common_namespace, attributes)

        return attributes

    @staticmethod
    def loadFromXML(xmlroot, symbol_namespace, common_namespace):
        a = L2NetworkMessage.restoreFromXML(xmlroot, symbol_namespace, common_namespace, dict())

        l2msg = None
        if 'data' in a.keys():
            l2msg = L2NetworkMessage(data=a['data'], date=a['date'], l2Protocol=a['l2Protocol'],
                                     l2SourceAddress=a['l2SourceAddress'], l2DestinationAddress=a['l2DestinationAddress'])

            if 'source' in a.keys():
                l2msg.source = a['source']
            if 'destination' in a.keys():
                l2msg.destination = a['destination']
            if 'messageType' in a.keys():
                l2msg.messageType = a['messageType']
            if 'id' in a.keys():
                l2msg.id = a['id']
            if 'metadata' in a.keys():
                l2msg.metadata = a['metadata']
            if 'semanticTags' in a.keys():
                l2msg.description = a['semanticTags']
            if 'visualizationFunctions' in a.keys():
                l2msg.visualizationFunctions = a['visualizationFunctions']
            if 'session' in a.keys():
                from netzob.Export.XMLHandler.XMLHandler import XMLHandler
                unresolved = {a['session']: l2msg}
                XMLHandler.add_to_unresolved_dict('session', unresolved)
        return l2msg
