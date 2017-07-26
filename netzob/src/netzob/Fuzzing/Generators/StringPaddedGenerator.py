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
from netzob.Fuzzing.Generator import Generator
from netzob.Common.Utils.Decorators import typeCheck


class StringPaddedGenerator(Generator):
    r"""Generates string values.

    >>> from netzob.all import *
    >>> seed = 1234
    >>> stringLength = Field(uint16le())
    >>> lengthMutator = IntegerMutator(
    ...     domain=stringLength.domain,
    ...     interval=(5, 25),
    ...     seed=seed)
    >>> genObject = StringPaddedGenerator(lengthMutator,
    ...     StringPaddedGenerator.DEFAULT_NAUGHTY_STRINGS)
    >>> genObject.updateSeed(seed)
    >>> genObject.getNewValue()
    '`ls -al\x00'
    """

    DEFAULT_NAUGHTY_STRINGS = [
        'System("ls -al /")',
        '`ls -al /`',
        'Kernel.exec("ls -al /")',
        'Kernel.exit(1)',
        '%x("ls -al /")',
        '<img \\x00src=x onerror="alert(1)">',
        '$ENV{"HOME"}',
        '%d',
        '%s']

    def __init__(self,
                 lengthMutator,
                 stringsList):
        super().__init__(values=stringsList)
        self._lengthMutator = lengthMutator

    def reset(self):
        """Reset the current position in the list.

        :type: :class:`set`
        """
        self.updateSeed(0)

    @typeCheck(int)
    def updateSeed(self, seedValue):
        super().updateSeed(seedValue % len(self._values))

    def getNewValue(self, endChar='\0'):
        """This is the method to get a new string value from the list.

        :return: a generated str value
        :rtype: :class:`str`
        """
        if self._seed >= len(self._values):
            self.reset()
        value = self._values[self._seed] + endChar
        self._seed += 1
        lm = self._lengthMutator
        lm_dom = lm.getDomain()
        length = int.from_bytes(lm.generate(),
                                lm_dom.dataType.endianness.value)
        if length > 0:
            if length > len(value):
                # Complete the string with padding characters to have the good
                # length
                value = value + (" " * (length - len(value)))
            else:
                # truncate the too long string value to length characters
                value = value[:length-1] + endChar
        else:
            value = ""
        return value
