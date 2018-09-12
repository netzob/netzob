#-*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|          01001110 01100101 01110100 01111010 01101111 01100010            |
#|                                                                           |
#|               Netzob : Inferring communication protocols                  |
#+---------------------------------------------------------------------------+
#| Copyright (C) 2011-2017 Georges Bossert and Frédéric Guihéry              |
#| This program is free software: you can redistribute it and/or modify      |
#| it under the terms of the GNU General Public License as published by      |
#| the Free Software Foundation, either version 3 of the License, or         |
#| (at your option) any later version.                                       |
#|                                                                           |
#| This program is distributed in the hope that it will be useful,           |
#| but WITHOUT ANY WARRANTY; without even the implied warranty of            |
#| MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the              |
#| GNU General Public License for more details.                              |
#|                                                                           |
#| You should have received a copy of the GNU General Public License         |
#| along with this program. If not, see <http://www.gnu.org/licenses/>.      |
#+---------------------------------------------------------------------------+
#| @url      : http://www.netzob.org                                         |
#| @contact  : contact@netzob.org                                            |
#| @sponsors : Amossys, http://www.amossys.fr                                |
#|             Supélec, http://www.rennes.supelec.fr/ren/rd/cidre/           |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| File contributors :                                                       |
#|       - Georges Bossert <georges.bossert (a) supelec.fr>                  |
#|       - Frédéric Guihéry <frederic.guihery (a) amossys.fr>                |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Standard library imports                                                  |
#+---------------------------------------------------------------------------+
import random
from typing import Callable, List
from bitarray import bitarray

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, public_api, NetzobLogger
from netzob.Model.Vocabulary.Domain.Variables.AbstractVariable import AbstractVariable
from netzob.Model.Vocabulary.Domain.Variables.Nodes.AbstractVariableNode import AbstractVariableNode
from netzob.Model.Vocabulary.Domain.GenericPath import GenericPath
from netzob.Model.Vocabulary.Domain.Parser.ParsingPath import ParsingPath, ParsingException
from netzob.Model.Vocabulary.Domain.Specializer.SpecializingPath import SpecializingPath
from netzob.Fuzzing.Mutators.DomainMutator import FuzzingMode


altCbkType = Callable[[GenericPath, List[AbstractVariable]], AbstractVariable]


