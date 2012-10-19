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
#| Standard library imports                                                  |
#+---------------------------------------------------------------------------+
import logging

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+


#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.MMSTD.Dictionary.DataTypes.IntegerType import IntegerType
from netzob.Common.MMSTD.Dictionary.RelationTypes.AbstractRelationType import \
    AbstractRelationType
from netzob.Common.Type.TypeConvertor import TypeConvertor


class SizeRelationType(AbstractRelationType):
    """SizeRelationType:
            It defines the type of a size relation variable.
    """

    TYPE = "Size Relation"

    def __init__(self, sized, minChars, maxChars, delimiter):
        """Constructor of SizeRelationType:
        """
        self.log = logging.getLogger('netzob.Common.MMSTD.Dictionary.RelationTypes.SizeRelationType.py')
        self.setAssociatedDataType(self.makeAssociatedDataType(sized, minChars, maxChars, delimiter))

    def getType(self):
        """getType:
        """
        return SizeRelationType.TYPE

    def makeAssociatedDataType(self, sized, minChars, maxChars, delimiter):
        """makeAssociatedDataType:
                The data type associated to a size field is obviously an integer.
        """
        return IntegerType(sized, minChars, maxChars, delimiter)

    def computeValue(self, value):
        """computeValue:
        """
        if value is not None:
            size = len(value)
            self.log.debug("Compute the size of {0} = {1}".format(value, size))
            return TypeConvertor.intstring2bin(str(size))
        else:
            return 0
