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
# +---------------------------------------------------------------------------+

# +---------------------------------------------------------------------------+
# | File contributors :                                                       |
# |       - Georges Bossert <georges.bossert (a) supelec.fr>                  |
# |       - Frédéric Guihéry <frederic.guihery (a) amossys.fr>                |
# +---------------------------------------------------------------------------+

# +---------------------------------------------------------------------------+
# | Standard library imports                                                  |
# +---------------------------------------------------------------------------+
import random
from typing import Callable, Optional, Tuple, Union

# +---------------------------------------------------------------------------+
# | Related third party imports                                               |
# +---------------------------------------------------------------------------+
from bitarray import bitarray
from enum import IntEnum

# +---------------------------------------------------------------------------+
# | Local application imports                                                 |
# +---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger
from netzob.Model.Vocabulary.Types.AbstractType import UnitSize
from netzob.Model.Vocabulary.Domain.Variables.AbstractVariable import AbstractVariable
from netzob.Model.Vocabulary.Domain.Variables.Nodes.AbstractVariableNode import AbstractVariableNode
from netzob.Model.Vocabulary.Domain.GenericPath import GenericPath
from netzob.Model.Vocabulary.Domain.Parser.ParsingPath import ParsingPath
from netzob.Model.Vocabulary.Domain.Specializer.SpecializingPath import SpecializingPath


class RepeatResult(IntEnum):
    CONTINUE = 0
    STOP_BEFORE = 1
    STOP_AFTER = 2


nbRepeatCbkType = Callable[[int, bitarray, Optional[bitarray],
                            Optional[GenericPath], Optional[AbstractVariable]],
                           RepeatResult]
nbRepeatType = Union[int, Tuple[int, int], nbRepeatCbkType]


