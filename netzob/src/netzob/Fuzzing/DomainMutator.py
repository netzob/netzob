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
import random
from enum import Enum
from typing import Type  # noqa: F401

# +---------------------------------------------------------------------------+
# | Related third party imports                                               |
# +---------------------------------------------------------------------------+

# +---------------------------------------------------------------------------+
# | Local application imports                                                 |
# +---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck
from netzob.Model.Vocabulary.Domain.Variables.AbstractVariable import AbstractVariable
from netzob.Model.Vocabulary.Domain.Variables.Leafs.AbstractVariableLeaf import AbstractVariableLeaf
from netzob.Fuzzing.Mutator import Mutator


class MutatorMode(Enum):
    """Mutator Fuzzing modes"""
    NONE     = 0  #: No fuzzing
    MUTATE   = 1  #: Fuzzing by mutation of a legitimate value
    GENERATE = 2  #: Fuzzing by generation


class MutatorInterval(Enum):
    """Mutator Fuzzing intervals"""
    DEFAULT_INTERVAL = 0  #: We use the legitimate domain interval (ex: DeterminitMutator(interval=MutatorInterval.DEFAULT_INTERVAL)
    FULL_INTERVAL    = 1  #: We cover the whole storage space of the domain (ex: DeterminitMutator(interval=MutatorInterval.FULL_INTERVAL)
    # else, we consider the tuple passed as parameter to override the domain interval (ex: DeterminitMutator(interval=(10, 42))


class DomainMutator(Mutator):
    """The model of domain mutators.

    This class provides the common properties and API to all inherited mutators.

    **Mutators for message formats fuzzing**

    Mutators may be used during symbol specialization process, in
    order to fuzz targeted fields variables. Mutators are specified in
    the ``symbol.specialize()`` through the ``mutators=``
    parameter. This parameter expects a dict containing fields objects
    for its keys and Mutators objects for its values. We can provide
    parameters to mutators by using tuple as values of the dict.

    The Mutator constructor expects some parameters:

    :param domain: The domain of the field to mutate, in case of a data
        mutator.
    :param mode: If set to **MutatorMode.GENERATE**, the generate() method will be
        used to produce the value.
        If set to **MutatorMode.MUTATE**, the mutate() method will be used to
        produce the value (not implemented).
        Default value is **MutatorMode.GENERATE**.
    :type domain: :class:`AbstractVariable
        <netzob.Model.Vocabulary.Domain.Variables.AbstractVariable>`, optional
    :type mode: :class:`int`, optional

    The following code shows the instanciation of a symbol composed of
    a string and an integer, and the fuzzing request during the
    specialization process:

    >>> from netzob.all import *
    >>> f1 = Field(String())
    >>> f2 = Field(Integer())
    >>> symbol = Symbol(fields=[f1, f2])
    >>> mutators = {f1: StringMutator,
    ...             f2: (PseudoRandomIntegerMutator, minValue=12, maxValue=20)}  # doctest: +SKIP
    >>> symbol.specialize(mutators=mutators)  # doctest: +SKIP

    """

    # Constants
    SEED_DEFAULT = 10
    COUNTER_MAX_DEFAULT = 1 << 16  #: :math:`2^16`
    DOMAIN_TYPE = AbstractVariable  # type: Type[AbstractVariable]

    def __init__(self,
                 domain,
                 mode=MutatorMode.GENERATE,  # type: MutatorMode
                 **kwargs):
        # Call parent init
        super().__init__(**kwargs)

        # Sanity checks
        if not isinstance(domain, self.DOMAIN_TYPE):
            raise TypeError("Mutator domain should be of type AbstractRelationVariableLeaf. Received object: '{}'"
                            .format(domain))

        # Handle parameters
        assert isinstance(mode, MutatorMode)
        self._domain = domain
        self._mode = mode.value

    def getDomain(self):
        """
        Get the domain of the DomainMutator

        :return: the domain of the mutator
        :raise: ValueError
        """
        if self._domain is None:
            raise ValueError("No domain has been set")
        return self._domain

    def mutate(self, data):
        """This is the mutation method of the field domain. It has to be
        overridden by all the inherited mutators which call the
        mutate() function.

        If the currentCounter reached counterMax, mutate() returns None.

        :param data: The data to mutate.
        :type data: :class:`bitarray.bitarray`
        :return: a generated content represented with bytes
        :rtype: :class:`bytes`

        :meth:`mutate` is an *abstract method* and must be inherited.
        """
        if data is None or len(data) == 0:
            return data

        # The current implementation makes a bitflip at a random position
        idx = random.randint(0, len(data) - 1)
        data[idx] = not data[idx]
        return data
