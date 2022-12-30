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

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger, public_api
from netzob.Model.Vocabulary.Domain.Variables.Leafs.AbstractRelationVariableLeaf import AbstractRelationVariableLeaf, RelationDependencyException, InaccessibleVariableException
from netzob.Model.Vocabulary.Domain.Parser.ParsingPath import ParsingPath
from netzob.Model.Vocabulary.Domain.GenericPath import GenericPath
from netzob.Model.Vocabulary.Domain.Variables.Nodes.Repeat import Repeat
from netzob.Model.Vocabulary.AbstractField import AbstractField
from netzob.Model.Vocabulary.Field import Field
from netzob.Model.Vocabulary.Types.BitArray import BitArray


@NetzobLogger
class Value(AbstractRelationVariableLeaf):
    r"""The Value class is a variable whose content is the value of another field.

    It is possible to define a field so that its value is equal to the
    value of another field, on which an operation can be
    performed.

    The Value constructor expects some parameters:

    :param target: The targeted object of the relationship. If a :class:`~netzob.Model.Vocabulary.Field.Field` is provided, it will be normalized by the associated :class:`Variable <netzob.Model.Vocabulary.Domain.Variables.AbstractVariable.AbstractVariable>`.
    :param name: The name of the variable. If None, the name
                     will be generated.
    :param operation: An optional transformation operation to be
                      applied to the targeted field value, through a callback.
                      The default is None.
    :type target: :class:`Field <netzob.Model.Vocabulary.Field>` or :class:`Variable <netzob.Model.Vocabulary.Domain.Variables.AbstractVariable.AbstractVariable>`, required
    :type name: :class:`str`, optional
    :type operation: :class:`Callable <collections.abc.Callable>`, optional


    The Value class provides the following public variables:

    :var target: The variable that is required before computing
                 the value of this relation.
    :var operation: Defines the operation to be performed on the found value.
                    The prototype of this callback is detailed below.
    :vartype target: :class:`Variable <netzob.Model.Vocabulary.Domain.Variables.AbstractVariable.AbstractVariable>`
    :vartype operation: :class:`Callable <collections.abc.Callable>`


    **Callback prototype**

    The callback function that can be used to specify a complex
    relationship in the ``operation`` parameter has the following
    prototype:

    .. function:: cbk_operation(data, path, variable)
       :noindex:

       :param data: contains the current data of the targeted field.
       :type data: ~bitarray.bitarray
       :param path: data structure that allows access to the values of the
                    :class:`Variable <netzob.Model.Vocabulary.Domain.Variables.AbstractVariable.AbstractVariable>`
                    element.
       :type path: object
       :param variable: the current Value variable.
       :type variable: ~netzob.Model.Vocabulary.Domain.Variables.Leafs.Value.Value

       :return: The callback function should return a :class:`bitarray
                <bitarray>` representing the computed data during
                specialization or abstraction. In the latter case, if
                the callback function does not succeed to parse the
                data, it should return the :const:`None` value. The length of the computed data may differ from the length of the targeted data.
       :rtype: :class:`bitarray <bitarray.bitarray>`

    Access to :class:`Variable <netzob.Model.Vocabulary.Domain.Variables.AbstractVariable.AbstractVariable>`
    values is done through the ``path``, thanks to its methods
    :meth:`~netzob.Model.Vocabulary.Domain.GenericPath.hasData` and
    :meth:`~netzob.Model.Vocabulary.Domain.GenericPath.getData`:

    * ``path.hasData(variable)`` will return a :class:`bool` telling if a data has
      been specialized or parsed for the Value variable
      :class:`Variable <netzob.Model.Vocabulary.Domain.Variables.AbstractVariable.AbstractVariable>`.
    * ``path.getData(variable)`` will return a :class:`bitarray` that corresponds
      to the data specialized or parsed for the Value variable
      :class:`Variable <netzob.Model.Vocabulary.Domain.Variables.AbstractVariable.AbstractVariable>`.

    The callback function is expected to implement relationship
    operations based on the provided data.


    **Value usage**

    The following example shows how to define a field with a copy of
    another field value, in specialization mode:

    >>> from netzob.all import *
    >>> f0 = Field(String("abcd"))
    >>> f1 = Field(Value(f0))
    >>> fheader = Field([f0, f1])
    >>> next(fheader.specialize())
    b'abcdabcd'


    .. ifconfig:: scope in ('netzob')

       The following example shows how to define a field with a copy of
       another field value, in abstraction mode:

       >>> from netzob.all import *
       >>> data = "john;john!"
       >>> f1 = Field(String(nbChars=(2, 8)), name="f1")
       >>> f2 = Field(String(";"), name="f2")
       >>> f3 = Field(Value(f1), name="f3")
       >>> f4 = Field(String("!"), name="f4")
       >>> s = Symbol(fields=[f1, f2, f3, f4])
       >>> s.abstract(data)  # doctest: +NORMALIZE_WHITESPACE
       OrderedDict([('f1', b'john'), ('f2', b';'), ('f3', b'john'), ('f4', b'!')])


    **Value field with a variable as a target**

    The following example shows the specialization process of a Value
    field whose target is a variable:

    >>> from netzob.all import *
    >>> d = Data(String("john"))
    >>> f1 = Field(domain=d, name="f1")
    >>> f2 = Field(String(";"), name="f2")
    >>> f3 = Field(Value(d), name="f3")
    >>> f4 = Field(String("!"), name="f4")
    >>> f = Field([f1, f2, f3, f4])
    >>> next(f.specialize())
    b'john;john!'


    **Specialization of Value objects**

    The following examples show the specialization process of Value
    objects. The first example illustrates a case where the Value
    variable is placed before the targeted variable.

    >>> from netzob.all import *
    >>> f1 = Field(String("john"), name="f1")
    >>> f2 = Field(String(";"), name="f2")
    >>> f3 = Field(Value(f1), name="f3")
    >>> f4 = Field(String("!"), name="f4")
    >>> f = Field([f1, f2, f3, f4])
    >>> next(f.specialize())
    b'john;john!'

    The second example illustrates a case where the Value variable is
    placed after the targeted variable.

    >>> from netzob.all import *
    >>> f3 = Field(String("john"), name="f3")
    >>> f2 = Field(String(";"), name="f2")
    >>> f1 = Field(Value(f3), name="f1")
    >>> f4 = Field(String("!"), name="f4")
    >>> f = Field([f1, f2, f3, f4])
    >>> next(f.specialize())
    b'john;john!'


    **Transformation operation on targeted field value**

    A named callback function can be used to specify a more complex
    relationship. The following example shows a relationship where the
    computed value corresponds to the reversed bits of the targeted
    field value. The ``data`` parameter of the ``cbk`` function contains a
    bitarray object of the targeted field value. The ``cbk`` function
    returns a bitarray object.

    >>> from netzob.all import *
    >>> def cbk(data, path, value):
    ...    ret = data.copy()
    ...    ret.reverse()
    ...    if ret == bitarray('10000000'):
    ...        return ret
    ...    else:
    ...        return None
    >>> f0 = Field(Raw(b'\x01'), name='f0')
    >>> f1 = Field(Value(f0, operation = cbk), name='f1')
    >>> f = Field([f0, f1], name='f')
    >>> data = next(f.specialize())
    >>> data
    b'\x01\x80'

    Callback functions are also triggered during data abstraction. In
    the next portion of the example, the previously specialized data
    is abstracted according to the field definition.

    >>> f.abstract(data)
    OrderedDict([('f0', b'\x01'), ('f1', b'\x80')])

    If the targeted field (``f0``) does not contain the expected data,
    the callback function should return :const:`None`, indicating that the
    relationship does not apply. In this case, the abstraction process
    will return an exception.

    >>> data = b'\x02\x80'
    >>> f.abstract(data)
    Traceback (most recent call last):
    ...
    netzob.Model.Vocabulary.AbstractField.AbstractionException: With the symbol/field 'f', cannot abstract the data: 'b'\x02\x80''. Error: 'No parsing path returned while parsing 'b'\x02\x80'''

    """

    @public_api
    def __init__(self, target, name=None, operation=None):

        if target is not None:
            targets = [target]
        else:
            targets = []

        super(Value, self).__init__(
            self.__class__.__name__, targets=targets, name=name)
        self.operation = operation

    @public_api
    def copy(self, map_objects=None):
        """Copy the current object as well as all its dependencies.

        :return: A new object of the same type.
        :rtype: :class:`Value <netzob.Model.Vocabulary.Domain.Variables.Leafs.Value.Value>`

        """
        if map_objects is None:
            map_objects = {}
        if self in map_objects:
            return map_objects[self]

        new_value = Value(self.targets[0], name=self.name, operation=self.operation)
        map_objects[self] = new_value

        return new_value

    @staticmethod
    def check_target_consistency(tmp_target):
        """Function used to check targets consistency (i.e. it should not
        contain a Repeat element, as it makes parsing ambiguous)
        """
        if isinstance(tmp_target, Field):
            tmp_target = tmp_target.domain
        if isinstance(tmp_target, Repeat):
            raise TypeError("Value target contains a Repeat variable, which is not supported")
        if tmp_target.isnode():
            for tmp_target_child in tmp_target.children:
                Value.check_target_consistency(tmp_target_child)
        else:
            current_parent = tmp_target.parent
            while current_parent is not None:
                if isinstance(current_parent, Repeat):
                    raise TypeError("Value target is a child of a Repeat variable, which is not supported")
                if isinstance(current_parent, AbstractField):
                    break
                current_parent = current_parent.parent

    @typeCheck(GenericPath)
    def valueCMP(self, parsingPath, acceptCallBack=True, carnivorous=False, triggered=False):
        self._logger.debug("ValueCMP")
        results = []
        if parsingPath is None:
            raise Exception("ParsingPath cannot be None")

        content = parsingPath.getData(self)
        if content is None:
            raise Exception("No data assigned.")

        # we verify we have access to the expected value
        try:
            expectedValue = self.computeExpectedValue(parsingPath)
        except RelationDependencyException as e:
            expectedValue = None

        if expectedValue is None:
            if len(self.targets) > 0:

                # Check targets consistency
                for target in self.targets:
                    Value.check_target_consistency(target)

                self._logger.debug("Let's compute what could be the possible value based on the target datatype")

                target_type_aligned_octets = False  # Tells if we are sure that the target type is aligned on octets
                if self.targets[0].isnode():
                    minSizeDep = 0
                    maxSizeDep = len(content)
                else:
                    (minSizeDep, maxSizeDep) = self.targets[0].dataType.size

                    if minSizeDep > len(content):
                        self._logger.debug("Size of the content to parse is smaller than the min expected size of the dependency field")
                        return results

                    if not isinstance(type(self.targets[0].dataType), BitArray):
                        target_type_aligned_octets = True

                if target_type_aligned_octets is True:
                    step = -8
                else:
                    step = -1  # In order to support a target that manipulates bitarays

                for size in range(min(maxSizeDep, len(content)), minSizeDep - 1, step):
                    # we create a new parsing path and returns it
                    newParsingPath = parsingPath.copy()
                    newParsingPath.addResult(self, content[:size].copy())
                    self._addCallBacksOnUndefinedVariables(newParsingPath)
                    results.append(newParsingPath)

        # If the expectedValue contains data
        else:
            self._logger.debug("Expected value to parse: {0}".format(expectedValue.tobytes()))
            if content[:len(expectedValue)] == expectedValue:
                self._logger.debug("add result: {0}".format(expectedValue.copy().tobytes()))
                parsingPath.addResult(self, content[:len(expectedValue)].copy())
                results.append(parsingPath)

        return results

    @typeCheck(ParsingPath)
    def domainCMP(self, parsingPath, acceptCallBack=True, carnivorous=False, triggered=False):
        """This method participates in the abstraction process.

        It creates a result in the provided path if the remainingData
        (or some if it) follows the type definition

        """

        return self.valueCMP(parsingPath, acceptCallBack)

    def computeExpectedValue(self, parsingPath, preset=None):
        self._logger.debug("Compute expected value for Value field '{}'".format(self.field))

        # Check target variable consistency
        target_data = None
        if len(self.targets) > 0:
            if parsingPath.isVariableInaccessible(self.targets[0]):
                error_message = "The following variable is inaccessible: '{}' for field '{}'. This may be because a parent field or variable is preset.".format(self.targets[0], self.targets[0].field)
                self._logger.debug(error_message)
                raise InaccessibleVariableException(error_message)

            # Check is target is part of the current symbol or not
            if self.is_same_symbol(self.targets[0]):
                if parsingPath.hasData(self.targets[0]):
                    target_data = parsingPath.getData(self.targets[0])
            else:
                if parsingPath.hasDataInMemory(self.targets[0]):
                    target_data = parsingPath.getDataInMemory(self.targets[0])
        else:
            raise Exception("No dependency field specified.")

        if target_data is None:
            # Check targets consistency
            for target in self.targets:
                Value.check_target_consistency(target)

            current_target = self.targets[0]
            error_message = "The following variable has no value: '{}' for field '{}'".format(current_target, current_target.field)
            self._logger.debug(error_message)
            raise RelationDependencyException(error_message, current_target)

        # Check if a callback operation is defined
        if self.__operation is None:
            self._logger.debug("Computed value for {}: '{}'".format(self, target_data.tobytes()))
            return target_data
        else:
            self._logger.debug("Use callback to compute expected value")
            target_data = self.__operation(target_data, parsingPath, self)
            self._logger.debug("Computed value for {}: '{}'".format(self, target_data.tobytes()))
            return target_data

    def __str__(self):
        """The str method."""
        if len(self.targets) > 0:
            return "Value({0})".format(str(self.targets[0].name))
        else:
            return "Value()"

    @property
    def operation(self):
        """
        Property (getter.setter  # type: ignore).
        Defines the operation to be performed on the found value.
        This operation takes the form of a python function that accepts
        a single parameter of BitArray type and returns a BitArray.

        :type: :class:`Callable <collections.abc.Callable>`
        """
        return self.__operation

    @operation.setter  # type: ignore
    def operation(self, operation):
        if operation is not None and not callable(operation):
            raise TypeError("Operation must be a function")
        self.__operation = operation


def _test_value():
    """

    The following example shows how to define a field with a copy of
    another field value:

    >>> from netzob.all import *
    >>> data = "john;john!"
    >>> f3 = Field(String(nbChars=4), name="f3")
    >>> f1 = Field(Value(f3), name="f1")
    >>> f2 = Field(String(";"), name="f2")
    >>> f4 = Field(String("!"), name="f4")
    >>> s = Symbol(fields=[f1, f2, f3, f4])
    >>> s.abstract(data)  # doctest: +NORMALIZE_WHITESPACE
    OrderedDict([('f1', b'john'), ('f2', b';'), ('f3', b'john'), ('f4', b'!')])

    """
