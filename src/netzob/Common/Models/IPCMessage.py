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
from netzob.Common.Models.Factories.IPCMessageFactory import IPCMessageFactory
from netzob.Common.Type.Format import Format
from netzob.Common.Property import Property


#+---------------------------------------------------------------------------+
#| IPCMessage:
#|     Definition of an IPC message
#+---------------------------------------------------------------------------+
class IPCMessage(AbstractMessage):
    def __init__(self, id, timestamp, data, category, key, direction):
        AbstractMessage.__init__(self, id, timestamp, data, "IPC")

        self.category = category
        self.key = key
        self.direction = direction

        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Common.Models.IPCMessage.py')

    #+-----------------------------------------------------------------------+
    #| getFactory
    #| @return the associated factory
    #+-----------------------------------------------------------------------+
    def getFactory(self):
        return IPCMessageFactory

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
        properties.append(Property('Category', Format.STRING, self.getCategory()))
        properties.append(Property('Key', Format.STRING, self.getKey()))
        properties.append(Property('Direction', Format.STRING, self.getDirection()))
        properties.append(Property('Data', Format.STRING, self.getStringData()))
        properties.extend(super(IPCMessage, self).getProperties())
        return properties

    #+----------------------------------------------
    #| GETTERS:
    #+----------------------------------------------
    def getCategory(self):
        return self.category

    def getKey(self):
        return self.key

    def getType(self):
        return self.type

    def getDirection(self):
        return self.direction

    #+----------------------------------------------
    #| SETTERS:
    #+----------------------------------------------
    def setCategory(self, category):
        self.category = category

    def setKey(self, key):
        self.key = key

    def setType(self, type):
        self.type = type

    def setDirection(self, direction):
        self.direction = direction
