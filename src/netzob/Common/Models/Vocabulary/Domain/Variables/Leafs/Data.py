#-*- coding: utf-8 -*-

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
#| File contributors :                                                       |
#|       - Georges Bossert <georges.bossert (a) supelec.fr>                  |
#|       - Frédéric Guihéry <frederic.guihery (a) amossys.fr>                |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Standard library imports                                                  |
#+---------------------------------------------------------------------------+
import logging

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+
from bitarray import bitarray

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck
from netzob.Common.Models.Types.AbstractType import AbstractType
from netzob.Common.Models.Vocabulary.Domain.Variables.Leafs.AbstractVariableLeaf import AbstractVariableLeaf
from netzob.Common.Models.Vocabulary.Domain.Variables.VariableProcessingTokens.AbstractVariableProcessingToken import AbstractVariableProcessingToken
from netzob.Common.Models.Vocabulary.Domain.Variables.VariableProcessingTokens.VariableReadingToken import VariableReadingToken
from netzob.Common.Models.Vocabulary.Domain.Variables.VariableProcessingTokens.VariableWritingToken import VariableWritingToken


class Data(AbstractVariableLeaf):
    """Represents a data, meaning a portion of content in the final
    message.

    For instance:

    >>> from netzob import *
    >>> f = Field()
    >>> f.domain = Data(dataType=ASCII, originalValue="zoby", name="pseudo")
    >>> print f.domain.varType
    Data
    >>> print f.domain.currentValue
    zoby
    >>> print f.domain.dataType.__name__
    ASCII
    >>> print f.domain.name
    pseudo

    >>> f = Field(ASCII("hello zoby"))
    >>> print f.domain.varType
    Data
    >>> print f.domain.currentValue
    hello zoby
    """

    def __init__(self, dataType, originalValue=None, name=None, size=(None, None)):
        """The constructor of a data variable

        :param dataType: the type of the data.
        :type dataType: :class:`netzob.Common.Models.Types.AbstractType.AbstractType`
        :keyword originalValue: the value of the data (can be None)
        :type originalValue: :class:`object`
        :keyword name: the name of the data, if None name will be generated
        :type name: :class:`str`
        :keyword size: the size of the data (minSize, maxSize) in bits, per default its (None, None)
        :type size: a tupple of int
        :raises: :class:`TypeError` or :class:`ValueError` if parameters are not valid.

        """

        super(Data, self).__init__(self.__class__.__name__, name=name)
        self.__logger = logging.getLogger(__name__)

        self.dataType = dataType
        self.currentValue = originalValue
        self.size = size

    @typeCheck(AbstractVariableProcessingToken)
    def isDefined(self, processingToken):
        """If the leaf has no values, it is not defined and returns False

        >>> from netzob import *
        >>> data = Data(ASCII, originalValue="hello")
        >>> rToken = VariableReadingToken()
        >>> data.isDefined(rToken)
        True
        >>> data.read(rToken)
        >>> data.isDefined(rToken)
        True

        :rtype: bool
        :return: True if the data has a current value or has memorized its value in the processing token
        :raises: TypeError if parameter is not Valid
        """
        if processingToken is None:
            raise TypeError("ProcessingToken cannot be None")

        return self.getValue(processingToken) is not None

    @typeCheck(AbstractVariableProcessingToken)
    def getValue(self, processingToken):
        """Return the current or memorized value.

        >>> from netzob import *
        >>> data = Data(ASCII, originalValue='helloworld')
        >>> rToken = VariableReadingToken()
        >>> print data.getValue(rToken)
        helloworld

        :param processingToken: the token in which the memory is located
        :type processingToken: :class:`netzob.Common.Models.Vocabulary.Domain.Variables.VariableProcessingTokens.AbstractVariableProcessingToken`
        """
        if self.currentValue is not None:
            return self.currentValue
        else:
            return processingToken.memory.recall(self)

    #+---------------------------------------------------------------------------+
    #| Functions inherited from AbstractLeafVariable                             |
    #+---------------------------------------------------------------------------+
    @typeCheck(AbstractVariableProcessingToken)
    def forget(self, processingToken):
        """The variable forgets its value both locally and from the memory attached to the processingToken

        >>> from netzob import *
        >>> d = Data(Decimal, originalValue=10)
        >>> rToken = VariableReadingToken()
        >>> d.memorize(rToken)
        >>> d.currentValue = 30
        >>> d.currentValue
        30
        >>> d.recall(rToken)
        >>> d.currentValue
        10
        >>> d.forget(rToken)
        >>> print d.currentValue
        None

        :param processingToken: the processing token where the memory is
        :type processingToken: :class:`netzob.Common.Models.Vocabulary.Domain.Variables.VariableProcessingTokens.AbstractVariableProcessingToken.AbstractVariableProcessingToken`
        :raise: a TypeError if parameter is not valid
        """
        if processingToken is None:
            raise TypeError("processingToken cannot be None")

        self.__logger.debug("- {0}: value is forgotten.".format(self))
        # We remove the memorized value.
        processingToken.memory.forget(self)
        # We remove the local value
        self.currentValue = None

    @typeCheck(AbstractVariableProcessingToken)
    def recall(self, processingToken):
        """The variable recall its memorized value.

        >>> from netzob import *
        >>> d = Data(ASCII, originalValue = "zoby")
        >>> print d.currentValue
        zoby
        >>> rToken = VariableReadingToken()
        >>> d.memorize(rToken)
        >>> d.currentValue = "netzob"
        >>> print d.currentValue
        netzob
        >>> d.recall(rToken)
        >>> print d.currentValue
        zoby

        :param processingToken: the processing token where the memory is
        :type processingToken: :class:`netzob.Common.Models.Vocabulary.Domain.Variables.VariableProcessingTokens.AbstractVariableProcessingToken.AbstractVariableProcessingToken`
        :raise: a TypeError if parameter is not valid
        """
        if processingToken is None:
            raise TypeError("processingToken cannot be None")

        self.__logger.debug("- {0}: value is recalled.".format(self))
        self.currentValue = processingToken.memory.recall(self)

    @typeCheck(AbstractVariableProcessingToken)
    def memorize(self, processingToken):
        """The variable memorizes its value.


        :param processingToken: the processing token where the memory is
        :type processingToken: :class:`netzob.Common.Models.Vocabulary.Domain.Variables.VariableProcessingTokens.AbstractVariableProcessingToken.AbstractVariableProcessingToken`
        :raise: a TypeError if parameter is not valid
        """
        if processingToken is None:
            raise TypeError("processingToken cannot be None")

        self.__logger.debug("- {0}: value is memorized.".format(self))
        processingToken.memory.memorize(self)

    @typeCheck(VariableReadingToken)
    def compareFormat(self, readingToken):
        """The variable checks if its format complies with the read value's format.

        >>> from netzob import *
        >>> data = Data(ASCII)
        >>> rToken = VariableReadingToken(value=TypeConvertor.encode(ASCII, bitarray, "helloworld"))
        >>> print data.compareFormat(rToken)
        True

        :param readingToken: the processing token where the memory is
        :type readingToken: :class:`netzob.Common.Models.Vocabulary.Domain.Variables.VariableProcessingTokens.VariableReadingToken.VariableReadingToken`
        :raise: a TypeError if parameter is not valid
        """
        if readingToken is None:
            raise TypeError("readingToken cannot be None")

        self.__logger.debug("- [ {0}: compareFormat.".format(self))

        self.varType.compareFormat(readingToken)

        self.__logger.debug("Variable {0}: {1}. ] -".format(self.name, readingToken))

    @typeCheck(VariableReadingToken)
    def learn(self, readingToken):
        """learn:

        .. warning:: WIP, the delimitor case is not yet managed.

        :param readingToken: the processing token where the memory is
        :type readingToken: :class:`netzob.Common.Models.Vocabulary.Domain.Variables.VariableProcessingTokens.VariableReadingToken.VariableReadingToken`
        :raise: a TypeError if parameter is not valid
        """
        if readingToken is None:
            raise TypeError("readingToken cannot be None")

        self.__logger.debug("- [ {0}: learn.".format(self))
        # A format comparison had been executed before, its result must be "OK".
        if readingToken.Ok():
            tmp = readingToken.value[readingToken.index():]

            minSize, maxSize = self.size

            # If the type has a definite size.
            if maxSize is not None:
                # Length comparison. (len(tmp) >= minBits is implicit as the readingToken is OK.)
                if len(tmp) <= maxSize:
                    self.currentValue = tmp
                    readingToken.incrementIndex(len(tmp))

                else:  # len(tmp) > self.maxBits
                    # We learn as much as we can.
                    self.currentValue = tmp[:maxSize]
                    readingToken.incrementIndex(maxSize)

            # TODO
            # If the type is delimited from 0 to a delimiter.
            else:
                endi = 0
                for i in range(len(tmp)):
                    if self.type.endsHere(tmp[i:]):
                        endi = i
                        break
                # We learn from the beginning to the delimiter.
                self.currentValue = tmp[:endi + len(self.type.getDelimiter())]  # The delimiter token is a part of the variable.
                readingToken.incrementIndex(endi + len(self.type.getDelimiter()))

            self.__logger.info("Learning done.")
        else:
            self.__logger.info("Learning abort because the previous format comparison failed.")

        self.__logger.debug("Variable {0}: {1}. ] -".format(self.name, readingToken))

    @typeCheck(VariableReadingToken)
    def compare(self, readingToken):
        """The variable compares its value to the read value.


        :param readingToken: the processing token where the memory is
        :type readingToken: :class:`netzob.Common.Models.Vocabulary.Domain.Variables.VariableProcessingTokens.VariableReadingToken.VariableReadingToken`
        :raise: a TypeError if parameter is not valid
        """
        if readingToken is None:
            raise TypeError("readingToken cannot be None")

        self.__logger.debug("- [ {0}: compare.".format(self))
        localValue = self.getValue(readingToken)
        tmp = readingToken.value[readingToken.index:]

        if len(tmp) >= len(localValue):
            if tmp[:len(localValue)] == localValue:
                self.__logger.debug("Comparison successful.")
                readingToken.incrementIndex(len(localValue))
                readingToken.Ok = True
            else:
                readingToken.Ok = False
                self.__logger.debug("Comparison failed: wrong value.")
        else:
            readingToken.Ok = False
            self.__logger.debug("Comparison failed: wrong size.")
        self.__logger.debug("Variable {0}: {1}. ] -".format(self.name, readingToken))

    @typeCheck(VariableWritingToken)
    def mutate(self, writingToken):
        """The current value is mutated according to the given generation strategy.


        :param writingToken: the processing token where the memory is
        :type writingToken: :class:`netzob.Common.Models.Vocabulary.Domain.Variables.VariableProcessingTokens.VariableWritingToken.VariableWritingToken`
        :raise: a TypeError if parameter is not valid
        """
        if writingToken is None:
            raise TypeError("writingToken cannot be None")

        self.__logger.debug("- {0}: mutate.".format(self))
        self.currentValue = self.dataType.mutateValue(writingToken.getGenerationStrategy(), self.getValue(writingToken))

    @typeCheck(VariableWritingToken)
    def generate(self, writingToken):
        """A new current value is generated according to the variable type and the given generation strategy.


        :param writingToken: the processing token where the memory is
        :type writingToken: :class:`netzob.Common.Models.Vocabulary.Domain.Variables.VariableProcessingTokens.VariableWritingToken.VariableWritingToken`
        :raise: a TypeError if parameter is not valid
        """
        if writingToken is None:
            raise TypeError("writingToken cannot be None")

        self.__logger.debug("- {0}: generate.".format(self))
        self.currentValue = self.dataType.generateValue(writingToken.getGenerationStrategy())

    def writeValue(self, writingToken):
        """Write the variable value if it has one, else it returns the memorized value.
                Write this value in the writingToken.
        """
        self.__logger.debug("- [ {0}: writeValue.".format(self))
        value = bitarray()
        value.extend(self.getValue(writingToken))
        if self.size[1] is None:
            # Do not forget to write the delimiter if the variable has one
            value.extend(self.dataType.getDelimiter())
        writingToken.write(self, value)
        # We impact the value this variable has written on its tokenChoppedIndex list and its fathers token list.
        self.__logger.debug("WritingToken linkedValue: {0}".format(writingToken.linkedValues))
        self.addTokenChoppedIndex(len(writingToken.linkedValues) - 1)
        self.__logger.debug("Variable {0}: {1}. ] -".format(self.name, writingToken))

    #+---------------------------------------------------------------------------+
    #| Properties                                                                |
    #+---------------------------------------------------------------------------+
    @property
    def dataType(self):
        """The type of the data.

        :type: :class:`netzob.Common.Models.Types.AbstractType.AbstractType`
        :raises: :class:`TypeError` or :class:`ValueError` if not valid.
        """
        return self.__dataType

    @dataType.setter
    @typeCheck(type)
    def dataType(self, dataType):
        if dataType is None:
            raise ValueError("dataType cannot be None")
        if not AbstractType.__subclasscheck__(dataType):
            raise ValueError("The specified type must inherit from the AbstractType class.")

        self.__dataType = dataType

    @property
    def currentValue(self):
        """The current value of the data.

        :type: :class:`object`
        """
        return self.__currentValue

    @currentValue.setter
    def currentValue(self, currentValue):
        self.__currentValue = currentValue

    @property
    def size(self):
        """The size of the data.
        size = (sizeMin, sizeMax)

        :type: a tupple of int


        >>> from netzob import *
        >>> data = Data(dataType=ASCII, originalValue="zoby", name="pseudo", size=None)

        >>> data = Data(dataType=ASCII, originalValue="zoby", name="pseudo", size=(-1, None))
        Traceback (most recent call last):
        ...
        ValueError: Minimum size must be greater than 0

        >>> data = Data(dataType=ASCII, originalValue="zoby", name="pseudo", size=(5, 2))
        Traceback (most recent call last):
        ...
        ValueError: Maximum must be greater than the minimum
        """
        return self.__size

    @size.setter
    def size(self, size):
        if size is None:
            size = (None, None)

        if isinstance(size, tuple):
            minSize, maxSize = size

            if minSize is not None and not isinstance(minSize, int):
                raise TypeError("Size must be defined with a tuple of int")
            if maxSize is not None and not isinstance(maxSize, int):
                raise TypeError("Size must be defined with a tuple of int")

            if minSize is None:
                minSize = 0

            if minSize < 0:
                raise ValueError("Minimum size must be greater than 0")
            if maxSize is not None and maxSize <= minSize:
                raise ValueError("Maximum must be greater than the minimum")

            self.__size = (minSize, maxSize)
        else:
            raise TypeError("Size must be defined by a tuple an int or with None")

        self.__size = size
