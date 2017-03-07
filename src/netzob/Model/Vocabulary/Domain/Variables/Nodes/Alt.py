#-*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|          01001110 01100101 01110100 01111010 01101111 01100010            |
#|                                                                           |
#|               Netzob : Inferring communication protocols                  |
#+---------------------------------------------------------------------------+
#| Copyright (C) 2011-2016 Georges Bossert and Frédéric Guihéry              |
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
import random

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger
from netzob.Model.Vocabulary.Domain.Variables.Nodes.AbstractVariableNode import AbstractVariableNode
from netzob.Model.Vocabulary.Domain.Parser.ParsingPath import ParsingPath
from netzob.Model.Vocabulary.Domain.Specializer.SpecializingPath import SpecializingPath

@NetzobLogger
class Alt(AbstractVariableNode):
    """Represents an Alternative (OR) in the domain definition

    To create an alternative:

    >>> from netzob.all import *
    >>> domain = Alt([Raw(), ASCII()])
    >>> print(domain.varType)
    Alt
    >>> print(domain.children[0].dataType)
    Raw=None ((0, None))
    >>> print(domain.children[1].dataType)
    ASCII=None ((0, None))

    Let's see how we can abstract an ALTERNATE

    >>> from netzob.all import *
    >>> v0 = ASCII("netzob")
    >>> v1 = ASCII("zoby")
    >>> f0 = Field(Alt([v0, v1]))
    >>> s = Symbol([f0])
    >>> msg1 = RawMessage("netzob")
    >>> mp = MessageParser()
    >>> print(mp.parseMessage(msg1, s))
    [bitarray('011011100110010101110100011110100110111101100010')]
    >>> msg2 = RawMessage("zoby")
    >>> mp = MessageParser()
    >>> print(mp.parseMessage(msg2, s))
    [bitarray('01111010011011110110001001111001')]
    >>> msg3 = RawMessage("nothing")
    >>> mp = MessageParser()
    >>> print(mp.parseMessage(msg3, s))
    Traceback (most recent call last):
      ...
    netzob.Model.Vocabulary.Domain.Parser.MessageParser.InvalidParsingPathException: No parsing path returned while parsing 'b'nothing''
    

    That's another simple example that also illustrates rollback mechanisms

    >>> from netzob.all import *
    >>> m1 = RawMessage("220044")
    >>> f1 = Field("22", name="f1")
    >>> f2 = Field(Alt(["00", "0044", "0", "004"]), name="f2")
    >>> s = Symbol([f1, f2], messages=[m1], name="S0")
    >>> print(s)
    f1   | f2    
    ---- | ------
    '22' | '0044'
    ---- | ------
    """

    def __init__(self, children=None, svas=None):
        super(Alt, self).__init__(self.__class__.__name__, children, svas=svas)

    @typeCheck(ParsingPath)
    def parse(self, parsingPath, carnivorous=False):
        """Parse the content with the definition domain of the alternate."""

        if parsingPath is None:
            raise Exception("ParsingPath cannot be None")

        if len(self.children) == 0:
            raise Exception("Cannot parse data if ALT has no children")
    
        dataToParse = parsingPath.getDataAssignedToVariable(self)
        self._logger.debug("Parse '{0}' with '{1}'".format(dataToParse, self))

        parserPaths = [parsingPath]
        parsingPath.assignDataToVariable(dataToParse.copy(), self.children[0])
        
        # create a path for each child
        if len(self.children)>1:
            for child in self.children[1:]:
                newParsingPath = parsingPath.duplicate()
                newParsingPath.assignDataToVariable(dataToParse.copy(), child)
                parserPaths.append(newParsingPath)

        # parse each child according to its definition
        for i_child, child in enumerate(self.children):
            parsingPath = parserPaths[i_child]
            self._logger.debug("ALT Parse of {0}/{1} with {2}".format(i_child+1, len(self.children), parsingPath))

            childParsingPaths = child.parse(parsingPath)
            for childParsingPath in childParsingPaths:
                if childParsingPath.ok():
                    childParsingPath.addResult(self, childParsingPath.getDataAssignedToVariable(child))
                    yield childParsingPath


    @typeCheck(SpecializingPath)        
    def specialize(self, specializingPath):
        """Specializes an Alt"""

        if specializingPath is None:
            raise Exception("SpecializingPath cannot be None")

        if len(self.children) == 0:
            raise Exception("Cannot specialize ALT if its has no children")
        
        specializingPaths = []
        
        # parse each child according to its definition
        for i_child, child in enumerate(self.children):
            newSpecializingPath = specializingPath.duplicate()
            self._logger.debug("ALT Specialize of {0}/{1} with {2}".format(i_child+1, len(self.children), newSpecializingPath))

            childSpecializingPaths = child.specialize(newSpecializingPath)
            if len(childSpecializingPaths) == 0:
                self._logger.debug("Path {0} on child {1} didn't succeed.".format(newSpecializingPath, child))
            else:
                self._logger.debug("Path {0} on child {1} succeed.".format(newSpecializingPath, child))
                for childSpecializingPath in childSpecializingPaths:
                    childSpecializingPath.addResult(self, childSpecializingPath.getDataAssignedToVariable(child))
                
                specializingPaths.extend(childSpecializingPaths)

        if len(specializingPaths) == 0:
            self._logger.debug("No children of {0} successfuly specialized".format(self))

        # lets shuffle this ( :) ) >>> by default we only consider the first valid parsing path.
        random.shuffle(specializingPaths)
        return specializingPaths

