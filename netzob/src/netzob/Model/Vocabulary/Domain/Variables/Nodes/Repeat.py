# -*- coding: utf-8 -*-

# +---------------------------------------------------------------------------+
# |          01001110 01100101 01110100 01111010 01101111 01100010            |
# |                                                                           |
# |               Netzob : Inferring communication protocols                  |
# +---------------------------------------------------------------------------+
# | Copyright (C) 2011-2017 Georges Bossert and Frédéric Guihéry              |
# | This program is free software: you can redistribute it and/or modify      |
# | it under the terms of the GNU General Public License as published by      |
# | the Free Software Foundation, either version 3 of the License, or         |
# | (at your option) any later version.                                       |
# |                                                                           |
# | This program is distributed in the hope that it will be useful,           |
# | but WITHOUT ANY WARRANTY; without even the implied warranty of            |
# | MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the              |
# | GNU General Public License for more details.                              |
# |                                                                           |
# | You should have received a copy of the GNU General Public License         |
# | along with this program. If not, see <http://www.gnu.org/licenses/>.      |
# +---------------------------------------------------------------------------+
# | @url      : http://www.netzob.org                                         |
# | @contact  : contact@netzob.org                                            |
# | @sponsors : Amossys, http://www.amossys.fr                                |
# |             Supélec, http://www.rennes.supelec.fr/ren/rd/cidre/           |
# +---------------------------------------------------------------------------+

# +---------------------------------------------------------------------------+
# | File contributors :                                                       |
# |       - Georges Bossert <georges.bossert (a) supelec.fr>                  |
# |       - Frédéric Guihéry <frederic.guihery (a) amossys.fr>                |
# +---------------------------------------------------------------------------+

# +---------------------------------------------------------------------------+
# | Standard library imports                                                  |
# +---------------------------------------------------------------------------+
import random
from bitarray import bitarray

# +---------------------------------------------------------------------------+
# | Related third party imports                                               |
# +---------------------------------------------------------------------------+

# +---------------------------------------------------------------------------+
# | Local application imports                                                 |
# +---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger
from netzob.Model.Vocabulary.Domain.Variables.Nodes.AbstractVariableNode import AbstractVariableNode
from netzob.Model.Vocabulary.Domain.Parser.ParsingPath import ParsingPath
from netzob.Model.Vocabulary.Domain.Specializer.SpecializingPath import SpecializingPath


