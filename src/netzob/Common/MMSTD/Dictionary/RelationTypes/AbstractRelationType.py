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

    def __init__(self):
        """Constructor of AbstractRelationType:
        """
        self.log = logging.getLogger('netzob.Common.MMSTD.Dictionary.RelationTypes.AbstractRelationType.py')

#+---------------------------------------------------------------------------+
#| Abstract methods                                                          |
#+---------------------------------------------------------------------------+
    @abstractmethod
    def getType(self):
        """getType:
                Return a string description of the current Type.

                @rtype: string
                @return: the current type in string format.
        """
        raise NotImplementedError(_("The current type does not implement 'getType'."))

    @abstractmethod
    def getAssociatedDataType(self):
        """getAssociatedDataType:
                Return a DataType properly associated to this RelationType (For instance IntegerType for SizeRelationType).

                @rtype: netzob.Common.MMSTD.Dictionary.DataTypes
                @return: the associated data type.
        """
        raise NotImplementedError(_("The current type does not implement 'getAssociatedDataType'."))

    @abstractmethod
    def computeValue(self, writingToken):
        """computeValue:
                Compute the value of the variable according to its type.

                @type writingToken: netzob.Common.MMSTD.Dictionary.VariableProcessingToken.VariableWritingToken.VariableWritingToken
                @param writingToken: a token which contains all critical information on this access.
                @rtype: bitarray
                @return: the computed value.
        """
        raise NotImplementedError(_("The current type does not implement 'computeValue'."))

#+---------------------------------------------------------------------------+
#| Static methods                                                            |
#+---------------------------------------------------------------------------+
    @staticmethod
    def makeType(typeString):
        _type = None
        from netzob.Common.MMSTD.Dictionary.RelationTypes.SizeRelationType import SizeRelationType
        if typeString == SizeRelationType.TYPE:
            _type = SizeRelationType()
        else:
            logging.error(_("Wrong type specified for this variable."))
        return _type
