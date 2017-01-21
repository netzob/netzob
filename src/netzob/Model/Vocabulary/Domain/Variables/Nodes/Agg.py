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
class Agg(AbstractVariableNode):
    """Represents an Aggregate (AND) in the domain definition

    To create an aggregate:

    >>> from netzob.all import *
    >>> domain = Agg([Raw(), ASCII()])
    >>> print(domain.varType)
    Agg
    >>> print(domain.children[0].dataType)
    Raw=None ((0, None))
    >>> print(domain.children[1].dataType)
    ASCII=None ((0, None))
    >>> domain.children.append(Agg([10, 20, 30]))
    >>> print(len(domain.children))
    3
    >>> domain.children.remove(domain.children[0])
    >>> print(len(domain.children))
    2

    Another example of an aggregate

    >>> from netzob.all import *
    >>> from bitarray import bitarray
    >>> f0 = Field(Agg([BitArray(bitarray('01101001')), BitArray(nbBits=3), BitArray(nbBits=5)]))
    >>> s = Symbol(fields=[f0])
    >>> t = s.specialize()
    >>> print(len(t))
    2

    Let's see the abstraction process of an AGGREGATE

    >>> from netzob.all import *
    >>> v1 = ASCII(nbChars=(1, 10))
    >>> v2 = ASCII(".txt")
    >>> f0 = Field(Agg([v1, v2]), name="f0")
    >>> f1 = Field(ASCII("!"))
    >>> s = Symbol([f0, f1])
    >>> msg1 = RawMessage("netzob.txt!")
    >>> mp = MessageParser()
    >>> print(mp.parseMessage(msg1, s))
    [bitarray('01101110011001010111010001111010011011110110001000101110011101000111100001110100'), bitarray('00100001')]

    >>> msg2 = RawMessage("netzobtxt!")
    >>> mp = MessageParser()
    >>> print(mp.parseMessage(msg2, s))
    Traceback (most recent call last):
      ...
    netzob.Model.Vocabulary.Domain.Parser.MessageParser.InvalidParsingPathException: No parsing path returned while parsing 'b'netzobtxt!''


    Let's see the specializing process of an AGGREGATE

    >>> from netzob.all import *
    >>> d1 = ASCII("hello")
    >>> d2 = ASCII(" netzob")
    >>> f = Field(Agg([d1, d2]))
    >>> s = Symbol(fields=[f])
    >>> print(s.specialize())
    b'hello netzob'

    """

    def __init__(self, children=None, svas=None):
        super(Agg, self).__init__(self.__class__.__name__, children, svas=svas)

    @typeCheck(ParsingPath)
    def parse(self, parsingPath, carnivorous=False):
        """Parse the content with the definition domain of the aggregate.
        """
        dataToParse = parsingPath.getDataAssignedToVariable(self).copy()
        self._logger.debug("Parse '{0}' as {1} with parser path '{2}'".format(dataToParse, self, parsingPath))

        # initialy, there is a unique path to test (the provided one)
        parsingPath.assignDataToVariable(dataToParse.copy(), self.children[0])
        parsingPaths = [parsingPath]

        # we parse all the children with the parserPaths produced by previous children
        for i_child in range(len(self.children)):
            current_child = self.children[i_child]
            if i_child < len(self.children) - 1:
                next_child = self.children[i_child + 1]
            else:
                next_child = None

            newParsingPaths = []

            for parsingPath in parsingPaths:
                self._logger.debug("Parse {0} with {1}".format(current_child.id, parsingPath))
                value_before_parsing = parsingPath.getDataAssignedToVariable(current_child).copy()
                childParsingPaths = current_child.parse(parsingPath, carnivorous=carnivorous)

                for childParsingPath in childParsingPaths:
                    if childParsingPath.ok():
                        value_after_parsing = childParsingPath.getDataAssignedToVariable(current_child).copy()
                        remainingValue = value_before_parsing[len(value_after_parsing):].copy()
                        if next_child is not None:
                            childParsingPath.assignDataToVariable(remainingValue, next_child)

                        # at least one child path managed to parse, we save the valid paths it produced
                        self._logger.debug("Children {0} succesfuly applied with the parsingPath {1}".format(current_child, parsingPath))
                        newParsingPaths.append(childParsingPath)

            parsingPaths = newParsingPaths

            if len(parsingPaths) == 0:
                self._logger.debug("Children {0} didn't apply to any of the parser path we have, we stop Agg parser".format(current_child))
                return []  # return no valid paths

        # ok we managed to parse all the children, and it produced some valid parser paths. We return them
        for parsingPath in parsingPaths:
            parsedData = None
            for child in self.children:
                if parsedData is None:
                    parsedData = parsingPath.getDataAssignedToVariable(child).copy()
                else:
                    parsedData += parsingPath.getDataAssignedToVariable(child).copy()

            parsingPath.addResult(self, parsedData)
        return parsingPaths

    @typeCheck(SpecializingPath)
    def specialize(self, originalSpecializingPath):
        """Specializes an Agg"""

        # initialy, there is a unique path to specialize (the provided one)
        specializingPaths = [originalSpecializingPath]

        # we parse all the children with the specializerPaths produced by previous children
        for child in self.children:
            newSpecializingPaths = []

            self._logger.debug("Specializing AGG child with {0} paths".format(len(specializingPaths)))

            for specializingPath in specializingPaths:
                self._logger.debug("Spcialize {0} with {1}".format(child, specializingPath))

                childSpecializingPaths = child.specialize(specializingPath)

                if len(childSpecializingPaths) > 0:
                    # at least one child path managed to specialize, we save the valid paths it produced
                    for childSpecializingPath in childSpecializingPaths:
                        newSpecializingPaths.append(childSpecializingPath)

            specializingPaths = newSpecializingPaths

        self._logger.debug("Specializing AGG child has produced {0} paths".format(len(specializingPaths)))

        if len(specializingPaths) == 0:
            self._logger.debug("Children {0} didn't apply to any of the specializer path we have, we stop Agg specializer".format(child))
            return []  # return no valid paths

        for specializingPath in specializingPaths:
            value = None
            for child in self.children:
                if value is None:
                    value = specializingPath.getDataAssignedToVariable(child)
                else:
                    value += specializingPath.getDataAssignedToVariable(child)

            specializingPath.addResult(self, value)

        # ok we managed to parse all the children, and it produced some valid specializer paths. We return them
        return specializingPaths

