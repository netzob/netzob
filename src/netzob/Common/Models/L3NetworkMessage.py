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
from netzob.Common.Models.L2NetworkMessage import L2NetworkMessage
from netzob.Common.Models.Factories.L3NetworkMessageFactory import L3NetworkMessageFactory
from netzob.Common.Property import Property


## Remarques :
# - Peut-être moins clair de parler de Layer 3 source Adress que IP Adress...
class L3NetworkMessage(L2NetworkMessage):
    """Definition of a layer 3 network message"""

    def __init__(self, id, timestamp, data, l2Protocol, l2SourceAddress,
                 l2DestinationAddress, l3Protocol, l3SourceAddress,
                 l3DestinationAddress, pattern=[]):
        if len(pattern) == 1:
            pattern.insert(0, str(l3DestinationAddress))
        super(L3NetworkMessage, self).__init__(id, timestamp, data, l2Protocol,
                                               l2SourceAddress, l2DestinationAddress, pattern=[])
        self.type = "L3Network"
        self.l3Protocol = str(l3Protocol)
        self.l3SourceAddress = str(l3SourceAddress)
        self.l3DestinationAddress = str(l3DestinationAddress)

    def getFactory(self):
        return L3NetworkMessageFactory

    def getL3Protocol(self):
        return self.l3Protocol

    def getL3SourceAddress(self):
        return self.l3SourceAddress

    def getL3DestinationAddress(self):
        return self.l3DestinationAddress

    def getProperties(self):
        properties = super(L3NetworkMessage, self).getProperties()
        properties.append(Property('Layer 3 Protocol', Format.STRING, self.getL3Protocol()))
        properties.append(Property('Layer 3 Source Address', Format.IP, self.getL3SourceAddress()))
        properties.append(Property('Layer 3 Destination Address', Format.IP, self.getL3DestinationAddress()))
        return properties
