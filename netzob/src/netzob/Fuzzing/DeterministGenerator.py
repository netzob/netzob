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


class DeterministGenerator(object):
    """Generates integer values from a list determined with the size of an
    Integer field.

    >>> from netzob.all import *
    >>> seed = 10
    >>> genObject = DeterministGenerator(seed)
    >>> result = genObject.getNewValue()
    """

    DEFAULT_MIN_VALUE = 0
    DEFAULT_BITSIZE = 32
    DEFAULT_MAX_VALUE = 2**DEFAULT_BITSIZE

    def __init__(self):
        self._currentPos = 0
        self._minValue = 0
        self._maxValue = 0
        self._bitSize = 0
        self._values = list()

    def createValues(self,
                     minValue,
                     maxValue,
                     bitSize):
        self._currentPos = 0
        self._minValue = minValue
        self._maxValue = maxValue
        self._bitSize = bitSize

        self._values = list()
        self._values.append(minValue)  # P
        self._values.append(maxValue)  # Q
        if (minValue-1) & 2**bitSize == minValue-1:
            self._values.append(minValue-1)  # P-1
        self._values.append(maxValue-1)  # Q-1
        self._values.append(minValue+1)  # P+1
        if (maxValue+1) & 2**bitSize == maxValue+1:
            self._values.append(maxValue+1)  # Q+1
        self._values.append(0)  # 0
        self._values.append(-1)  # -1
        self._values.append(1)  # 1

        for k in range(0, self._bitSize-2):  # k in [0..N-2]
            self._values.append(-2**k)  # -2^k
            self._values.append(-2**k - 1)  # -2^k - 1
            self._values.append(-2**k + 1)  # -2^k + 1

            self._values.append(2**k)  # 2^k
            self._values.append(2**k - 1)  # 2^k - 1
            self._values.append(2**k + 1)  # 2^k + 1

    def reset(self):
        """Reset the current position in the list.

        :type: :class:`set`
        """
        self._currentPos = 0

    @property
    def values(self):
        """The list of available values.

        :type: :class:`set`
        """
        return self._values

    def getNewValue(self):
        """This is the method to get the next value in the generated list.
        To obtain the previous values again, call reset() then getNewValue()
        or use accessor getValueAt().

        :return: a generated int value
        :rtype: :class:`int`
        """
        if self._currentPos >= len(self._values):
            self.reset()
        value = self._values[self._currentPos]
        self._currentPos += 1
        return value

    def getValueAt(self, pos):
        """Returns the value set at postion 'pos' from the generated list.

        :return: a generated int value
        :rtype: :class:`int`
        """
        if pos < len(self._values):
            return self._values(pos)
        else:
            return None
