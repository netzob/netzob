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


#+----------------------------------------------
#| Class for representation potential unit size for data representation
#+----------------------------------------------
class UnitSize():
    NONE = "none"
    BIT = "bit"
    BITS4 = "4-bits"
    BITS8 = "8-bits"
    BITS16 = "16-bits"
    BITS32 = "32-bits"
    BITS64 = "64-bits"

    unitSizeInBits = {BIT: 1, BITS4: 4, BITS8: 8, BITS16: 16, BITS32: 32, BITS64: 64}

    @staticmethod
    def getPackDefiniton(unitSize):
        result = "B"
        size = UnitSize.getSizeInBits(unitSize)

        if size == 8:
            result = "B"
        elif size == 16:
            result = "H"
        elif size == 32:
            result = "L"
        elif size == 64:
            result = "Q"
        else:
            logging.warning("Error, unknown conversion value for provided unitsize {0}".format(unitSize))
        return result

    @staticmethod
    def getSizeInBits(unitSize):
        if unitSize in UnitSize.unitSizeInBits:
            return UnitSize.unitSizeInBits[unitSize]
        else:
            return None
