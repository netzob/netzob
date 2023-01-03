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
try:
    from typing import Tuple  # noqa: F401
except ImportError:
    pass
import string

# +---------------------------------------------------------------------------+
# | Related third party imports                                               |
# +---------------------------------------------------------------------------+

# +---------------------------------------------------------------------------+
# | Local application imports                                                 |
# +---------------------------------------------------------------------------+
from netzob.Fuzzing.Mutator import Mutator, FuzzingMode
from netzob.Fuzzing.Mutators.DomainMutator import DomainMutator, FuzzingInterval
from netzob.Fuzzing.Generators.GeneratorFactory import GeneratorFactory
from netzob.Common.Utils.Decorators import NetzobLogger
from netzob.Model.Vocabulary.Types.AbstractType import AbstractType
from netzob.Model.Vocabulary.Types.String import String


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
    :param mode: If set to :attr:`FuzzingMode.GENERATE <netzob.Fuzzing.DomainMutator.FuzzingMode.GENERATE>`, :meth:`generate` will be
        used to produce the value.
        If set to :attr:`FuzzingMode.MUTATE <netzob.Fuzzing.DomainMutator.FuzzingMode.MUTATE>`, :meth:`mutate` will be used to
        produce the value (not used yet).
        Default value is :attr:`FuzzingMode.GENERATE <netzob.Fuzzing.DomainMutator.FuzzingMode.GENERATE>`.
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
    :type domain: :class:`Variable
        <netzob.Model.Vocabulary.Domain.Variables.AbstractVariable.AbstractVariable>`, required
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
    b'Syste\x00'
    >>> mutator.generate()
    b'$ENV{"\x00'
    >>> mutator.generate()
    b'%x("\x00'


    Constant definitions:
    """

    DEFAULT_END_CHAR = '\0'
    PADDING_CHAR = ' '
    DATA_TYPE = String

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
                 domain,
                 mode=FuzzingMode.GENERATE,
                 generator='xorshift',
                 seed=Mutator.SEED_DEFAULT,
                 counterMax=DomainMutator.COUNTER_MAX_DEFAULT,
                 endChar=DEFAULT_END_CHAR,  # type: str
                 interval=FuzzingInterval.FULL_INTERVAL,
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

        if self.mode == FuzzingMode.FIXED:
            self.generator = generator
        else:
            # Configure generator

            # Variables
            self.naughtyStrings = naughtyStrings
            self.endChar = endChar

            # Initialize data generator
            self.generator = GeneratorFactory.buildGenerator(self.generator, seed=self.seed, minValue=0, maxValue=len(self.naughtyStrings) - 1)

            # Initialize length generator
            model_min = int(self.domain.dataType.size[0] / 8)
            model_max = int(self.domain.dataType.size[1] / 8)
            model_unitSize = self.domain.dataType.unitSize
            self._initializeLengthGenerator(generator, interval, (model_min, model_max), model_unitSize)

    def copy(self):
        r"""Return a copy of the current mutator.

        >>> from netzob.all import *
        >>> f = Field(String())
        >>> m = StringMutator(f.domain).copy()
        >>> m.mode
        FuzzingMode.GENERATE

        """
        m = StringMutator(self.domain,
                          mode=self.mode,
                          generator=self.generator,
                          seed=self.seed,
                          counterMax=self.counterMax,
                          naughtyStrings=self.naughtyStrings,
                          endChar=self.endChar,
                          lengthBitSize=self.lengthBitSize)
        return m

    def count(self):
        r"""

        >>> from netzob.all import *
        >>> f = Field(String())
        >>> StringMutator(f.domain).count()
        86400000000

        >>> f = Field(String(nbChars=4))
        >>> StringMutator(f.domain).count()
        100000000

        >>> f = Field(String(nbChars=(1, 2)))
        >>> StringMutator(f.domain).count()
        10100

        >>> f = Field(String("hello"))
        >>> StringMutator(f.domain).count()
        10000000000

        """

        if self.mode == FuzzingMode.FIXED:
            count = 1
        else:
            range_min = int(self.domain.dataType.size[0] / 8)
            range_max = int(self.domain.dataType.size[1] / 8)
            permitted_values = len(string.printable)
            count = 0
            for i in range(range_min, range_max + 1):
                count += permitted_values ** i
                if count > AbstractType.MAXIMUM_POSSIBLE_VALUES:
                    return AbstractType.MAXIMUM_POSSIBLE_VALUES
        return count

    def generate(self):
        """This is the fuzz generation method of the string field.

        :return: a generated content represented with bytes
        :rtype: :class:`bytes`
        """
        # Call parent generate() method
        if self.mode != FuzzingMode.FIXED:
            super().generate()

        if self.mode == FuzzingMode.FIXED:
            valueBytes = next(self.generator)
        else:

            # Choose the string to mutate
            index = next(self.generator)
            value = self.naughtyStrings[index] + self.endChar

            # Generate length of random data
            length = next(self._lengthGenerator)

            # Adapt the initial value according to the final length
            if length > 0:
                if length > len(value):
                    # Complete the string with padding characters to have the good
                    # length
                    value = value + (" " * (length - len(value)))
                else:
                    # truncate the too long string value to length characters
                    value = value[:length - 1] + self.endChar
            else:
                value = ""
            valueData = value.encode('utf-8')
            valueBytes = String.decode(valueData,
                                       unitSize=self.domain.dataType.unitSize,
                                       endianness=self.domain.dataType.endianness,
                                       sign=self.domain.dataType.sign)

        # Conversion
        return valueBytes

    def mutate(self, data):
        raise NotImplementedError

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
            self._naughtyStrings = StringMutator.DEFAULT_NAUGHTY_STRINGS
        else:
            self._naughtyStrings = naughtyStrings

    @property
    def endChar(self):
        return self._endChar

    @endChar.setter  # type: ignore
    def endChar(self, endChar):
        self._endChar = endChar


def _test():
    r"""

    >>> from netzob.all import *
    >>> f = Field(String(nbChars=(35, 60)))
    >>> f.domain.dataType.unitSize
    UnitSize.SIZE_16
    >>> mutator = StringMutator(f.domain)
    >>> mutator._minLength
    0
    >>> len(mutator.generate())
    65536
    >>> len(mutator.generate())
    65535
    >>> len(mutator.generate())
    65534

    """


def _test_string_length():
    r"""
    # Fuzzing of String: ensure that StringMutator always give positive length and that the maximum is defined by a bit number

    >>> from netzob.all import *
    >>> from netzob.Fuzzing.Mutators.StringMutator import StringMutator

    >>> fieldString = Field(String(nbChars=(35, 60)))
    >>> len_list = []
    >>> mutator = StringMutator(fieldString.domain, seed=10, lengthBitSize=UnitSize.SIZE_8)
    >>> len_list.append(len(mutator.generate()))
    >>> mutator = StringMutator(fieldString.domain, seed=10, lengthBitSize=UnitSize.SIZE_16)
    >>> len_list.append(len(mutator.generate()))
    >>> mutator = StringMutator(fieldString.domain, seed=10, lengthBitSize=UnitSize.SIZE_4)
    >>> len_list.append(len(mutator.generate()))
    >>> len_list
    [256, 65536, 16]
    >>> len_is_good = True
    >>> for _ in range(70):
    ...     if len(mutator.generate()) < 0:
    ...         len_is_good = False
    >>> len_is_good
    True

    """


def _test_string_values():
    r"""

    # Fuzzing of String: ensure that value used is generated by: naughty string, end of string symbol, code point lib, truncated version of end of string symbol
    # TODO: value from code point (invalid unicode) and truncated value of eos symbol...

    >>> from netzob.all import *
    >>> from netzob.Fuzzing.Mutators.StringMutator import StringMutator

    >>> fieldString = Field(String(nbChars=(35, 60)))
    >>> eos_symbol = '123456789'
    >>> mutator = StringMutator(fieldString.domain, seed=10, lengthBitSize=UnitSize.SIZE_8, endChar=eos_symbol)
    >>> naughty_string = StringMutator.DEFAULT_NAUGHTY_STRINGS

    >>> has_naughty_str = False
    >>> has_several_eos_symbol = False
    >>> for _ in range(20):
    ...     a_str = mutator.generate()
    ...     for ns in naughty_string:
    ...         if ns in a_str.decode():
    ...             has_naughty_str = True
    ...     idx = a_str.find(eos_symbol.encode())
    ...     if idx != -1:
    ...         if a_str[idx :].find(eos_symbol.encode()) != -1:
    ...             has_several_eos_symbol = True

    >>> has_naughty_str
    True
    >>> has_several_eos_symbol
    True
    """


def _test_fixed():
    r"""

    Reset the underlying random generator

    >>> from netzob.all import *
    >>> Conf.apply()


    **Fixing the value of a field**

    >>> from netzob.all import *
    >>> f1 = Field(String(nbChars=1))
    >>> symbol = Symbol([f1], name="sym")
    >>> preset = Preset(symbol)
    >>> preset[f1] = '\x41'
    >>> messages_gen = symbol.specialize(preset)
    >>> next(messages_gen)
    b'A'
    >>> next(messages_gen)
    b'A'
    >>> next(messages_gen)
    b'A'


    **Fixing the value of a sub-field**

    >>> from netzob.all import *
    >>> f1 = Field(String(nbChars=1))
    >>> f2_1 = Field(String(nbChars=1))
    >>> f2_2 = Field(String(nbChars=1))
    >>> f2 = Field([f2_1, f2_2])
    >>> symbol = Symbol([f1, f2], name="sym")
    >>> preset = Preset(symbol)
    >>> preset[f2_1] = '\x41'
    >>> messages_gen = symbol.specialize(preset)
    >>> next(messages_gen)
    b',Aq'
    >>> next(messages_gen)
    b',A!'
    >>> next(messages_gen)
    b',A@'


    **Fixing the value of a field that contains sub-fields**

    This should trigger an exception as it is only possible to fix a value to leaf fields.

    >>> from netzob.all import *
    >>> f1 = Field(String(nbChars=1))
    >>> f2_1 = Field(String(nbChars=1))
    >>> f2_2 = Field(String(nbChars=1))
    >>> f2 = Field([f2_1, f2_2])
    >>> symbol = Symbol([f1, f2], name="sym")
    >>> preset = Preset(symbol)
    >>> preset[f2] = '\x41'
    Traceback (most recent call last):
    ...
    Exception: Cannot set a fixed value on a field that contains sub-fields


    **Fixing the value of a leaf variable**

    >>> from netzob.all import *
    >>> v1 = Data(String(nbChars=1))
    >>> v2 = Data(String(nbChars=1))
    >>> v_agg = Agg([v1, v2])
    >>> f1 = Field(v_agg)
    >>> symbol = Symbol([f1], name="sym")
    >>> preset = Preset(symbol)
    >>> preset[v1] = '\x41'
    >>> messages_gen = symbol.specialize(preset)
    >>> next(messages_gen)
    b'A%'
    >>> next(messages_gen)
    b'AF'
    >>> next(messages_gen)
    b'Av'


    **Fixing the value of a node variable**

    >>> from netzob.all import *
    >>> v1 = Data(String(nbChars=1))
    >>> v2 = Data(String(nbChars=1))
    >>> v_agg = Agg([v1, v2])
    >>> f1 = Field(v_agg)
    >>> symbol = Symbol([f1], name="sym")
    >>> preset = Preset(symbol)
    >>> preset[v_agg] = b'\x41\x42\x43'
    >>> messages_gen = symbol.specialize(preset)
    >>> next(messages_gen)
    b'ABC'
    >>> next(messages_gen)
    b'ABC'
    >>> next(messages_gen)
    b'ABC'


    **Fixing the value of a field, by relying on a provided generator**

    >>> from netzob.all import *
    >>> f1 = Field(String(nbChars=1))
    >>> symbol = Symbol([f1], name="sym")
    >>> preset = Preset(symbol)
    >>> my_generator = (x for x in [b'\x41', b'\x42', b'\x43'])
    >>> preset[f1] = my_generator
    >>> messages_gen = symbol.specialize(preset)
    >>> next(messages_gen)
    b'A'
    >>> next(messages_gen)
    b'B'
    >>> next(messages_gen)
    b'C'
    >>> next(messages_gen)
    Traceback (most recent call last):
    ...
    RuntimeError: generator raised StopIteration


    **Fixing the value of a field, by relying on a provided iterator**

    >>> from netzob.all import *
    >>> f1 = Field(String(nbChars=1))
    >>> symbol = Symbol([f1], name="sym")
    >>> preset = Preset(symbol)
    >>> my_iter = iter([b'\x41', b'\x42', b'\x43'])
    >>> preset[f1] = my_iter
    >>> messages_gen = symbol.specialize(preset)
    >>> next(messages_gen)
    b'A'
    >>> next(messages_gen)
    b'B'
    >>> next(messages_gen)
    b'C'
    >>> next(messages_gen)
    Traceback (most recent call last):
    ...
    RuntimeError: generator raised StopIteration


    **Fixing the value of a field, by relying on a provided function**

    >>> from netzob.all import *
    >>> f1 = Field(String(nbChars=1))
    >>> symbol = Symbol([f1], name="sym")
    >>> preset = Preset(symbol)
    >>> def my_callable():
    ...     return random.choice([b'\x41', b'\x42', b'\x43'])
    >>> preset[f1] = my_callable
    >>> messages_gen = symbol.specialize(preset)
    >>> next(messages_gen)
    b'C'
    >>> next(messages_gen)
    b'B'
    >>> next(messages_gen)
    b'A'


    **Fixing the value of a field through its name**

    >>> from netzob.all import *
    >>> f1 = Field(String(nbChars=1), name='f1')
    >>> symbol = Symbol([f1], name="sym")
    >>> preset = Preset(symbol)
    >>> preset['f1'] = '\x41'
    >>> messages_gen = symbol.specialize(preset)
    >>> next(messages_gen)
    b'A'
    >>> next(messages_gen)
    b'A'
    >>> next(messages_gen)
    b'A'


    **Fixing the value of a variable leaf through its name**

    >>> from netzob.all import *
    >>> v1 = Data(String(nbChars=1), name='v1')
    >>> v2 = Data(String(nbChars=1), name='v2')
    >>> v_agg = Agg([v1, v2], name='v_agg')
    >>> f1 = Field(v_agg)
    >>> symbol = Symbol([f1], name="sym")
    >>> preset = Preset(symbol)
    >>> preset['v1'] = '\x41\x42\x43'
    >>> messages_gen = symbol.specialize(preset)
    >>> next(messages_gen)
    b'ABCM'
    >>> next(messages_gen)
    b'ABCA'
    >>> next(messages_gen)
    b'ABCW'


    **Fixing the value of a variable node through its name**

    >>> from netzob.all import *
    >>> v1 = Data(String(nbChars=1), name='v1')
    >>> v2 = Data(String(nbChars=1), name='v2')
    >>> v_agg = Agg([v1, v2], name='v_agg')
    >>> f1 = Field(v_agg)
    >>> symbol = Symbol([f1], name="sym")
    >>> preset = Preset(symbol)
    >>> preset['v_agg'] = b'\x41\x42\x43'
    >>> messages_gen = symbol.specialize(preset)
    >>> next(messages_gen)
    b'ABC'
    >>> next(messages_gen)
    b'ABC'
    >>> next(messages_gen)
    b'ABC'

    """
