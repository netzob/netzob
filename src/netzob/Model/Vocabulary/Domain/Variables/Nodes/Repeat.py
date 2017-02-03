# -*- coding: utf-8 -*-

# +---------------------------------------------------------------------------+
# |          01001110 01100101 01110100 01111010 01101111 01100010            |
# |                                                                           |
# |               Netzob : Inferring communication protocols                  |
# +---------------------------------------------------------------------------+
# | Copyright (C) 2011-2016 Georges Bossert and Frédéric Guihéry              |
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
    """Represents a Repeat in the domain definition


    Let's see how a repeat domain can be parsed

    >>> from netzob.all import *
    >>> f1 = Field(Repeat(ASCII("netzob"), nbRepeat=(0,3)))
    >>> f2 = Field(ASCII("zoby"))
    >>> s = Symbol([f1, f2])

    >>> msg1 = RawMessage("netzobnetzobzoby")
    >>> mp = MessageParser()
    >>> print(mp.parseMessage(msg1, s))
    [bitarray('011011100110010101110100011110100110111101100010011011100110010101110100011110100110111101100010'), bitarray('01111010011011110110001001111001')]

    >>> msg2 = RawMessage("netzobzoby")
    >>> mp = MessageParser()
    >>> print(mp.parseMessage(msg2, s))
    [bitarray('011011100110010101110100011110100110111101100010'), bitarray('01111010011011110110001001111001')]

    >>> msg4 = RawMessage("zoby")
    >>> mp = MessageParser()
    >>> print(mp.parseMessage(msg4, s))
    [bitarray(), bitarray('01111010011011110110001001111001')]
    

    You can also specify a delimitor between each repeated element

    >>> from netzob.all import *
    >>> f1 = Field(Repeat(Alt([ASCII("netzob"), ASCII("zoby")]), nbRepeat=(1, 4), delimitor=TypeConverter.convert(";", Raw, BitArray)))
    >>> f2 = Field(ASCII("zoby"))
    >>> s = Symbol([f1, f2])
    >>> msg1 = RawMessage("netzob;zoby;netzobzoby")
    >>> mp = MessageParser()
    >>> print(mp.parseMessage(msg1, s))
    [bitarray('011011100110010101110100011110100110111101100010001110110111101001101111011000100111100100111011011011100110010101110100011110100110111101100010'), bitarray('01111010011011110110001001111001')]


    Let's illustrate the specialization of a repeat:

    >>> from netzob.all import *
    >>> f1 = Field(Repeat(ASCII("netzob"), nbRepeat=2))
    >>> s = Symbol([f1])
    >>> print(s.specialize())
    b'netzobnetzob'

    >>> from netzob.all import *
    >>> f1 = Field(Repeat(IPv4(), nbRepeat=3, delimitor=TypeConverter.convert(";", Raw, BitArray)))
    >>> s = Symbol([f1])
    >>> gen = s.specialize()
    >>> len(gen) == 14
    True
    >>> gen.count(b";") >= 2
    True

    >>> from netzob.all import *
    >>> child = Data(dataType=ASCII(nbChars=(5)), svas=SVAS.PERSISTENT)
    >>> f1 = Field(Repeat(child, nbRepeat=3, delimitor=TypeConverter.convert(";", Raw, BitArray)))
    >>> s = Symbol([f1])
    >>> gen = s.specialize()
    >>> gen == gen[:5]+b";"+gen[:5]+b";"+gen[:5]
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

        min_nb_repeat = self.nbRepeat[0]-1
        max_nb_repeat = self.nbRepeat[1]-1
        
        for nb_repeat in range(max_nb_repeat, min_nb_repeat, -1):
            
            # initiate a new parsing path based on the current one
            newParsingPath = parsingPath.duplicate()
            newParsingPath.assignDataToVariable(dataToParse.copy(), self.children[0])            
            newParsingPaths = [newParsingPath]

            # deal with the case no repetition is accepted
            if nb_repeat == 0:
                newParsingPath.addResult(self, bitarray())
                yield newParsingPath

            # check we can apply nb_repeat times the child
            for i_repeat in range(nb_repeat):
                tmp_result = []
                for newParsingPath in newParsingPaths:
                    for childParsingPath in self.children[0].parse(newParsingPath, carnivorous=carnivorous):
                        
                        if childParsingPath.isDataAvailableForVariable(self):
                            newResult = childParsingPath.getDataAssignedToVariable(self).copy()
                            newResult += childParsingPath.getDataAssignedToVariable(self.children[0])
                        else:
                            newResult = childParsingPath.getDataAssignedToVariable(self.children[0])


                        childParsingPath.addResult(self, newResult)
                        childParsingPath.assignDataToVariable(dataToParse.copy()[len(newResult):], self.children[0])

                        # apply delimitor
                        if self.delimitor is not None:
                            if i_repeat < nb_repeat - 1:
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
            for result in newParsingPaths:
                yield result

    @typeCheck(SpecializingPath)
    def specialize(self, originalSpecializingPath):
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

