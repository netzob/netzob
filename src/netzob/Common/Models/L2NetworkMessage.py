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

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.Type.Format import Format
from netzob.Common.Models.AbstractMessage import AbstractMessage
from netzob.Common.Models.Factories.L2NetworkMessageFactory import L2NetworkMessageFactory
from netzob.Common.Property import Property


class L2NetworkMessage(AbstractMessage):
    """Definition of a layer 2 network message"""

    def __init__(self, id, timestamp, data, l2Protocol, l2SourceAddress,
                 l2DestinationAddress, pattern=[]):
        super(L2NetworkMessage, self).__init__(id, timestamp, data, "L2Network", pattern)
        self.log = logging.getLogger(__name__)
        self.l2Protocol = str(l2Protocol)
        self.l2SourceAddress = str(l2SourceAddress)
        self.l2DestinationAddress = str(l2DestinationAddress)

    def getFactory(self):
        return L2NetworkMessageFactory

    def getL2Protocol(self):
        return self.l2Protocol

    def getL2SourceAddress(self):
        return self.l2SourceAddress

    def getL2DestinationAddress(self):
        return self.l2DestinationAddress

    def getProperties(self):
        properties = []
        properties.append(Property('ID', Format.STRING, str(self.getID())))
        properties.append(Property('Type', Format.STRING, self.getType()))
        properties.append(Property('Timestamp', Format.DECIMAL, self.getTimestamp()))
        properties.append(Property('Layer 2 Protocol', Format.STRING, self.getL2Protocol()))
        properties.append(Property('Layer 2 Source Address', Format.STRING, self.getL2SourceAddress()))
        properties.append(Property('Layer 2 Destination Address', Format.STRING, self.getL2DestinationAddress()))
        properties.append(Property('Data', Format.HEX, self.getStringData()))
        properties.extend(super(L2NetworkMessage, self).getProperties())
        return properties
