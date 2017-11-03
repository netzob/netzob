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
from netzob.Model.Vocabulary.Messages.L2NetworkMessage import L2NetworkMessage


class L3NetworkMessage(L2NetworkMessage):
    """Definition of a layer 3 network message.

    >>> msg = L3NetworkMessage(b"090002300202f000")
    >>> print(msg.data)
    b'090002300202f000'

    >>> msg = L3NetworkMessage(b"090002300202f000", date=1352293417.28, l3SourceAddress="192.168.10.100", l3DestinationAddress="192.168.10.245")
    >>> print(msg.source)
    192.168.10.100
    >>> print(msg.destination)
    192.168.10.245
    >>> print(msg)
    [0;32m[1352293417.28 [0;m[1;32m192.168.10.100[1;m[0;32m->[0;m[1;32m192.168.10.245[1;m[0;32m][0;m '090002300202f000'

    """

    def __init__(self,
                 data,
                 date=None,
                 l2Protocol=None,
                 l2SourceAddress=None,
                 l2DestinationAddress=None,
                 l3Protocol=None,
                 l3SourceAddress=None,
                 l3DestinationAddress=None):
        super(L3NetworkMessage, self).__init__(
            data, date, l2Protocol, l2SourceAddress, l2DestinationAddress)
        self.l3Protocol = str(l3Protocol)
        self.l3SourceAddress = str(l3SourceAddress)
        self.l3DestinationAddress = str(l3DestinationAddress)

    @property
    def l3Protocol(self):
        """The protocol of the third layer

        :type: str
        """
        return self.__l3Protocol

    @l3Protocol.setter
    @typeCheck(str)
    def l3Protocol(self, l3Protocol):
        self.__l3Protocol = l3Protocol

    @property
    def l3SourceAddress(self):
        """The source address of the third layer

        :type: str
        """
        return self.__l3SourceAddress

    @l3SourceAddress.setter
    @typeCheck(str)
    def l3SourceAddress(self, l3SourceAddress):
        self.__l3SourceAddress = l3SourceAddress

    @property
    def l3DestinationAddress(self):
        """The destination address of the second layer

        :type: str
        """
        return self.__l3DestinationAddress

    @l3DestinationAddress.setter
    @typeCheck(str)
    def l3DestinationAddress(self, l3DestinationAddress):
        self.__l3DestinationAddress = l3DestinationAddress

    @property
    def source(self):
        """The name or type of the source which emitted
        the current message

        :type: str
        """
        return self.__l3SourceAddress

    @property
    def destination(self):
        """The name or type of the destination which received
        the current message

        :type: str
        """
        return self.__l3DestinationAddress

    def XMLProperties(currentMessage, xmlL3Message, symbol_namespace, common_namespace):
        if currentMessage.l3Protocol is not None:
            xmlL3Message.set("l3Protocol", str(currentMessage.l3Protocol))
        if currentMessage.l3SourceAddress is not None:
            xmlL3Message.set("l3SourceAddress", str(currentMessage.l3SourceAddress))
        if currentMessage.l3DestinationAddress is not None:
            xmlL3Message.set("l3DestinationAddress", str(currentMessage.l3DestinationAddress))

        # Save the Properties inherited from  L2NetworkMessage
        L2NetworkMessage.XMLProperties(currentMessage, xmlL3Message, symbol_namespace, common_namespace)

    def saveToXML(self, xmlRoot, symbol_namespace, common_namespace):
        xmlL3Message = etree.SubElement(xmlRoot, "{" + symbol_namespace + "}L3NetworkMessage")

        L3NetworkMessage.XMLProperties(self, xmlL3Message, symbol_namespace, common_namespace)

    @staticmethod
    def restoreFromXML(xmlroot, symbol_namespace, common_namespace, attributes):
        if xmlroot.get('l3Protocol') is not None:
            attributes['l3Protocol'] = str(xmlroot.get('l3Protocol'))
        else:
            attributes['l3Protocol'] = None
        if xmlroot.get('l3SourceAddress') is not None:
            attributes['l3SourceAddress'] = str(xmlroot.get('l3SourceAddress'))
        else:
            attributes['l3SourceAddress'] = None
        if xmlroot.get('l3DestinationAddress') is not None:
            attributes['l3DestinationAddress'] = str(xmlroot.get('l3DestinationAddress'))
        else:
            attributes['l3DestinationAddress'] = None

        L2NetworkMessage.restoreFromXML(xmlroot, symbol_namespace, common_namespace, attributes)

        return attributes

    @staticmethod
    def loadFromXML(xmlroot, symbol_namespace, common_namespace):
        a = L3NetworkMessage.restoreFromXML(xmlroot, symbol_namespace, common_namespace, dict())

        l3msg = None
        if 'data' in a.keys():
            l3msg = L3NetworkMessage(data=a['data'], date=a['date'],
                                     l2Protocol=a['l2Protocol'],
                                     l2SourceAddress=a['l2SourceAddress'],
                                     l2DestinationAddress=a['l2DestinationAddress'],
                                     l3Protocol=a['l3Protocol'],
                                     l3SourceAddress=a['l3SourceAddress'],
                                     l3DestinationAddress=a['l3DestinationAddress'])

            # This might be not correct
            # if 'source' in a.keys():
            #     l3msg.source = a['source']
            # if 'destination' in a.keys():
            #     l3msg.destination = a['destination']

            if 'messageType' in a.keys():
                l3msg.messageType = a['messageType']
            if 'id' in a.keys():
                l3msg.id = a['id']
            if 'metadata' in a.keys():
                l3msg.metadata = a['metadata']
            if 'semanticTags' in a.keys():
                l3msg.description = a['semanticTags']
            if 'visualizationFunctions' in a.keys():
                l3msg.visualizationFunctions = a['visualizationFunctions']
            if 'session' in a.keys():
                from netzob.Export.XMLHandler.XMLHandler import XMLHandler
                unresolved = {a['session']: l3msg}
                XMLHandler.add_to_unresolved_dict('session', unresolved)
        return l3msg
