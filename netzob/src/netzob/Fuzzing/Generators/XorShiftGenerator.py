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
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger
from netzob.Fuzzing.Generator import Generator
from netzob.Model.Vocabulary.Types.AbstractType import AbstractType, UnitSize


## Parameters taken from reference: "Xorshift RNGs" from George Marsaglia (https://www.jstatsoft.org/article/view/v008i14)

def xorshift8(state):
    state ^= (state << 7) & 0xff
    state ^= (state >> 5) & 0xff
    state ^= (state << 3) & 0xff
    return state

def xorshift16(state):
    state ^= (state << 13) & 0xffff
    state ^= (state >> 9) & 0xffff
    state ^= (state << 7) & 0xffff
    return state

def xorshift32(state):
    state ^= (state << 13) & 0xffffffff
    state ^= (state >> 17) & 0xffffffff
    state ^= (state << 5) & 0xffffffff
    return state

def xorshift64(state):
    state ^= (state << 11) & 0xffffffffffffffff
    state ^= (state >> 5) & 0xffffffffffffffff
    state ^= (state << 32) & 0xffffffffffffffff
    return state


@NetzobLogger
class XorShiftGenerator(Generator):
    """Generates integer values from a list determined with the size of an
    Integer field.

    >>> from netzob.all import *
    >>> seed = 14
    >>> g = XorShiftGenerator(seed, minValue=0, maxValue=255)
    >>> next(g)
    0
    >>> next(g)
    126
    >>> next(g)
    149

    """

    name = "xorshift"

    def __init__(self,
                 seed=1,
                 minValue=None,
                 maxValue=None,
                 bitsize=None,
                 signed=False):

        # Call parent init
        super().__init__(seed=seed)

        if seed == 0:
            raise ValueError("A seed=0 is not compatible with the generator XorShiftGenerator")

        # Initialize variables
        self._state = seed
        self.minValue = minValue
        self.maxValue = maxValue
        self.bitsize = bitsize
        self.signed = signed
        self._firstCall = True  # Tells if the generator is called for the first time

        # Handle bitsize
        bitsize = AbstractType.computeUnitSize(abs(self._maxValue - self._minValue) + 1)  # Compute unit size according to the maximum length
        bitsize = bitsize.value

        if bitsize == 8 or bitsize == 4:
            self.xorshift = xorshift8
        elif bitsize == 16:
            self.xorshift = xorshift16
        elif bitsize == 32:
            self.xorshift = xorshift32
        elif bitsize == 64:
            self.xorshift = xorshift64
        else:
            raise ValueError("Bitsize value '{}' not supported".format(bitsize))

    def __iter__(self):
        return self

    def __next__(self):
        """This is the method to get the next value.
        
        :return: A generated int value.
        :rtype: :class:`int`

        """

        if self._firstCall:
            # We force the first iteration to return 0, as it is never reached by xorshift generator
            self._firstCall = False
            result = 0
        else:
            self._state = self.xorshift(self._state)
            result = self._state

        # We respect the interval
        if self.signed:
            # Convert uint to int
            result = result.to_bytes(int(self.bitsize/8), byteorder='big')
            result = int.from_bytes(result, byteorder='big', signed=True)
            
            if result > self.maxValue:
                result = next(self)
            elif result < self.minValue:
                result = next(self)
        else:
            if result > self.maxValue:
                result = next(self)
            elif result < self.minValue:
                result = next(self)

        return result


    ## Properties

    @property
    def minValue(self):
        return self._minValue

    @minValue.setter  # type: ignore
    def minValue(self, minValue):
        if minValue is None:
            raise ValueError("minValue should not be None")
        if not isinstance(minValue, int):
            raise ValueError("minValue should be an integer, not: '{}'".format(type(minValue)))
        self._minValue = minValue

    @property
    def maxValue(self):
        return self._maxValue

    @maxValue.setter  # type: ignore
    def maxValue(self, maxValue):
        if maxValue is None:
            raise ValueError("maxValue should not be None")
        if not isinstance(maxValue, int):
            raise ValueError("maxValue should be an integer, not: '{}'".format(type(maxValue)))
        self._maxValue = maxValue

    @property
    def bitsize(self):
        return self._bitsize

    @bitsize.setter  # type: ignore
    def bitsize(self, bitsize):
        self._bitsize = bitsize

    @property
    def signed(self):
        return self._signed

    @signed.setter  # type: ignore
    def signed(self, signed):
        self._signed = signed
