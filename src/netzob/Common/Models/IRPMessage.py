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
from netzob.Common.Models.Factories.IRPMessageFactory import IRPMessageFactory
from netzob.Common.Type.Format import Format
from netzob.Common.Type.TypeConvertor import TypeConvertor


#+---------------------------------------------------------------------------+
#| IRPMessage:
#|     Definition of a Windows IRP message
#+---------------------------------------------------------------------------+
class IRPMessage(AbstractMessage):
    def __init__(self, id, timestamp, data, type, direction, major, minor, requestmode, pid, status, information, cancel, sizeIn, sizeOut, pattern=[]):
        AbstractMessage.__init__(self, id, timestamp, data, type, pattern)
        self.direction = direction
        self.major = major
        self.minor = minor
        self.requestmode = requestmode
        self.pid = pid
        self.status = status
        self.information = information
        self.cancel = cancel
        self.sizeIn = sizeIn
        self.sizeOut = sizeOut

        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Common.Models.IRPMessage.py')
        #print "CALL Network "+str(self.getPattern())

        if len(self.pattern) == 1:
            self.pattern.insert(0, direction)

        #print str(self.pattern[0])+" "+str([str(i) for i in self.pattern[1]])+" "+str(TypeConvertor.netzobRawToString(str(self.getData())))

    #+-----------------------------------------------------------------------+
    #| getFactory
    #| @return the associated factory
    #+-----------------------------------------------------------------------+
    def getFactory(self):
        return IRPMessageFactory

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

        properties.append(['Direction', Format.STRING, self.getDirection()])
        properties.append(['Major', Format.STRING, self.getMajor()])
        properties.append(['Minor', Format.DECIMAL, self.getMinor()])
        properties.append(['Requestmode', Format.STRING, self.getRequestMode()])
        properties.append(['PID', Format.DECIMAL, self.getPID()])
        properties.append(['Status', Format.DECIMAL, self.getStatus()])
        properties.append(['Information', Format.DECIMAL, self.getInformation()])
        properties.append(['Cancel', Format.STRING, self.getCancel()])
        properties.append(['SizeIn', Format.DECIMAL, self.getSizeIn()])
        properties.append(['SizeOut', Format.DECIMAL, self.getSizeOut()])

        properties.append(['Data', Format.HEX, self.getStringData()])
        properties.append(['Pattern', Format.STRING, self.getPatternString()])

        return properties

    #+----------------------------------------------
    #| GETTERS:
    #+----------------------------------------------
    def getDirection(self):
        return self.direction

    def getMajor(self):
        return self.major

    def getMinor(self):
        return self.minor

    def getRequestMode(self):
        return self.requestmode

    def getPID(self):
        return self.pid

    def getStatus(self):
        return self.status

    def getInformation(self):
        return self.information

    def getCancel(self):
        return self.cancel

    def getSizeIn(self):
        return self.sizeIn

    def getSizeOut(self):
        return self.sizeOut

    #+----------------------------------------------
    #| SETTERS:
    #+----------------------------------------------
    #TODO
