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
from gettext import gettext as _
import logging

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.Models.L3NetworkMessage import L3NetworkMessage
from netzob.Common.Models.Factories.L4NetworkMessageFactory import L4NetworkMessageFactory
from netzob.Common.Type.Format import Format
from netzob.Common.Type.TypeConvertor import TypeConvertor
from netzob.Common.Property import Property


class L4NetworkMessage(L3NetworkMessage):
    """Definition of a layer 4 network message"""

    def __init__(self, id, timestamp, data, l2Protocol, l2SourceAddress,
                 l2DestinationAddress, l3Protocol, l3SourceAddress,
                 l3DestinationAddress, l4Protocol, l4SourcePort, l4DestinationPort,
                 pattern=[]):
        super(L4NetworkMessage, self).__init__(id, timestamp, data, l2Protocol,
                                               l2SourceAddress, l2DestinationAddress, l3Protocol, l3SourceAddress,
                                               l3DestinationAddress, pattern=[])
        self.type = "L4Network"
        self.l4Protocol = str(l4Protocol)
        self.l4SourcePort = l4SourcePort
        self.l4DestinationPort = l4DestinationPort
        self.log = logging.getLogger('netzob.Common.Models.NetworkMessage.py')

    def getFactory(self):
        """@return the associated factory"""
        return L4NetworkMessageFactory

    def getProperties(self):
        """Computes and returns the properties of the current message
           @return an array with all the properties [[key,type,val],...]"""
        properties = super(L4NetworkMessage, self).getProperties()
        properties.append(Property('Layer 4 Protocol', Format.STRING, self.getL4Protocol()))
        properties.append(Property('Source port', Format.DECIMAL, self.getL4SourcePort()))
        properties.append(Property('Target port', Format.DECIMAL, self.getL4DestinationPort()))
        return properties

    def getL4Protocol(self):
        return self.l4Protocol

    def getL4SourcePort(self):
        return self.l4SourcePort

    def getL4DestinationPort(self):
        return self.l4DestinationPort
