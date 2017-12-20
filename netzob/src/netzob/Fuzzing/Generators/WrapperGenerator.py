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
from netzob.Common.Utils.Decorators import NetzobLogger
from netzob.Fuzzing.Generator import Generator


@NetzobLogger
class WrapperGenerator(Generator):
    """Wrapper for generating integer values.

    """

    name = "wrapper"

    def __init__(self,
                 iterator,
                 minValue=None,
                 maxValue=None,
                 bitsize=None,
                 signed=False):

        # Call parent init
        super().__init__()

        # Initialize variables
        self._iterator = iterator
        self.minValue = minValue
        self.maxValue = maxValue
        self.bitsize = bitsize  # Not used
        self.signed = signed    # Not used

    def __iter__(self):
        return self

    def __next__(self):
        """This is the method to get the next value in the generated list.
        
        :return: a generated int value
        :rtype: :class:`int`

        """
        result = next(self._iterator)

        if self._minValue is not None and self._maxValue is not None:
            result = center(result, self._minValue, self._maxValue)

        return result


    ## Properties

    @property
    def minValue(self):
        return self._minValue

    @minValue.setter  # type: ignore
    def minValue(self, minValue):
        if minValue is None:
            self._minValue = 0
        else:
            self._minValue = minValue

    @property
    def maxValue(self):
        return self._maxValue

    @maxValue.setter  # type: ignore
    def maxValue(self, maxValue):
        if maxValue is None:
            self._maxValue = 1 << 16
        else:
            self._maxValue = maxValue

    @property
    def bitsize(self):
        return self._bitsize

    @bitsize.setter  # type: ignore
    def bitsize(self, bitsize):
        if bitsize is None:
            self._bitsize = 16
        else:
            self._bitsize = bitsize

    @property
    def signed(self):
        return self._signed

    @signed.setter  # type: ignore
    def signed(self, signed):
        self._signed = signed


## Utility functions

def center(val, lower, upper):
    """
    Center :attr:`val` between :attr:`lower` and :attr:`upper`.
    """

    number_values = float(upper) - float(lower) + 1.0
    result = lower + int(val * number_values)

    # Ensure the produced value is in the range of the permitted values of the domain datatype
    if result > upper:
        result = upper
    elif result < lower:
        result = lower
    return result
