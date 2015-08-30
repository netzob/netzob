# -*- coding: utf-8 -*-

# +---------------------------------------------------------------------------+
# |          01001110 01100101 01110100 01111010 01101111 01100010            |
# |                                                                           |
# |               Netzob : Inferring communication protocols                  |
# +---------------------------------------------------------------------------+
# | Copyright (C) 2011-2014 Georges Bossert and Frédéric Guihéry              |
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
from netzob.Common.Models.Vocabulary.Domain.Variables.Nodes.AbstractVariableNode import AbstractVariableNode
from netzob.Common.Models.Vocabulary.Domain.Parser.ParsingPath import ParsingPath
from netzob.Common.Models.Vocabulary.Domain.Specializer.SpecializingPath import SpecializingPath


@NetzobLogger
class Repeat(AbstractVariableNode):
    """Represents a Repeat in the domain definition


    Let's see how a repeat domain can be parsed

    >>> from netzob.all import *
    >>> f1 = Field(Repeat(ASCII("netzob"), nbRepeat=(1, 4)))
    >>> f2 = Field(ASCII("zoby"))
    >>> s = Symbol([f1, f2])
    >>> msg1 = RawMessage("netzobnetzobzoby")
    >>> mp = MessageParser()
    >>> print mp.parseMessage(msg1, s)
    [bitarray('011011100110010101110100011110100110111101100010011011100110010101110100011110100110111101100010'), bitarray('01111010011011110110001001111001')]

    You can also specify a delimitor between each repeated element

    >>> from netzob.all import *
    >>> f1 = Field(Repeat(Alt([ASCII("netzob"), ASCII("zoby")]), nbRepeat=(1, 4), delimitor=TypeConverter.convert(";", Raw, BitArray)))
    >>> f2 = Field(ASCII("zoby"))
    >>> s = Symbol([f1, f2])
    >>> msg1 = RawMessage("netzob;zoby;netzobzoby")
    >>> mp = MessageParser()
    >>> print mp.parseMessage(msg1, s)
    [bitarray('011011100110010101110100011110100110111101100010001110110111101001101111011000100111100100111011011011100110010101110100011110100110111101100010'), bitarray('01111010011011110110001001111001')]


    Let's illustrate the specialization of a repeat:

    >>> from netzob.all import *
    >>> f1 = Field(Repeat(ASCII("netzob"), nbRepeat=2))
    >>> s = Symbol([f1])
    >>> print s.specialize()
    netzobnetzob

    >>> from netzob.all import *
    >>> f1 = Field(Repeat(IPv4(), nbRepeat=3, delimitor=TypeConverter.convert(";", Raw, BitArray)))
    >>> s = Symbol([f1])
    >>> gen = s.specialize()
    >>> len(gen) == 14
    True
    >>> gen.count(";") >= 2
    True

    >>> from netzob.all import *
    >>> child = Data(dataType=ASCII(nbChars=(5)), svas=SVAS.PERSISTENT)
    >>> f1 = Field(Repeat(child, nbRepeat=3, delimitor=TypeConverter.convert(";", Raw, BitArray)))
    >>> s = Symbol([f1])
    >>> gen = s.specialize()
    >>> gen == gen[:5]+";"+gen[:5]+";"+gen[:5]
    True

    """

    def __init__(self, child, nbRepeat, delimitor=None):
        super(Repeat, self).__init__(self.__class__.__name__, [child])
        self.nbRepeat = nbRepeat
        self.delimitor = delimitor

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

        self._logger.debug("Parse '{0}' as {1} with parser path '{2}'".format(dataToParse, self, parsingPath))

        results = []
        # we try to parse according to the various different number of repetitions
        for i_repeat in xrange(self.nbRepeat[0], self.nbRepeat[1]):

            newParsingPaths = [parsingPath.duplicate()]
            newParsingPaths[0].assignDataToVariable(dataToParse.copy(), self.children[0])

            for i in xrange(i_repeat):
                tmp_result = []
                for newParsingPath in newParsingPaths:
                    childParsingPaths = self.children[0].parse(newParsingPath, carnivorous=carnivorous)
                    for childParsingPath in childParsingPaths:
                        if childParsingPath.isDataAvailableForVariable(self):
                            newResult = childParsingPath.getDataAssignedToVariable(self).copy()
                            newResult += childParsingPath.getDataAssignedToVariable(self.children[0])
                        else:
                            newResult = childParsingPath.getDataAssignedToVariable(self.children[0])

                        childParsingPath.addResult(self, newResult)
                        childParsingPath.assignDataToVariable(dataToParse.copy()[len(newResult):], self.children[0])

                        if self.delimitor is not None:
                            if i < i_repeat - 1:
                                # check the delimitor is available
                                toParse = childParsingPath.getDataAssignedToVariable(self.children[0]).copy()
                                if toParse[:len(self.delimitor)] == self.delimitor:
                                    newResult = childParsingPath.getDataAssignedToVariable(self).copy() + self.delimitor
                                    childParsingPath.addResult(self, newResult)
                                    childParsingPath.assignDataToVariable(dataToParse.copy()[len(newResult):], self.children[0])
                                    tmp_result.append(childParsingPath)
                            else:
                                tmp_result.append(childParsingPath)

                        else:
                            tmp_result.append(childParsingPath)
                newParsingPaths = tmp_result

            for newParsingPath in newParsingPaths:
                results.append(newParsingPath)

        return results

    @typeCheck(SpecializingPath)
    def specialize(self, originalSpecializingPath):
        """Specializes a Repeat"""

        if originalSpecializingPath is None:
            raise Exception("Specializing path cannot be None")

        # initialy, there is a unique path to specialize (the provided one)
        specializingPaths = []
    
        for i_repeat in xrange(self.nbRepeat[0], self.nbRepeat[1]):
            newSpecializingPaths = [originalSpecializingPath.duplicate()]

            for i in xrange(i_repeat):
                childSpecializingPaths = []
                for newSpecializingPath in newSpecializingPaths:
                    for path in self.children[0].specialize(newSpecializingPath):
                        if path.isDataAvailableForVariable(self):
                            newResult = path.getDataAssignedToVariable(self).copy()
                            if self.delimitor is not None:
                                newResult += self.delimitor
                            newResult += path.getDataAssignedToVariable(self.children[0])
                        else:
                            newResult = path.getDataAssignedToVariable(self.children[0])
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
                raise ValueError("Maximum must be greater or equals to the minimum")
            if maxNbRepeat is not None and maxNbRepeat > MAX_REPEAT:
                raise ValueError("Maximum nbRepeat supported for a variable is {0}.".format(MAX_REPEAT))

        self.__nbRepeat = (minNbRepeat, maxNbRepeat)

    @property
    def delimitor(self):
        return self.__delimitor

    @delimitor.setter
    @typeCheck(bitarray)
    def delimitor(self, delimitor):
        self.__delimitor = delimitor
