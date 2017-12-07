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
from netzob.Fuzzing.Mutator import center
from netzob.Fuzzing.Generator import Generator
from netzob.Fuzzing.Generators.DeterministGenerator import DeterministGenerator
from netzob.Fuzzing.Generators.GeneratorFactory import GeneratorFactory
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger


@NetzobLogger
class StringPaddedGenerator(Generator):
    r"""Generates string values.

    >>> from netzob.all import *
    >>> seed = 1234
    >>> lengthGenerator = GeneratorFactory.buildGenerator(DeterministGenerator.NG_determinist,
    ...     seed = seed,
    ...     minValue = 10,
    ...     maxValue = 20,
    ...     bitsize = 8,
    ...     signed = False)
    >>> genObject = StringPaddedGenerator(seed = seed,
    ...     lengthGenerator = lengthGenerator,
    ...     stringsList = StringPaddedGenerator.DEFAULT_NAUGHTY_STRINGS)
    >>> next(genObject)
    'Kernel.exit(1)\x00                                                                                                                                                                                                                                               '
    """

    NG_stringpadded = "stringpadded"
    name = NG_stringpadded

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
                 seed = 0,
                 lengthGenerator = DeterministGenerator.NG_determinist,
                 stringsList = DEFAULT_NAUGHTY_STRINGS,
                 endchar = '\0',
                 minLength = None,
                 maxLength = None):

        # Call parent init
        super().__init__(seed=seed)

        # Variables from parameters
        self._endchar = endchar
        self._values = stringsList
        self._minLength = minLength
        self._maxLength = maxLength

        # Initialize length generator
        self.lengthGenerator = GeneratorFactory.buildGenerator(lengthGenerator, seed=self.seed)

    def __iter__(self):
        return self

    def __next__(self):
        """This is the method to get a new string value from the list.

        :return: a generated str value
        :rtype: :class:`str`
        """
        index = next(self.lengthGenerator) % len(self._values)

        # Generate the initial value
        value = self._values[index] + self._endchar

        # Generate length of random data
        if self.lengthGenerator is not None:
            length = next(self.lengthGenerator)
        else:
            raise Exception("Length generator not initialized")

        if self._minLength is not None and self._maxLength is not None:
            length = center(length, self._minLength, self._maxLength)

        # Adapt the initial value according to the final length
        if length > 0:
            if length > len(value):
                # Complete the string with padding characters to have the good
                # length
                value = value + (" " * (length - len(value)))
            else:
                # truncate the too long string value to length characters
                value = value[:length-1] + self._endchar
        else:
            value = ""
        return value