@NetzobLogger
class Repeat(AbstractVariableNode):
    """The Repeat class is a node variable that represents a sequence of
    the same variable. This denotes an n-time repetition of a
    variable, which can be a terminal leaf or a non-terminal node.

    The Repeat constructor expects some parameters:

    :param child: The variable element that will be repeated.
    :param nbRepeat: The number of repetitions of the element. This value can be a fixed integer, a tuple of integers defining the minimum and maximum of permitted repetitions, a constant from the calling script, a value present in another field, or can be identified by calling a callback function. In the latter case, the callback function should return a boolean telling if the expected number of repetitions is reached. Those use cases are described below.
    :param delimiter: The delimiter used to separate the repeated element. The default is None.
    :type child: :class:`Variable <netzob.Model.Vocabulary.Domain.Variables.AbstractVariable>`, required
    :type nbRepeat: an :class:`int` or a :class:`tuple` of :class:`int` or
                    a Python variable containing an :class:`int` or a
                    :class:`Field
                    <netzob.Model.Vocabulary.Field.Field>` or a
                    :class:`func` method, required
    :type delimiter: :class:`bitarray`, optional


    The Repeat class provides the following public variables:

    :var children: The list of one element which is the child attached to the variable node.
    :var varType: The type of the variable (Read-only).
    :vartype children: a list of :class:`Variable <netzob.Model.Vocabulary.Variables.Variable>`
    :vartype varType: :class:`str`

    **Callback prototype**

    The callback function that can be used in the ``nbRepeat``
    parameter has the following prototype:

    ``def cbk_nbRepeat(nb_repeat, data, path, child, remaining=None)``

    Where:

    * ``nb_repeat`` is an :class:`int` that corresponds
      to the amount of time the child element has been parsed or specialized.
    * ``data`` is a :class:`bitarray` that corresponds to the already parsed or
      specialized data.
    * ``path`` is a data structure that allows access to the values of the
      parsed :class:`Variable <Netzob.Model.Vocabulary.Domain.Variables.AbstractVariable.AbstractVariable>`
      elements.
    * ``child`` is a :class:`Variable <Netzob.Model.Vocabulary.Domain.Variables.AbstractVariable.AbstractVariable>`
      that corresponds to the repeated element.
    * ``remaining`` is a :class:`bitarray` that corresponds to the remaining
      data to be parsed. Only set in parsing mode. In specialization mode, this
      parameter will have a `None` value. This parameter can therefore be used
      to identify the current mode.

    The ``child`` parameter allows access to the root of a tree structure.
    The ``child`` :class:`Variable <Netzob.Model.Vocabulary.Domain.Variables.AbstractVariable.AbstractVariable>`
    can have children.
    Access to :class:`Variable <Netzob.Model.Vocabulary.Domain.Variables.AbstractVariable.AbstractVariable>`
    values is done through the ``path``, thanks to its methods ``hasData``
    and ``getData``:

    * ``path.hasData(child)`` will return a :class:`bool` telling if a data has
      been specialized or parsed for the child
      :class:`Variable <Netzob.Model.Vocabulary.Domain.Variables.AbstractVariable.AbstractVariable>`.
    * ``path.getData(child)`` will return a :class:`bitarray` that corresponds
      to the value specialized or parsed for the child
      :class:`Variable <Netzob.Model.Vocabulary.Domain.Variables.AbstractVariable.AbstractVariable>`.

    The callback function is called each time the child element is
    seen.

    The callback function should return a boolean telling if the
    expected number of repetitions is reached (True) or not (False).


    **Basic usage of Repeat**

    The following example shows a repeat variable where the repeated
    element is a String:

    >>> from netzob.all import *
    >>> f1 = Field(Repeat(String("A"), nbRepeat=16))
    >>> f1.specialize()
    b'AAAAAAAAAAAAAAAA'


    **Usage of a delimiter in Repeat**

    We can specify a delimiter between each repeated element, as
    depicted in the following example:

    >>> from netzob.all import *
    >>> delimiter = bitarray(endian='big')
    >>> delimiter.frombytes(b"-")
    >>> f = Field(Repeat(Alt([String("A"), String("B")]), nbRepeat=(2, 4),
    ...           delimiter=delimiter), name='f1')
    >>> f.specialize()
    b'A-B-B'


    **Limiting the number of repetitions with an integer**

    The following example shows how to create a Repeat variable whose
    number of repetitions is limited by an integer:

    >>> from netzob.all import *
    >>> f1 = Field(Repeat(String("john"), nbRepeat=3))


    **Limiting the number of repetitions with an interval of integers**

    The following example shows how to create a Repeat variable whose
    number of repetitions is limited by an interval of integers:

    >>> from netzob.all import *
    >>> f1 = Field(Repeat(String("john"), nbRepeat=(2,5)))


    **Limiting the number of repetitions with a Python integer variable**

    The following example shows how to create a Repeat variable whose
    number of repetitions is limited by a Python integer
    variable. Such a variable is typically managed by the calling script:

    >>> from netzob.all import *
    >>> var = 3
    >>> f1 = Field(Repeat(String("john"), nbRepeat=var))


    **Limiting the number of repetitions with the value of another field**

    The following example shows how to create a Repeat variable whose
    number of repetitions is limited by the value of another field:

    >>> from netzob.all import *
    >>> f_end = Field(Integer(interval=(2, 5)))
    >>> f1 = Field(Repeat(String("john"), nbRepeat=f_end)) # doctest: +SKIP


    **Limiting the number of repetitions by calling a callback function**

    The following example shows how to create a Repeat variable whose
    number of repetitions is handled by calling a callback function
    which returns a boolean telling if the expected number of
    repetitions is reached. Here, in parsing mode, the repeat stops
    when the `b'B'` byte is encountered. In specialization mode, the
    repeat stops at the first iteration.

    >>> from netzob.all import *
    >>> def cbk(nb_repeat, data, path, child, remaining=None):
    ...     if remaining is not None:  # This means we are in parsing mode
    ...         print("in cbk: nb_repeat:{} -- data:{} -- remaining:{}".format(nb_repeat, data.tobytes(), remaining.tobytes()))
    ...
    ...         # We check the value of the second child of the parameter child
    ...         if child.isnode() and len(child.children) > 1:
    ...             second_subchild = child.children[1]
    ...             if path.hasData(second_subchild) and path.getData(second_subchild).tobytes() == b'B':
    ...                 return RepeatResult.STOP_BEFORE
    ...         return RepeatResult.CONTINUE
    ...     return RepeatResult.STOP_AFTER
    >>> f1 = Field(Repeat(Alt([String("A"), String("B")]), nbRepeat=cbk), name="f1")
    >>> f2 = Field(String("B"), name="f2")
    >>> f3 = Field(String("C"), name="f3")
    >>> f = Field([f1, f2, f3])
    >>> d = f.specialize()
    >>> d == b'ABC' or d == b'BBC'
    True
    >>> data = "AABC"
    >>> Field.abstract(data, [f])
    in cbk: nb_repeat:1 -- data:b'A' -- remaining:b'ABC'
    in cbk: nb_repeat:2 -- data:b'AA' -- remaining:b'BC'
    in cbk: nb_repeat:3 -- data:b'AAB' -- remaining:b'C'
    (Field, OrderedDict([('f1', b'AA'), ('f2', b'B'), ('f3', b'C')]))


    .. ifconfig:: scope in ('netzob')

       **Abstraction of repeat variables**

       The following examples show how repeat variable can be parsed:

       >>> from netzob.all import *
       >>> f1 = Field(Repeat(String("john"), nbRepeat=(0,3)), name="f1")
       >>> f2 = Field(String("kurt"), name="f2")
       >>> s = Symbol([f1, f2])
       >>> data = "johnkurt"
       >>> Symbol.abstract(data, [s])  # doctest: +NORMALIZE_WHITESPACE
       (Symbol, OrderedDict([('f1', b'john'), ('f2', b'kurt')]))
       >>> data = "kurt"
       >>> Symbol.abstract(data, [s])
       (Symbol, OrderedDict([('f1', b''), ('f2', b'kurt')]))


       **Specialization of repeat variables**

       The following examples show how repeat variable can be specialized:

       >>> from netzob.all import *
       >>> f1 = Field(Repeat(String("john"), nbRepeat=2))
       >>> s = Symbol([f1])
       >>> s.specialize()
       b'johnjohn'
       >>> from netzob.all import *
       >>> delimiter = bitarray(endian='big')
       >>> delimiter.frombytes(b";")
       >>> f1 = Field(Repeat(IPv4(), nbRepeat=3,
       ...           delimiter=delimiter))
       >>> s = Symbol([f1])
       >>> gen = s.specialize()
       >>> len(gen) == 14
       True
       >>> gen.count(b";") >= 2
       True

       >>> from netzob.all import *
       >>> delimiter = bitarray(endian='big')
       >>> delimiter.frombytes(b";")
       >>> child = Data(dataType=String(nbChars=(5)))
       >>> f1 = Field(Repeat(child, nbRepeat=3,
       ...            delimiter=delimiter))
       >>> s = Symbol([f1])
       >>> gen = s.specialize()
       >>> len(gen) == 17
       True
       >>> gen.count(b";") >= 2
       True

    """

    UNIT_SIZE = UnitSize.SIZE_8
    MAX_REPEAT = 2**UNIT_SIZE.value

    def __init__(self, child, nbRepeat, delimiter=None):
        super(Repeat, self).__init__(self.__class__.__name__, [child])
        self.nbRepeat = nbRepeat  # type: nbRepeatType
        self.delimiter = delimiter

    @typeCheck(ParsingPath)
    def parse(self, parsingPath, **kwargs):
        """Parse the content with the definition domain of the Repeat
        """

        if parsingPath is None:
            raise Exception("Parsing path cannot be None")

        # retrieve the data to parse
        dataToParse = parsingPath.getData(self)

        self._logger.debug("Parse '{}' as {} with parser path '{}'".format(
            dataToParse.tobytes(), self, parsingPath))

        # remove any data assigned to this variable
        parsingPath.removeData(self)

        if callable(self.nbRepeat):
            gen = self._parse_callback
        else:
            gen = self._parse_without_callback

        # result generator
        results = gen(parsingPath, dataToParse, **kwargs)

        # filter on results having a data for this variable
        valid_results = [result for result in results if result.hasData(self)]

        # if no valid result if found, provide a fallback parsing path with
        # an empty result
        if len(valid_results) == 0:
            newParsingPath = parsingPath.duplicate()
            newParsingPath.addResult(self, bitarray())
            valid_results.append(newParsingPath)

        return valid_results

    def _parse_without_callback(self, parsingPath, dataToParse, carnivorous=False):
        min_nb_repeat = self.nbRepeat[0] - 1
        max_nb_repeat = self.nbRepeat[1]

        for nb_repeat in range(max_nb_repeat, min_nb_repeat, -1):

            # initiate a new parsing path based on the current one
            newParsingPath = parsingPath.duplicate()
            newParsingPath.assignData(dataToParse, self.children[0])
            newParsingPaths = [newParsingPath]

            # check we can apply nb_repeat times the child
            for i_repeat in range(nb_repeat):
                tmp_results = []
                break_repeat = RepeatResult.CONTINUE
                for newParsingPath in newParsingPaths:
                    for childParsingPath in self.children[0].parse(newParsingPath, carnivorous=carnivorous):

                        newResult = bitarray()
                        if childParsingPath.hasData(self):
                            newResult += childParsingPath.getData(self)
                        newResult += childParsingPath.getData(self.children[0])

                        remainingDataToParse = dataToParse[len(newResult):]

                        childParsingPath.addResult(self, newResult)

                        childParsingPath.assignData(remainingDataToParse, self.children[0])

                        # apply delimiter if necessary
                        if self.delimiter is not None and i_repeat < nb_repeat - 1:
                            # check the delimiter is available
                            toParse = childParsingPath.getData(self.children[0])
                            if toParse[:len(self.delimiter)] == self.delimiter:
                                newResult = childParsingPath.getData(self) + self.delimiter
                                childParsingPath.addResult(self, newResult)
                                childParsingPath.assignData(dataToParse[len(newResult):],
                                                            self.children[0])
                                tmp_results.append(childParsingPath)
                        else:
                            tmp_results.append(childParsingPath)

                        if len(dataToParse) == len(newResult):
                            break_repeat = RepeatResult.STOP_AFTER

                if break_repeat is RepeatResult.STOP_BEFORE:
                    break
                newParsingPaths = tmp_results
                if break_repeat is RepeatResult.STOP_AFTER:
                    break

            # deal with the case where no repetition is expected
            if nb_repeat == 0:
                newParsingPath.addResult(self, bitarray())

            yield from newParsingPaths

    def _parse_callback(self, parsingPath, dataToParse, carnivorous=False):
        # initiate a new parsing path based on the current one
        newParsingPath = parsingPath.duplicate()
        newParsingPath.assignData(dataToParse, self.children[0])
        newParsingPaths = [newParsingPath]

        break_repeat = RepeatResult.CONTINUE
        for i_repeat in range(self.MAX_REPEAT):
            tmp_results = []
            break_repeat = RepeatResult.CONTINUE
            for newParsingPath in newParsingPaths:
                for childParsingPath in self.children[0].parse(newParsingPath, carnivorous=carnivorous):

                    newResult = bitarray()
                    if childParsingPath.hasData(self):
                        newResult += childParsingPath.getData(self)
                    newResult += childParsingPath.getData(self.children[0])

                    remainingDataToParse = dataToParse[len(newResult):]

                    break_repeat = self.nbRepeat(i_repeat + 1,
                                                 newResult,
                                                 childParsingPath,
                                                 self.children[0],
                                                 remainingDataToParse)

                    childParsingPath.addResult(self, newResult)
                    childParsingPath.assignData(remainingDataToParse, self.children[0])

                    # apply delimiter if necessary
                    if self.delimiter is not None:
                        raise NotImplementedError("may be buggy")
                        # check the delimiter is available
                        toParse = childParsingPath.getData(self.children[0])
                        if toParse[:len(self.delimiter)] == self.delimiter:
                            newResult = childParsingPath.getData(self) + self.delimiter
                            childParsingPath.addResult(self, newResult)
                            childParsingPath.assignData(dataToParse[len(newResult):], self.children[0])
                            tmp_results.append(childParsingPath)
                    else:
                        tmp_results.append(childParsingPath)

                    if len(dataToParse) == len(newResult):
                        break_repeat = RepeatResult.STOP_AFTER
                        break

            if break_repeat is RepeatResult.STOP_BEFORE:
                break
            if len(tmp_results) > 0:
                newParsingPaths = tmp_results
            if break_repeat is RepeatResult.STOP_AFTER:
                break

        yield from newParsingPaths

    @typeCheck(SpecializingPath)
    def specialize(self, originalSpecializingPath, fuzz=None):
        """Specializes a Repeat"""

        if originalSpecializingPath is None:
            raise Exception("Specializing path cannot be None")

        # initialy, there is a unique path to specialize (the provided one)
        specializingPaths = []

        # If we are in a fuzzing mode
        if fuzz is not None and fuzz.get(self) is not None:

            # Retrieve the mutator
            mutator = fuzz.get(self)

            # Chose the child according to the integer returned by the mutator
            i_repeat = mutator.generate()

        # Else, randomly chose the child
        else:
            if callable(self.nbRepeat):
                i_repeat = Repeat.MAX_REPEAT
            else:
                i_repeat = random.randint(self.nbRepeat[0], self.nbRepeat[1])

        newSpecializingPath = originalSpecializingPath.duplicate()
        newSpecializingPaths = [newSpecializingPath]

        if i_repeat == 0:
            newSpecializingPath.addResult(self, bitarray())

        for i in range(i_repeat):
            break_repeat = RepeatResult.CONTINUE
            childSpecializingPaths = []
            for newSpecializingPath in newSpecializingPaths:

                child = self.children[0]
                for path in child.specialize(newSpecializingPath, fuzz=fuzz):

                    oldResult = bitarray()
                    if path.hasData(self):
                        oldResult += path.getData(self)
                        if self.delimiter is not None:
                            oldResult += self.delimiter
                    newResult = oldResult + path.getData(child)

                    if callable(self.nbRepeat):
                        break_repeat = self.nbRepeat(i + 1, newResult,
                                                     path, child, None)

                    if break_repeat is RepeatResult.STOP_BEFORE:
                        # save previous result, then notify
                        path.addResult(self, oldResult, notify=True)
                    elif break_repeat is RepeatResult.STOP_AFTER:
                        # save last result, then notify
                        path.addResult(self, newResult, notify=True)
                    else:
                        # save last result, then notify on last iteration only
                        last_round = (i == i_repeat - 1)
                        path.addResult(self, newResult, notify=last_round)

                    # We forget the assigned data to the child variable and its children
                    path.removeDataRecursively(child)

                    childSpecializingPaths.append(path)

            newSpecializingPaths = childSpecializingPaths

            if break_repeat is not RepeatResult.CONTINUE:
                break

        specializingPaths.extend(newSpecializingPaths)

        # lets shuffle this ( :) ) >>> by default we only consider the first valid parsing path.
        random.shuffle(specializingPaths)

        return specializingPaths

    @property
    def nbRepeat(self):
        return self.__nbRepeat

    @nbRepeat.setter  # type: ignore
    def nbRepeat(self, nbRepeat):
        if nbRepeat is None:
            raise Exception("NB Repeat cannot be None")

        if isinstance(nbRepeat, int):
            nbRepeat = (nbRepeat, nbRepeat)

        if isinstance(nbRepeat, tuple):
            minNbRepeat, maxNbRepeat = nbRepeat

            if minNbRepeat is not None and not isinstance(minNbRepeat, int):
                raise TypeError("NbRepeat must be defined with a tuple of int")
            if maxNbRepeat is not None and not isinstance(maxNbRepeat, int):
                raise TypeError("NbRepeat must be defined with a tuple of int")

            if minNbRepeat is None:
                minNbRepeat = 0

            if minNbRepeat < 0:
                raise ValueError("Minimum nbRepeat must be greater than 0")
            if maxNbRepeat is not None and maxNbRepeat < minNbRepeat:
                raise ValueError(
                    "Maximum must be greater or equals to the minimum")
            if maxNbRepeat is not None and maxNbRepeat > Repeat.MAX_REPEAT:
                raise ValueError(
                    "Maximum nbRepeat supported for a variable is {0}.".format(
                        Repeat.MAX_REPEAT))
            self.__nbRepeat = (minNbRepeat, maxNbRepeat)
        elif callable(nbRepeat):
            self.__nbRepeat = nbRepeat
        else:
            raise TypeError(
                "nbRepeat is of wrong type: '{}'.".format(nbRepeat))

    @property
    def delimiter(self):
        return self.__delimiter

    @delimiter.setter  # type: ignore
    @typeCheck(bitarray)
    def delimiter(self, delimiter):
        self.__delimiter = delimiter


