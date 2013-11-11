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
import time
import binascii

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck
from netzob.Common.Models.Vocabulary.Messages.RawMessage import RawMessage


class L2NetworkMessage(RawMessage):
    """Definition of a layer 2 network message.

    >>> msg = L2NetworkMessage("090002300202f000")
    >>> print msg.data
    090002300202f000

    >>> msg = L2NetworkMessage("090002300202f000", date=1352293417.28, l2SourceAddress="00:02:7b:00:bf:33", l2DestinationAddress="00:02:3f:a8:bf:21")
    >>> print msg.source
    00:02:7b:00:bf:33
    >>> print msg.destination
    00:02:3f:a8:bf:21
    >>> print msg
    [1352293417.28 00:02:7b:00:bf:33->00:02:3f:a8:bf:21] 090002300202f000

    """

    def __init__(self, data, date=None, l2Protocol=None, l2SourceAddress=None,
                 l2DestinationAddress=None):
        super(L2NetworkMessage, self).__init__(data, date, l2SourceAddress, l2DestinationAddress)
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

    @property
    def source(self):
        """The name or type of the source which emitted
        the current message

        :type: str
        """
        return self.__l2SourceAddress

    @property
    def destination(self):
        """The name or type of the destination which received
        the current message

        :type: str
        """
        return self.__l2DestinationAddress

    def __str__(self):
        HLS = "\033[1;32m"
        HLE = "\033[1;m"
        data = super(L2NetworkMessage, self).__str__()
        return HLS + "[{0} {1}->{2}]".format(self.date, self.source, self.destination) + HLE + " {0}".format(str(binascii.b2a_hex(self.data)))