@NetzobLogger
class Alt(AbstractVariableNode):
    """The Alt class is a node variable that represents an alternative of variables.

    A definition domain can take the form of a combination of
    permitted values/types/domains. This combination is represented by
    an alternate node. It can be seen as an OR operator between two or
    more children nodes.

    The Alt constructor expects some parameters:

    :param children: The set of variable elements permitted in the
                     alternative. The default is None.
    :param callback: The callback function that may be used to determine the child index to select. The default is None.
    :param name: The name of the variable (if None, the name will
                 be generated).
    :type children: a :class:`list` of :class:`Variable <netzob.Model.Vocabulary.Domain.Variables.AbstractVariable.AbstractVariable>`, optional
    :type callback: :class:`Callable <collections.abc.Callable>`, optional
    :type name: :class:`str`, optional

    The Alt class provides the following public variables:

    :var children: The sorted typed list of children attached to the variable node.
    :var callback: The callback function that may be used to determine the child index to select.
    :vartype children: a list of :class:`Variable <netzob.Model.Vocabulary.Domain.Variables.AbstractVariable.AbstractVariable>`
    :vartype callback: :class:`Callable <collections.abc.Callable>`


    **Callback prototype**

    The callback function that can be used to determine the child
    index to select has the following prototype:

    .. function:: cbk_child_selection(path, children)
       :noindex:

       :param path: data structure that allows access to the values of the
                    :class:`Variable <netzob.Model.Vocabulary.Domain.Variables.AbstractVariable.AbstractVariable>`
                    elements.
       :type path: object
       :param children: children of the
                        :class:`~netzob.Model.Vocabulary.Domain.Variables.Nodes.Alt.Alt`
                        variable.
       :type children: ~typing.List[~netzob.Model.Vocabulary.Domain.Variables.Nodes.Alt.Alt]

       :return: The callback function should return an integer used to determine
                the child index to select.
       :rtype: :class:`int`

    The ``children`` is a list of :class:`Variable
    <netzob.Model.Vocabulary.Domain.Variables.AbstractVariable.AbstractVariable>`. Each
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


    **Alt examples**

    The following code denotes an alternate object that
    accepts either the string "filename1.txt" or the string
    "filename2.txt":

    >>> from netzob.all import *
    >>> t1 = String("filename1.txt")
    >>> t2 = String("filename2.txt")
    >>> domain = Alt([t1, t2])


    **Examples of Alt internal attribute access**

    >>> from netzob.all import *
    >>> domain = Alt([Raw(), String()])
    >>> print(domain.children[0].dataType)
    Raw(nbBytes=(0,8192))
    >>> print(domain.children[1].dataType)
    String(nbChars=(0,8192))


    **Example of a deterministic Alt computation**

    >>> def cbk(path, children):
    ...    return -1
    >>> f = Field(Alt([String(_) for _ in "abc"], callback=cbk), "alt")
    >>> sym = Symbol([f])
    >>> data = next(sym.specialize())
    >>> print(data)
    b'c'
    >>> sym.abstract(data)
    OrderedDict([('alt', b'c')])


    .. ifconfig:: scope in ('netzob')

       **Abstraction of alternate variables**

       This example shows the abstraction process of an Alternate
       variable:

       >>> from netzob.all import *
       >>> v0 = String("john")
       >>> v1 = String("kurt")
       >>> f0 = Field(Alt([v0, v1]), name='f0')
       >>> s = Symbol([f0])
       >>> data = "john"
       >>> s.abstract(data)
       OrderedDict([('f0', b'john')])
       >>> data = "kurt"
       >>> s.abstract(data)
       OrderedDict([('f0', b'kurt')])

       In the following example, an Alternate variable is defined. A
       message that does not correspond to the expected model is then
       parsed, thus an exception is returned:

       >>> data = "nothing"
       >>> s.abstract(data)
       Traceback (most recent call last):
       ...
       netzob.Model.Vocabulary.AbstractField.AbstractionException: With the symbol/field 'Symbol', cannot abstract the data: 'nothing'. Error: 'No parsing path returned while parsing 'b'nothing'''

    """

    @public_api
    def __init__(self, children=None, callback=None, name=None):
        super(Alt, self).__init__(self.__class__.__name__, children=children, name=name)
        self._callback = callback  # type: altCbkType

    @public_api
    def copy(self, map_objects=None):
        """Copy the current object as well as all its dependencies.

        :return: A new object of the same type.
        :rtype: :class:`Alt <netzob.Model.Vocabulary.Domain.Variables.Nodes.Alt.Alt>`

        """
        if map_objects is None:
            map_objects = {}
        if self in map_objects:
            return map_objects[self]

        new_alt = Alt([], callback=self.callback)
        map_objects[self] = new_alt

        new_children = []
        for child in self.children:
            if child in map_objects.keys():
                new_children.append(map_objects[child])
            else:
                new_child = child.copy(map_objects)
                new_children.append(new_child)

        new_alt.children = new_children
        return new_alt

    @typeCheck(ParsingPath)
    def parse(self, parsingPath, acceptCallBack=True, carnivorous=False, triggered=False):
        """Parse the content with the definition domain of the alternate."""

        if parsingPath is None:
            raise Exception("ParsingPath cannot be None")

        if len(self.children) == 0:
            raise Exception("Cannot parse data if ALT has no children")

        dataToParse = parsingPath.getData(self)
        self._logger.debug("Parse '{}' with '{}'".format(dataToParse.tobytes(), self))

        parserPaths = [parsingPath]
        parsingPath.assignData(dataToParse.copy(), self.children[0])

        # create a path for each child
        if len(self.children) > 1:
            for child in self.children[1:]:
                newParsingPath = parsingPath.copy()
                newParsingPath.assignData(dataToParse.copy(), child)
                parserPaths.append(newParsingPath)

        # parse each child according to its definition
        for i_child, child in enumerate(self.children):
            parsingPath = parserPaths[i_child]
            self._logger.debug("Start Alt parsing of {0}/{1} with {2}".format(i_child + 1, len(self.children), parsingPath))

            try:
                childParsingPaths = child.parse(parsingPath)
            except ParsingException:
                self._logger.debug("Error in parsing of child")
            else:
                for childParsingPath in childParsingPaths:
                    data_parsed = childParsingPath.getData(child)
                    self._logger.debug("End of Alt parsing of {}/{} with {}. Data parsed: '{}'".format(i_child + 1, len(self.children), parsingPath, data_parsed))
                    childParsingPath.addResult(self, data_parsed)
                    yield childParsingPath
        self._logger.debug("End of parsing of Alt variable")

    @typeCheck(SpecializingPath)
    def specialize(self, specializingPath, acceptCallBack=True, preset=None, triggered=False):
        """Specializes an Alt"""

        from netzob.Fuzzing.Mutator import MaxFuzzingException

        if specializingPath is None:
            raise Exception("SpecializingPath cannot be None")

        if len(self.children) == 0:
            raise Exception("Cannot specialize ALT if its has no children")

        # If we are in a fuzzing mode
        if preset is not None and preset.get(self) is not None:

            # Retrieve the mutator
            mutator = preset.get(self)

            # As the current node variable is preset, we set its children to be inaccessible when targeted by another field/variable
            for child in self.children:
                specializingPath.setInaccessibleVariableRecursively(child)

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

                    specializingPath.addResult(self, value)
                    yield specializingPath

            if 0 <= generated_value < len(self.children):
                child = self.children[generated_value]
            else:
                raise ValueError("Field position '{}' is bigger than the length of available children '{}'"
                                 .format(generated_value, len(self.children)))

        elif callable(self.callback):
            i_child = self.callback(specializingPath, self.children)
            if not isinstance(i_child, int):
                raise Exception("The Alt callback return value must be the index"
                                " (int) of the child to select, not '{}'"
                                .format(i_child))
            child = self.children[i_child]
        # Else, randomly chose the child
        else:
            child = random.choice(self.children)

        newSpecializingPath = specializingPath#.copy()

        self._logger.debug("Specialize {0} child with {1}".format(child, newSpecializingPath))

        if not newSpecializingPath.hasData(child):
            childSpecializingPaths = child.specialize(newSpecializingPath, preset=preset)
        else:
            self._logger.debug("Not specializing the ALT.child as it has already a data")
            childSpecializingPaths = (newSpecializingPath, )

        for childSpecializingPath in childSpecializingPaths:
            if childSpecializingPath.hasData(child):
                value = childSpecializingPath.getData(child)
                self._logger.debug("Generated value for {}: {} ({})".format(self, value, id(self)))
                childSpecializingPath.addResult(self, value)

                yield childSpecializingPath
            else:
                self._logger.debug("The ALT child ('{}') has no content, therefore we don't produce content for the ALT".format(child))
                self._logger.debug("Callback registered on ancestor node: '{}'".format(self))
                self._logger.debug("Callback registered due to absence of content in target: '{}'".format(child))
                childSpecializingPath.registerVariablesCallBack(
                    [child], self, parsingCB=False)
                yield childSpecializingPath

    @public_api
    @property
    def callback(self):
        """A callback function can be used to determine the child index to
        select, during specialization (see 'Callback prototype' above
        for further explanation).

        """
        return self._callback

    @callback.setter  # type: ignore
    def callback(self, callback):
        if not callable(callback):
            raise TypeError("Callback function should be a callable, not a '{}'".format(callback))
        self._callback = callback


