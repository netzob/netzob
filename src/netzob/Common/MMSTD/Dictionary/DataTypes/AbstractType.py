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
import random

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+


#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Type.TypeConvertor import TypeConvertor


class AbstractType():
    """AbstractType:
            It defines the type that rules the data of a variable.
            Such a typed data can be delimited by a minimum and a maximum or by a delimiter at the end.
    """

    MAX_CHARS = 100

    def __init__(self, sized, minChars=0, maxChars=0, delimiter=None):
        """Constructor of AbstractType:

                @type sized: boolean
                @param sized: tell if the variable can be delimited by a size or by a delimiter.
                @type minChars: integer
                @param minChars: the minimum number of characters of the variable associated to the given type.
                @type maxChars: integer
                @param maxChars: the maximum number of characters of the variable associated to the given type.
                @type delimiter: bitarray
                @param delimiter: a set of bits that tells where the associated variable ends.
        """
        self.log = logging.getLogger('netzob.Common.MMSTD.Dictionary.Types.AbstractType.py')
        self.sized = sized
        self.setNumberBitsAndNumberChars(minChars, maxChars)
        self.delimiter = None
        try:
            # We assume that delimiters are written by the user as hex string.
            self.delimiter = TypeConvertor.hexstring2bin(delimiter)
        except:
            self.log.error("The delimiter {0} is not a valid hexadecimal string.".format(str(delimiter)))

    def toString(self):
        if self.sized:
            return ("{0}, bits: ({1}, {2}), chars: ({3}, {4})".format(self.getType(), str(self.minBits), str(self.maxBits), str(self.minChars), str(self.maxChars)))
        else:
            return ("{0}, delimiter: {1}").format(self.getType(), self.bin2str(self.delimiter))

    def endsHere(self, bina):
        """endsHere:
                (For unsized type)
                Tell if the type ends at the beginning of bita. i.e. we found the delimiter as a prefix of bina.

                @type bina: bitarray
                @param bina: the bitarray which could prefix with the variable's type delimiter which would indicate the end of the data block.
                @rtype: boolean
                @return: True if it ends here, False if we have to go deeper.
        """
        if len(bina) < len(self.delimiter):
            return False
        for i in range(len(self.delimiter)):
            if bina[i] != self.delimiter[i]:
                return False
        return True

    def generateValue(self, generationStrategies):
        """generateValue:
                Generate a bit array value according to the generationStrategy specification.

                @type generationStrategies: string List
                @param generationStrategies: a list of strategy ("random" for instance) that defines the way the value will be generated. The first allowed strategy is used.
                @rtype: bitarray
                @return: the generated value.
        """
        if self.sized:
            size = random.randint(self.minChars, self.maxChars)
            self.log.debug("Generate Fixed Sized value (generated size = {0})".format(size))
            return self.generateFixedSizeValue(generationStrategies, size)
        else:
            size = random.randint(0, AbstractType.MAX_CHARS)
            self.log.debug("Generate unsized value (generated size = {0})".format(size))
            value = self.generateFixedSizeValue(generationStrategies, size)
            value += self.delimiter  # The delimiter is a part of the final value.
            return value

    def compareFormat(self, readingToken):
        """compareFormat:
                Compare (starting at the "indice"-th character) the readingToken's value format to the type format.

                @type readingToken: netzob.Common.MMSTD.Dictionary.VariableProcessingToken.VariableReadingToken.VariableReadingToken
                @param readingToken: a token which contains all critical information on this access.
        """
        tmp = readingToken.getValue()[readingToken.getIndex():]

        # If the type has a definite size.
        if self.isSized():
            minBits = self.getMinBits()
            maxBits = self.getMaxBits()
            # Length comparison.
            if len(tmp) >= minBits:
                #self.log.debug(str(len(tmp)) + " - " + str(minBits) + " - " + str(maxBits))
                if len(tmp) <= maxBits:
                    # Format comparison.
                    if self.suitsBinary(tmp):
                        readingToken.setOk(True)
                        self.log.info("Format comparison successful.")
                    else:
                        readingToken.setOk(False)
                        self.log.info("Format comparison failed: wrong format.")
                else:  # len(tmp) > self.maxBits
                    # Format comparison.
                    if self.suitsBinary(tmp[:maxBits]):
                        readingToken.setOk(True)
                        self.log.info("Format comparison successful.")
                    else:
                        readingToken.setOk(False)
                        self.log.info("Format comparison failed: wrong format.")
            else:
                readingToken.setOk(False)
                self.log.info("Format comparison failed: wrong size.")

        # If the type is delimited from 0 to a delimiter.
        else:
            endi = -1
            for i in range(len(tmp)):
                if self.endsHere(tmp[i:]):
                    endi = i
                    break
            if endi != -1:
                # We learn from the beginning to the delimiter.
                self.log.info("Format comparison successful.")
                readingToken.setOk(True)
            else:
                readingToken.setOk(False)
                self.log.info("Format comparison failed: no delimiter found.")

