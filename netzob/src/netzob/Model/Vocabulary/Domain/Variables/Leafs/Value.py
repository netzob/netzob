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

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+
from bitarray import bitarray

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger
from netzob.Model.Vocabulary.Domain.Variables.Leafs.AbstractRelationVariableLeaf import AbstractRelationVariableLeaf
from netzob.Model.Vocabulary.AbstractField import AbstractField
from netzob.Model.Vocabulary.Types.String import String
from netzob.Model.Vocabulary.Types.AbstractType import AbstractType
from netzob.Model.Vocabulary.Types.TypeConverter import TypeConverter
from netzob.Model.Vocabulary.Types.BitArray import BitArray
from netzob.Model.Vocabulary.Domain.Specializer.SpecializingPath import SpecializingPath
from netzob.Model.Vocabulary.Domain.Parser.ParsingPath import ParsingPath
from netzob.Model.Vocabulary.Domain.GenericPath import GenericPath


@NetzobLogger
class Value(AbstractRelationVariableLeaf):
    r"""The Value class is a variable whose content is the value of another field.

    Netzob can define a field so that its value is equal to the
    value of another field, on which a transformation operation can be
    realized.

    The Value constructor expects some parameters:

    :param target: The targeted field of the relationship.
    :param name: The name of the Value variable. If None, the name
                     will be generated.
    :param operation: An optional transformation operation to be
                      applied on the targeted data.
    :type target: :class:`Field <netzob.Model.Vocabulary.Field>`, required
    :type name: :class:`str`, optional
    :type operation: :class:`Callable <collections.abc.Callable>`, optional


    The following examples show how to define a field with a copy of
    another field value:

    >>> from netzob.all import *
    >>> f0 = Field(String("abcd"))
    >>> f1 = Field(Value(f0))
    >>> s  = Symbol(fields=[f0, f1])
    >>> print(s.specialize())
    b'abcdabcd'

    >>> msg = RawMessage("netzob;netzob!")
    >>> f1 = Field(String(nbChars=(2, 8)), name="f1")
    >>> f2 = Field(String(";"), name="f2")
    >>> f3 = Field(Value(f1), name="f3")
    >>> f4 = Field(String("!"), name="f4")
    >>> s = Symbol(fields=[f1, f2, f3, f4])
    >>> mp = MessageParser()
    >>> print(mp.parseMessage(msg, s))  # doctest: +NORMALIZE_WHITESPACE
    [bitarray('011011100110010101110100011110100110111101100010'),
     bitarray('00111011'),
     bitarray('011011100110010101110100011110100110111101100010'),
     bitarray('00100001')]

    The following example shows another way to define a field with a
    copy of another field value:

    >>> from netzob.all import *
    >>> msg = RawMessage("netzob;netzob!")
    >>> f3 = Field(String(nbChars=6), name="f3")
    >>> f1 = Field(Value(f3), name="f1")
    >>> f2 = Field(String(";"), name="f2")
    >>> f4 = Field(String("!"), name="f4")
    >>> s = Symbol(fields=[f1, f2, f3, f4])
    >>> mp = MessageParser()
    >>> print(mp.parseMessage(msg, s))  # doctest: +NORMALIZE_WHITESPACE
    [bitarray('011011100110010101110100011110100110111101100010'),
     bitarray('00111011'),
     bitarray('011011100110010101110100011110100110111101100010'),
     bitarray('00100001')]


    **Value field with a variable as a target**

    The following example shows the specialization process of a Value
    field whose target is a variable:

    >>> d = Data(String("netzob"))
    >>> f1 = Field(domain=d, name="f1")
    >>> f2 = Field(String(";"), name="f2")
    >>> f3 = Field(Value(d), name="f3")
    >>> f4 = Field(String("!"), name="f4")
    >>> s = Symbol(fields=[f1, f2, f3, f4])
    >>> print(s.specialize())
    b'netzob;netzob!'


    **Specialization of Value objects**

    The following examples show the specialization process of Value
    objects:

    >>> f1 = Field(String("netzob"), name="f1")
    >>> f2 = Field(String(";"), name="f2")
    >>> f3 = Field(Value(f1), name="f3")
    >>> f4 = Field(String("!"), name="f4")
    >>> s = Symbol(fields=[f1, f2, f3, f4])
    >>> print(s.specialize())
    b'netzob;netzob!'

    >>> f3 = Field(String("netzob"), name="f3")
    >>> f2 = Field(String(";"), name="f2")
    >>> f1 = Field(Value(f3), name="f1")
    >>> f4 = Field(String("!"), name="f4")
    >>> s = Symbol(fields=[f1, f2, f3, f4])
    >>> print(s.specialize())
    b'netzob;netzob!'


    **Transformation operation on targeted field value**

    A value relationship also accepts custom operations, as shown on
    the following example with a lambda function:

    >>> f0 = Field(1, name="f0")
    >>> f1 = Field(String(":"), name="f1")
    >>> f2 = Field(Value(f0, operation = lambda x: TypeConverter.convert(
    ... TypeConverter.convert(x, BitArray, Integer) + 1, Integer, BitArray)), name="f2")
    >>> s = Symbol([f0, f1, f2])
    >>> print(s.specialize())
    b'\x01:\x02'
    >>> m1 = RawMessage(s.specialize())
    >>> s.messages = [m1]
    >>> print(s.str_data())
    f0     | f1  | f2    
    ------ | --- | ------
    '\x01' | ':' | '\x02'
    ------ | --- | ------


    A named callback function can also be used to specify a more
    complex relationship. The following example shows a relationship
    where the computed value corresponds to the reversed bits of the
    targeted field. The ``data`` parameter of the ``cbk`` function
    contains a bitarray object of the targeted fields. The ``cbk``
    function returns a bitarray object.

    >>> def cbk(data):
    ...    ret = data.copy()
    ...    ret.reverse()
    ...    return ret
    >>> f0 = Field(Raw(b'\x01'))
    >>> f1 = Field(Value(f0, operation = cbk))
    >>> s = Symbol([f0, f1])
    >>> print(s.specialize())
    b'\x01\x80'


    """

    def __init__(self, target, name=None, operation=None):
        super(Value, self).__init__(
            self.__class__.__name__, targets=[target], name=name)
        self.operation = operation

    @typeCheck(GenericPath)
    def valueCMP(self, parsingPath, acceptCallBack=True, carnivorous=False):
        self._logger.debug("ValueCMP")
        results = []
        if parsingPath is None:
            raise Exception("ParsingPath cannot be None")

        content = parsingPath.getDataAssignedToVariable(self)
        if content is None:
            raise Exception("No data assigned.")

        # we verify we have access to the expected value
        expectedValue = self.computeExpectedValue(parsingPath)

        self._logger.debug(
            "Expected value to parse: {0}".format(expectedValue))

        if expectedValue is None:

            # lets compute what could be the possible value
            variable = self.targets[0]
            (minSizeDep, maxSizeDep) = variable.dataType.size
            if minSizeDep > len(content):
                self._logger.debug(
                    "Size of the content to parse is smallest than the min expected size of the dependency field"
                )
                return results

            for size in range(
                    min(maxSizeDep, len(content)), minSizeDep - 1, -1):
                # we create a new parsing path and returns it
                newParsingPath = parsingPath.duplicate()
                newParsingPath.addResult(self, content[:size].copy())
                self._addCallBacksOnUndefinedVariables(newParsingPath)
                results.append(newParsingPath)
        else:
            if content[:len(expectedValue)] == expectedValue:
                self._logger.debug(
                    "add result: {0}".format(expectedValue.copy()))
                parsingPath.addResult(self, expectedValue.copy())
                results.append(parsingPath)

        return results

    @typeCheck(ParsingPath)
    def domainCMP(self, parsingPath, acceptCallBack=True, carnivorous=False):
        """This method participates in the abstraction process.

        It creates a VariableSpecializerResult in the provided path if
        the remainingData (or some if it) follows the type definition"""

        return self.valueCMP(parsingPath, acceptCallBack)

    def computeExpectedValue(self, parsingPath):
        self._logger.debug("Compute expected value for Value field")

        variable = self.targets[0]
        if variable is None:
            raise Exception("No dependency field specified.")

        if not parsingPath.isDataAvailableForVariable(variable):
            return None
        else:
            return self._applyOperation(parsingPath.getDataAssignedToVariable(variable))

    def _applyOperation(self, data):
        """This method can be used to apply the specified operation function to the data parameter.
        If no operation function is known, the data parameter is returned"""

        if self.__operation is None:
            return data

        return self.__operation(data)

    def __str__(self):
        """The str method."""
        return "Value({0})".format(str(self.targets[0].name))

    @property
    def factor(self):
        """Defines the multiplication factor to apply on the targeted length (in bits)"""
        return self.__factor

    @factor.setter
    @typeCheck(float)
    def factor(self, factor):
        if factor is None:
            raise TypeError("Factor cannot be None, use 1.0 for the identity.")
        self.__factor = factor

    @property
    def offset(self):
        """Defines the offset to apply on the computed length
        computed size = (factor*size(targetField)+offset)"""
        return self.__offset

    @offset.setter
    @typeCheck(int)
    def offset(self, offset):
        if offset is None:
            raise TypeError(
                "Offset cannot be None, use 0 if no offset should be applied.")
        self.__offset = offset

    @property
    def operation(self):
        """Defines the operation to be performed on the found value. This operation takes the form
        of a python function that accepts a single parameter of BitArray type and returns a BitArray."""
        return self.__operation

    @operation.setter
    def operation(self, operation):
        if operation is not None and not callable(operation):
            raise TypeError("Operation must be a function")
        self.__operation = operation
