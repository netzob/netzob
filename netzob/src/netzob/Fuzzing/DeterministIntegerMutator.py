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
from typing import Iterable

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
from netzob.Model.Vocabulary.Domain.Variables.AbstractVariable import AbstractVariable


class DeterministIntegerMutator(Mutator):
    """The integer mutator, using determinist generator.

    >>> from netzob.all import *
    >>> mutator = DeterministIntegerMutator()
    >>> intField = uint16le()
    >>> dataHex = mutator.mutate(intField.domain)

    """

    def __init__(self, domain, interval=None, mode=None):
        # Sanity checks
        if domain is None:
            raise Exception("Domain should be known to initialize a mutator")
        if not isinstance(domain, AbstractVariable):
            raise Exception("Mutator domain should be of type AbstractVariable. Received object: '{}'".format(domain))
        if not hasattr(domain, 'dataType'):
            raise Exception("Mutator domain should have a dataType Integer")
        if not isinstance(domain.dataType, Integer):
            raise Exception("Mutator domain dataType should be an Integer, not '{}'".format(type(domain.dataType)))

        # Find min and max potential values for interval
        minValue = 0
        maxValue = 0
        if isinstance(interval, tuple) and len(interval) == 2 and isinstance(interval[0], int) and isinstance(interval[1], int):
            # Handle desired interval according to the storage space of the domain dataType
            minValue = max(interval[0], domain.dataType.getMinStorageValue())
            maxValue = min(interval[1], domain.dataType.getMinStorageValue())
        elif (interval == Mutator.DEFAULT_INTERVAL or interval is None) and hasattr(domain, 'dataType'):
            minValue = domain.dataType.getMinValue()
            maxValue = domain.dataType.getMaxValue()
        elif interval == Mutator.FULL_INTERVAL and hasattr(domain, 'dataType'):
            minValue = domain.dataType.getMinStorageValue()
            maxValue = domain.dataType.getMaxStorageValue()
        else:
            raise Exception("Not enough information to generate the mutated data")
        self._minValue = minValue
        self._maxValue = maxValue

        # Call parent init
        super().__init__(domain=domain, mode=mode)
        
        # Initialize values to generate
        self._ng = DeterministGenerator()
        self._ng.createValues(self._minValue,
                              self._maxValue,
                              domain.dataType.unitSize,
                              domain.dataType.sign == AbstractType.SIGN_SIGNED)

    def reset(self):
        self._ng.reset()
        self.resetCurrentCounter()

    def getValueAt(self, position):
        """Returns the value at the given position in the list of determinist values.
        if **position** is outside of the list, it returns **None**.

        :return: the value at the given position
        :rtype: :class:`int`
        """
        value = self._ng.getValueAt(position)
        return Integer.decode(value,
                              unitSize=self.field.domain.dataType.unitSize,
                              endianness=self.field.domain.dataType.endianness,
                              sign=self.field.domain.dataType.sign)

    def getNbValues(self):
        """Returns the number of determinist values generated for the field domain.

        :return: the number of determinist values
        :rtype: :class:`int`
        """
        return len(self._ng.values)

    def generate(self, domain):
        """This is the fuzz generation method of the integer field domain.
        It uses a determinist generator to produce the value.

        :return: a generated content represented with bytes
        :rtype: :class:`bytes`
        """
        if self._currentCounter < self.counterMax:
            self._currentCounter += 1
            value = self._ng.getNewValue()
            return Integer.decode(value,
                                  unitSize=domain.dataType.unitSize,
                                  endianness=domain.dataType.endianness,
                                  sign=domain.dataType.sign)
        else:
            raise Exception("Max mutation counter reached")
