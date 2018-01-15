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
from bitarray import bitarray

# +---------------------------------------------------------------------------+
# | Related third party imports                                               |
# +---------------------------------------------------------------------------+

# +---------------------------------------------------------------------------+
# | Local application imports                                                 |
# +---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger
from netzob.Model.Vocabulary.Domain.Variables.Nodes.AbstractVariableNode import AbstractVariableNode
from netzob.Model.Vocabulary.Domain.Parser.ParsingPath import ParsingPath
from netzob.Model.Vocabulary.Domain.Specializer.SpecializingPath import SpecializingPath


# Class used to denote current variable, in order to handle self recursivity
class SELF(object):
    pass


@NetzobLogger
class Agg(AbstractVariableNode):
    r"""The Agg class is a node variable that represents a concatenation of variables.

    An aggregate node concatenates the values that are accepted by
    its children nodes. It can be used to specify a succession of
    tokens.

    The Agg constructor expects some parameters:

    :param children: The sequence of variable elements contained in
                     the aggregate. The default value is None.
    :param last_optional: A flag indicating if the last element of the children is optional or not. The default value is False.
    :type children: a :class:`list` of :class:`Variable <netzob.Model.Vocabulary.Domain.Variables.AbstractVariable>`, optional
    :type last_optional: :class:`bool`, optional


    The Agg class supports modeling of direct recursions on the
    right. To do so, the flag ``SELF`` is available, and should only
    be used in the last position of the aggregate (see example below).

    The Agg class provides the following public variables:

    :var children: The sorted typed list of children attached to the variable node.
    :var varType: The type of the variable (Read-only).
    :vartype children: a list of :class:`Variable <netzob.Model.Vocabulary.Variables.Variable>`
    :vartype varType: :class:`str`


    **Aggregate examples**

    For example, the following code represents a field that
    accepts values that are made of a String of 3 to 20 random
    characters followed by a ".txt" extension:

    >>> from netzob.all import *
    >>> t1 = String(nbChars=(3,20))
    >>> t2 = String(".txt")
    >>> f = Field(Agg([t1, t2]))

    The following example shows an aggregate between BitArray
    variables:

    >>> from netzob.all import *
    >>> f = Field(Agg([BitArray('01101001'), BitArray(nbBits=3), BitArray(nbBits=5)]))
    >>> t = f.specialize()
    >>> len(t)
    2


    **Examples of Agg internal attribute access**

    >>> from netzob.all import *
    >>> domain = Agg([Raw(), String()])
    >>> domain.varType
    'Agg'
    >>> print(domain.children[0].dataType)
    Raw(nbBytes=(0,8192))
    >>> print(domain.children[1].dataType)
    String(nbChars=(0,8192))
    >>> domain.children.append(Agg([10, 20, 30]))
    >>> len(domain.children)
    3
    >>> domain.children.remove(domain.children[0])
    >>> len(domain.children)
    2


    **Abstraction of aggregate variables**

    This example shows the abstraction process of an Aggregate
    variable:

    >>> from netzob.all import *
    >>> v1 = String(nbChars=(1, 10))
    >>> v2 = String(".txt")
    >>> f0 = Field(Agg([v1, v2]), name="f0")
    >>> f1 = Field(String("!"), name="f1")
    >>> f = Field([f0, f1])
    >>> data = "john.txt!"
    >>> Field.abstract(data, [f])
    (Field, OrderedDict([('f0', b'john.txt'), ('f1', b'!')]))

    In the following example, an Aggregate variable is defined. A
    message that does not correspond to the expected model is then
    parsed, thus the returned field is unknown:

    >>> from netzob.all import *
    >>> v1 = String(nbChars=(1, 10))
    >>> v2 = String(".txt")
    >>> f0 = Field(Agg([v1, v2]), name="f0")
    >>> f1 = Field(String("!"), name="f1")
    >>> f = Field([f0, f1])
    >>> data = "johntxt!"
    >>> Field.abstract(data, [f])
    (Unknown message 'johntxt!', OrderedDict())


    **Specialization of aggregate variables**

    This example shows the specialization process of an Aggregate
    variable:

    >>> from netzob.all import *
    >>> d1 = String("hello")
    >>> d2 = String(" john")
    >>> f = Field(Agg([d1, d2]))
    >>> f.specialize()
    b'hello john'


    **Optional last variable**

    This example shows the specialization and parsing of an aggregate
    with an optional last variable*:

    >>> from netzob.all import *
    >>> a = Agg([int8(2), int8(3)], last_optional=True)
    >>> f = Field(a)
    >>> res = f.specialize()
    >>> res == b'\x02' or res == b'\x02\x03'
    True
    >>> d = b'\x02\x03'
    >>> Field.abstract(d, [f])
    (Field, OrderedDict([('Field', b'\x02\x03')]))
    >>> d = b'\x02'
    >>> Field.abstract(d, [f])
    (Field, OrderedDict([('Field', b'\x02')]))


    **Modeling indirect imbrication**

    The following example shows how to specify a field with a
    structure (``v2``) that can contain another structure (``v0``),
    through a tierce structure (``v1``). The flag ``last_optional`` is
    used to indicate that the specialization or parsing of the last
    element of the aggregates ``v1`` and ``v2`` is optional.

    >>> from netzob.all import *
    >>> v0 = Agg(["?", int8(4)])
    >>> v1 = Agg(["!", int8(3), v0], last_optional=True)
    >>> v2 = Agg([int8(2), v1], last_optional=True)
    >>> f = Field(v2)
    >>>
    >>> # Test specialization
    >>> res = f.specialize()
    >>> res == b'\x02' or res == b'\x02!\x03' or res == b'\x02!\x03?\x04'
    True
    >>>
    >>> # Test parsing
    >>> (res_object, res_data) = Field.abstract(res, [f])
    >>> res_object == f
    True


    .. warning::
       **Important note about recursion**

       The library can handle both direct and indirect recursion. However,
       there is a limitation requiring the use of a recursing variable on the
       **right side of a statement**. Any other behavior could lead to
       infinite recursion during the loading of the model.
       To help understand what syntax should be preferred, here is a list of
       annotated BNF syntaxes.

       *invalid syntaxes:*

       .. productionlist::
          A: [A] integer
           : <recursion on the left side>
          B: ( "(" B ) | ( "." ")" )
           : <recursion on the middle>

       *valid adaptations from above examples*:

       .. productionlist::
          A: integer+
           : <recursion is replaced by a repeat approach>
          B: B' ")"
           : <split the statement ...>
          B': ( "(" B ) | "."
            : <to transform a direct recursion into an indirect recursion on the right side>

       *valid recursion examples*:

       .. productionlist::
          C: "." C*
           :  <a string with one or more dot characters>
          D: ( D | "." )*
           :  <a string with zero or more dot characters>

    **Modeling direct recursion, simple example**

    The following example shows how to specify a field with a
    structure (``v``) that can optionally contain itself. To model
    such recursive structure, the ``SELF`` flag has to be used in the
    last position of the aggregate.

    >>> from netzob.all import *
    >>> v = Agg([int8(interval=(1, 5)), SELF], last_optional=True)
    >>> f = Field(v)
    >>>
    >>> # Test specialization
    >>> res = f.specialize()
    >>> res  # doctest: +SKIP
    b'\x02\x04\x01'
    >>>
    >>> # Test parsing
    >>> (res_object, res_data) = Field.abstract(res, [f])
    >>> res_object == f  # doctest: +SKIP
    True

    **Modeling direct recursion, more complex example**

    This example introduces a recursion in the middle of an expression by
    modeling a pair group of parentheses (``'('`` and ``')'``), around a
    single character (``'+'``).
    The BNF syntax of this model would be:

    .. productionlist::
       parentheses: ( "(" parentheses)  | ( "+"  ")" )

    This syntax introduces a recursivity in the middle of the `left` statement,
    which **is not supported**. Instead, this syntax could be adapted to move
    the recursivity to the right.

    .. productionlist::
       parentheses: left right
       left: ( "(" parentheses ) | "+"
       right: ")"

    The following models describe this issue and provide a workaround.

    **BAD way**

    >>> from netzob.all import *
    >>> parentheses = Agg(["(", Alt([SELF, "+"]), ")"])
    Traceback (most recent call last):
    ValueError: SELF can only be set at the last position of an Agg

    **GOOD way**

    >>> from netzob.all import *
    >>> parentheses = Agg([])
    >>> left = Agg(["(", Alt([parentheses, "+"])])
    >>> right = ")"
    >>> parentheses.children += [left, right]
    >>>
    >>> symbol = Symbol([Field(parentheses)])
    >>> symbol.specialize()
    b'((+))'


    **Modeling indirect recursion, simple example**

    The following example shows how to specify a field with a
    structure (``v2``) that contains another structure (``v1``), which
    can itself contain the first structure (``v2``). The flag
    ``last_optional`` is used to indicate that the specialization or
    parsing of the last element of the aggregate ``v2`` is optional.

    >>> from netzob.all import *
    >>> v1 = Agg([])
    >>> v2 = Agg([int8(interval=(1, 3)), v1], last_optional=True)
    >>> v1.children = ["!", v2]
    >>> f = Field(v2)
    >>> res = f.specialize()
    >>> res  # doctest: +SKIP
    b'\x03!\x03!\x03!\x03'
    >>>
    >>> # Test parsing
    >>> (res_object, res_data) = Field.abstract(res, [f])
    >>> res_object == f  # doctest: +SKIP
    True


    **Modeling indirect recursion, more complex example**

    The following syntax provides a way to parse and specialize a subset of
    mathematical expressions including pair group of parentheses, digits from 0
    to 9 and two arithmetic operators ('+' and '*').

    .. productionlist::
       num: "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9"
       operator: "+" | "*"
       operation: left right?
       left: num | subop
       right: operator operation
       subop: "(" operation ")"

    The following examples **should** be compatible with these expressions::

        1 + 2
        1 + 2 + 3
        1 + (2 + 3)
        (1 + 2) + 3
        (1 + 2) + 3 + 4
        1 + (2 * 3) + (4 * 5)
        1 + (2 * (3 + 4)) + 5
        1 + ((2 * 3) * 4) * 5

    These last expressions **should not** be compatible with these expressions::

        1
        1 ** 2
        1 * (2 * 3
        1 *

    This example of indirect recursion introduces a recursion of the
    `operation` statement, called in the `subop` statement.

    >>> from netzob.all import *
    >>> num = Alt("0123456789")
    >>> operator = Alt([" + ", " * "])
    >>> operation = Agg([], last_optional=True)
    >>> subop1 = Agg(["(", operation])
    >>> subop2 = Agg([subop1, ")"])
    >>> left = Alt([num, subop2])
    >>> right = Agg([operator, operation])
    >>> operation.children += [left, right]
    >>> sym = Symbol([Field(operation)])  # doctest: +SKIP
    >>> sym.specialize()  # doctest: +SKIP
    b'((((4 * 8 * 4) + 5 + 9 + 0) * 7 * 0 + (4 + 9 + (3 * 4 + 2) * 0) * 9) + 4 * 7)'

    """

    def __init__(self, children=None, last_optional=False):
        super(Agg, self).__init__(self.__class__.__name__, children)

        self._last_optional = last_optional

    @typeCheck(ParsingPath)
    def parse(self, parsingPath, carnivorous=False):
        """Parse the content with the definition domain of the aggregate.
        """
        dataToParse = parsingPath.getData(self).copy()
        self._logger.debug("Parse '{}' as {} with parser path '{}'".format(
            dataToParse.tobytes(), self, parsingPath))

        # initialy, there is a unique path to test (the provided one)
        parsingPath.assignData(dataToParse.copy(), self.children[0])
        parsingPaths = [parsingPath]

        # we parse all the children with the parserPaths produced by previous children
        all_parsed = False
        for i_child in range(len(self.children)):

            # Handle optional field situation, where all data may have already been parsed before the last field
            if all_parsed is True:
                break

            current_child = self.children[i_child]
            if i_child < len(self.children) - 1:
                next_child = self.children[i_child + 1]
            else:
                next_child = None

            newParsingPaths = []

            for parsingPath in parsingPaths:
                self._logger.debug(
                    "Parse {0} with {1}".format(id(current_child), parsingPath))
                value_before_parsing = parsingPath.getData(
                    current_child).copy()
                childParsingPaths = current_child.parse(
                    parsingPath, carnivorous=carnivorous)

                for childParsingPath in childParsingPaths:
                    value_after_parsing = childParsingPath.getData(
                        current_child).copy()
                    remainingValue = value_before_parsing[len(
                        value_after_parsing):].copy()

                    if next_child is not None:
                        # Handle optional field
                        if len(remainingValue) == 0 and i_child == len(self.children) - 2 and self._last_optional:
                            all_parsed = True
                        # Else send the remaining data to the last field
                        else:
                            childParsingPath.assignData(
                                remainingValue, next_child)

                    # at least one child path managed to parse, we save the valid paths it produced
                    self._logger.debug(
                        "Children {0} succesfuly applied with the parsingPath {1}".
                        format(current_child, parsingPath))
                    newParsingPaths.append(childParsingPath)

            parsingPaths = newParsingPaths

            if len(parsingPaths) == 0:
                self._logger.debug("Children {0} didn't apply to any of the parser path we have, we stop Agg parser".format(current_child))
                return []  # return no valid paths

        # ok we managed to parse all the children, and it produced some valid parser paths. We return them
        for parsingPath in parsingPaths:
            parsedData = None
            for child in self.children:
                if parsingPath.hasData(child):
                    child_data = parsingPath.getData(child).copy()
                    if parsedData is None:
                        parsedData = child_data
                    else:
                        parsedData = parsedData + child_data

            self._logger.debug("Data successfuly parsed with {}: '{}'".format(self, parsedData.tobytes()))
            parsingPath.addResult(self, parsedData)
        return parsingPaths

    @typeCheck(SpecializingPath)
    def specialize(self, specializingPath, fuzz=None):
        """Specializes an Agg"""

        from netzob.Fuzzing.Fuzz import MaxFuzzingException

        # If we are in a fuzzing mode
        if fuzz is not None and fuzz.get(self) is not None:

            # Retrieve the mutator
            mutator = fuzz.get(self)

            for path in self._inner_specialize(specializingPath, 0, fuzz):

                try:
                    # Just call the generate() method to increment the counter of mutation
                    mutator.generate()
                except MaxFuzzingException:
                    self._logger.debug("Maximum mutation counter reached")
                    break

                yield path

        else:
            yield from self._inner_specialize(specializingPath, 0, fuzz)

    def _inner_specialize(self, specializingPath, idx, fuzz):

        # Select the child to specialize
        child = self.children[idx]
        self._logger.debug("Specialize {0} child with {1}".format(child, specializingPath))

        specialize_last_child = True
        if len(self.children) - 1 == idx and self._last_optional:
            self._logger.debug("Last child is optional")

            # Randomely select if we are going to specialize the last child
            specialize_last_child = random.choice([True, False])
            if specialize_last_child:
                self._logger.debug("Last child is optional, and this option is taken")
            else:
                self._logger.debug("Last child is optional, and this option is not taken")
                self._produce_data(specializingPath, specialize_last_child)
                yield specializingPath
                return

        # Handle self recursivity
        if type(child) == type and child == SELF:
            # Nothing to specialize in this case (the recursive specialization is done later)
            childSpecializingPaths = (specializingPath, )
        else:
            childSpecializingPaths = child.specialize(specializingPath, fuzz=fuzz)

        for path in childSpecializingPaths:

            # Handle recursive mode
            if type(child) == type and child == SELF and specialize_last_child:
                if path.hasData(self):
                    newResult = path.getData(self)
                else:
                    newResult = bitarray('')
                for inner_path in self._inner_specialize(path, idx, fuzz):

                    if inner_path.hasData(self):
                        current_value = inner_path.getData(self)
                        newResult = newResult + current_value
                        self._logger.debug("Cumulative generated value for {}: {}".format(self, newResult.tobytes()))

            if idx == len(self.children) - 1:
                self._produce_data(path, specialize_last_child)
                yield path
            else:
                yield from self._inner_specialize(path, idx + 1, fuzz)

    def _produce_data(self, path, specialize_last_child):
        data = bitarray()
        for idx, child in enumerate(self.children):
            if len(self.children) - 1 == idx and not specialize_last_child:
                pass
            elif type(child) == type and child == SELF:
                pass
            else:
                data += path.getData(child)
        self._logger.debug("Generated value for {}: {}".format(self, data.tobytes()))
        path.addResult(self, data)


