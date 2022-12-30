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
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger, public_api
from netzob.Model.Vocabulary.Types.AbstractType import AbstractType, UnitSize
from netzob.Model.Vocabulary.Types.TypeConverter import TypeConverter
from netzob.Model.Vocabulary.Types.BitArray import BitArray
from netzob.Model.Vocabulary.Types.Integer import Integer
from netzob.Model.Vocabulary.Types.Raw import Raw
from netzob.Model.Vocabulary.Domain.Variables.AbstractVariable import AbstractVariable
from netzob.Model.Vocabulary.Domain.Variables.Leafs.Data import Data
from netzob.Model.Vocabulary.Domain.Variables.Nodes.AbstractVariableNode import AbstractVariableNode
from netzob.Model.Vocabulary.Domain.GenericPath import GenericPath
from netzob.Model.Vocabulary.Domain.Parser.ParsingPath import ParsingPath, ParsingException
from netzob.Model.Vocabulary.Domain.Specializer.SpecializingPath import SpecializingPath
from netzob.Fuzzing.Mutators.DomainMutator import FuzzingMode


@public_api
class RepeatResult(IntEnum):
    CONTINUE = 0
    STOP_BEFORE = 1
    STOP_AFTER = 2


nbRepeatCbkType = Callable[[int, bitarray, Optional[bitarray],
                            Optional[GenericPath], Optional[AbstractVariable]],
                           RepeatResult]
nbRepeatType = Union[int, Tuple[int, int], nbRepeatCbkType, AbstractVariable]


