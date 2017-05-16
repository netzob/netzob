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

# +---------------------------------------------------------------------------+
# | Related third party imports                                               |
# +---------------------------------------------------------------------------+

# +---------------------------------------------------------------------------+
# | Local application imports                                                 |
# +---------------------------------------------------------------------------+
from netzob.Fuzzing.Mutator import Mutator
from netzob.Fuzzing.DeterministGenerator import DeterministGenerator
from netzob.Model.Vocabulary.Types.Integer import Integer
from netzob.Model.Vocabulary.Types.AbstractType import AbstractType
from netzob.Model.Vocabulary.AbstractField import AbstractField

from typing import Iterable


class DeterministIntegerMutator(Mutator):
    """The integer mutator, using determinist generator.

    >>> from netzob.all import *
    >>> mutator = DeterministIntegerMutator()
    >>> intField = uint16le()
    >>> mutator.field = intField
    >>> dataHex = mutator.mutate()

    """

    def __init__(self, minValue=None, maxValue=None):
        super().__init__()
        self._field = None
        self._minValue = minValue
        self._maxValue = maxValue
        self._ng = DeterministGenerator()

    @property
    def field(self):
        """The field to which the mutation is applied.
        When setting the field, the determinist values are generated.

        :type: :class:`AbstractField <netzob.Model.Vocabulary.AbstractField>`
        """
        return self._field

    @field.setter
    def field(self, abstractField):
        self._field = abstractField
        if abstractField is None:
            raise Exception("Field is None")
        if not isinstance(abstractField.domain.dataType, Integer):
            raise Exception("Field does not correspond to an Integer")

        # Retrieve the min and max values from the field properties
        fieldType = abstractField.domain.dataType
        interval = fieldType.interval
        if interval is not None:
            if isinstance(interval, Iterable) and len(interval) == 2:
                low, high = interval
                if self._minValue is None or low > self._minValue:
                    self._minValue = low
                if self._maxValue is None or high < self._maxValue:
                    self._maxValue = high

        if (fieldType.unitSize == AbstractType.UNITSIZE_1 or
            fieldType.unitSize == AbstractType.UNITSIZE_4 or
            fieldType.unitSize == AbstractType.UNITSIZE_8 or
            fieldType.unitSize == AbstractType.UNITSIZE_16 or
            fieldType.unitSize == AbstractType.UNITSIZE_32 or
            fieldType.unitSize == AbstractType.UNITSIZE_64):

            if fieldType.sign == AbstractType.SIGN_UNSIGNED:
                if self._minValue is None or self._minValue < 0:
                    self._minValue = 0
                if self._maxValue is None:
                    self._maxValue = 2**int(fieldType.unitSize) - 1
            else:
                low = -int((2**int(fieldType.unitSize))/2)
                high = -low - 1
                if self._minValue is None or self._minValue < low:
                    self._minValue = low
                if self._maxValue is None or self._maxValue > high:
                    self._maxValue = high
        if isinstance(self._ng, DeterministGenerator):
            self._ng.createValues(self._minValue,
                                  self._maxValue,
                                  int(fieldType.unitSize),
                                  fieldType.sign == AbstractType.SIGN_SIGNED)

    def reset(self):
        self._ng.reset()
        self.resetCurrentCounter()

    def getValueAt(self, position):
        """Returns the value at the given position in the list of determinist values.
        if **position** is outside of the list, it returns **None**.

        :return: the value at the given position
        :rtype: :class:`int`
        """
        if self.field is not None:
            value = self._ng.getValueAt(position)
            return Integer.decode(value,
                                  unitSize=self.field.domain.dataType.unitSize,
                                  endianness=self.field.domain.dataType.endianness,
                                  sign=self.field.domain.dataType.sign)
        else:
            raise Exception("Field to mutate not set")

    def getNbValues(self):
        """Returns the number of determinist values generated for the field.

        :return: the number of determinist values
        :rtype: :class:`int`
        """
        return len(self._ng.values)

    def mutate(self):
        """This is the mutation method of the integer field.
        It uses a determinist generator to produce the value.

        :return: a generated content represented with bytes
        :rtype: :class:`bytes`
        """
        if self.field is not None:
            if self._currentCounter < self.counterMax:
                self._currentCounter += 1
                value = self._ng.getNewValue()
                return Integer.decode(value,
                                      unitSize=self.field.domain.dataType.unitSize,
                                      endianness=self.field.domain.dataType.endianness,
                                      sign=self.field.domain.dataType.sign)
            else:
                raise Exception("Max mutation counter reached")
        else:
            raise Exception("Field to mutate not set")