@NetzobLogger
class Repeat(AbstractVariableNode):
    """The Repeat class is a node variable that represents a sequence of the same variable.

    A field can be defined under a repetition form of one or multiple
    tokens with a repeat node. This denotes an n-time repetition of a
    variable, which can be a terminal leaf or a non-terminal node.

    The Repeat constructor expects some parameters:

    :param child: The variable element that will be repeated.
    :param nbRepeat: The number of repetitions of the element. This value can be a fixed integer, a tuple of integers defining the minimum and maximum of permitted repetitions, a constant from the calling script, a value present in another field, or can be identified by calling a callback function. In the latter case, the callback function should return a boolean telling if the expected number of repetitions is reached.
    :param delimiter: The delimiter used to separate the repeated element.
    :type child: :class:`AbstractVariable <netzob.Model.Vocabulary.Domain.Variables.AbstractVariable>`, required
    :type nbRepeat: a :class:`int` describing the number of
                    repetitions, or a tuple of :class:`int` describing
                    the min,max of repetitions, required
    :type delimiter: :class:`BitArray <netzob.Model.Vocabulary.Types.BitArray>`, optional
    :type eof: an :class:`int` or a :class:`tuple` of :class:`int` or
               a Python variable containing an :class:`int` or a
               :class:`AbstractField
               <netzob.Model.Vocabulary.AbstractField>` or a
               :class:`func` method, optional

    The following example shows a repeat variable where the repeated
    element is an aggregate of String characters:

    >>> from netzob.all import *
    >>> f1 = Field(Repeat(Agg([String("A"), String("B"), String("C")]), nbRepeat=16))
    >>> print(f1.specialize())
    b'ABCABCABCABCABCABCABCABCABCABCABCABCABCABCABCABC'


    **Usage of a delimiter**

    We can specify a delimiter between each repeated element, as
    depicted in the following example:

    >>> f1 = Field(Repeat(Alt([String("netzob"), String("kurt")]), nbRepeat=(1, 4),
    ...            delimiter=TypeConverter.convert(";", Raw, BitArray)))
    >>> f2 = Field(String("kurt"))
    >>> s = Symbol([f1, f2])
    >>> msg1 = RawMessage("netzob;kurt;netzobkurt")
    >>> mp = MessageParser()
    >>> print(mp.parseMessage(msg1, s))
    ... # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
    [bitarray('011011100110010101110100011110100110111101100010001110110110...,
     bitarray('01101011011101010111001001110100')]


    **Limiting the number of repetitions with an integer**

    The following examples show how to create a Repeat variable whose
    number of repetitions is limited by an integer:

    >>> f1 = Field(Repeat(String("netzob"), nbRepeat=3))


    **Limiting the number of repetitions with a interval of integers**

    The following examples show how to create a Repeat variable whose
    number of repetitions is limited by a interval of integers:

    >>> f1 = Field(Repeat(String("netzob"), nbRepeat=(2,5)))


    **Limiting the number of repetitions with a Python integer variable**

    The following examples show how to create a Repeat variable whose
    number of repetitions is limited by a Python integer
    variable. Such variable is typically managed by the calling script:

    >>> var = 3
    >>> f1 = Field(Repeat(String("netzob"), nbRepeat=var))


    **Limiting the number of repetitions with the value of another field**

    The following examples show how to create a Repeat variable whose
    number of repetitions is limited by the value of another field:

    >>> f_end = Field(Integer(interval=(2, 5)))
    >>> f1 = Field(Repeat(String("netzob"), nbRepeat=f_end))


    **Limiting the number of repetitions by calling a callback function**

    The following examples show how to create a Repeat variable whose
    number of repetitions is handled by calling a callback function
    which returns a boolean telling if the expected number of
    repetitions is reached:

    >>> def cbk(current_nb_repetitions):
    ...     if len(current_nb_repetitions) == 5:
    ...         return True
    ...     else:
    ...         return False
    >>> f1 = Field(Repeat(String("netzob"), nbRepeat=cbk))


    **Abstraction of repeat variables**

    The following examples show how repeat variable can be parsed:

    >>> from netzob.all import *
    >>> f1 = Field(Repeat(String("netzob"), nbRepeat=(0,3)))
    >>> f2 = Field(String("kurt"))
    >>> s = Symbol([f1, f2])

    >>> msg1 = RawMessage("netzobnetzobkurt")
    >>> mp = MessageParser()
    >>> print(mp.parseMessage(msg1, s))
    ... # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
    [bitarray('011011100110010101110100011110100110111101100010011011100110...,
     bitarray('01101011011101010111001001110100')]

    >>> msg2 = RawMessage("netzobkurt")
    >>> mp = MessageParser()
    >>> print(mp.parseMessage(msg2, s))  # doctest: +NORMALIZE_WHITESPACE
    [bitarray('011011100110010101110100011110100110111101100010'),
     bitarray('01101011011101010111001001110100')]

    >>> msg4 = RawMessage("kurt")
    >>> mp = MessageParser()
    >>> print(mp.parseMessage(msg4, s))
    [bitarray(), bitarray('01101011011101010111001001110100')]


    **Specialization of repeat variables**

    The following examples show how repeat variable can be specialized:

    >>> from netzob.all import *
    >>> f1 = Field(Repeat(String("netzob"), nbRepeat=2))
    >>> s = Symbol([f1])
    >>> print(s.specialize())
    b'netzobnetzob'

    >>> from netzob.all import *
    >>> f1 = Field(Repeat(IPv4(), nbRepeat=3,
    ...           delimiter=TypeConverter.convert(";", Raw, BitArray)))
    >>> s = Symbol([f1])
    >>> gen = s.specialize()
    >>> len(gen) == 14
    True
    >>> gen.count(b";") >= 2
    True

    >>> from netzob.all import *
    >>> child = Data(dataType=String(nbChars=(5)), svas=SVAS.PERSISTENT)
    >>> f1 = Field(Repeat(child, nbRepeat=3,
    ...            delimiter=TypeConverter.convert(";", Raw, BitArray)))
    >>> s = Symbol([f1])
    >>> gen = s.specialize()
    >>> gen == gen[:5]+b";"+gen[:5]+b";"+gen[:5]
    True

    """

    def __init__(self, child, nbRepeat, delimiter=None):
        super(Repeat, self).__init__(self.__class__.__name__, [child])
        self.nbRepeat = nbRepeat
        self.delimiter = delimiter

    @typeCheck(ParsingPath)
    def parse(self, parsingPath, carnivorous=False):
        """Parse the content with the definition domain of the Repeat
        """

        if parsingPath is None:
            raise Exception("Parsing path cannot be None")

        # retrieve the data to parse
        dataToParse = parsingPath.getDataAssignedToVariable(self).copy()

        # remove any data assigned to this variable
        parsingPath.removeAssignedDataToVariable(self)

        min_nb_repeat = self.nbRepeat[0] - 1
        max_nb_repeat = self.nbRepeat[1] - 1

        for nb_repeat in range(max_nb_repeat, min_nb_repeat, -1):

            # initiate a new parsing path based on the current one
            newParsingPath = parsingPath.duplicate()
            newParsingPath.assignDataToVariable(dataToParse.copy(),
                                                self.children[0])
            newParsingPaths = [newParsingPath]

            # deal with the case no repetition is accepted
            if nb_repeat == 0:
                newParsingPath.addResult(self, bitarray())
                yield newParsingPath

            # check we can apply nb_repeat times the child
            for i_repeat in range(nb_repeat):
                tmp_result = []
                for newParsingPath in newParsingPaths:
                    for childParsingPath in self.children[0].parse(
                            newParsingPath, carnivorous=carnivorous):

                        if childParsingPath.isDataAvailableForVariable(self):
                            newResult = childParsingPath.getDataAssignedToVariable(
                                self).copy()
                            newResult += childParsingPath.getDataAssignedToVariable(
                                self.children[0])
                        else:
                            newResult = childParsingPath.getDataAssignedToVariable(
                                self.children[0])

                        childParsingPath.addResult(self, newResult)
                        childParsingPath.assignDataToVariable(
                            dataToParse.copy()[len(newResult):],
                            self.children[0])

                        # apply delimiter
                        if self.delimiter is not None:
                            if i_repeat < nb_repeat - 1:
                                # check the delimiter is available
                                toParse = childParsingPath.getDataAssignedToVariable(
                                    self.children[0]).copy()
                                if toParse[:len(
                                        self.delimiter)] == self.delimiter:
                                    newResult = childParsingPath.getDataAssignedToVariable(
                                        self).copy() + self.delimiter
                                    childParsingPath.addResult(self, newResult)
                                    childParsingPath.assignDataToVariable(
                                        dataToParse.copy()[len(newResult):],
                                        self.children[0])
                                    tmp_result.append(childParsingPath)
                            else:
                                tmp_result.append(childParsingPath)

                        else:
                            tmp_result.append(childParsingPath)

                newParsingPaths = tmp_result
            for result in newParsingPaths:
                yield result

    @typeCheck(SpecializingPath)
    def specialize(self, originalSpecializingPath, fuzz=None):
        """Specializes a Repeat"""

        if originalSpecializingPath is None:
            raise Exception("Specializing path cannot be None")

        # initialy, there is a unique path to specialize (the provided one)
        specializingPaths = []

        for i_repeat in range(self.nbRepeat[0], self.nbRepeat[1]):
            newSpecializingPaths = [originalSpecializingPath.duplicate()]

            for i in range(i_repeat):
                childSpecializingPaths = []
                for newSpecializingPath in newSpecializingPaths:
                    for path in self.children[0].specialize(
                            newSpecializingPath,
                            fuzz=fuzz):
                        if path.isDataAvailableForVariable(self):
                            newResult = path.getDataAssignedToVariable(
                                self).copy()
                            if self.delimiter is not None:
                                newResult += self.delimiter
                            newResult += path.getDataAssignedToVariable(
                                self.children[0])
                        else:
                            newResult = path.getDataAssignedToVariable(
                                self.children[0])
                        path.addResult(self, newResult)
                        childSpecializingPaths.append(path)

                newSpecializingPaths = childSpecializingPaths
            specializingPaths.extend(newSpecializingPaths)

        # lets shuffle this ( :) ) >>> by default we only consider the first valid parsing path.
        random.shuffle(specializingPaths)

        return specializingPaths

    @property
    def nbRepeat(self):
        return self.__nbRepeat

    @nbRepeat.setter
    def nbRepeat(self, nbRepeat):
        if nbRepeat is None:
            raise Exception("NB Repeat cannot be None")
        MAX_REPEAT = 1000

        if isinstance(nbRepeat, int):
            nbRepeat = (nbRepeat, nbRepeat + 1)

        if isinstance(nbRepeat, tuple):
            minNbRepeat, maxNbRepeat = nbRepeat

            if minNbRepeat is not None and not isinstance(minNbRepeat, int):
                raise TypeError("NbRepeat must be defined with a tuple of int")
            if maxNbRepeat is not None and not isinstance(maxNbRepeat, int):
                raise TypeError("NbRepeat must be defined with a tuple of int")

            if minNbRepeat is None:
                minNbRepeat = 0

            if minNbRepeat < 0:
                raise ValueError("Minimum nbRepeat must be greater than 0")
            if maxNbRepeat is not None and maxNbRepeat < minNbRepeat:
                raise ValueError(
                    "Maximum must be greater or equals to the minimum")
            if maxNbRepeat is not None and maxNbRepeat > MAX_REPEAT:
                raise ValueError(
                    "Maximum nbRepeat supported for a variable is {0}.".format(
                        MAX_REPEAT))

        self.__nbRepeat = (minNbRepeat, maxNbRepeat)

    @property
    def delimiter(self):
        return self.__delimiter

    @delimiter.setter
    @typeCheck(bitarray)
    def delimiter(self, delimiter):
        self.__delimiter = delimiter