@NetzobLogger
class Repeat(AbstractVariableNode):
    r"""The Repeat class is a node variable that represents a sequence of
    the same variable. This denotes an n-time repetition of a
    variable, which can be a terminal leaf or a non-terminal node.

    The Repeat constructor expects some parameters:

    :param child: The variable element that will be repeated.
    :param nbRepeat: The number of repetitions of the element. This value can be a fixed integer, a tuple of integers defining the minimum and maximum of permitted repetitions, a constant from the calling script, a value present in another field, or can be identified by calling a callback function. In the latter case, the callback function should return a boolean telling if the expected number of repetitions is reached. Those use cases are described below.
    :param delimiter: The delimiter used to separate the repeated element. The default is None.
    :param name: The name of the variable (if None, the name will
                 be generated).
    :type child: :class:`Variable <netzob.Model.Vocabulary.Domain.Variables.AbstractVariable.AbstractVariable>`, required
    :type nbRepeat: an :class:`int` or a :class:`tuple` of :class:`int` or
                    a Python variable containing an :class:`int` or a
                    :class:`Field
                    <netzob.Model.Vocabulary.Field.Field>` or a
                    :class:`Callable <collections.abc.Callable>`, required
    :type delimiter: :class:`bitarray`, optional
    :type name: :class:`str`, optional

    The Repeat class provides the following public variables:

    :var children: The list of one element which is the child attached to the variable node.
    :vartype children: a list of :class:`Variable <netzob.Model.Vocabulary.Variables.Variable>`


    **Callback prototype**

    The callback function that can be used in the ``nbRepeat``
    parameter has the following prototype:

    .. function:: cbk_nbRepeat(nb_repeat, data, path, child, remaining)
       :noindex:

       :param nb_repeat: the number of times the child element has been parsed
                          or specialized.
       :type nb_repeat: int
       :param data: the already parsed or specialized data.
       :type data: ~bitarray.bitarray
       :param path: data structure that allows access to the values of the
                    parsed :class:`Variable <netzob.Model.Vocabulary.Domain.Variables.AbstractVariable.AbstractVariable>`
                    elements.
       :type path: object
       :param child: the repeated element.
       :type child: :class:`Variable <netzob.Model.Vocabulary.Domain.Variables.AbstractVariable.AbstractVariable>`
       :param remaining: the remaining data to be parsed.
                         Only set in parsing mode. In specialization mode, this
                         parameter will have a :const:`None` value. This parameter can
                         therefore be used to identify the current mode.
       :type remaining: ~bitarray.bitarray

       :return: The callback function should return one of the following values:

         * :attr:`RepeatResult.CONTINUE`: this tells to continue the repetition.
         * :attr:`RepeatResult.STOP_BEFORE`: this tells to stop the repetition before the current value of the child.
         * :attr:`RepeatResult.STOP_AFTER`: this tells to stop the repetition after the current value of the child.

       :rtype: :class:`int`

    The ``child`` is a :class:`Variable
    <netzob.Model.Vocabulary.Domain.Variables.AbstractVariable.AbstractVariable>`. The
    ``child`` can have children if it is a node. Access to child
    values, as well as to its own children values, is done through the
    ``path`` data structure, thanks to its methods
    :meth:`~netzob.Model.Vocabulary.Domain.GenericPath.hasData` and
    :meth:`~netzob.Model.Vocabulary.Domain.GenericPath.getData`. Those
    methods therefore allow access to a hierarchy of elements for
    which the ``child`` is the root element:

    * ``path.hasData(element)`` will return a :class:`bool` telling if a data has
      been specialized or parsed for the element
      :class:`Variable <netzob.Model.Vocabulary.Domain.Variables.AbstractVariable.AbstractVariable>`.
    * ``path.getData(element)`` will return a :class:`bitarray` that corresponds
      to the value specialized or parsed for the element
      :class:`Variable <netzob.Model.Vocabulary.Domain.Variables.AbstractVariable.AbstractVariable>`.

    It is possible to test if a ``child`` variable is a node
    of the tree structure through the ``isnode(child)`` method. A
    node may represent an ``Agg``, an ``Alt``, a ``Repeat`` or an
    ``Opt`` variable. Access to the node leafs is possible with the
    attribute ``children`` (i.e. ``child.children``). The type of the
    children leafs is also :class:`Variable
    <netzob.Model.Vocabulary.Domain.Variables.AbstractVariable.AbstractVariable>`.

    The callback function is called each time the child element is
    seen.


    **Basic usage of Repeat**

    The following example shows a repeat variable where the repeated
    element is a String:

    >>> from netzob.all import *
    >>> f1 = Field(Repeat(String("A"), nbRepeat=16))
    >>> next(f1.specialize())
    b'AAAAAAAAAAAAAAAA'


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


    **Usage of a delimiter in Repeat**

    We can specify a delimiter between each repeated element, as
    depicted in the following example:

    >>> from netzob.all import *
    >>> delimiter = bitarray(endian='big')
    >>> delimiter.frombytes(b"-")
    >>> f = Field(Repeat(Alt([String("A"), String("B")]), nbRepeat=(2, 4),
    ...           delimiter=delimiter), name='f1')
    >>> next(f.specialize())
    b'B-A-A'


    **Limiting the number of repetitions with the value of another field**

    The following example shows how to create a Repeat variable whose
    number of repetitions is limited by the value of another field:

    >>> from netzob.all import *
    >>> f_nb = Field(Integer(interval=(2, 5)))
    >>> f_pattern = Field(Repeat(String("john"), nbRepeat=f_nb))
    >>> f_header = Field([f_nb, f_pattern])
    >>> next(f_header.specialize())
    b'\x00\x05johnjohnjohnjohnjohn'


    **Limiting the number of repetitions by calling a callback function**

    The following example shows how to create a Repeat variable whose
    number of repetitions is handled by calling a callback function
    telling if the expected number of repetitions is reached. Here, in
    parsing mode, the repeat stops when the `b'B'` byte is
    encountered. In specialization mode, the repeat stops at the first
    iteration.

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
    >>> d = next(f.specialize())
    >>> d == b'ABC' or d == b'BBC'
    True
    >>> data = "AABC"
    >>> f.abstract(data)
    in cbk: nb_repeat:1 -- data:b'A' -- remaining:b'ABC'
    in cbk: nb_repeat:2 -- data:b'AA' -- remaining:b'BC'
    in cbk: nb_repeat:3 -- data:b'AAB' -- remaining:b'C'
    OrderedDict([('f1', b'AA'), ('f2', b'B'), ('f3', b'C')])


    .. ifconfig:: scope in ('netzob')

       **Abstraction of repeat variables**

       The following examples show how repeat variable can be parsed:

       >>> from netzob.all import *
       >>> f1 = Field(Repeat(String("john"), nbRepeat=(0,3)), name="f1")
       >>> f2 = Field(String("kurt"), name="f2")
       >>> s = Symbol([f1, f2])
       >>> data = "johnkurt"
       >>> s.abstract(data)  # doctest: +NORMALIZE_WHITESPACE
       OrderedDict([('f1', b'john'), ('f2', b'kurt')])
       >>> data = "kurt"
       >>> s.abstract(data)
       OrderedDict([('f1', b''), ('f2', b'kurt')])


       **Specialization of repeat variables**

       The following examples show how repeat variable can be specialized:

       >>> from netzob.all import *
       >>> f1 = Field(Repeat(String("john"), nbRepeat=2))
       >>> s = Symbol([f1])
       >>> next(s.specialize())
       b'johnjohn'
       >>> from netzob.all import *
       >>> delimiter = bitarray(endian='big')
       >>> delimiter.frombytes(b";")
       >>> f1 = Field(Repeat(IPv4(), nbRepeat=3,
       ...           delimiter=delimiter))
       >>> s = Symbol([f1])
       >>> gen = next(s.specialize())
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
       >>> gen = next(s.specialize())
       >>> len(gen) == 17
       True
       >>> gen.count(b";") >= 2
       True

    """

    UNIT_SIZE = UnitSize.SIZE_8
    MAX_REPEAT = 2**UNIT_SIZE.value

    @public_api
    def __init__(self, child, nbRepeat, delimiter=None, name=None):
        super(Repeat, self).__init__(self.__class__.__name__, children=[child], name=name)
        self.nbRepeat = nbRepeat  # type: nbRepeatType
        self.delimiter = delimiter

    @public_api
    def copy(self, map_objects=None):
        """Copy the current object as well as all its dependencies.

        :return: A new object of the same type.
        :rtype: :class:`Repeat <netzob.Model.Vocabulary.Domain.Variables.Nodes.Repeat.Repeat>`

        """
        if map_objects is None:
            map_objects = {}
        if self in map_objects:
            return map_objects[self]

        if isinstance(self.nbRepeat, AbstractVariable):
            if self.nbRepeat in map_objects.keys():
                new_nbRepeat = map_objects[self.nbRepeat]
            else:
                new_nbRepeat = self.nbRepeat.copy(map_objects)
        else:
            new_nbRepeat = self.nbRepeat

        new_repeat = Repeat(Data(Raw()), new_nbRepeat, self.delimiter)
        map_objects[self] = new_repeat

        new_children = []
        for child in self.children:
            if child in map_objects.keys():
                new_children.append(map_objects[child])
            else:
                new_child = child.copy(map_objects)
                new_children.append(new_child)

        new_repeat.children = [new_children]
        return new_repeat

    def count(self, preset=None):
        r"""

        >>> from netzob.all import *
        >>> d = Repeat(uint8(), nbRepeat=3)
        >>> d.count()
        16777216

        >>> d = Repeat(uint8(), nbRepeat=(1, 2))
        >>> d.count()
        65536

        >>> def cbk(nb_repeat, data, path, child, remaining=None):
        ...     return RepeatResult.STOP_AFTER
        >>> d = Repeat(uint8(), nbRepeat=cbk)
        >>> d.count()
        86400000000

        """

        from netzob.Fuzzing.Mutators.DomainMutator import FuzzingMode

        if preset is not None and preset.get(self) is not None and preset.get(self).mode == FuzzingMode.GENERATE:
            # Retrieve the mutator
            mutator = preset.get(self)
            return mutator.count()
        else:
            # Handle max repeat
            if isinstance(self.nbRepeat, tuple):
                max_repeat = self.nbRepeat[1]
            elif isinstance(self.nbRepeat, int):
                max_repeat = self.nbRepeat
            else:
                max_repeat = Repeat.MAX_REPEAT

            # Handle count() of children
            count = self.children[0].count(preset=preset)

            # Result
            count = count ** max_repeat
            if count > AbstractType.MAXIMUM_POSSIBLE_VALUES:
                return AbstractType.MAXIMUM_POSSIBLE_VALUES
            else:
                return count

    @typeCheck(ParsingPath)
    def parse(self, parsingPath, acceptCallBack=True, triggered=False, **kwargs):
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
        elif isinstance(self.nbRepeat, AbstractVariable):
            if parsingPath.hasData(self.nbRepeat):
                i_repeat = parsingPath.getData(self.nbRepeat)
                i_repeat = TypeConverter.convert(i_repeat, BitArray, Integer,
                                                 src_unitSize=self.nbRepeat.dataType.unitSize,
                                                 src_endianness=self.nbRepeat.dataType.endianness,
                                                 src_sign=self.nbRepeat.dataType.sign,
                                                 dst_unitSize=self.nbRepeat.dataType.unitSize,
                                                 dst_endianness=self.nbRepeat.dataType.endianness,
                                                 dst_sign=self.nbRepeat.dataType.sign)
                kwargs['min_nb_repeat'] = i_repeat - 1
                kwargs['max_nb_repeat'] = i_repeat
            else:
                kwargs['min_nb_repeat'] = 0
                kwargs['max_nb_repeat'] = Repeat.MAX_REPEAT
                parsingPath.registerVariablesCallBack([self.nbRepeat], self, parsingCB=True)
            gen = self._parse_without_callback
        else:
            kwargs['min_nb_repeat'] = self.nbRepeat[0] - 1
            kwargs['max_nb_repeat'] = self.nbRepeat[1]
            gen = self._parse_without_callback

        # result generator
        results = gen(parsingPath, dataToParse, **kwargs)

        # filter on results having a data for this variable
        valid_results = [result for result in results if result.hasData(self) and result.ok]

        # if no valid result if found, provide a fallback parsing path with
        # an empty result
        if len(valid_results) == 0:
            newParsingPath = parsingPath.copy()
            newParsingPath.addResult(self, bitarray(), notify=False)
            valid_results.append(newParsingPath)

        return valid_results

    def _parse_without_callback(self, parsingPath, dataToParse, min_nb_repeat=0, max_nb_repeat=0, carnivorous=False, acceptCallBack=True):

        for nb_repeat in range(max_nb_repeat, min_nb_repeat, -1):

            # initiate a new parsing path based on the current one
            newParsingPath = parsingPath.copy()
            newParsingPath.assignData(dataToParse, self.children[0])
            newParsingPaths = [newParsingPath]

            # check we can apply nb_repeat times the child
            for i_repeat in range(nb_repeat):
                tmp_results = []
                break_repeat = RepeatResult.CONTINUE
                for newParsingPath in newParsingPaths:

                    # Parse child
                    try:
                        childParsingPaths = self.children[0].parse(newParsingPath, carnivorous=carnivorous)
                    except ParsingException:
                        self._logger.debug("Error in parsing of child")
                        continue

                    # Handle child parsing results
                    for childParsingPath in childParsingPaths:

                        newResult = bitarray()
                        if childParsingPath.hasData(self):
                            newResult += childParsingPath.getData(self)
                        newResult += childParsingPath.getData(self.children[0])

                        remainingDataToParse = dataToParse[len(newResult):]

                        childParsingPath.ok = True
                        (addresult_succeed, addresult_parsingPaths) = childParsingPath.addResult(self, newResult)
                        if not addresult_succeed:
                            childParsingPath.ok = False

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

                        if len(dataToParse) <= len(newResult):
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
        newParsingPath = parsingPath.copy()
        newParsingPath.assignData(dataToParse, self.children[0])
        newParsingPaths = [newParsingPath]

        break_repeat = RepeatResult.CONTINUE
        for i_repeat in range(self.MAX_REPEAT):
            self._logger.debug("Repeat iteration: {}".format(i_repeat))
            if break_repeat is not RepeatResult.CONTINUE:
                break

            tmp_results = []
            break_repeat = RepeatResult.STOP_AFTER
            for newParsingPath in newParsingPaths:

                # Parse child
                try:
                    childParsingPaths = self.children[0].parse(newParsingPath, carnivorous=carnivorous)
                except ParsingException:
                    self._logger.debug("Error in parsing of child")
                    continue

                for childParsingPath in childParsingPaths:

                    newResult = bitarray()
                    if childParsingPath.hasData(self):
                        newResult += childParsingPath.getData(self)

                    if childParsingPath.hasData(self.children[0]):
                        newResult += childParsingPath.getData(self.children[0])

                    remainingDataToParse = dataToParse[len(newResult):]

                    break_repeat = self.nbRepeat(i_repeat + 1,
                                                 newResult,
                                                 childParsingPath,
                                                 self.children[0],
                                                 remainingDataToParse)

                    childParsingPath.ok = True
                    (addresult_succeed, addresult_parsingPaths) = childParsingPath.addResult(self, newResult)
                    if not addresult_succeed:
                        childParsingPath.ok = False

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

                    if len(dataToParse) <= len(newResult):
                        break_repeat = RepeatResult.STOP_AFTER
                        break

            if break_repeat is RepeatResult.STOP_BEFORE:
                break
            if len(tmp_results) > 0:
                newParsingPaths = tmp_results
            if break_repeat is RepeatResult.STOP_AFTER:
                break
            if break_repeat is RepeatResult.CONTINUE:
                for res in tmp_results:
                    res.ok = True

        yield from newParsingPaths

    @typeCheck(SpecializingPath)
    def specialize(self, originalSpecializingPath, acceptCallBack=True, preset=None, triggered=False):
        """Specializes a Repeat"""

        from netzob.Fuzzing.Mutator import MaxFuzzingException

        if originalSpecializingPath is None:
            raise Exception("Specializing path cannot be None")

        self._logger.debug("Specialize with {}".format(originalSpecializingPath))

        newSpecializingPath = originalSpecializingPath

        # If we are in a fuzzing mode
        if preset is not None and preset.get(self) is not None:

            # Retrieve the mutator
            mutator = preset.get(self)

            # As the current node variable is preset, we set its children to be inaccessible when targeted by another field/variable
            for child in self.children:
                originalSpecializingPath.setInaccessibleVariableRecursively(child)

            try:
                # Chose the child according to the integer returned by the mutator
                generated_value = mutator.generate()
            except MaxFuzzingException:
                self._logger.debug("Maximum mutation counter reached")
                return

            if mutator.mode == FuzzingMode.FIXED:
                while True:
                    if isinstance(generated_value, bitarray):
                        value = generated_value
                    else:
                        value = bitarray(endian='big')
                        value.frombytes(generated_value)

                    originalSpecializingPath.addResult(self, value)
                    yield originalSpecializingPath
            else:
                i_repeat = generated_value

        # Else, randomly chose the child
        else:
            if callable(self.nbRepeat):
                i_repeat = Repeat.MAX_REPEAT
            elif isinstance(self.nbRepeat, AbstractVariable):
                if newSpecializingPath.hasData(self.nbRepeat):
                    i_repeat_bits = newSpecializingPath.getData(self.nbRepeat)
                    i_repeat_bytes = i_repeat_bits.tobytes()
                    i_repeat = int.from_bytes(i_repeat_bytes, byteorder=self.nbRepeat.dataType.endianness.value)
                else:
                    i_repeat = 0
                    newSpecializingPath.registerVariablesCallBack([self.nbRepeat], self, parsingCB=False)
            else:
                i_repeat = random.randint(self.nbRepeat[0], self.nbRepeat[1])

        if i_repeat == 0:
            newSpecializingPath.addResult(self, bitarray())
            yield newSpecializingPath
        else:
            yield from self._inner_specialize(newSpecializingPath, 0, i_repeat, preset)

    def _inner_specialize(self, newSpecializingPath, i_repeat, max_repeat, preset):

        self._logger.debug("Try iteration {}/{} of Repeat specialize with {}".format(i_repeat, max_repeat, newSpecializingPath))

        break_repeat = RepeatResult.CONTINUE

        child = self.children[0]

        for path in child.specialize(newSpecializingPath, preset=preset):

            # Compute precedent REPEAT result
            if path.hasData(self):
                oldResult = path.getData(self)
                newResult = path.getData(self).copy()
                if self.delimiter is not None:
                    newResult += self.delimiter
            else:
                oldResult = bitarray('')
                newResult = bitarray('')

            # Compute current REPEAT result
            if path.hasData(child):
                newResult += path.getData(child)
            else:
                self._logger.debug("The REPEAT child ('{}') has no content, therefore we don't produce content for the REPEAT".format(child))
                self._logger.debug("Callback registered on ancestor node: '{}'".format(self))
                self._logger.debug("Callback registered due to absence of content in target: '{}'".format(child))
                path.registerVariablesCallBack(
                    [child], self, parsingCB=False)
                yield path

            if callable(self.nbRepeat):
                break_repeat = self.nbRepeat(i_repeat + 1, newResult,
                                             path, child, None)

            if break_repeat is RepeatResult.STOP_BEFORE:
                # save previous result, then notify
                path.addResult(self, oldResult, notify=True)
            elif break_repeat is RepeatResult.STOP_AFTER:
                # save last result, then notify
                path.addResult(self, newResult, notify=True)
            else:
                # save last result, then notify on last iteration only
                last_round = (i_repeat == max_repeat - 1)
                path.addResult(self, newResult, notify=last_round)

            # We forget the assigned data to the child variable and its children
            path.removeDataRecursively(child)

            if break_repeat is not RepeatResult.CONTINUE or i_repeat == max_repeat - 1:
                yield path
            else:
                yield from self._inner_specialize(path, i_repeat + 1, max_repeat, preset)

    @property
    def nbRepeat(self):
        return self.__nbRepeat

    @nbRepeat.setter  # type: ignore
    def nbRepeat(self, nbRepeat):
        if nbRepeat is None:
            raise Exception("NB Repeat cannot be None")

        if isinstance(nbRepeat, int):
            nbRepeat = (nbRepeat, nbRepeat)

        from netzob.Model.Vocabulary.Field import Field
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
        elif isinstance(nbRepeat, AbstractVariable):
            self.__nbRepeat = nbRepeat
        elif isinstance(nbRepeat, Field):
            self.__nbRepeat = nbRepeat.domain
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