#+---------------------------------------------------------------------------+
#| Abstract methods                                                          |
#+---------------------------------------------------------------------------+
    @abstractmethod
    def mutateValue(self, generationStrategies, value, mutationRate=10, deletionRate=5, additionRate=5):
        """mutateValue:
                Mutate the given bit array value according to the generationStrategy specification.

                @type generationStrategies: string List
                @param generationStrategies: a list of strategy ("random" for instance) that defines the way the value will be generated. The first allowed strategy is used.
                @type value: bitarray
                @param value: the value before mutation.
                @type mutationRate: integer (between 0 and 100)
                @param mutationRate: the percentage of characters that will be mutated.
                @type deletionRate: integer (between 0 and 100)
                @param deletionRate: the percentage of characters that will be deleted.
                @type additionRate: integer (between 0 and 100)
                @param additionRate: the percentage of characters that will be added.
                @rtype: bitarray
                @return: the value after mutation.
        """
        raise NotImplementedError("The current type does not implement 'mutateValue'.")

    @abstractmethod
    def generateFixedSizeValue(self, generationStrategies, charSize):
        """generateFixedSizeValue:
                Generate a bit array having charSize typed-characters according to the generationStrategy specification.

                @type generationStrategies: string List
                @param generationStrategies: a list of strategy ("random" for instance) that defines the way the value will be generated. The first allowed strategy is used.
                @type charSize: integer
                @param charSize: the size of the value in characters.
                @rtype: bitarray
                @return: the generated value.
        """
        raise NotImplementedError("The current type does not implement 'generateFixedSizeValue'.")

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
        raise NotImplementedError("The current type does not implement 'str2bin'.")

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
        raise NotImplementedError("The current type does not implement 'bin2str'.")

    @abstractmethod
    def getBitSize(self, typeValue):
        """getBitSize:
                Get the size in bits of the type value given.

                @type typeValue: linked to the instance of Type.
                @param typeValue: the original value in the authentic type format.
                @rtype: integer
                @return: the size in bits of the given value.
        """
        raise NotImplementedError("The current type does not implement 'getBitSize'.")

    @abstractmethod
    def getMaxBitSize(self, nbChars):
        """getMaxBitSize:
                Get the size in bits of the maximal word of this type that we can make with nbChars characters.

                @type nbChars: integer
                @param nbChars: number of characters used to make the maximal word.
                @rtype: integer
                @return: the size in bits of the maximal word.
        """
        raise NotImplementedError("The current type does not implement 'getMaxBitSize'.")

    @abstractmethod
    def getMinBitSize(self, nbChars):
        """getMinBitSize:
                Get the size in bits of the minimal word of this type that we can make with nbChars characters.

                @type nbChars: integer
                @param nbChars: number of characters used to make the minimal word.
                @rtype: integer
                @return: the size in bits of the minimal word.
        """
        raise NotImplementedError("The current type does not implement 'getMinBitSize'.")

    @abstractmethod
    def getType(self):
        """getType:
                Return a string description of the current Type.

                @rtype: string
                @return: the current type in string format.
        """
        raise NotImplementedError("The current type does not implement 'getType'.")

    @abstractmethod
    def suitsBinary(self, bina):
        """suitsBinary:
                Tell if a bitarray is well formatted and the type suits it.

                @type bina: bitarray
                @param bina: the bitarray that is being analyzed.
                @rtype: boolean
                @return: True if the type suits the bitarray.
        """
        raise NotImplementedError("The current type does not implement 'suitsBinary'.")

#+---------------------------------------------------------------------------+
#| Getters and Setters                                                       |
#+---------------------------------------------------------------------------+
    def isSized(self):
        return self.sized

    def getMinChars(self):
        return self.minChars

    def getMaxChars(self):
        return self.maxChars

    def getDelimiter(self):
        return self.delimiter

    def getMinBits(self):
        return self.minBits

    def getMaxBits(self):
        return self.maxBits

    def setNumberBitsAndNumberChars(self, minChars, maxChars):
        if minChars is not None and minChars >= 0:
            self.minBits = self.getMinBitSize(minChars)
            self.minChars = minChars
        else:
            self.log.info("Type {0} : minChars undefined or < 0. MinBits value is fixed to 0.".format(self.getType()))
            self.minBits = 0
            self.minChars = 0
        if maxChars is not None and maxChars >= minChars:
            self.maxBits = self.getMaxBitSize(maxChars)
            self.maxChars = maxChars
        else:
            self.log.info("Type {0} : maxChars undefined or < minChars. MaxBits value is fixed to minBits.".format(self.getType()))
            self.maxBits = self.minBits
            self.maxChars = self.minChars

#+---------------------------------------------------------------------------+
#| Static methods                                                            |
#+---------------------------------------------------------------------------+
    @staticmethod
    def makeType(typeString, sized, minSize=0, maxSize=0, delimiter=None):
        _type = None
        from netzob.Common.MMSTD.Dictionary.DataTypes.BinaryType import BinaryType
        from netzob.Common.MMSTD.Dictionary.DataTypes.DecimalWordType import DecimalWordType
        from netzob.Common.MMSTD.Dictionary.DataTypes.HexWordType import HexWordType
        from netzob.Common.MMSTD.Dictionary.DataTypes.IPv4WordType import IPv4WordType
        from netzob.Common.MMSTD.Dictionary.DataTypes.MACWordType import MACWordType
        from netzob.Common.MMSTD.Dictionary.DataTypes.IntegerType import IntegerType
        from netzob.Common.MMSTD.Dictionary.DataTypes.WordType import WordType
        if typeString == BinaryType.TYPE:
            _type = BinaryType(sized, minSize, maxSize, delimiter)
        elif typeString == DecimalWordType.TYPE:
            _type = DecimalWordType(sized, minSize, maxSize, delimiter)
        elif typeString == HexWordType.TYPE:
            _type = HexWordType(sized, minSize, maxSize, delimiter)
        elif typeString == IntegerType.TYPE:
            _type = IntegerType(sized, minSize, maxSize, delimiter)
        elif typeString == IPv4WordType.TYPE:
            _type = IPv4WordType(sized, minSize, maxSize, delimiter)
        elif typeString == MACWordType.TYPE:
            _type = MACWordType(sized, minSize, maxSize, delimiter)
        elif typeString == WordType.TYPE:
            _type = WordType(sized, minSize, maxSize, delimiter)
        else:
            logging.error("Wrong type specified for this variable.")
        return _type
