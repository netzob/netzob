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
from netzob.Fuzzing.Mutator import Mutator
from netzob.Common.Utils.Decorators import typeCheck
from netzob.Fuzzing.DeterministIntegerMutator import (
    DeterministIntegerMutator)
from netzob.Model.Vocabulary.Types.Integer import uint16le
from netzob.Model.Vocabulary.Types.Integer import Integer
from netzob.Model.Vocabulary.Field import Field
from netzob.Fuzzing.Xorshift128plus import Xorshift128plus
from netzob.Model.Vocabulary.Types.TypeConverter import TypeConverter
from netzob.Model.Vocabulary.Types.BitArray import BitArray
from netzob.Model.Vocabulary.Types.AbstractType import AbstractType
from netzob.Model.Vocabulary.Domain.Variables.AbstractVariable import AbstractVariable

from bitarray import bitarray


class BinarySequenceMutator(Mutator):
    """The binary sequence mutator, using pseudo-random generator.
    The generated sequence shall not be longer than 2^32 bits.

    The BinarySequenceMutator constructor expects some parameters:

    :param domain: The domain of the field to mutate.
    :param mode: If set to **Mutator.GENERATE**, the generate() method will be
        used to produce the value.
        If set to **Mutator.MUTATE**, the mutate() method will be used to
        produce the value (not implemented).
        Default value is **Mutator.GENERATE**.
    :param length: The scope of sequence length to generate. If set to
        (min, max), the values will be generate between min and max.
        Default value is **(None, None)**.
    :param lengthBitSize: The size in bits of the memory on which the generated
        length will be encoded.
    :type domain: :class:`AbstractVariable
        <netzob.Model.Vocabulary.Domain.Variables.AbstractVariable>`, required
    :type mode: :class:`int`, optional
    :type length: :class:`tuple`, optional
    :type lengthBitSize: :class:`int`, optional

    The following example shows how to generate a binary sequence with a length
    in [0, 30] interval:

    >>> from netzob.all import *
    >>> fieldBits = Field(BitArray())
    >>> mutator = BinarySequenceMutator(fieldBits.domain, length=(0,30))
    >>> mutator.seed = 19
    >>> mutator.generate()
    bitarray('00000000000000000000000000000000000010011000000000000100110100110')

    """

    DEFAULT_MIN_LENGTH = 0
    DEFAULT_MAX_LENGTH = 100

    def __init__(self,
                 domain,
                 mode=None,
                 length=(None, None),
                 lengthBitSize=None):
        # Sanity checks
        if domain is None:
            raise Exception("Domain should be known to initialize a mutator")
        if not isinstance(domain, AbstractVariable):
            raise Exception("Mutator domain should be of type AbstractVariable. Received object: '{}'".format(domain))
        if not hasattr(domain, 'dataType'):
            raise Exception("Mutator domain should have a dataType")
        if not isinstance(domain.dataType, BitArray):
            raise Exception("Mutator domain dataType should be an Integer, not '{}'".format(type(domain.dataType)))

        # Call parent init
        super().__init__(domain=domain, mode=mode)

        if isinstance(length, tuple) and \
           len(length) == 2 and \
           isinstance(length[0], int) and \
           isinstance(length[1], int):
            self._minLength = length[0]
            self._maxLength = length[1]
        if isinstance(domain.dataType.size, tuple) and \
           len(domain.dataType.size) == 2 and \
           isinstance(domain.dataType.size[0], int) \
           and isinstance(domain.dataType.size[1], int):
            # Handle desired interval according to the storage space of the domain dataType
            self._minLength = max(self._minLength, domain.dataType.size[0])
            self._maxLength = min(self._maxLength, domain.dataType.size[1])
        if self._minLength is None or self._maxLength is None:
            self._minLength = BinarySequenceMutator.DEFAULT_MIN_LENGTH
            self._maxLength = BinarySequenceMutator.DEFAULT_MAX_LENGTH

        self._sequenceLength = Field(uint16le())
        self._lengthMutator = DeterministIntegerMutator(
            domain=self._sequenceLength.domain,
            mode=mode,
            interval=(self._minLength, self.maxLength),
            bitsize=lengthBitSize)
        self._prng = Xorshift128plus(self.seed)

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
        self._lengthMutator.seed = self._seed
        self._prng.seed = self._seed

    @property
    def lengthMutator(self):
        """The mutator used to generate the sequence length, between
        MIN_LENGTH and maxLength.

        :type: :class:`DeterministIntegerMutator <netzob.Fuzzing.DeterministIntegerMutator>`
        """
        return self._lengthMutator

    @property
    def minLength(self):
        """The min length of the binary sequence. Default value is DEFAULT_MIN_LENGTH.

        :type: :class:`int`
        """
        return self._minLength

    @property
    def maxLength(self):
        """The max length of the binary sequence. Default value is DEFAULT_MAX_LENGTH.

        :type: :class:`int`
        """
        return self._maxLength

    def getLength(self):
        """The length of the last generated sequence.

        :rtype: :class:`int`
        """
        return self._sequenceLength.value

    def generate(self):
        """This is the fuzz generation method of the binary sequence field.
        It uses lengthMutator to get a sequence length, then a PRNG to produce
        the value.

        :return: a generated content represented with bytes
        :rtype: :class:`bytes`
        """
        length = int.from_bytes(self._lengthMutator.generate(),
                                self._lengthMutator.domain.dataType.endianness)

        valueBits = bitarray()
        if length == 0:
            return valueBits
        while True:
            valueInt = self._prng.getNew64bitsValue()
            bits = TypeConverter.convert(data=valueInt,
                                         sourceType=Integer,
                                         destinationType=BitArray,
                                         src_unitSize=AbstractType.UNITSIZE_64,
                                         src_sign=AbstractType.SIGN_UNSIGNED,
                                         dst_sign=AbstractType.SIGN_UNSIGNED)
            valueBits += bits
            if len(valueBits) >= length:
                break
        return valueBits[:length]
