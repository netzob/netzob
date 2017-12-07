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
import abc
from enum import Enum

# +---------------------------------------------------------------------------+
# | Related third party imports                                               |
# +---------------------------------------------------------------------------+

# +---------------------------------------------------------------------------+
# | Local application imports                                                 |
# +---------------------------------------------------------------------------+
from netzob.Model.Grammar.Automata import Automata  # noqa: F401
from netzob.Fuzzing.Generator import Generator
from netzob.Common.Utils.Constant import Constant
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger


class MutatorMode(Enum):
    """Mutator Fuzzing modes"""
    MUTATE = 1  #: Fuzzing by mutation of a legitimate value
    GENERATE = 2  #: Fuzzing by generation
    __repr__ = Enum.__str__


@NetzobLogger
class Mutator(metaclass=abc.ABCMeta):
    """This class provides the interface that a mutator should implement.

    The Mutator constructor expects some parameters:

    :param seed: The initial seed value of the mutator. Default value is :attr:`SEED_DEFAULT` = 10.
    :param counterMax: The max number of mutations to produce (a :class:`int` should be used to represent an absolute value, whereas a :class:`float` should be used to represent a ratio in percent). Default value is :attr:`COUNTER_MAX_DEFAULT` = 65536.
    :type seed: :class:`int`
    :type counterMax: :class:`int` or :class:`float`


    The Mutator class provides the following public variables:

    :var mode: The mode of fuzzing (either MutationMode.GENERATE or MutationMode.MUTATE)
    :var generator: The underlying generator used to produce pseudo-random or deterministic values.
    :var seed: The seed value of the mutator used to initialize the generator.
    :var counterMax: The max number of mutations to produce (a :class:`int` should be used to represent an absolute value, whereas a :class:`float` should be used to represent a ratio in percent).
    :vartype mode: :class:`MutatorMode`
    :vartype generator: :class:`iter`
    :vartype seed: :class:`int`
    :vartype counterMax: :class:`int` or :class:`float`

    """

    # Class constants
    SEED_DEFAULT = 10  #: the default seed value
    COUNTER_MAX_DEFAULT = Constant(2 ** 16)  #: the default max counter value (65536)

    # Class variables
    globalCounterMax = COUNTER_MAX_DEFAULT

    def __init__(self,
                 mode=MutatorMode.GENERATE,  # type: MutatorMode
                 generator=Generator.NG_mt19937,
                 seed=SEED_DEFAULT,
                 counterMax=COUNTER_MAX_DEFAULT):
        # type: (...) -> None

        # Public variables linked with parameters
        self.mode = mode
        self.generator = generator
        self.seed = seed
        self.counterMax = counterMax

        # Public variables
        self.currentCounter = 0
        self.currentState = 0


    # API methods

    def generate(self):
        """This is the fuzz generation method of the field domain. It has to
        be overridden by all the inherited mutators which call the
        :meth:`generate` function.

        :return: a generated content represented with bytes
        :rtype: :class:`bytes`
        :raises: :class:`Exception` when **currentCounter** reaches
                 :attr:`Mutator.counterMax`.
        """
        if self.currentCounter >= self.counterMax:
            raise Exception("Max mutation counter reached")

        if self.currentCounter >= Mutator.globalCounterMax:
            raise Exception("Max mutation counter reached")

        self.currentCounter += 1

    @abc.abstractmethod
    def mutate(self, data):
        """This is the mutation method of the field domain. It has to be
        overridden by all the inherited mutators which call the
        :meth:`mutate` function.

        If the currentCounter reached counterMax, :meth:`mutate` returns None.

        :param data: The data to mutate.
        :type data: :class:`bitarray`
        :return: a generated content represented with bytes
        :rtype: :class:`bytes`

        :meth:`mutate` is an *abstract method* and must be inherited.
        """


    # Properties

    @property
    def mode(self):
        return self._mode

    @mode.setter  # type: ignore
    def mode(self, mode):
        # Sanity checks on mutator mode
        if not isinstance(mode, MutatorMode):
            raise TypeError("Mutator mode should be of type '{}'. Received object: '{}'"
                            .format(MutatorMode, mode))
        self._mode = mode

    @property
    def generator(self):
        return self._generator

    @generator.setter  # type: ignore
    def generator(self, generator):
        self._generator = generator

    @property
    def seed(self):
        return self._seed

    @seed.setter  # type: ignore
    def seed(self, seed):
        self._seed = seed

    @property
    def counterMax(self):
        return self._counterMax

    @counterMax.setter  # type: ignore
    def counterMax(self, counterMax):
        self._counterMax = counterMax

    @property
    def currentCounter(self):
        return self._currentCounter

    @currentCounter.setter  # type: ignore
    def currentCounter(self, currentCounter):
        self._currentCounter = currentCounter

    @property
    def currentState(self):
        """
        Property (getter.setter  # type: ignore).
        The current state of the pseudo-random mutator.
        The mutator can reproduce a value by using this state.

        :type: :class:`int`
        """
        return self._currentState

    @currentState.setter  # type: ignore
    def currentState(self, currentState):
        self._currentState = currentState


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
    if result < lower:
        result = lower
    return result
