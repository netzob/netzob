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
import pickle

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
    """Wrapper for generating integer values, from various underlying
    iterators or generators. This wrapper ensures that the returns
    integers fit into the expected interval.

    >>> from itertools import cycle
    >>> from netzob.Fuzzing.Generators.GeneratorFactory import GeneratorFactory
    >>> g = GeneratorFactory.buildGenerator(cycle(range(20, 42)))
    >>> type(g)
    <class 'netzob.Fuzzing.Generators.WrapperGenerator.WrapperGenerator'>
    >>> next(g)
    20
    >>> next(g)
    21
    >>> next(g)
    22

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
        """Iterate over generated values

        :return: a generated int value iterator
        :rtype: :class:`int` iterator

        """
        while True:
            # Get next value
            result = next(self._iterator)

            if self.minValue is not None and self.maxValue is not None:

                # Specification expanding for floats
                if isinstance(result, float):
                    number_values = float(self.maxValue) - float(self.minValue) + 1.0
                    result = self.minValue + int(result * number_values)

                # Ensure the produced value is in the range of the permitted values of the domain datatype
                if result > self.maxValue:
                    result = self.maxValue
                elif result < self.minValue:
                    result = self.minValue

            yield int(result)

    def get_state(self):
        # type: () -> bytes
        r"""
        Return a :class:`bytes` representing the internal state of the generator.

        >>> it = iter(range(10))
        >>> gen = WrapperGenerator(it)
        >>> gen.get_state()  # doctest: +ELLIPSIS
        b'\x80\x04\x95;\x00\x00\x00\x00\x00\x00\x00\x8c\x08builtins\x94\x8c\x04iter\x94\x93\x94\x8c\x08builtins\x94\x8c\x05range\x94\x93\x94K\x00K\nK\x01\x87\x94R\x94\x85\x94R\x94K\x00b.'
        >>> next(gen)
        0
        >>> gen.get_state()  # doctest: +ELLIPSIS
        b'\x80\x04\x95;\x00\x00\x00\x00\x00\x00\x00\x8c\x08builtins\x94\x8c\x04iter\x94\x93\x94\x8c\x08builtins\x94\x8c\x05range\x94\x93\x94K\x00K\nK\x01\x87\x94R\x94\x85\x94R\x94K\x01b.'
        """
        return pickle.dumps(self._iterator)

    def set_state(self, state):
        # type: (bytes) -> None
        """
        Set the internal state of the generator from a :class:`bytes`.

        >>> it = iter(range(10))
        >>> gen = WrapperGenerator(it)
        >>> next(gen) # blank shot
        0
        >>> state = gen.get_state()
        >>> next(gen); next(gen)
        1
        2
        >>> gen.set_state(state)
        >>> next(gen); next(gen)
        1
        2
        """
        self._iterator = pickle.loads(state)

    ## Properties

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
