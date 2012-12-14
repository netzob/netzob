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
from abc import abstractmethod
from gettext import gettext as _
import logging

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+


#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+


class AbstractRelationType():
    """AbstractRelationType:
            It defines the type of a relation variable.
    """

    def __init__(self, sized, nbChars=0, delimiter=None):
        """Constructor of AbstractRelationType:

                @type sized: boolean
                @param sized: tell if the variable can be delimited by a size or by a delimiter.
                @type nbChars: integer
                @param nbChars: the number of elementary character the value of this variable can have.
                @type delimiter: bitarray
                @param delimiter: a set of bits that tells where the associated variable ends.
        """
        self.log = logging.getLogger('netzob.Common.MMSTD.Dictionary.RelationTypes.AbstractRelationType.py')
        self.associatedDataType = self.makeAssociatedDataType(sized, nbChars, nbChars, delimiter)

    def toString(self):
        return "{0}, associatedDataType: {1}".format(self.getType(), self.associatedDataType.toString())

#+---------------------------------------------------------------------------+
#| Abstract methods                                                          |
#+---------------------------------------------------------------------------+
    @abstractmethod
    def getType(self):
        """getType:
                Return a string describing the current Type.

                @rtype: string
                @return: the current type in string format.
        """
        raise NotImplementedError("The current type does not implement 'getType'.")

    def makeAssociatedDataType(self, sized, minChars, maxChars, delimiter):
        """makeAssociatedDataType
                Make the associated data type.

                @type minChars: integer
                @type sized: boolean
                @param sized: tell if the variable can be delimited by a size or by a delimiter.
                @param minChars: the minimum number of elementary character the value of this variable can have.
                @type maxChars: integer
                @param maxChars: the maximum number of elementary character the value of this variable can have.
                @type delimiter: bitarray
                @param delimiter: a set of bits that tells where the associated variable ends.
        """
        raise NotImplementedError("The current type does not implement 'makeAssociatedDataType'.")

    @abstractmethod
    def computeValue(self, writingToken):
        """computeValue:
                Compute the value of the variable according to its type.

                @type writingToken: netzob.Common.MMSTD.Dictionary.VariableProcessingToken.VariableWritingToken.VariableWritingToken
                @param writingToken: a token which contains all critical information on this access.
                @rtype: bitarray
                @return: the computed value.
        """
        raise NotImplementedError("The current type does not implement 'computeValue'.")

#+---------------------------------------------------------------------------+
#| Getters and setters                                                       |
#+---------------------------------------------------------------------------+
    def getAssociatedDataType(self):
        return self.associatedDataType

    def getNbChars(self):
        return self.associatedDataType.getMaxChars()

    def getNbBits(self):
        return self.associatedDataType.getMaxBits()

    def setAssociatedDataType(self, dataType):
        self.associatedDataType = dataType

#+---------------------------------------------------------------------------+
#| Static methods                                                            |
#+---------------------------------------------------------------------------+
    @staticmethod
    def makeType(typeString, sized, minChars, maxChars, delimiter):
        _type = None
        from netzob.Common.MMSTD.Dictionary.RelationTypes.SizeRelationType import SizeRelationType
        if typeString == SizeRelationType.TYPE:
            _type = SizeRelationType(sized, minChars, maxChars, delimiter)
        else:
            logging.error("Wrong type specified for this variable.")
        return _type
