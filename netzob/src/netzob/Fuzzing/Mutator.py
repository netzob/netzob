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
import abc

# +---------------------------------------------------------------------------+
# | Related third party imports                                               |
# +---------------------------------------------------------------------------+

# +---------------------------------------------------------------------------+
# | Local application imports                                                 |
# +---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck
from netzob.Model.Vocabulary.AbstractField import AbstractField
from netzob.Model.Grammar.Automata import Automata


class Mutator(object):
    """The model of any mutator.

    This class provides the common properties and API to all inherited mutators.

    **Mutators for message formats fuzzing**

    Mutators may be used during symbol specialization process, in
    order to fuzz targeted fields. Mutators are specified in the
    ``symbol.specialize()`` through the ``mutators=`` parameter. This
    parameter expects a dict containing fields objects for its keys
    and Mutators objects for its values. We can provide parameters to
    mutators by using tuple as values of the dict.

    The following code shows the instanciation of a symbol composed of
    a string and an integer, and the fuzzing request during the
    specialization process:

    >>> f1 = Field(String())
    >>> f2 = Field(Integer())
    >>> symbol = Symbol(fields=[f1, f2])
    >>> mutators = {f1: StringMutator,
    ...             f2: (PseudoRandomIntegerMutator, minValue=12, maxValue=20)}
    >>> symbol.specialize(mutators=mutators)

    """

    # Constants
    SEED_DEFAULT = 0

    def __init__(self):
        self._seed = Mutator.SEED_DEFAULT
        self._field = None
        self._automata = None
        self._currentState = 0
        self._counterMax = 0
        self._currentCounter = 0

    @property
    def seed(self):
        """The seed used in pseudo-random generator

        :type: :class:`int`
        """
        return self._seed

    @seed.setter
    @typeCheck(int)
    def seed(self, seedValue):
        self._seed = seedValue

    @property
    def currentState(self):
        """The current state of the pseudo-random generator.
        the generator can reproduce a value by using this state.

        :type: :class:`int`
        """
        return self._currentState

    @currentState.setter
    @typeCheck(int)
    def currentState(self, stateValue):
        self._currentState = stateValue

    @property
    def counterMax(self):
        """The max number of values that the generator has to produce.
        When this limit is reached, mutate() returns None.

        :type: :class:`int`
        """
        return self._counterMax

    @counterMax.setter
    @typeCheck(int)
    def counterMax(self, counterMaxValue):
        self._counterMax = counterMaxValue

    @property
    def currentCounter(self):
        """The counter of mutate() calls.
        In mutate(), this value is compared to counterMax, to determine if the
        limit of mutation is reached.

        :type: :class:`int`
        """
        return self._currentCounter

    def resetCurrentCounter(self):
        """Reset the current counter of mutate().

        :type: :class:`int`
        """
        self._currentCounter = 0

    @property
    def field(self):
        """The field to which the mutation is applied.

        :type: :class:`AbstractField <netzob.Model.Vocabulary.AbstractField>`
        """
        return self._field

    @field.setter
    @typeCheck(AbstractField)
    def field(self, abstractField):
        self._field = abstractField

    @property
    def automata(self):
        """The automata to which the mutation is applied.

        :type: :class:`Automata <netzob.Model.Grammar.Automata.Automata>`
        """
        return self._automata

    @automata.setter
    @typeCheck(Automata)
    def automata(self, automata):
        self._automata = automata

    @abc.abstractmethod
    def mutate(self):
        """This is the mutation method of the field. It has to be overridden by
        all the inherited mutators which call the generator function.

        If the currentCounter reached counterMax, mutate() returns None.

        Raises NotImplementedMutatorError if the inherited mutator has not
        overridden this method.

        :return: a generated content represented with bytes
        :rtype: :class:`bytes`
        :raises: :class:`NotImplementedMutatorError <netzob.Fuzzing.Mutator.NotImplementedMutatorError>`
        """
        raise NotImplementedError("mutate() is not implemented yet")
