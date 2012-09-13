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
from netzob.Common.Models.IRPMessage import IRPMessage
from netzob.Common.Models.Factories.IRPDeviceIoControlMessageFactory import IRPDeviceIoControlMessageFactory
from netzob.Common.Type.Format import Format
from netzob.Common.Type.TypeConvertor import TypeConvertor
from netzob.Common.Property import Property


#+---------------------------------------------------------------------------+
#| IRPDeviceIoControlMessage:
#|     Definition of a Windows IRP IOCTL message
#+---------------------------------------------------------------------------+
class IRPDeviceIoControlMessage(IRPMessage):
    def __init__(self, id, timestamp, data, direction, major, minor, requestmode, pid, status, information, cancel, sizeIn, sizeOut, ioctl, pattern=[]):
        IRPMessage.__init__(self, id, timestamp, data, "IRPDeviceIoControl", direction, major, minor, requestmode, pid, status, information, cancel, sizeIn, sizeOut, pattern)
        self.ioctl = ioctl

        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Common.Models.IRPDeviceIoControlMessage.py')
        #print "CALL Network "+str(self.getPattern())

        #print str(self.pattern[0])+" "+str([str(i) for i in self.pattern[1]])+" "+str(TypeConvertor.netzobRawToString(str(self.getData())))

    #+-----------------------------------------------------------------------+
    #| getFactory
    #| @return the associated factory
    #+-----------------------------------------------------------------------+
    def getFactory(self):
        return IRPDeviceIoControlFactory

    #+-----------------------------------------------------------------------+
    #| getProperties
    #|     Computes and returns the properties of the current message
    #| @return an array with all the properties [[key,type,val],...]
    #+-----------------------------------------------------------------------+
    def getProperties(self):
        properties = []
        properties.extend(super(IRPDeviceIoControlMessage, self).getProperties())
        properties.append(Property('IOCTL', Format.DECIMAL, self.getIOCTL()))

        return properties

    #+----------------------------------------------
    #| GETTERS:
    #+----------------------------------------------
    def getIOCTL(self):
        return self.ioctl

    #+----------------------------------------------
    #| SETTERS:
    #+----------------------------------------------
    #TODO
