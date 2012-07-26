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


class AbstractType():
    """AbstractType:
            It defines the type of a variable.
    """

    def __init__(self):
        """Constructor of AbstractType:
                @type atomicSize: integer
                @param atomicSize: the size of an element of this type in bits. 1 for bits, 8 for bytes.
        """
        self.log = logging.getLogger('netzob.Common.MMSTD.Dictionary.Type.AbstractType.py')

    @abstractmethod
    def generateValue(self, generationStrategies, minSize, maxSize):
        """generateValue:
                Generate a bit array value according to the generationStrategy specification and which size is between minSize and maxSize.

                @type generationStrategies: string List
                @param generationStrategies: a list of strategy ("random" for instance) that defines the way the value will be generated. The first allowed strategy is used.
                @type minSize: integer
                @param minSize: the minimum size of the value in bits.
                @type maxSize: integer
                @param maxSize: the maximum size of the value in bits.
                @rtype: bitarray
                @return: the generated value.
        """
        raise NotImplementedError(_("The current type does not implement 'generateValue'."))

    @abstractmethod
    def str2bin(self, stri):
        """str2bin:
                Transform a string type value (string for a word, str(integer)...) in a binary value.
                Must be the bin2str's inverse.

                @type stri: string
                @param stri: the original value in an appropriate string format.
                @rtype: bitarray
                @return: the value in bitarray.
        """
        raise NotImplementedError(_("The current type does not implement 'str2bin'."))

    @abstractmethod
    def bin2str(self, bina):
        """bin2str:
                Transform a binary type value (bitarray) in an appropriate string format.
                Must be the str2bin's inverse.

                @type bina: bitarray
                @param bina: the original value in bitarray format.
                @rtype: string
                @return: the value in string.
        """
        raise NotImplementedError(_("The current type does not implement 'bin2str'."))

    @abstractmethod
    def getBitSize(self, typeValue):
        """getBitSize:
                Get the size in bits of the type value given.

                @type typeValue: linked to the instance of Type.
                @param typeValue: the original value in the authentic type format.
                @rtype: integer
                @return: the size in bits of the given value.
        """
        raise NotImplementedError(_("The current type does not implement 'getBitSize'."))

    @abstractmethod
    def getMaxBitSize(self, nbChars):
        """getMaxBitSize:
                Get the size in bits of the maximal word of this type that we can make with nbChars characters.

                @type nbChars: integer
                @param nbChars: number of characters used to make the maximal word.
                @rtype: integer
                @return: the size in bits of the maximal word.
        """
        raise NotImplementedError(_("The current type does not implement 'getMaxBitSize'."))

    @abstractmethod
    def getMinBitSize(self, nbChars):
        """getMinBitSize:
                Get the size in bits of the minimal word of this type that we can make with nbChars characters.

                @type nbChars: integer
                @param nbChars: number of characters used to make the minimal word.
                @rtype: integer
                @return: the size in bits of the minimal word.
        """
        raise NotImplementedError(_("The current type does not implement 'getMinBitSize'."))

    def getType(self):
        """getType:
                Return a string description of the current Type.

                @rtype: string
                @return: the current type in string format.
        """
        raise NotImplementedError(_("The current type does not implement 'getType'."))

#+---------------------------------------------------------------------------+
#| Static methods                                                            |
#+---------------------------------------------------------------------------+
    @staticmethod
    def makeType(typeString):
        type = None
        from netzob.Common.MMSTD.Dictionary.Types.BinaryType import BinaryType
        from netzob.Common.MMSTD.Dictionary.Types.DecimalWordType import DecimalWordType
        from netzob.Common.MMSTD.Dictionary.Types.HexWordType import HexWordType
        from netzob.Common.MMSTD.Dictionary.Types.IPv4WordType import IPv4WordType
        from netzob.Common.MMSTD.Dictionary.Types.MACWordType import MACWordType
        from netzob.Common.MMSTD.Dictionary.Types.IntegerType import IntegerType
        from netzob.Common.MMSTD.Dictionary.Types.WordType import WordType
        if typeString == BinaryType.TYPE:
            type = BinaryType()
        elif typeString == DecimalWordType.TYPE:
            type = DecimalWordType()
        elif typeString == HexWordType.TYPE:
            type = HexWordType()
        elif typeString == IPv4WordType.TYPE:
            type = IPv4WordType()
        elif typeString == MACWordType.TYPE:
            type = MACWordType()
        elif typeString == IntegerType.TYPE:
            type = IntegerType()
        elif typeString == WordType.TYPE:
            type = WordType()
        else:
            logging.error(_("Wrong type specified for this variable."))
        return type
