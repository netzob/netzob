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
from typing import Tuple  # noqa: F401

# +---------------------------------------------------------------------------+
# | Related third party imports                                               |
# +---------------------------------------------------------------------------+

# +---------------------------------------------------------------------------+
# | Local application imports                                                 |
# +---------------------------------------------------------------------------+
from netzob.Fuzzing.Mutator import Mutator, MutatorMode, center
from netzob.Fuzzing.Mutators.DomainMutator import DomainMutator, MutatorInterval
from netzob.Fuzzing.Mutators.IntegerMutator import IntegerMutator
from netzob.Fuzzing.Generator import Generator
from netzob.Fuzzing.Generators.GeneratorFactory import GeneratorFactory
from netzob.Fuzzing.Generators.DeterministGenerator import DeterministGenerator
from netzob.Fuzzing.Generators.StringPaddedGenerator import StringPaddedGenerator
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger
from netzob.Model.Vocabulary.Types.AbstractType import UnitSize
from netzob.Model.Vocabulary.Types.Integer import uint16le
from netzob.Model.Vocabulary.Types.String import String
from netzob.Model.Vocabulary.Field import Field


@NetzobLogger
class StringMutator(DomainMutator):
    r"""The string mutator, using a determinist generator to get a string length.
    The generated string shall not be longer than 2^16 bytes.

    The fuzzing of strings provides the following capabilities:

    * Data coming from dictionaries of naughty strings will be
      inserted in strings.
    * Data coming from dictionaries of malformed code points will be
      inserted in Unicode strings.
    * If a string contains a terminal character, this character will be
      repeated or inserted at regular intervals.
    * If a string contains a terminal character encoded in multiple
      bytes, this character will be truncated.


    The StringMutator constructor expects some parameters:

    :param domain: The domain of the field to mutate.
    :param mode: If set to :attr:`MutatorMode.GENERATE <netzob.Fuzzing.DomainMutator.MutatorMode.GENERATE>`, :meth:`generate` will be
        used to produce the value.
        If set to :attr:`MutatorMode.MUTATE <netzob.Fuzzing.DomainMutator.MutatorMode.MUTATE>`, :meth:`mutate` will be used to
        produce the value (not used yet).
        Default value is :attr:`MutatorMode.GENERATE <netzob.Fuzzing.DomainMutator.MutatorMode.GENERATE>`.
    :param endchar: The character(s) ending the string.
        Default value is :attr:`DEFAULT_END_CHAR`. It is used to set the eos parameter of :class:`String <netzob.Model.Vocabulary.Types.String>`.
        This terminal symbol will be mutated by truncating its value if defined on several bytes.
    :param interval: The scope of string length to generate. If set to
        (min, max), the values will be generated between min and max.
        Default value is **(None, None)**.
    :param lengthBitSize: The size in bits of the memory on which the generated
        length will be encoded.
    :param naughtyStrings: The list of potentially dangerous strings.
        Default value is :attr:`DEFAULT_NAUGHTY_STRINGS`.
    :type domain: :class:`AbstractVariable
        <netzob.Model.Vocabulary.Domain.Variables.AbstractVariable>`, required
    :type mode: :class:`int`, optional
    :type endchar: :class:`str`, optional
    :type interval: :class:`tuple`, optional
    :type lengthBitSize: :class:`int`, optional
    :type naughtyStrings: :class:`list` of :class:`str`, optional


    The following example shows how to generate a string with a length in
    [35, 60] interval, the smaller one between the field domain and the length
    given to the constructor of StringMutator:

    >>> from netzob.all import *
    >>> fieldString = Field(String(nbChars=(5, 8)))
    >>> mutator = StringMutator(fieldString.domain, interval=(5, 12), seed=10)
    >>> mutator.generate()
    b'`ls -al /`\x00 '

    Constant definitions:
    """

    DEFAULT_END_CHAR = '\0'
    PADDING_CHAR = ' '
    DATA_TYPE = String

    def __init__(self,
                 domain,
                 mode=MutatorMode.GENERATE,
                 generator=Generator.NG_mt19937,
                 seed=Mutator.SEED_DEFAULT,
                 counterMax=Mutator.COUNTER_MAX_DEFAULT,
                 endchar=DEFAULT_END_CHAR,  # type: str
                 interval=MutatorInterval.DEFAULT_INTERVAL,
                 lengthBitSize=None,
                 naughtyStrings=None):
        # type: (...) -> None

        # Call parent init
        super().__init__(domain,
                         mode=mode,
                         generator=generator,
                         seed=seed,
                         counterMax=counterMax,
                         lengthBitSize=lengthBitSize)

        # Variables
        self.naughtyStrings = naughtyStrings

        # Initialize length generator
        model_min = int(self.domain.dataType.size[0] / 8)
        model_max = int(self.domain.dataType.size[1] / 8)
        model_unitSize = self.domain.dataType.unitSize
        self._initializeLengthGenerator(interval, (model_min, model_max), model_unitSize)

        # Initialize data generator
        self.generator = StringPaddedGenerator(seed = self.seed,
                                               lengthGenerator = self._lengthGenerator,
                                               stringsList = self.naughtyStrings,
                                               endchar = endchar,
                                               minLength = self._minLength,
                                               maxLength = self._maxLength)


    ## Properties

    @property
    def naughtyStrings(self):
        """
        Property (getter).
        The string list to use for the mutation.

        :type: :class:`list`
        """
        return self._naughtyStrings

    @naughtyStrings.setter  # type: ignore
    def naughtyStrings(self, naughtyStrings):
        if not isinstance(naughtyStrings, list):
            self._naughtyStrings = StringPaddedGenerator.DEFAULT_NAUGHTY_STRINGS
        else:
            self._naughtyStrings = naughtyStrings


    ## API methods

    def generate(self):
        """This is the fuzz generation method of the string field.

        :return: a generated content represented with bytes
        :rtype: :class:`bytes`
        """
        # Call parent generate() method
        super().generate()

        # Choose the next string
        value = next(self.generator)

        # Conversion
        return String.decode(value,
                             unitSize = self.domain.dataType.unitSize,
                             endianness = self.domain.dataType.endianness,
                             sign = self.domain.dataType.sign)

    def mutate(self, data):
        raise NotImplementedError
