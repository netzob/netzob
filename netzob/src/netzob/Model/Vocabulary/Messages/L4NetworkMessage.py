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

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+
from lxml import etree
from lxml.etree import ElementTree
#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck
from netzob.Model.Vocabulary.Messages.L3NetworkMessage import L3NetworkMessage


class L4NetworkMessage(L3NetworkMessage):
    """Definition of a layer 4 network message

    >>> import binascii
    >>> msg = L4NetworkMessage(b"090002300202f000", date=1352293417.28, l3SourceAddress="192.168.10.100", l3DestinationAddress="192.168.10.245", l4SourceAddress=2049, l4DestinationAddress=80)
    >>> print(msg.source)
    192.168.10.100:2049
    >>> print(msg.destination)
    192.168.10.245:80
    >>> print(msg)
    [0;32m[1352293417.28 [0;m[1;32m192.168.10.100:2049[1;m[0;32m->[0;m[1;32m192.168.10.245:80[1;m[0;32m][0;m '090002300202f000'

    """

    def __init__(self,
                 data,
                 date=None,
                 l2Protocol=None,
                 l2SourceAddress=None,
                 l2DestinationAddress=None,
                 l3Protocol=None,
                 l3SourceAddress=None,
                 l3DestinationAddress=None,
                 l4Protocol=None,
                 l4SourceAddress=None,
                 l4DestinationAddress=None):
        super(L4NetworkMessage, self).__init__(
            data, date, l2Protocol, l2SourceAddress, l2DestinationAddress,
            l3Protocol, l3SourceAddress, l3DestinationAddress)
        self.l4Protocol = str(l4Protocol)
        self.l4SourceAddress = l4SourceAddress
        self.l4DestinationAddress = l4DestinationAddress

    @property
    def l4Protocol(self):
        """The protocol of the fourth layer

        :type: str
        """
        return self.__l4Protocol

    @l4Protocol.setter
    @typeCheck(str)
    def l4Protocol(self, l4Protocol):
        self.__l4Protocol = l4Protocol

    @property
    def l4SourceAddress(self):
        """The source address of the fourth layer

        :type: int
        """
        return self.__l4SourceAddress

    @l4SourceAddress.setter
    @typeCheck(int)
    def l4SourceAddress(self, l4SourceAddress):
        self.__l4SourceAddress = l4SourceAddress

    @property
    def l4DestinationAddress(self):
        """The destination address of the fourth layer

        :type: int
        """
        return self.__l4DestinationAddress

    @l4DestinationAddress.setter
    @typeCheck(int)
    def l4DestinationAddress(self, l4DestinationAddress):
        self.__l4DestinationAddress = l4DestinationAddress

    @property
    def source(self):
        """The name or type of the source which emitted
        the current message

        :type: str
        """
        return "{0}:{1}".format(
            str(self.l3SourceAddress), str(self.l4SourceAddress))

    @property
    def destination(self):
        """The name or type of the destination which received
        the current message

        :type: str
        """
        return "{0}:{1}".format(
            str(self.l3DestinationAddress), str(self.l4DestinationAddress))

    def XMLProperties(currentMessage, xmlL4Message, symbol_namespace, common_namespace):
        if currentMessage.l4Protocol is not None:
            xmlL4Message.set("l4Protocol", str(currentMessage.l4Protocol))
        if currentMessage.l4SourceAddress is not None:
            xmlL4Message.set("l4SourceAddress", str(currentMessage.l4SourceAddress))
        if currentMessage.l4DestinationAddress is not None:
            xmlL4Message.set("l4DestinationAddress", str(currentMessage.l4DestinationAddress))

        # Save the Properties inherited from  L3NetworkMassage
        L3NetworkMessage.XMLProperties(currentMessage, xmlL4Message, symbol_namespace, common_namespace)


    def saveToXML(self, xmlRoot, symbol_namespace, common_namespace):
        xmlL4Message = etree.SubElement(xmlRoot, "{" + symbol_namespace + "}L4NetworkMessage")

        L4NetworkMessage.XMLProperties(self, xmlL4Message, symbol_namespace, common_namespace)

    @staticmethod
    def restoreFromXML(xmlroot, symbol_namespace, common_namespace, attributes):
        if xmlroot.get('l4Protocol') is not None:
            attributes['l4Protocol'] = str(xmlroot.get('l4Protocol'))
        else:
            attributes['l4Protocol'] = None
        if xmlroot.get('l4SourceAddress') is not None:
            attributes['l4SourceAddress'] = int(xmlroot.get('l4SourceAddress'))
        else:
            attributes['l4SourceAddress'] = None
        if xmlroot.get('l4DestinationAddress') is not None:
            attributes['l4DestinationAddress'] = int(xmlroot.get('l4DestinationAddress'))
        else:
            attributes['l4DestinationAddress'] = None

        L3NetworkMessage.restoreFromXML(xmlroot, symbol_namespace, common_namespace, attributes)

        return attributes

    @staticmethod
    def loadFromXML(xmlroot, symbol_namespace, common_namespace):
        a = L4NetworkMessage.restoreFromXML(xmlroot, symbol_namespace, common_namespace, dict())

        l4msg = None
        if 'data' in a.keys():
            l4msg = L4NetworkMessage(data=a['data'], date=a['date'],
                                     l2Protocol=a['l2Protocol'],
                                     l2SourceAddress=a['l2SourceAddress'],
                                     l2DestinationAddress=a['l2DestinationAddress'],
                                     l3Protocol=a['l3Protocol'],
                                     l3SourceAddress=a['l3SourceAddress'],
                                     l3DestinationAddress=a['l3DestinationAddress'],
                                     l4Protocol=a['l4Protocol'],
                                     l4SourceAddress=a['l4SourceAddress'],
                                     l4DestinationAddress=a['l4DestinationAddress'])

            # This might be not correct
            # if 'source' in a.keys():
            #     l4msg.source = a['source']
            # if 'destination' in a.keys():
            #     l4msg.destination = a['destination']

            if 'messageType' in a.keys():
                l4msg.messageType = a['messageType']
            if 'id' in a.keys():
                l4msg.id = a['id']
            if 'metadata' in a.keys():
                l4msg.metadata = a['metadata']
            if 'semanticTags' in a.keys():
                l4msg.description = a['semanticTags']
            if 'visualizationFunctions' in a.keys():
                l4msg.visualizationFunctions = a['visualizationFunctions']
            if 'session' in a.keys():
                from netzob.Export.XMLHandler.XMLHandler import XMLHandler
                unresolved = {a['session']: l4msg}
                XMLHandler.add_to_unresolved_dict('session', unresolved)
        return l4msg
