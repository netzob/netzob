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

from netzob.Common.Utils.Decorators import typeCheck


class StringPaddedGenerator(object):
    """Generates string values.

    >>> from netzob.all import *
    >>> seed = 1234
    >>> genObject = StringGenerator(seed)
    >>> result = genObject.getNewValue()
    """

    def __init__(self, lengthMutator, stringsList):
        self._seed = 0
        self._lengthMutator = lengthMutator
        self._values = stringsList

    def reset(self):
        """Reset the current position in the list.

        :type: :class:`set`
        """
        self._seed = 0

    @property
    def values(self):
        """The list of available values.

        :type: :class:`set`
        """
        return self._values

    @property
    def seed(self):
        """ The seed in this generator gives the position of the string to
        return from the values list (modulo len(values)).

        :type: :class:`int`
        """
    @seed.setter
    @typeCheck(int)
    def seed(self, seedValue):
        self._seed = seedValue % len(self._values)

    def getNewValue(self, endChar):
        """This is the method to get a new string value from the list.

        :return: a generated str value
        :rtype: :class:`str`
        """
        if self._seed >= len(self._values):
            self.reset()
        value = self._values[self._seed] + endChar
        self._seed += 1
        length = int.from_bytes(self._lengthMutator.generate(),
                                self._lengthMutator.domain.dataType.endianness.value)
        if length > 0:
            if length > len(value):
                # Complete the string with padding characters to have the good
                # length
                value = value + (" " * (length - len(value)))
            else:
                # truncate the too long string value to length characters
                value = value[:length-1] + endChar
        else:
            value = ""
        return value
