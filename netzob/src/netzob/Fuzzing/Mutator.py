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

# +---------------------------------------------------------------------------+
# | Related third party imports                                               |
# +---------------------------------------------------------------------------+

# +---------------------------------------------------------------------------+
# | Local application imports                                                 |
# +---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck
from netzob.Model.Grammar.Automata import Automata  # noqa: F401


class Mutator(metaclass=abc.ABCMeta):
    """The model of any mutator.

    This class provides the common properties and API to all inherited mutators.

    The Mutator constructor expects some parameters:

    :param seed: the initial seed value of the mutator
    :type seed: :class:`int`, defaults to :attr:`SEED_DEFAULT`

    Constant definitions:
    """

    # Constants
    SEED_DEFAULT = 10  #: the default seed value
    COUNTER_MAX_DEFAULT = 2**16  #: the default max counter value

    def __init__(self,
                 seed=SEED_DEFAULT,
                 counterMax=COUNTER_MAX_DEFAULT,
                 counterMaxRelative=False
                 ):
        # Handle class variables
        self._seed = seed
        self._currentState = 0
        self.setCounterMax(counterMax, counterMaxRelative)
        self._currentCounter = 0

    @typeCheck(int)
    def updateSeed(self,
                   seedValue  # type: int
                   ):
        """
        Update the seed value and forward value to all nested mutators.

        :param seedValue: the new seed value
        :type seedValue: int
        """
        self._seed = seedValue

    @property
    def currentState(self):
        """
        Property (getter/setter).
        The current state of the pseudo-random mutator.
        The mutator can reproduce a value by using this state.

        :type: :class:`int`
        """
        return self._currentState

    @currentState.setter
    @typeCheck(int)
    def currentState(self, stateValue):
        self._currentState = stateValue

    def getCounterMax(self):
        """
        Get the max number of values that the mutator would produce.
        When this limit is reached, :meth:`mutate` returns None.

        :type: :class:`int` (absolute) or :class:`float` (relative)
        """
        return self._counterMax

    @typeCheck((int, float), bool)
    def setCounterMax(self, counterMaxValue, relative):
        """
        Set the max number of values that the mutator would produce.

        :param counterMaxValue: the counter max value
        :type counterMaxValue: :class:`int` (absolute) or :class:`float` (relative)
        :param relative: wether the counter value is absolute or relative
        :type relative: :class:`bool`
        """
        self._counterMax = (self.COUNTER_MAX_DEFAULT if counterMaxValue is None
                            else counterMaxValue)
        self._counterMaxRelative = relative

    @property
    def currentCounter(self):
        """
        Property (getter).
        The counter of :meth:`mutate` calls.
        In :meth:`mutate`, this value is compared to counterMax, to determine if the
        limit of mutation is reached.

        :type: :class:`int`
        """
        return self._currentCounter

    def resetCurrentCounter(self):
        """Reset the current counter of :meth:`mutate`.

        :type: :class:`int`
        """
        self._currentCounter = 0

    def reset(self):
        """Reset environment of the mutator.
        """
        self._currentCounter = 0

    def generate(self):
        """This is the fuzz generation method of the field domain. It has to
        be overridden by all the inherited mutators which call the
        :meth:`generate` function.

        :return: a generated content represented with bytes
        :rtype: :class:`bytes`
        :raises: :class:`Exception` when **currentCounter** reaches
                 :attr:`Mutator.counterMax`.
        """
        if self._currentCounter >= self.getCounterMax():
            raise Exception("Max mutation counter reached")
        self._currentCounter += 1

    @abc.abstractmethod
    def mutate(self, *args):
        """This is the mutation method of the field domain. It has to be
        overridden by all the inherited mutators which call the
        :meth:`mutate` function.

        If the currentCounter reached counterMax, :meth:`mutate` returns None.

        :param data: The data to mutate.
        :type data: :class:`bitarray.bitarray`
        :return: a generated content represented with bytes
        :rtype: :class:`bytes`

        :meth:`mutate` is an *abstract method* and must be inherited.
        """
