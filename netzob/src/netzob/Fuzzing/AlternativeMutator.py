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
# |             ANSSI,   https://www.ssi.gouv.fr                              |
# +---------------------------------------------------------------------------+

# +---------------------------------------------------------------------------+
# | File contributors :                                                       |
# |       - Frédéric Guihéry <frederic.guihery (a) amossys.fr>                |
# |       - Rémy Delion <remy.delion (a) amossys.fr>                          |
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
from netzob.Fuzzing.Mutator import Mutator
from netzob.Common.Utils.Decorators import typeCheck
from netzob.Model.Vocabulary.Types.AbstractType import AbstractType


class RecursivityMutatorError(Exception):
    pass


class AlternativeMutator(Mutator):
    """The alternative mutator.

    >>> from netzob.all import *
    >>> altField = Field(name="Integer or container of Integer")
    >>> altField.domain = Alt( [Integer(1234),
    >>>                         Ref(altField.domain)] )
    >>> mutator = AlternativeMutator()
    >>> mutator.seed = 10
    >>> mutator.field = altField
    >>> dataHex = mutator.mutate()

    """

    DEFAULT_MAX_DEPTH = 10

    def __init__(self):
        self._maxDepth = AlternativeMutator.DEFAULT_MAX_DEPTH
        self._typesMutators = {}

    @property
    def typesMutators(self):
        """The list of mutators corresponding to types of fields.

        :type: :class:`dict`
        """
        return self._typesMutators

    @typeCheck(AbstractType, Mutator)
    def setTypeMutator(self, domain, mutator):
        """Associate a mutator to the given type (domain) of field.

        :parameter domain: the type of the field
        :type domain: :class:`AbstractType <netzob.Model.Vocabulary.Types.AbstractType>`

        :parameter mutator: the mutator to use with the given domain
        :type mutator: :class:`Mutator <netzob.Fuzzing.Mutator>`
        """
        self._typesMutators[domain] = mutator

    @property
    def maxDepth(self):
        """The depth limit when recursivity occurs.

        :type: :class:`int`
        """
        return self._maxDepth

    @maxDepth.setter
    @typeCheck(int)
    def maxDepth(self, depth):
        self._maxDepth = depth

    def generate(self):
        """This is the fuzz generation method of the alternative field.
        For each type, we produce the value with the associated mutator
        from typesMutators.
        If no mutator is set, the default value of the type is used.
        If the mutation encounters recursivity, infinite loop is avoided by
        controlling the number of iterations with maxDepth.
        If it exceeds maxDepth, a RecursivityMutatorError is raised.

        :return: a generated content represented with bytes
        :rtype: :class:`bytes`
        :raises: :class:`RecursivityMutatorError <netzob.Fuzzing.AlternativeMutator.RecursivityMutatorError>`
        """
        depth = 0
        if depth > self._maxDepth:
            raise RecursivityMutatorError(
                "{}.mutate() : max depth reached".format(self._type()))

        # TODO : implement the sequence generator, which uses generatedLength
        return super().generate()
