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
from netzob.Fuzzing.Mutator import Mutator
from netzob.Common.Utils.Decorators import typeCheck


class PseudoRandomIntegerMutator(Mutator):
    """The integer mutator, using pseudo-random generator.

    >>> from netzob.all import *
    >>> mutator = PseudoRandomIntegerMutator()
    >>> mutator.seed = 10
    >>> intField = uint16le()
    >>> mutator.field = intField
    >>> dataHex = mutator.mutate()

    """

    def __init__(self, minValue=None, maxValue=None):
        super().__init__()
        self._minValue = minValue
        self._maxValue = maxValue

    @property
    def minValue(self):
        """The min value of the integer to generate. If not defined, it uses
        the field domain information.

        :type: :class:`int`
        """
        return self._minValue

    @minValue.setter
    @typeCheck(int)
    def minValue(self, minValue):
        self._minValue = minValue

    @property
    def maxValue(self):
        """The max value of the integer to generate. If not defined, it uses
        the field domain information.

        :type: :class:`int`
        """
        return self._maxValue

    @maxValue.setter
    @typeCheck(int)
    def maxValue(self, maxValue):
        self._maxValue = maxValue

    def mutate(self):
        """This is the mutation method of the integer field.
        It uses a PRNG to produce the value between minValue and maxValue.

        :return: a generated content represented with bytes
        :rtype: :class:`bytes`
        """
        # TODO : implement the PRNG
        return super().mutate()
