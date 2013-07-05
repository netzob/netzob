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
from netzob.Common.Models.AbstractMessage import AbstractMessage
from netzob.Common.Models.Factories.USBMessageFactory import USBMessageFactory
from netzob.Common.Type.Format import Format
from netzob.Common.Property import Property


#+---------------------------------------------------------------------------+
#| USBMessage:
#|     Definition of a USB message
#+---------------------------------------------------------------------------+
class USBMessage(AbstractMessage):
    def __init__(self, id, timestamp, data, endpointConfiguration, endpointInterface, endpointType, endpointDir, endpointNumber, direction, status, bufferLength, actualLength):
        AbstractMessage.__init__(self, id, timestamp, data, "USB")
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Common.Models.USBMessage.py')
        self.endpointConfiguration = endpointConfiguration
        self.endpointInterface = endpointInterface
        self.endpointType = endpointType
        self.endpointDir = endpointDir
        self.endpointNumber = endpointNumber
        self.direction = direction
        self.status = status
        self.bufferLength = bufferLength
        self.actualLength = actualLength

    #+-----------------------------------------------------------------------+
    #| getFactory
    #| @return the associated factory
    #+-----------------------------------------------------------------------+
    def getFactory(self):
        return USBMessageFactory

    #+-----------------------------------------------------------------------+
    #| getProperties
    #|     Computes and returns the properties of the current message
    #| @return an array with all the properties [[key,val],...]
    #+-----------------------------------------------------------------------+
    def getProperties(self):
        properties = []
        properties.append(Property('ID', Format.STRING, str(self.getID())))
        properties.append(Property('Type', Format.STRING, self.getType()))
        properties.append(Property('Timestamp', Format.DECIMAL, self.getTimestamp()))
        properties.append(Property('EndpointConfiguration', Format.STRING, self.getEndpointConfiguration()))
        properties.append(Property('EndpointInterface', Format.STRING, self.getEndpointInterface()))
        properties.append(Property('EndpointType', Format.STRING, self.getEndpointType()))
        properties.append(Property('EndpointDir', Format.STRING, self.getEndpointDir()))
        properties.append(Property('EndpointNumber', Format.STRING, self.getEndpointNumber()))
        properties.append(Property('Direction', Format.STRING, self.getDirection()))
        properties.append(Property('Status', Format.STRING, self.getStatus()))
        properties.append(Property('BufferLength', Format.STRING, self.getBufferLength()))
        properties.append(Property('ActualLength', Format.STRING, self.getActualLength()))
        properties.extend(super(USBMessage, self).getProperties())
        return properties

    def getSource(self):
        return "-"

    def getDestination(self):
        return "-"

    def getEndpointConfiguration(self):
        return self.endpointConfiguration

    def getEndpointInterface(self):
        return self.endpointInterface

    def getEndpointType(self):
        return self.endpointType

    def getEndpointDir(self):
        return self.endpointDir

    def getEndpointNumber(self):
        return self.endpointNumber

    def getDirection(self):
        return self.direction

    def getStatus(self):
        return self.status

    def getBufferLength(self):
        return self.bufferLength

    def getActualLength(self):
        return self.actualLength
