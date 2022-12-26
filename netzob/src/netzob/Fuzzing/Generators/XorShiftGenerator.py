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
try:
    from typing import Tuple  # noqa: F401
except ImportError:
    pass

# +---------------------------------------------------------------------------+
# | Related third party imports                                               |
# +---------------------------------------------------------------------------+

# +---------------------------------------------------------------------------+
# | Local application imports                                                 |
# +---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import NetzobLogger
from netzob.Fuzzing.Generator import Generator
from netzob.Fuzzing.Generators.xorshift import (
    native_xorshift8,
    native_xorshift16,
    native_xorshift32,
    native_xorshift64
)
from netzob.Model.Vocabulary.Types.AbstractType import AbstractType


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

    # Generation of integers from an interval

    >>> from netzob.all import *
    >>> seed = 14
    >>> g = XorShiftGenerator(seed, minValue=0, maxValue=255)
    >>> next(g)
    0
    >>> next(g)
    126
    >>> next(g)
    149


    # Generation of signed integers from an interval

    >>> seed = 14
    >>> g = XorShiftGenerator(seed, minValue=-128, maxValue=127, signed=True)
    >>> a = set()
    >>> for _ in range(256):
    ...     a.add(next(g))
    >>> len(a)
    256


    # If incompatible parameters are passed to the generator, it should return None

    >>> seed = 14
    >>> g = XorShiftGenerator(seed, minValue=-20, maxValue=-20, signed=False)
    Traceback (most recent call last):
    ...
    ValueError: negative values implies signed=True

    """

    name = "xorshift"

    def __init__(self,
                 seed=1,
                 minValue=None,
                 maxValue=None,
                 bitsize=None,  # Not used
                 signed=False):

        # Call parent init
        super().__init__(seed=seed)

        if seed == 0:
            raise ValueError("A seed=0 is not compatible with the generator XorShiftGenerator")

        if not (minValue is None or maxValue is None):
            if minValue > maxValue:
                raise ValueError("maxValue must be greater than minValue")

            if minValue < 0 and maxValue < 0 and not signed:
                raise ValueError("negative values implies signed=True")

        # Initialize variables
        self._state = seed
        self.minValue = minValue
        self.maxValue = maxValue
        self.signed = signed
        self._nbCall = 0
        self.nb_values_full = False

        # Compute the number of uniq possible values
        self.nb_values = abs(self._maxValue - self._minValue) + 1

        # Handle bitsize
        bitsize = AbstractType.computeUnitSize(self.nb_values)  # Compute unit size according to the maximum length
        self.bitsize = bitsize.value

        # Bitsize of 4 should be converted to 8, as there is no xorshift function for 4 bits
        if self.bitsize == 4:
            self.bitsize = 8

        # Bitsize of 24 should be converted to 32, as there is no xorshift function for 24 bits
        if self.bitsize == 24:
            self.bitsize = 32

        # Specific case for min == max
        if self.minValue == self.maxValue:
            self._xorshift_func = lambda x: self.maxValue
            return

        # Select xorshift according to bitsize
        if self.bitsize == 8:
            self._xorshift_func = native_xorshift8
            if self.nb_values == 1<<8:
                self.nb_values_full = True
        elif self.bitsize == 16:
            self._xorshift_func = native_xorshift16
            if self.nb_values == 1<<16:
                self.nb_values_full = True
        elif self.bitsize == 32:
            self._xorshift_func = native_xorshift32
            if self.nb_values == 1<<32:
                self.nb_values_full = True
        elif self.bitsize == 64:
            self._xorshift_func = native_xorshift64
            if self.nb_values == 1<<64:
                self.nb_values_full = True
        else:
            raise ValueError("Bitsize value '{}' not supported".format(self.bitsize))

    def __iter__(self):
        """This is the method to get the next value.

        :return: A generated int value.
        :rtype: :class:`int` or None

        """

        self._state = self.seed

        result = 0  # initial value (first call)

        while True:
            # We respect the interval
            if self.signed:
                # Convert uint to int
                result = result.to_bytes(self.bitsize // 8, byteorder='big', signed=False)
                result = int.from_bytes(result, byteorder='big', signed=True)

            # If the value does not match the expected interval, we recursively call for the next value
            if self.minValue <= result <= self.maxValue:
                yield result

            result = self.xorshift()

    def __next__(self):
        nb_values = abs(self._maxValue - self._minValue) + 1
        value = super().__next__()
        self._nbCall = (self._nbCall + 1) % nb_values
        if self._nbCall == 0:
            # reset iterator after a full cycle to include 0 again
            self._reset_iterator()
        return value

    def get_state(self):
        # type: () -> Tuple[int, bool]
        """
        Return a tuple representing the internal state of the generator.

        >>> gen = XorShiftGenerator(minValue=0, maxValue=100, seed=1)
        >>> val = next(gen)
        >>> val = next(gen)
        >>> val == gen.get_state()
        True
        """
        return self._state

    def set_state(self, state):
        # type: (Tuple[int, bool]) -> None
        """
        Set the internal state of the generator from a tuple.

        >>> gen = XorShiftGenerator(minValue=0, maxValue=100, seed=1)
        >>> val = next(gen) # blank shot
        >>> state = gen.get_state()
        >>> val = next(gen)
        >>> gen.set_state(state)
        """
        self._state = state

    def xorshift(self):
        self._state = self._xorshift_func(self._state)
        return self._state


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
