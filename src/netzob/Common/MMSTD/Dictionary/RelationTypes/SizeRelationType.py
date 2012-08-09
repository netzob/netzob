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
from bitarray import bitarray
from gettext import gettext as _
import logging

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+


#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.MMSTD.Dictionary.DataTypes.IntegerType import IntegerType
from netzob.Common.MMSTD.Dictionary.VariableProcessingToken.VariableWritingToken import \
    VariableWritingToken


class SizeRelationType():
    """SizeRelationType:
            It defines the type of a size relation variable.
    """

    TYPE = "Size Relation"

    def __init__(self):
        """Constructor of SizeRelationType:
        """
        self.log = logging.getLogger('netzob.Common.MMSTD.Dictionary.RelationTypes.SizeRelationType.py')

    def getType(self):
        """getType:
        """
        return SizeRelationType.TYPE

    def getAssociatedDataType(self):
        """getAssociatedDataType:
                The data type associated to a size field is obviously an integer.
        """
        return IntegerType()

    def computeValue(self, pointedVariable, writingToken):
        """computeValue:
        """
        writingToken2 = VariableWritingToken(writingToken.getNegative(), writingToken.getVocabulary(), writingToken.getMemory(), bitarray(''), writingToken.getGenerationStrategy())
        pointedVariable.write(writingToken)
        if writingToken2.isOk():
            pointedVariable.setChecked(True)
            return len(writingToken2.getValue())
        else:
            return 0
