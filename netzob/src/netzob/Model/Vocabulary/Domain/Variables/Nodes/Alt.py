#-*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|          01001110 01100101 01110100 01111010 01101111 01100010            |
#|                                                                           |
#|               Netzob : Inferring communication protocols                  |
#+---------------------------------------------------------------------------+
#| Copyright (C) 2011-2017 Georges Bossert and Frédéric Guihéry              |
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
    """The Alt class is a node variable that represents an alternative of variables.

    A definition domain can take the form of a combination of
    permitted values/types/domains. This combination is represented by
    an alternate node. It can be seen as an OR operator between two or
    more children nodes.

    The Alt constructor expects some parameters:

    :param children: The set of variable elements permitted in the
                     alternative.
    :param svas: The SVAS strategy defining how the Alternate
                     behaves during abstraction and specialization.
    :type children: a :class:`list` of :class:`AbstractVariable <netzob.Model.Vocabulary.Domain.Variables.AbstractVariable>`, optional
    :type svas: :class:`str`, optional


    For example, the following code denotes a field accepts either
    "filename1.txt" or "filename2.txt":

    >>> from netzob.all import *
    >>> t1 = String("filename1.txt")
    >>> t2 = String("filename2.txt")
    >>> f = Field(Alt([t1, t2]))


    **Examples of Alt internal attribute access**

    >>> domain = Alt([Raw(), String()])
    >>> print(domain.varType)
    Alt
    >>> print(domain.children[0].dataType)
    Raw=None ((0, 524288))
    >>> print(domain.children[1].dataType)
    String=None ((None, None))


    **Abstraction of alternate variables**

    This example shows the abstraction process of an Alternate
    variable:

    >>> from netzob.all import *
    >>> v0 = String("john")
    >>> v1 = String("kurt")
    >>> f0 = Field(Alt([v0, v1]), name='f0')
    >>> s = Symbol([f0])
    >>> data = "john"
    >>> Symbol.abstract(data, [s])
    (Symbol, OrderedDict([('f0', b'john')]))
    >>> data = "kurt"
    >>> Symbol.abstract(data, [s])
    (Symbol, OrderedDict([('f0', b'kurt')]))

    In the following example, an Alternate variable is defined. A
    message that does not correspond to the expected model is then
    parsed, thus the returned symbol is unknown:

    >>> data = "nothing"
    >>> Symbol.abstract(data, [s])
    (Unknown Symbol 'nothing', OrderedDict())

    That is another simple example that also illustrates rollback mechanisms

    >>> from netzob.all import *
    >>> m1 = RawMessage("220044")
    >>> f1 = Field("22", name="f1")
    >>> f2 = Field(Alt(["00", "0044", "0", "004"]), name="f2")
    >>> s = Symbol([f1, f2], messages=[m1], name="S0")
    >>> print(s.str_data())
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
        self._logger.debug("Parse '{}' with '{}'".format(dataToParse.tobytes(), self))

        parserPaths = [parsingPath]
        parsingPath.assignDataToVariable(dataToParse.copy(), self.children[0])

        # create a path for each child
        if len(self.children) > 1:
            for child in self.children[1:]:
                newParsingPath = parsingPath.duplicate()
                newParsingPath.assignDataToVariable(dataToParse.copy(), child)
                parserPaths.append(newParsingPath)

        # parse each child according to its definition
        for i_child, child in enumerate(self.children):
            parsingPath = parserPaths[i_child]
            self._logger.debug("ALT Parse of {0}/{1} with {2}".format(
                i_child + 1, len(self.children), parsingPath))

            childParsingPaths = child.parse(parsingPath)
            for childParsingPath in childParsingPaths:
                childParsingPath.addResult(
                    self,
                    childParsingPath.getDataAssignedToVariable(child))
                yield childParsingPath

    @typeCheck(SpecializingPath)
    def specialize(self, specializingPath, fuzz=None):
        """Specializes an Alt"""

        if specializingPath is None:
            raise Exception("SpecializingPath cannot be None")

        if len(self.children) == 0:
            raise Exception("Cannot specialize ALT if its has no children")

        specializingPaths = []

        # If we are in a fuzzing mode
        if fuzz is not None and fuzz.get(self) is not None:

            # Retrieve the mutator
            mutator = fuzz.get(self)

            # Chose the child according to the integer returned by the mutator
            generated_value = mutator.generate()

            if 0 <= generated_value < len(self.children):
                child = self.children[generated_value]
            else:
                raise ValueError("Field position '{}' is bigger than the length of available children '{}'"
                                 .format(generated_value, len(self.children)))

        # Else, randomly chose the child
        else:
            child = random.choice(self.children)

        newSpecializingPath = specializingPath.duplicate()

        childSpecializingPaths = child.specialize(newSpecializingPath, fuzz=fuzz)
        if len(childSpecializingPaths) == 0:
            self._logger.debug("Path {0} on child {1} didn't succeed.".
                               format(newSpecializingPath, child))
        else:
            self._logger.debug("Path {} on child {} succeed ({}).".format(
                newSpecializingPath, child, self.id))
            for childSpecializingPath in childSpecializingPaths:
                value = childSpecializingPath.getDataAssignedToVariable(child)
                self._logger.debug("Generated value for {}: {} ({})".format(self, value, self.id))
                childSpecializingPath.addResult(self, value)

            specializingPaths.extend(childSpecializingPaths)

        if len(specializingPaths) == 0:
            self._logger.debug(
                "No children of {0} successfuly specialized".format(self))

        # lets shuffle this ( :) ) >>> by default we only consider the first valid parsing path.
        random.shuffle(specializingPaths)
        return specializingPaths
