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
from netzob.Fuzzing.DomainMutator import DomainMutator
from netzob.Common.Utils.Decorators import typeCheck
from netzob.Fuzzing.DeterministIntegerMutator import (
    DeterministIntegerMutator)
from netzob.Model.Vocabulary.Types.Integer import uint16le
from netzob.Model.Vocabulary.Field import Field
from netzob.Model.Vocabulary.Domain.Variables.Nodes.Repeat import Repeat


class SequenceMutator(DomainMutator):
    """The sequence mutator, using a determinist generator to get a sequence
    length.

    The SequenceMutator constructor expects some parameters:

    :param domain: The domain of the field to mutate.
    :param mode: If set to **MutatorMode.GENERATE**, the generate() method will be
        used to produce the value.
        If set to **MutatorMode.MUTATE**, the mutate() method will be used to
        produce the value (not implemented).
        Default value is **MutatorMode.GENERATE**.
    :param mutateChild: If true, sub-field has to be mutated.
        Default value is **False**.
    :param length: The scope of sequence length to generate. If set to
        (min, max), the values will be generate between min and max.
        Default value is **(None, None)**.
    :param lengthBitSize: The size in bits of the memory on which the generated
        length will be encoded.
    :type domain: :class:`AbstractVariable
        <netzob.Model.Vocabulary.Domain.Variables.AbstractVariable>`, required
    :type mode: :class:`int`, optional
    :type mutateChild: :class:`bool`, optional
    :type length: :class:`tuple`, optional
    :type lengthBitSize: :class:`int`, optional

    >>> from netzob.all import *
    >>> child = Data(dataType=String("abc"), svas=SVAS.PERSISTENT)
    >>> fieldRepeat = Field(Repeat(child, nbRepeat=3))
    >>> mutator = SequenceMutator(fieldRepeat.domain, length=(0, 30), seed=10)
    >>> mutator.generate()
    >>> mutator.sequenceLength
    16
    >>> mutator.generate()
    >>> mutator.sequenceLength
    17
    >>> mutator.generate()
    >>> mutator.sequenceLength
    31

    Constant definitions:
    """

    # Constants
    DEFAULT_MIN_LENGTH = 0
    DEFAULT_MAX_LENGTH = 10
    DOMAIN_TYPE = Repeat

    def __init__(self,
                 domain,
                 mutateChild=False,
                 length=(None, None),
                 lengthBitSize=None,
                 **kwargs):
        # Call parent init
        super().__init__(domain, **kwargs)

        if isinstance(length, tuple) and len(length) == 2:
            if all(isinstance(_, int) for _ in length):
                self._minLength, self._maxLength = length
            else:
                self._minLength, self._maxLength = (0, 0)
        if isinstance(domain.nbRepeat, tuple):
            # Handle desired length according to the domain information
            self._minLength = max(self._minLength, int(domain.nbRepeat[0]))
            self._maxLength = min(self._maxLength, int(domain.nbRepeat[1]))
        if self._minLength is None or self._maxLength is None:
            self._minLength = self.DEFAULT_MIN_LENGTH
            self._maxLength = self.DEFAULT_MAX_LENGTH

        self._mutateChild = mutateChild

        self._sequenceLengthField = Field(uint16le())
        self._lengthMutator = DeterministIntegerMutator(
            domain=self._sequenceLengthField.domain,
            interval=(self._minLength, self._maxLength),
            bitsize=lengthBitSize,
            **kwargs)
        self._sequenceLength = None

        self._seed = 0

    @typeCheck(int)
    def updateSeed(self, seedValue):
        super().updateSeed(seedValue)
        self._lengthMutator.updateSeed(seedValue)

    @property
    def sequenceLength(self):
        """
        Property (getter).
        The last generated length of the sequence.

        :rtype: int
        :raises: :class:`ValueError` if _randomType is None
        """
        if self._sequenceLength is None:
            raise ValueError("Random type is None : generate() has to be \
called, first")
        return self._sequenceLength

    def generate(self):
        """This is the fuzz generation method of the sequence field.
        It generates a sequence length by using lengthMutator.
        To access this length value, use **sequenceLength** property.

        :return: None
        :rtype: :class:`None`
        """
        # Call parent generate() method
        super().generate()

        self._sequenceLength = self._lengthMutator.generateInt()
        return None

    def mutate(self, data):
        raise NotImplementedError
