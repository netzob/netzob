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
from netzob.Fuzzing.Generator import Generator


class DeterministGenerator(Generator):
    """Generates integer values from a list determined with the size of an
    Integer field.

    >>> from netzob.all import *
    >>> seed = 14
    >>> g = DeterministGenerator(seed, minValue=0, maxValue=255, bitsize=8)
    >>> next(g)
    255
    >>> next(g)
    254
    >>> next(g)
    253
    """

    name = "determinist"

    def __init__(self,
                 seed,
                 minValue,
                 maxValue,
                 bitsize,
                 signed=False):

        # Call parent init
        super().__init__(seed=seed)

        # Initialize other variables
        self._currentPos = 0
        self._values = []

        self.minValue = minValue
        self.maxValue = maxValue
        self.bitsize = bitsize

        # Initialize deterministic values
        self._createValues(signed)

    def __iter__(self):
        """Iterate over generated values

        :return: a generated int value iterator
        :rtype: :class:`int` iterator
        :raise: ValueError if values is empty

        """
        while True:
            if len(self._values) == 0:
                raise ValueError("Value list is empty.")

            self._currentPos %= len(self._values)

            value = self._values[self._currentPos]
            self._currentPos += 1
            yield value

    def get_state(self):
        # type: () -> int
        """
        Return an integer representing the internal state of the generator.

        >>> gen = DeterministGenerator(minValue=0, maxValue=100, seed=1, bitsize=8)
        >>> gen.get_state()  # before consuming generator
        0
        >>> next(gen)
        255
        >>> gen.get_state()  # after consuming generator
        1
        """
        return self._currentPos

    def set_state(self, state):
        # type: (int) -> None
        """
        Set the internal state of the generator from an integer.

        >>> gen = DeterministGenerator(minValue=0, maxValue=100, seed=1, bitsize=8)
        >>> next(gen) # blank shot
        255
        >>> state = gen.get_state()
        >>> next(gen); next(gen)
        254
        253
        >>> gen.set_state(state)
        >>> next(gen); next(gen)
        254
        253
        """
        self._currentPos = state

    def _createValues(self, signed):
        self._currentPos = 0
        signedShift = 0

        if not signed:
            # on 8 bits : -1 = 0b11111111 = 255 = -1 + 2^8
            signedShift = 2**self.bitsize

        self._values = list()
        self._values.append(self.maxValue)  # Q
        self._values.append(self.minValue)  # P
        if (self.minValue - 1) & ((2**self.bitsize) - 1) == self.minValue - 1:
            self._values.append(self.minValue - 1)  # P-1
        self._values.append(self.maxValue - 1)  # Q-1
        self._values.append(self.minValue + 1)  # P+1
        if signed:
            if (self.maxValue + 1) & (2**(self.bitsize - 1) - 1) == self.maxValue + 1:
                self._values.append(self.maxValue + 1)  # Q+1
        else:
            if (self.maxValue + 1) & ((2**self.bitsize) - 1) == self.maxValue + 1:
                self._values.append(self.maxValue + 1)  # Q+1
        self._values.append(0)  # 0
        self._values.append(-1 + signedShift)  # -1
        self._values.append(1)  # 1

        self._values.append(-1 + signedShift)  # -2^0 = -1
        self._values.append(-2 + signedShift)  # -2^0 - 1 = -2
        self._values.append(0)  # -2^0 + 1 = 0
        self._values.append(1)  # 2^0 = 1
        self._values.append(0)  # 2^0 - 1 = 0
        self._values.append(2)  # 2^0 + 1 = 2
        for k in range(1, self.bitsize - 2):  # k in [0..N-2]
            self._values.append(-2**k + signedShift)  # -2^k
            self._values.append(-2**k - 1 + signedShift)  # -2^k - 1
            self._values.append(-2**k + 1 + signedShift)  # -2^k + 1

            self._values.append(2**k)  # 2^k
            self._values.append(2**k - 1)  # 2^k - 1
            self._values.append(2**k + 1)  # 2^k + 1

        # Removing duplicates
        self._values = sorted(set(self._values))

        # Order by greater values first
        self._values.reverse()

        # Update seed value
        self.seed = self.seed % len(self._values)

    def getValueAt(self, pos):
        """Returns the value set at postion 'pos' from the generated list.

        :return: a generated int value
        :rtype: :class:`int`
        :raise: ValueError if values is empty
        """
        if len(self._values) == 0:
            raise ValueError("Value list is empty.")

        if pos < len(self._values):
            return self._values(pos)
        else:
            return None

    ## Properties

    @property
    def minValue(self):
        return self._minValue

    @minValue.setter  # type: ignore
    def minValue(self, minValue):
        if minValue is None:
            raise ValueError("minValue should not be None")
        if not isinstance(minValue, int):
            raise ValueError("minValue should be an integer, not: '{}'"
                             .format(type(minValue)))
        self._minValue = minValue

    @property
    def maxValue(self):
        return self._maxValue

    @maxValue.setter  # type: ignore
    def maxValue(self, maxValue):
        if maxValue is None:
            raise ValueError("maxValue should not be None")
        if not isinstance(maxValue, int):
            raise ValueError("maxValue should be an integer, not: '{}'"
                             .format(type(maxValue)))
        self._maxValue = maxValue

    @property
    def bitsize(self):
        return self._bitsize

    @bitsize.setter  # type: ignore
    def bitsize(self, bitsize):
        if bitsize is None:
            raise ValueError("bitsize should not be None")
        if not isinstance(bitsize, int):
            raise ValueError("bitsize should be an int, not: '{}'"
                             .format(type(bitsize)))
        self._bitsize = bitsize
