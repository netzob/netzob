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


class Xorshift128plus(object):
    """Python implementation of the xorshift128plus algorithm.
    See : https://en.wikipedia.org/wiki/Xorshift

    >>> from netzob.all import *
    >>> seed = 10
    >>> prngObject = Xorshift128plus(seed)
    >>> result = prngObject.getNew32bitsValue()
    """

    DEFAULT_SEED_VALUE = 1234
    MASK_64BITS = 0xFFFFFFFFFFFFFFFF
    MASK_32BITS = 0xFFFFFFFF
    MASK_16BITS = 0xFFFF

    def __init__(self, seedValue=None):
        if seedValue is not None:
            self.seed = seedValue
        else:
            self.seed = Xorshift128plus.DEFAULT_SEED_VALUE

    @property
    def seed(self):
        """The seed used in pseudo-random generator

        :type: :class:`int`
        """
        return self._seed

    @seed.setter
    def seed(self, seedValue):
        try:
            self._seed = int(seedValue)
        except ValueError:
            print("[ERROR] Invalid seed " +
                  str(seedValue) +
                  ", use default value " +
                  str(Xorshift128plus.DEFAULT_SEED_VALUE))
            self._seed = Xorshift128plus.DEFAULT_SEED_VALUE
        self._s = [self._seed, 0]

    def reset(self):
        """Reset the state of the pseudo-random generator.
        It allows to produce the same values previously produced with
        getNew64bitsValue().
        """
        self._s = [self._seed, 0]

    def getNew64bitsValue(self):
        """This is the method to generate a pseudo-random value from the seed.
        Each time this method is called, it produces a different value.
        To obtain the previous values again, call reset().

        :return: a generated int value on 64bits, initially based on the seed
        :rtype: :class:`int`
        """
        # MASK_64BITS is used to not overflow 64bits
        x = self._s[0]
        y = self._s[1]
        self._s[0] = y & Xorshift128plus.MASK_64BITS
        x ^= x << 23
        x = x & Xorshift128plus.MASK_64BITS
        self._s[1] = (x ^ y ^ (x >> 17) ^ (y >> 26)) & \
            Xorshift128plus.MASK_64BITS
        return ((self._s[1] + y) & Xorshift128plus.MASK_64BITS)

    def getNew32bitsValue(self):
        """Same method as getNew64bitsValue(), but with a 32bits mask.

        :return: a generated int value on 32bits, initially based on the seed
        :rtype: :class:`int`
        """
        return self.getNew64bitsValue() & Xorshift128plus.MASK_32BITS

    def getNew0To1Value32Bits(self):
        """This is the method to generate a pseudo-random value between 0 and
        1, from the seed, with 32bits resolution.
        Each time this method is called, it produces a different value.
        To obtain the previous values again, call resetSeed().

        :return: a generated float value between 0 and 1, initially based on
            the seed
        :rtype: :class:`float`
        """
        return (float(self.getNew64bitsValue() & Xorshift128plus.MASK_32BITS)
                / 2 ** 32)

    def getNew0To1Value64Bits(self):
        """This is the method to generate a pseudo-random value between 0 and
        1, from the seed, with 64bits resolution.
        Each time this method is called, it produces a different value.
        To obtain the previous values again, call resetSeed().

        :return: a generated float value between 0 and 1, initially based on
            the seed
        :rtype: :class:`float`
        """
        return (float(self.getNew64bitsValue())
                / 2 ** 64)

    def getNew16bitsValue(self):
        """Same method as getNew64bitsValue(), but with a 16bits mask.

        :return: a generated int value on 16bits, initially based on the seed
        :rtype: :class:`int`
        """
        return self.getNew64bitsValue() & Xorshift128plus.MASK_16BITS

    def getState0(self):
        """:return: the low part of the generator state
        :rtype: :class:`int`
        """
        return self._s[0]

    def getState1(self):
        """:return: the high part of the generator state
        :rtype: :class:`int`
        """
        return self._s[1]