def _test_alt(self):
    r"""

    >>> from netzob.all import *
    >>> Conf.apply()

    Here is an example with an Alt variable:

    >>> from netzob.all import *
    >>> m1 = RawMessage("220044")
    >>> f1 = Field("22", name="f1")
    >>> f2 = Field(Alt(["00", "0044", "0", "004"]), name="f2")
    >>> s = Symbol([f1, f2], messages=[m1], name="S0")
    >>> print(s.str_data())
    f1   | f2    
    ---- | ------
    '22' | '0044'
    ---- | ------


    ## Size field on the right

    Size field targeting a field containing a alt variable, with size field on the right:

    >>> f1 = Field(Alt(["A", "B", "C"]), name='f1')
    >>> f2 = Field(Size(f1, dataType=uint8()), name='f2')
    >>> s = Symbol([f2, f1])
    >>> d = next(s.specialize())
    >>> d
    b'\x01C'
    >>> s.abstract(d)
    OrderedDict([('f2', b'\x01'), ('f1', b'C')])

    Size field targeting a alt variable, with size field on the right:

    >>> v1 = Alt(["A", "B", "C"])
    >>> v2 = Size(v1, dataType=uint8())
    >>> s = Symbol([Field(v2, name='f2'), Field(v1, name='f1')])
    >>> d = next(s.specialize())
    >>> d
    b'\x01A'
    >>> s.abstract(d)
    OrderedDict([('f2', b'\x01'), ('f1', b'A')])


    ## Size field on the left

    Size field targeting a field containing a alt variable, with size field on the left:

    >>> f1 = Field(Alt(["A", "B", "C"]), name='f1')
    >>> f2 = Field(Size(f1, dataType=uint8()), name='f2')
    >>> s = Symbol([f1, f2])
    >>> d = next(s.specialize())
    >>> d
    b'B\x01'
    >>> s.abstract(d)
    OrderedDict([('f1', b'B'), ('f2', b'\x01')])

    Size field targeting a alt variable, with size field on the left:

    >>> v1 = Alt(["A", "B", "C"])
    >>> v2 = Size(v1, dataType=uint8())
    >>> s = Symbol([Field(v1, name='f1'), Field(v2, name='f2')])
    >>> d = next(s.specialize())
    >>> d
    b'B\x01'
    >>> s.abstract(d)
    OrderedDict([('f1', b'B'), ('f2', b'\x01')])


    ## Value field on the right

    Value field targeting a field containing a alt variable, with value field on the right:

    >>> f1 = Field(Alt(["A", "B", "C"]), name='f1')
    >>> f2 = Field(Value(f1), name='f2')
    >>> s = Symbol([f2, f1])
    >>> d = next(s.specialize())
    >>> d
    b'CC'
    >>> s.abstract(d)
    OrderedDict([('f2', b'C'), ('f1', b'C')])

    Value field targeting a alt variable, with value field on the right:

    >>> v1 = Alt(["A", "B", "C"])
    >>> v2 = Value(v1)
    >>> s = Symbol([Field(v2, name='f2'), Field(v1, name='f1')])
    >>> d = next(s.specialize())
    >>> d
    b'AA'
    >>> s.abstract(d)
    OrderedDict([('f2', b'A'), ('f1', b'A')])


    ## Value field on the left

    Value field targeting a field containing a alt variable, with value field on the left:

    >>> f1 = Field(Alt(["A", "B", "C"]), name='f1')
    >>> f2 = Field(Value(f1), name='f2')
    >>> s = Symbol([f1, f2])
    >>> d = next(s.specialize())
    >>> d
    b'AA'
    >>> s.abstract(d)
    OrderedDict([('f1', b'A'), ('f2', b'A')])

    Value field targeting a alt variable, with value field on the left:

    >>> v1 = Alt(["A", "B", "C"])
    >>> v2 = Value(v1)
    >>> s = Symbol([Field(v1, name='f1'), Field(v2, name='f2')])
    >>> d = next(s.specialize())
    >>> d
    b'BB'
    >>> s.abstract(d)
    OrderedDict([('f1', b'B'), ('f2', b'B')])

    """