def _test_repeat():
    r"""

    >>> from netzob.all import *
    >>> Conf.apply()

    ## Size field on the left

    Size field targeting a field containing a repeat variable, with size field on the left:

    >>> f1 = Field(Repeat(Raw(b"A"), nbRepeat=4), name='f1')
    >>> f2 = Field(Size(f1, dataType=uint8()), name='f2')
    >>> s = Symbol([f2, f1])
    >>> d = next(s.specialize())
    >>> d
    b'\x04AAAA'
    >>> s.abstract(d)
    OrderedDict([('f2', b'\x04'), ('f1', b'AAAA')])

    Size field targeting a field containing a repeat variable of non fixed size, with size field on the left:

    >>> f1 = Field(Repeat(Raw(b"A"), nbRepeat=(2,5)), name='f1')
    >>> f2 = Field(Size(f1, dataType=uint8()), name='f2')
    >>> s = Symbol([f2, f1])
    >>> d = next(s.specialize())
    >>> d
    b'\x05AAAAA'
    >>> s.abstract(d)
    OrderedDict([('f2', b'\x05'), ('f1', b'AAAAA')])

    Size field targeting a repeat variable, with size field on the left:

    >>> v1 = Repeat(Raw(b"A"), nbRepeat=5)
    >>> v2 = Size(v1, dataType=uint8())
    >>> s = Symbol([Field(v2, name='f1'), Field(v1, name='f2')])
    >>> d = next(s.specialize())
    >>> d
    b'\x05AAAAA'
    >>> s.abstract(d)
    OrderedDict([('f1', b'\x05'), ('f2', b'AAAAA')])

    Size field targeting a repeat variable of non fixed size, with size field on the left:

    >>> v1 = Repeat(Raw(b"A"), nbRepeat=(2, 5))
    >>> v2 = Size(v1, dataType=uint8())
    >>> s = Symbol([Field(v2, name='f1'), Field(v1, name='f2')])
    >>> d = next(s.specialize())
    >>> d
    b'\x02AA'
    >>> s.abstract(d)
    OrderedDict([('f1', b'\x02'), ('f2', b'AA')])


    ## Size field on the right

    Size field targeting a field containing a repeat variable, with size field on the right:

    >>> f1 = Field(Repeat(Raw(b"A"), nbRepeat=4), name='f1')
    >>> f2 = Field(Size(f1, dataType=uint8()), name='f2')
    >>> s = Symbol([f1, f2])
    >>> d = next(s.specialize())
    >>> d
    b'AAAA\x04'
    >>> s.abstract(d)
    OrderedDict([('f1', b'AAAA'), ('f2', b'\x04')])

    Size field targeting a field containing a repeat variable of non fixed size, with size field on the right:

    >>> f1 = Field(Repeat(Raw(b"A"), nbRepeat=(2,5)), name='f1')
    >>> f2 = Field(Size(f1, dataType=uint8()), name='f2')
    >>> s = Symbol([f1, f2])
    >>> d = next(s.specialize())
    >>> d
    b'AAAAA\x05'
    >>> s.abstract(d)
    OrderedDict([('f1', b'AAAAA'), ('f2', b'\x05')])

    Size field targeting a repeat variable, with size field on the right:

    >>> v1 = Repeat(Raw(b"A"), nbRepeat=5)
    >>> v2 = Size(v1, dataType=uint8())
    >>> s = Symbol([Field(v1, name='f1'), Field(v2, name='f2')])
    >>> d = next(s.specialize())
    >>> d
    b'AAAAA\x05'
    >>> s.abstract(d)
    OrderedDict([('f1', b'AAAAA'), ('f2', b'\x05')])

    Size field targeting a repeat variable of non fixed size, with size field on the right:

    >>> v1 = Repeat(Raw(b"A"), nbRepeat=(2, 5))
    >>> v2 = Size(v1, dataType=uint8())
    >>> s = Symbol([Field(v1, name='f1'), Field(v2, name='f2')])
    >>> d = next(s.specialize())
    >>> d
    b'AAAA\x04'
    >>> s.abstract(d)
    OrderedDict([('f1', b'AAAA'), ('f2', b'\x04')])


    ## Value field on the left

    Value field targeting a field containing a repeat variable, with value field on the left:

    >>> f1 = Field(Repeat(Raw(b"A"), nbRepeat=4), name='f1')
    >>> f2 = Field(Value(f1), name='f2')
    >>> s = Symbol([f2, f1])
    >>> next(s.specialize())
    Traceback (most recent call last):
    ...
    TypeError: Value target contains a Repeat variable, which is not supported
    >>> s.abstract(b'AAAAAAAA')
    Traceback (most recent call last):
    ...
    TypeError: Value target contains a Repeat variable, which is not supported


    Value field targeting a field containing a repeat variable of non fixed size, with value field on the left:

    >>> f1 = Field(Repeat(Raw(b"A"), nbRepeat=(2,5)), name='f1')
    >>> f2 = Field(Value(f1), name='f2')
    >>> s = Symbol([f2, f1])
    >>> next(s.specialize())
    Traceback (most recent call last):
    ...
    TypeError: Value target contains a Repeat variable, which is not supported
    >>> s.abstract(b'AAAA')
    Traceback (most recent call last):
    ...
    TypeError: Value target contains a Repeat variable, which is not supported


    Value field targeting a repeat variable, with value field on the left:

    >>> v1 = Repeat(Raw(b"A"), nbRepeat=5)
    >>> v2 = Value(v1)
    >>> s = Symbol([Field(v2, name='f1'), Field(v1, name='f2')])
    >>> next(s.specialize())
    Traceback (most recent call last):
    ...
    TypeError: Value target contains a Repeat variable, which is not supported
    >>> s.abstract(b'AAAAAAAAAA')
    Traceback (most recent call last):
    ...
    TypeError: Value target contains a Repeat variable, which is not supported


    Value field targeting a repeat variable of non fixed size, with value field on the left:

    >>> v1 = Repeat(Raw(b"A"), nbRepeat=(2, 5))
    >>> v2 = Value(v1)
    >>> s = Symbol([Field(v2, name='f1'), Field(v1, name='f2')])
    >>> next(s.specialize())
    Traceback (most recent call last):
    ...
    TypeError: Value target contains a Repeat variable, which is not supported
    >>> s.abstract(b'AAAAAAAA')
    Traceback (most recent call last):
    ...
    TypeError: Value target contains a Repeat variable, which is not supported


    ## Value field on the right

    Value field targeting a field containing a repeat variable, with value field on the right:

    >>> f1 = Field(Repeat(Raw(b"A"), nbRepeat=4), name='f1')
    >>> f2 = Field(Value(f1), name='f2')
    >>> s = Symbol([f1, f2])
    >>> d = next(s.specialize())
    >>> d
    b'AAAAAAAA'
    >>> s.abstract(d)
    OrderedDict([('f1', b'AAAA'), ('f2', b'AAAA')])

    Value field targeting a field containing a repeat variable of non fixed size, with value field on the right:

    >>> f1 = Field(Repeat(Raw(b"A"), nbRepeat=(2,5)), name='f1')
    >>> f2 = Field(Value(f1), name='f2')
    >>> s = Symbol([f1, f2])
    >>> d = next(s.specialize())
    >>> d
    b'AAAA'
    >>> s.abstract(d)
    OrderedDict([('f1', b'AA'), ('f2', b'AA')])


    Value field targeting a repeat variable, with value field on the right:

    >>> v1 = Repeat(Raw(b"A"), nbRepeat=5)
    >>> v2 = Value(v1)
    >>> s = Symbol([Field(v1, name='f1'), Field(v2, name='f2')])
    >>> d = next(s.specialize())
    >>> d
    b'AAAAAAAAAA'
    >>> s.abstract(d)
    OrderedDict([('f1', b'AAAAA'), ('f2', b'AAAAA')])

    Value field targeting a repeat variable of non fixed size, with value field on the right:

    >>> v1 = Repeat(Raw(b"A"), nbRepeat=(2, 5))
    >>> v2 = Value(v1)
    >>> s = Symbol([Field(v1, name='f1'), Field(v2, name='f2')])
    >>> d = next(s.specialize())
    >>> d
    b'AAAAAAAA'
    >>> s.abstract(d)
    OrderedDict([('f1', b'AAAA'), ('f2', b'AAAA')])


    # Repeat variable whose nbRepeat is a field/variable on the left

    >>> f1 = Field(uint8(4), name='Nb repeat')
    >>> f2 = Field(Repeat(Raw(b"A"), nbRepeat=f1), name='Repeat')
    >>> s = Symbol([f1, f2])
    >>> d = next(s.specialize())
    >>> d
    b'\x04AAAA'
    >>>
    >>> s.abstract(d)
    OrderedDict([('Nb repeat', b'\x04'), ('Repeat', b'AAAA')])

    >>> f1 = Field(uint8(), name='Nb repeat')
    >>> f2 = Field(Repeat(Raw(b"A"), nbRepeat=f1), name='Repeat')
    >>> s = Symbol([f1, f2])
    >>> d = next(s.specialize())
    >>> d
    b'&AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
    >>>
    >>> s.abstract(d)
    OrderedDict([('Nb repeat', b'&'), ('Repeat', b'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA')])


    >>> f1 = Field(uint8(), name='Nb repeat')
    >>> f2 = Field(Repeat(Raw(b"A"), nbRepeat=f1), name='Repeat')
    >>> f3 = Field(Raw(b"A"))
    >>> s = Symbol([f1, f2, f3])
    >>> d = next(s.specialize())
    >>> d
    b'\x7fAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
    >>>
    >>> s.abstract(d)
    OrderedDict([('Nb repeat', b'\x7f'), ('Repeat', b'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'), ('Field', b'A')])


    # Repeat variable whose nbRepeat is a field/variable on the right

    >>> f2 = Field(uint8(4), name='Size field')
    >>> f1 = Field(Repeat(Raw(b"A"), nbRepeat=f2), name='Repeat field')
    >>> s = Symbol([f1, f2])
    >>> d = next(s.specialize())
    >>> d
    b'AAAA\x04'
    >>>
    >>> s.abstract(d)
    OrderedDict([('Repeat field', b'AAAA'), ('Size field', b'\x04')])

    >>> f2 = Field(uint8(), name='Size field')
    >>> f1 = Field(Repeat(Raw(b"A"), nbRepeat=f2), name='Repeat field')
    >>> s = Symbol([f1, f2])
    >>> d = next(s.specialize())
    >>> d
    b'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\xb8'
    >>> s.abstract(d)
    OrderedDict([('Repeat field', b'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'), ('Size field', b'\xb8')])

    >>> f3 = Field(uint8(), name='Size field')
    >>> f1 = Field(Repeat(Raw(b"A"), nbRepeat=f3), name='Repeat field')
    >>> f2 = Field(Raw(b"A"))
    >>> s = Symbol([f1, f2, f3])
    >>> d = next(s.specialize())
    >>> d
    b'AAAAAAAAAAAAAAAAAAAAAAA\x16'
    >>> s.abstract(d)
    OrderedDict([('Repeat field', b'AAAAAAAAAAAAAAAAAAAAAA'), ('Field', b'A'), ('Size field', b'\x16')])


    # Test of Repeat and Length field encoded with a Raw datatype

    >>> from netzob.all import *
    >>> f1=Field(uint8(), name="count")
    >>> f2=Field(Repeat(Raw(b'abc'), nbRepeat=f1), name="elements")
    >>> f3=Field(Size([f1, f2], dataType=Raw(nbBytes=2)), name="total")
    >>> s = Symbol([f1, f2, f3])
    >>> next(s.specialize())
    b'\xd7abcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabc\x02\x86'

    """
