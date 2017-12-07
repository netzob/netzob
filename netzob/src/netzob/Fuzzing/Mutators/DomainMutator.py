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
from netzob.Model.Vocabulary.Types.AbstractType import AbstractType, UnitSize
from netzob.Fuzzing.Mutator import Mutator
from netzob.Fuzzing.Mutator import MutatorMode
from netzob.Fuzzing.Generator import Generator
from netzob.Fuzzing.Generators.GeneratorFactory import GeneratorFactory
from netzob.Fuzzing.Generators.DeterministGenerator import DeterministGenerator
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger


class MutatorInterval(Enum):
    """Mutator Fuzzing intervals"""
    DEFAULT_INTERVAL = 0  #: We use the legitimate domain interval (ex: DeterminitMutator(interval=MutatorInterval.DEFAULT_INTERVAL)
    FULL_INTERVAL    = 1  #: We cover the whole storage space of the domain (ex: DeterminitMutator(interval=MutatorInterval.FULL_INTERVAL)
    # else, we consider the tuple passed as parameter to override the domain interval (ex: DeterminitMutator(interval=(10, 42))


@NetzobLogger
class DomainMutator(Mutator):
    """This class provides the interface of domain mutators.

    This class provides the common properties and API to all inherited mutators.

    **Mutators for message formats fuzzing**

    Mutators may be used during symbol specialization process, in
    order to fuzz targeted field variables. Mutators are specified in
    the :meth:`symbol.specialize <netzob.Model.Vocabulary.Symbol.Symbol.specialize>`
    through the ``mutators=`` parameter. This parameter expects a dict containing
    field objects for its keys and Mutator objects for its values.
    We can provide parameters to mutators by using tuple as values of the dict.

    The DomainMutator constructor expects some parameters:

    :param domain: The domain of the field to mutate, in case of a data
        mutator.
    :param mode: If set to :attr:`MutatorMode.GENERATE`, :meth:`Mutator.generate()` will be
        called in order to produce the fuzzing value.
        If set to :attr:`MutatorMode.MUTATE`, :meth:`Mutator.mutate()` will be called in order to
        mutate the current value. Default value is :attr:`MutatorMode.GENERATE`.
    :type domain: :class:`AbstractVariable
        <netzob.Model.Vocabulary.Domain.Variables.AbstractVariable>`, optional
    :type mode: :class:`MutatorMode`, optional

    """

    # Constants
    DOMAIN_TYPE = None    # type: Type[AbstractVariable]
    DATA_TYPE = None      # type: Type[AbstractType]

    def __init__(self,
                 domain,
                 mode=MutatorMode.GENERATE,  # type: MutatorMode
                 generator=Generator.NG_mt19937,
                 seed=Mutator.SEED_DEFAULT,
                 counterMax=Mutator.COUNTER_MAX_DEFAULT,
                 lengthBitSize=None):
        # type: (...) -> None

        # Call parent init
        super().__init__(mode=mode,
                         generator=generator,
                         seed=seed,
                         counterMax=counterMax)

        # Variables initialized from parameters
        self.domain = domain
        self.lengthBitSize = lengthBitSize

        # Internal variables
        self._lengthGenerator = None
        self._minLength = None
        self._maxLength = None

    def mutate(self, data):
        """This is the mutation method of the field domain. It has to be
        overridden by all the inherited mutators which call the
        :meth:`mutate` function.

        If the currentCounter reached counterMax, :meth:`mutate` returns None.

        :param data: The data to mutate.
        :type data: :class:`bitarray`
        :return: a generated content represented with bytes
        :rtype: :class:`bytes`
        """
        if data is None or len(data) == 0:
            return data

        # The current implementation makes a bitflip at a random position
        idx = int(next(self.generator) % len(data))
        data[idx] = not data[idx]
        return data


    # Internal methods

    def _initializeLengthGenerator(self, fuzzing_interval, model_interval, model_unitSize):
        """Initialize a DeterministGenerator according to the given parameter.

        """

        # Identify min and max interval from default datatype storage size
        if fuzzing_interval == MutatorInterval.FULL_INTERVAL:
            self._logger.debug("Computed fuzzing interval from datatype storage size")

            if self.lengthBitSize is None:
                self.lengthBitSize = model_unitSize  # Use default bitsize

            self._minLength = 0
            self._maxLength = 2**self.lengthBitSize.value

        else:
            # Identify min and max interval from default datatype interval
            if fuzzing_interval == MutatorInterval.DEFAULT_INTERVAL:
                self._logger.debug("Computed fuzzing interval from default datatype interval")
                self._minLength = model_interval[0]
                self._maxLength = model_interval[1]

            # Identify min and max interval from fuzzing parameters
            elif (isinstance(fuzzing_interval, tuple) and len(fuzzing_interval) == 2 and all(isinstance(_, int) for _ in fuzzing_interval)):
                self._logger.debug("Computed fuzzing interval with tupple: {}".format(fuzzing_interval))
                self._minLength, self._maxLength = fuzzing_interval
            else:
                raise Exception("Not enough information to generate the fuzzing data.")

            # Compute lengthBitSize
            if self.lengthBitSize is None:
                self.lengthBitSize = model_unitSize  # Use default bitsize
            else:
                # Compute bitsize according to the interval length
                bitsize_tmp = AbstractType.computeUnitSize(self._maxLength)  # Compute unit size according to the maximum length

                # Check size consistency
                if self.lengthBitSize.value < bitsize_tmp.value:
                    raise Exception("Specified lengthBitSize ({}) is too small to represent all possible data size from interval: ({}, {})".format(self.lengthBitSize, self._minLength, self._maxLength))

        self._logger.debug("Computed fuzzing interval: ({}, {}) with lengthBitSize: {}".format(self._minLength, self._maxLength, self.lengthBitSize))

        # Build the length generator
        self._lengthGenerator = GeneratorFactory.buildGenerator(DeterministGenerator.NG_determinist,
                                                                seed = self.seed,
                                                                minValue = self._minLength,
                                                                maxValue = self._maxLength,
                                                                bitsize = self.lengthBitSize.value,
                                                                signed = False)


    ## Properties

    @property
    def domain(self):
        return self._domain

    @domain.setter  # type: ignore
    def domain(self, domain):
        # Sanity checks on domain parameter
        if not (self.DOMAIN_TYPE is None or isinstance(domain, self.DOMAIN_TYPE)):
            raise TypeError("Mutator domain should be of type {}. Received object: '{}'"
                            .format(self.DOMAIN_TYPE, domain))

        # Sanity checks on domain datatype (AbstractVariableLeaf have a dataType, so we check its consistency)
        if isinstance(domain, AbstractVariableLeaf):
            domain_datatype = type(getattr(domain, 'dataType', None))

            if domain_datatype is None:
                raise TypeError("Mutator domain dataType (DATA_TYPE) not set")

            if not (isinstance(domain_datatype, self.DATA_TYPE) or issubclass(domain_datatype, self.DATA_TYPE)):
                raise TypeError("Mutator domain dataType should be of type '{}'. Received object: '{}'"
                                .format(self.DATA_TYPE, domain_datatype))

        self._domain = domain

    @property
    def lengthBitSize(self):
        return self._lengthBitSize

    @lengthBitSize.setter  # type: ignore
    def lengthBitSize(self, lengthBitSize):
        if lengthBitSize is not None and not isinstance(lengthBitSize, UnitSize):
            raise Exception("lengthBitSize parameter should be an element of the enum UnitSize")
        self._lengthBitSize = lengthBitSize


