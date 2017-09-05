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
    """The Agg class is a node variable that represents a concatenation of variables.

    An Aggregate node concatenates the values that are accepted by
    its children nodes. It can be used to specify a succession of
    tokens.

    The Agg constructor expects some parameters:

    :param children: The sequence of variable elements contained in
                     the aggregate.
    :param svas: The SVAS strategy defining how the Aggregate
                 behaves during abstraction and specialization. The default strategy is SVAS.EPHEMERAL.
    :type children: a :class:`list` of :class:`AbstractVariable <netzob.Model.Vocabulary.Domain.Variables.AbstractVariable>`, optional
    :type svas: :class:`SVAS <netzob.Model.Vocabulary.Domain.Variables.SVAS.SVAS>`, optional


    For example, the following code represents a field that
    accepts values that are made of a String of 3 to 20 random
    characters followed by a ".txt" extension:

    >>> from netzob.all import *
    >>> t1 = String(nbChars=(3,20))
    >>> t2 = String(".txt")
    >>> f = Field(Agg([t1, t2]))

    The following example shows an aggregate between BitArray
    variables:

    >>> from netzob.all import *
    >>> from bitarray import bitarray
    >>> f0 = Field(Agg([BitArray('01101001'), BitArray(nbBits=3), BitArray(nbBits=5)]))
    >>> s = Symbol(fields=[f0])
    >>> t = s.specialize()
    >>> len(t)
    2


    **Examples of Agg internal attribute access**

    >>> domain = Agg([Raw(), String()])
    >>> domain.varType
    'Agg'
    >>> print(domain.children[0].dataType)
    Raw=None ((0, 524288))
    >>> print(domain.children[1].dataType)
    String=None ((None, None))
    >>> domain.children.append(Agg([10, 20, 30]))
    >>> len(domain.children)
    3
    >>> domain.children.remove(domain.children[0])
    >>> len(domain.children)
    2


    **Abstraction of aggregate variables**

    This example shows the abstraction process of an Aggregate
    variable:

    >>> from netzob.all import *
    >>> v1 = String(nbChars=(1, 10))
    >>> v2 = String(".txt")
    >>> f0 = Field(Agg([v1, v2]), name="f0")
    >>> f1 = Field(String("!"), name="f1")
    >>> s = Symbol([f0, f1])
    >>> data = "john.txt!"
    >>> Symbol.abstract(data, [s])
    (Symbol, OrderedDict([('f0', b'john.txt'), ('f1', b'!')]))

    In the following example, an Aggregate variable is defined. A
    message that does not correspond to the expected model is then
    parsed, thus the returned symbol is unknown:

    >>> data = "johntxt!"
    >>> Symbol.abstract(data, [s])
    (Unknown Symbol 'johntxt!', OrderedDict())


    **Specialization of aggregate variables**

    This example shows the specialization process of an Aggregate
    variable:

    >>> from netzob.all import *
    >>> d1 = String("hello")
    >>> d2 = String(" john")
    >>> f = Field(Agg([d1, d2]))
    >>> s = Symbol(fields=[f])
    >>> s.specialize()
    b'hello john'

    """

    def __init__(self, children=None, svas=None):
        super(Agg, self).__init__(self.__class__.__name__, children, svas=svas)

    @typeCheck(ParsingPath)
    def parse(self, parsingPath, carnivorous=False):
        """Parse the content with the definition domain of the aggregate.
        """
        dataToParse = parsingPath.getData(self).copy()
        self._logger.debug("Parse '{}' as {} with parser path '{}'".format(
            dataToParse.tobytes(), self, parsingPath))

        # initialy, there is a unique path to test (the provided one)
        parsingPath.assignData(dataToParse.copy(), self.children[0])
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
                self._logger.debug(
                    "Parse {0} with {1}".format(current_child.id, parsingPath))
                value_before_parsing = parsingPath.getData(
                    current_child).copy()
                childParsingPaths = current_child.parse(
                    parsingPath, carnivorous=carnivorous)

                for childParsingPath in childParsingPaths:
                    value_after_parsing = childParsingPath.getData(
                        current_child).copy()
                    remainingValue = value_before_parsing[len(
                        value_after_parsing):].copy()
                    if next_child is not None:
                        childParsingPath.assignData(
                            remainingValue, next_child)

                    # at least one child path managed to parse, we save the valid paths it produced
                    self._logger.debug(
                        "Children {0} succesfuly applied with the parsingPath {1}".
                        format(current_child, parsingPath))
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
                    parsedData = parsingPath.getData(
                        child).copy()
                else:
                    parsedData = parsedData + parsingPath.getData(
                        child).copy()

            self._logger.debug("Data successfuly parsed with {}: '{}'".format(self, parsedData.tobytes()))
            parsingPath.addResult(self, parsedData)
        return parsingPaths

    @typeCheck(SpecializingPath)
    def specialize(self, originalSpecializingPath, fuzz=None):
        """Specializes an Agg"""

        # initialy, there is a unique path to specialize (the provided one)
        specializingPaths = [originalSpecializingPath]

        # we parse all the children with the specializerPaths produced by previous children
        for child in self.children:
            newSpecializingPaths = []

            self._logger.debug("Specializing AGG child with {0} paths".format(len(specializingPaths)))

            for specializingPath in specializingPaths:
                self._logger.debug("Specialize {0} with {1}".format(child, specializingPath))

                childSpecializingPaths = child.specialize(specializingPath, fuzz=fuzz)

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
                    value = specializingPath.getData(child)
                else:
                    value = value + specializingPath.getData(child)

            self._logger.debug("Generated value for {}: {}".format(self, value))
            specializingPath.addResult(self, value)

        # ok we managed to parse all the children, and it produced some valid specializer paths. We return them
        return specializingPaths