def _test():
    r"""

    >>> from netzob.all import *
    >>> Conf.seed = 0
    >>> Conf.apply()
    

    ## Size field on the right

    Size field targeting a field containing a agg variable, with size field on the right:

    >>> f1 = Field(Agg(["A", "B", "C"]), name='f1')
    >>> f2 = Field(Size(f1, dataType=uint8()), name='f2')
    >>> s = Symbol([f2, f1])
    >>> d = s.specialize()
    >>> d
    b'\x03ABC'
    >>> Symbol.abstract(d, [s])
    (Symbol, OrderedDict([('f2', b'\x03'), ('f1', b'ABC')]))

    Size field targeting a agg variable, with size field on the right:

    >>> v1 = Agg(["A", "B", "C"])
    >>> v2 = Size(v1, dataType=uint8())
    >>> s = Symbol([Field(v2, name='f1'), Field(v1, name='f2')])
    >>> d = s.specialize()
    >>> d
    b'\x03ABC'
    >>> Symbol.abstract(d, [s])
    (Symbol, OrderedDict([('f1', b'\x03'), ('f2', b'ABC')]))


    ## Size field on the left

    Size field targeting a field containing a agg variable, with size field on the left:

    >>> f1 = Field(Agg(["A", "B", "C"]), name='f1')
    >>> f2 = Field(Size(f1, dataType=uint8()), name='f2')
    >>> s = Symbol([f1, f2])
    >>> d = s.specialize()
    >>> d
    b'ABC\x03'
    >>> Symbol.abstract(d, [s])
    (Symbol, OrderedDict([('f1', b'ABC'), ('f2', b'\x03')]))

    Size field targeting a agg variable, with size field on the left:

    >>> v1 = Agg(["A", "B", "C"])
    >>> v2 = Size(v1, dataType=uint8())
    >>> s = Symbol([Field(v1, name='f1'), Field(v2, name='f2')])
    >>> d = s.specialize()
    >>> d
    b'ABC\x03'
    >>> Symbol.abstract(d, [s])
    (Symbol, OrderedDict([('f1', b'ABC'), ('f2', b'\x03')]))


    ## Value field on the right

    Value field targeting a field containing a agg variable, with value field on the right:

    >>> f1 = Field(Agg(["A", "B", "C"]), name='f1')
    >>> f2 = Field(Value(f1), name='f2')
    >>> s = Symbol([f2, f1])
    >>> d = s.specialize()
    >>> d
    b'ABCABC'
    >>> Symbol.abstract(d, [s])
    (Symbol, OrderedDict([('f2', b'ABC'), ('f1', b'ABC')]))

    Value field targeting a agg variable, with value field on the right:

    >>> v1 = Agg(["A", "B", "C"])
    >>> v2 = Value(v1)
    >>> s = Symbol([Field(v2, name='f2'), Field(v1, name='f1')])
    >>> d = s.specialize()
    >>> d
    b'ABCABC'
    >>> Symbol.abstract(d, [s])
    (Symbol, OrderedDict([('f2', b'ABC'), ('f1', b'ABC')]))


    ## Value field on the left

    Value field targeting a field containing a agg variable, with value field on the left:

    >>> f1 = Field(Agg(["A", "B", "C"]), name='f1')
    >>> f2 = Field(Value(f1), name='f2')
    >>> s = Symbol([f1, f2])
    >>> d = s.specialize()
    >>> d
    b'ABCABC'
    >>> Symbol.abstract(d, [s])
    (Symbol, OrderedDict([('f1', b'ABC'), ('f2', b'ABC')]))

    Value field targeting a agg variable, with value field on the left:

    >>> v1 = Agg(["A", "B", "C"])
    >>> v2 = Value(v1)
    >>> s = Symbol([Field(v1, name='f1'), Field(v2, name='f2')])
    >>> d = s.specialize()
    >>> d
    b'ABCABC'
    >>> Symbol.abstract(d, [s])
    (Symbol, OrderedDict([('f1', b'ABC'), ('f2', b'ABC')]))

    """
