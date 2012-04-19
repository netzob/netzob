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
#| Related third party imports
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.Models.AbstractMessage import AbstractMessage
from netzob.Common.Models.Factories.NetworkMessageFactory import NetworkMessageFactory
from netzob.Common.Type.Format import Format
from netzob.Common.Type.TypeConvertor import TypeConvertor


#+---------------------------------------------------------------------------+
#| NetworkMessage:
#|     Definition of a network message
#+---------------------------------------------------------------------------+
class NetworkMessage(AbstractMessage):
    def __init__(self, id, timestamp, data, ip_source, ip_destination, protocol, l4_source_port, l4_destination_port, pattern=[]):
        AbstractMessage.__init__(self, id, timestamp, data, "Network", pattern)
        self.ip_source = ip_source
        self.ip_destination = ip_destination
        self.protocol = protocol
        self.l4_source_port = l4_source_port
        self.l4_destination_port = l4_destination_port
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Common.Models.NetworkMessage.py')
        #print "CALL Network "+str(self.getPattern())

        if len(self.pattern) == 1:
            self.pattern.insert(0, ip_destination)

        #print str(self.pattern[0])+" "+str([str(i) for i in self.pattern[1]])+" "+str(TypeConvertor.netzobRawToString(str(self.getData())))

    #+-----------------------------------------------------------------------+
    #| getFactory
    #| @return the associated factory
    #+-----------------------------------------------------------------------+
    def getFactory(self):
        return NetworkMessageFactory

    #+-----------------------------------------------------------------------+
    #| getProperties
    #|     Computes and returns the properties of the current message
    #| @return an array with all the properties [[key,type,val],...]
    #+-----------------------------------------------------------------------+
    def getProperties(self):
        properties = []
        properties.append(['ID', Format.STRING, str(self.getID())])
        properties.append(['Type', Format.STRING, self.getType()])
        properties.append(['Timestamp', Format.DECIMAL, self.getTimestamp()])
        properties.append(['Protocol', Format.STRING, self.getProtocol()])
        properties.append(['IP source', Format.IP, self.getIPSource()])
        properties.append(['IP target', Format.IP, self.getIPDestination()])
        properties.append(['Source port', Format.DECIMAL, self.getL4SourcePort()])
        properties.append(['Target port', Format.DECIMAL, self.getL4DestinationPort()])
        properties.append(['Data', Format.HEX, self.getStringData()])
        properties.append(['Pattern', Format.STRING, self.getPatternString()])

        return properties

    #+----------------------------------------------
    #| GETTERS:
    #+----------------------------------------------
    def getProtocol(self):
        return self.protocol

    def getIPSource(self):
        return self.ip_source

    def getIPDestination(self):
        return self.ip_destination

    def getL4SourcePort(self):
        return self.l4_source_port

    def getL4DestinationPort(self):
        return self.l4_destination_port

    def getTimestamp(self):
        return self.timestamp

    #+----------------------------------------------
    #| SETTERS:
    #+----------------------------------------------
    def setProtocol(self, protocol):
        self.protocol = protocol

    def setIPSource(self, ipSource):
        self.ip_source = ipSource

    def setIPDestination(self, ipDestination):
        self.ip_destination = ipDestination

    def setL4SourcePort(self, l4sourcePort):
        try:
            self.l4_source_port = int(l4sourcePort)
        except:
            self.log.warning("Impossible to set the given L4 source port since its not an int ! " + l4sourcePort)
            self.l4_source_port = -1

    def setL4DestinationPort(self, l4targetPort):
        try:
            self.l4_destination_port = int(l4targetPort)
        except:
            self.log.warning("Impossible to set the given L4 target port since its not an int !")
            self.l4_destination_port = -1

    def setTimestamp(self, timestamp):
        self.timestamp = timestamp