def _test():
    r"""

    >>> from netzob.all import *
    >>> Conf.seed = 0
    >>> Conf.apply()
    

    ## Size field on the right

    Size field targeting a field containing a repeat variable, with size field on the right:

    >>> f1 = Field(Repeat(Raw(b"A"), nbRepeat=4), name='f1')
    >>> f2 = Field(Size(f1, dataType=uint8()), name='f2')
    >>> s = Symbol([f2, f1])
    >>> d = s.specialize()
    >>> d
    b'\x04AAAA'
    >>> Symbol.abstract(d, [s])
    (Symbol, OrderedDict([('f2', b'\x04'), ('f1', b'AAAA')]))

    Size field targeting a field containing a repeat variable of non fixed size, with size field on the right:

    >>> f1 = Field(Repeat(Raw(b"A"), nbRepeat=(2,5)), name='f1')
    >>> f2 = Field(Size(f1, dataType=uint8()), name='f2')
    >>> s = Symbol([f2, f1])
    >>> d = s.specialize()
    >>> d
    b'\x05AAAAA'
    >>> Symbol.abstract(d, [s])
    (Symbol, OrderedDict([('f2', b'\x05'), ('f1', b'AAAAA')]))

    Size field targeting a repeat variable, with size field on the right:

    >>> v1 = Repeat(Raw(b"A"), nbRepeat=5)
    >>> v2 = Size(v1, dataType=uint8())
    >>> s = Symbol([Field(v2, name='f1'), Field(v1, name='f2')])
    >>> d = s.specialize()
    >>> d
    b'\x05AAAAA'
    >>> Symbol.abstract(d, [s])
    (Symbol, OrderedDict([('f1', b'\x05'), ('f2', b'AAAAA')]))

    Size field targeting a repeat variable of non fixed size, with size field on the right:

    >>> v1 = Repeat(Raw(b"A"), nbRepeat=(2, 5))
    >>> v2 = Size(v1, dataType=uint8())
    >>> s = Symbol([Field(v2, name='f1'), Field(v1, name='f2')])
    >>> d = s.specialize()
    >>> d
    b'\x04AAAA'
    >>> Symbol.abstract(d, [s])
    (Symbol, OrderedDict([('f1', b'\x04'), ('f2', b'AAAA')]))


    ## Size field on the left

    Size field targeting a field containing a repeat variable, with size field on the left:

    >>> f1 = Field(Repeat(Raw(b"A"), nbRepeat=4), name='f1')
    >>> f2 = Field(Size(f1, dataType=uint8()), name='f2')
    >>> s = Symbol([f1, f2])
    >>> d = s.specialize()
    >>> d
    b'AAAA\x04'
    >>> Symbol.abstract(d, [s])
    (Symbol, OrderedDict([('f1', b'AAAA'), ('f2', b'\x04')]))

    Size field targeting a field containing a repeat variable of non fixed size, with size field on the left:

    >>> f1 = Field(Repeat(Raw(b"A"), nbRepeat=(2,5)), name='f1')
    >>> f2 = Field(Size(f1, dataType=uint8()), name='f2')
    >>> s = Symbol([f1, f2])
    >>> d = s.specialize()
    >>> d
    b'AAAAA\x05'
    >>> Symbol.abstract(d, [s])
    (Symbol, OrderedDict([('f1', b'AAAAA'), ('f2', b'\x05')]))

    Size field targeting a repeat variable, with size field on the left:

    >>> v1 = Repeat(Raw(b"A"), nbRepeat=5)
    >>> v2 = Size(v1, dataType=uint8())
    >>> s = Symbol([Field(v1, name='f1'), Field(v2, name='f2')])
    >>> d = s.specialize()
    >>> d
    b'AAAAA\x05'
    >>> Symbol.abstract(d, [s])
    (Symbol, OrderedDict([('f1', b'AAAAA'), ('f2', b'\x05')]))

    Size field targeting a repeat variable of non fixed size, with size field on the left:

    >>> v1 = Repeat(Raw(b"A"), nbRepeat=(2, 5))
    >>> v2 = Size(v1, dataType=uint8())
    >>> s = Symbol([Field(v1, name='f1'), Field(v2, name='f2')])
    >>> d = s.specialize()
    >>> d
    b'AAAAA\x05'
    >>> Symbol.abstract(d, [s])
    (Symbol, OrderedDict([('f1', b'AAAAA'), ('f2', b'\x05')]))


    ## Value field on the right

    Value field targeting a field containing a repeat variable, with value field on the right:

    >>> f1 = Field(Repeat(Raw(b"A"), nbRepeat=4), name='f1')
    >>> f2 = Field(Value(f1), name='f2')
    >>> s = Symbol([f2, f1])
    >>> d = s.specialize()
    >>> d
    b'AAAAAAAA'

    >>> Symbol.abstract(d, [s])  # doctest: +SKIP
    (Symbol, OrderedDict([('f2', b'AAAA'), ('f1', b'AAAA')]))

    Value field targeting a field containing a repeat variable of non fixed size, with value field on the right:

    >>> f1 = Field(Repeat(Raw(b"A"), nbRepeat=(2,5)), name='f1')
    >>> f2 = Field(Value(f1), name='f2')
    >>> s = Symbol([f2, f1])
    >>> d = s.specialize()
    >>> d
    b'AAAAAA'
    >>> Symbol.abstract(d, [s])  # doctest: +SKIP
    (Symbol, OrderedDict([('f2', b'AAA'), ('f1', b'AAA')]))


    Value field targeting a repeat variable, with value field on the right:

    >>> v1 = Repeat(Raw(b"A"), nbRepeat=5)
    >>> v2 = Value(v1)
    >>> s = Symbol([Field(v2, name='f1'), Field(v1, name='f2')])
    >>> d = s.specialize()
    >>> d
    b'AAAAAAAAAA'
    >>> Symbol.abstract(d, [s])  # doctest: +SKIP
    (Symbol, OrderedDict([('f1', b'AAAAA'), ('f2', b'AAAAA')]))


    Value field targeting a repeat variable of non fixed size, with value field on the right:

    >>> v1 = Repeat(Raw(b"A"), nbRepeat=(2, 5))
    >>> v2 = Value(v1)
    >>> s = Symbol([Field(v2, name='f1'), Field(v1, name='f2')])
    >>> d = s.specialize()
    >>> d
    b'AAAAAAAA'
    >>> Symbol.abstract(d, [s])  # doctest: +SKIP
    (Symbol, OrderedDict([('f1', b'AAAA'), ('f2', b'AAAA')]))


    ## Value field on the left

    Value field targeting a field containing a repeat variable, with value field on the left:

    >>> f1 = Field(Repeat(Raw(b"A"), nbRepeat=4), name='f1')
    >>> f2 = Field(Value(f1), name='f2')
    >>> s = Symbol([f1, f2])
    >>> d = s.specialize()
    >>> d
    b'AAAAAAAA'
    >>> Symbol.abstract(d, [s])
    (Symbol, OrderedDict([('f1', b'AAAA'), ('f2', b'AAAA')]))

    Value field targeting a field containing a repeat variable of non fixed size, with value field on the left:

    >>> f1 = Field(Repeat(Raw(b"A"), nbRepeat=(2,5)), name='f1')
    >>> f2 = Field(Value(f1), name='f2')
    >>> s = Symbol([f1, f2])
    >>> d = s.specialize()
    >>> d
    b'AAAA'
    >>> Symbol.abstract(d, [s])
    (Symbol, OrderedDict([('f1', b'AA'), ('f2', b'AA')]))


    Value field targeting a repeat variable, with value field on the left:

    >>> v1 = Repeat(Raw(b"A"), nbRepeat=5)
    >>> v2 = Value(v1)
    >>> s = Symbol([Field(v1, name='f1'), Field(v2, name='f2')])
    >>> d = s.specialize()
    >>> d
    b'AAAAAAAAAA'
    >>> Symbol.abstract(d, [s])
    (Symbol, OrderedDict([('f1', b'AAAAA'), ('f2', b'AAAAA')]))

    Value field targeting a repeat variable of non fixed size, with value field on the left:

    >>> v1 = Repeat(Raw(b"A"), nbRepeat=(2, 5))
    >>> v2 = Value(v1)
    >>> s = Symbol([Field(v1, name='f1'), Field(v2, name='f2')])
    >>> d = s.specialize()
    >>> d
    b'AAAAAA'
    >>> Symbol.abstract(d, [s])
    (Symbol, OrderedDict([('f1', b'AAA'), ('f2', b'AAA')]))

    """