## Unit tests
    
def _test():
    """

    Test constructor with different parameters:

    >>> from netzob.all import *
    >>> from netzob.Fuzzing.Mutators.IntegerMutator import IntegerMutator
    >>> domain = Data(Integer())
    >>> d = IntegerMutator(domain)
    >>> type(d)
    <class 'netzob.Fuzzing.Mutators.IntegerMutator.IntegerMutator'>

    >>> d = IntegerMutator(domain, mode=MutatorMode.MUTATE)
    >>> type(d)
    <class 'netzob.Fuzzing.Mutators.IntegerMutator.IntegerMutator'>

    >>> d = IntegerMutator(domain, generator=Generator.NG_mt19937)
    >>> type(d)
    <class 'netzob.Fuzzing.Mutators.IntegerMutator.IntegerMutator'>
    >>> type(d.generator)
    <class 'itertools.starmap'>

    >>> d = IntegerMutator(domain, seed=42)
    >>> type(d)
    <class 'netzob.Fuzzing.Mutators.IntegerMutator.IntegerMutator'>
    >>> d.seed
    42

    >>> d = IntegerMutator(domain, counterMax=42)
    >>> type(d)
    <class 'netzob.Fuzzing.Mutators.IntegerMutator.IntegerMutator'>
    >>> d.counterMax
    42

        """
