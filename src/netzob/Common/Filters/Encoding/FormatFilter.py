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
from netzob.Common.Type.Format import Format
from netzob.Common.Filters.EncodingFilter import EncodingFilter
from netzob.Common.Type.TypeConvertor import TypeConvertor
from netzob.Common.Type.UnitSize import UnitSize
from netzob.Common.Type.Endianess import Endianess

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+


#+---------------------------------------------------------------------------+
#| FormatFilter:
#|     Definition of an encoding filter which apply a format on a message
#+---------------------------------------------------------------------------+
class FormatFilter(EncodingFilter):

    TYPE = "FormatFilter"

    def __init__(self, name, formatType, unitSize, endianness):
        EncodingFilter.__init__(self, FormatFilter.TYPE, name)
        self.formatType = formatType
        self.unitsize = unitSize
        self.endianness = endianness

    def apply(self, message):

        if self.unitsize != UnitSize.NONE:
            # First we apply the unit size
            # Default modulo = 2 => 8BITS
            modulo = UnitSize.getSizeInBits(self.unitsize) / 4

            splittedData = []
            tmpResult = ""
            for i in range(0, len(message)):
                if i > 0 and i % modulo == 0:
                    splittedData.append(tmpResult)
                    tmpResult = ""
                tmpResult = tmpResult + message[i]
            splittedData.append(tmpResult)
        else:
            splittedData = [message]

        # Now we have the message splitted per unit size
        # we apply endianess on it
        # we consider the normal mode is big-endian
        if self.endianness == Endianess.LITTLE:
            # none ou 4 bits : A0B1C2 -> A0B1C2 -> 2C1B0A
            # 8 bits : A0B1C2 -> A0 B1 C2 -> C2B1A0
            # 16 bits : A0B1C2 -> A0B1 C2 -> C2 A0B1
            # 32 bits ...
            if self.unitsize == UnitSize.NONE:
                local_value = ""
                for i in range(0, len(splittedData)):
                    local_value = splittedData[i][::-1]
                    splittedData[i] = local_value
            else:
                tmpData = splittedData[::-1]
                splittedData = tmpData

        # we encode each data
        encodedSplittedData = []
        for d in splittedData:
            encodedSplittedData.append(TypeConvertor.encodeNetzobRawToGivenType(d, self.formatType))

        # Before sending back (;D) we join everything
        return " ".join(encodedSplittedData)

    def getConversionAddressingTable(self, message):
        return None
