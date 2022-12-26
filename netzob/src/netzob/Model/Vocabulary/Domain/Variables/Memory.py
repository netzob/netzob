# -*- coding: utf-8 -*-

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
#| Standard library imports                                                  |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+
from bitarray import bitarray

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, public_api, NetzobLogger
from netzob.Model.Vocabulary.Domain.Variables.AbstractVariable import AbstractVariable
from netzob.Model.Vocabulary.Types.TypeConverter import TypeConverter
from netzob.Model.Vocabulary.Types.BitArray import BitArray
from netzob.Model.Vocabulary.Types.Raw import Raw


@NetzobLogger
class Memory(object):
    """This class provides a memory, used to store variable values (in bitarray) in a persisting and independent way.

    To compute or verify the constraints and relationships that
    participate to the definition of the fields, the Netzob library
    relies on a memory. This memory stores the values of previously
    captured or emitted fields. More precisely, the Memory contains
    all the field variables that are needed according to the field
    definition during the abstraction and specialization processes.


    .. ifconfig:: scope in ('netzob')

       **Relationships between fields of successive messages**

       The following example shows how to define a relationship
       between a received message and the next message to send. A
       memory is used to store the value of each variable. During the
       first call to :meth:`specialize` on the ``s1`` symbol, the
       value associated to the field ``f3`` is notably stored in
       memory, so that it can be retrieved when calling
       :meth:`specialize` on the ``s2`` symbol. In order to create
       persistence for the ``f3`` field, it is mandatory to use the
       ``scope`` parameter.

       >>> from netzob.all import *
       >>> f1 = Field(domain=String("hello"), name="F1")
       >>> f2 = Field(domain=String(";"), name="F2")
       >>> f3 = Field(domain=Data(String(nbChars=(5,10)), scope=Scope.MESSAGE), name="F3")
       >>> s1 = Symbol(fields=[f1, f2, f3], name="S1")
       >>>
       >>> f4 = Field(domain=String("master"), name="F4")
       >>> f5 = Field(domain=String(">"), name="F5")
       >>> f6 = Field(domain=Value(f3), name="F6")
       >>> s2 = Symbol(fields=[f4, f5, f6], name="S2")
       >>>
       >>> memory = Memory()
       >>> m1 = next(s1.specialize(memory=memory))
       >>> m2 = next(s2.specialize(memory=memory))
       >>>
       >>> m1[6:] == m2[7:]
       True


       **Relationships between a message field and the environment**

       The following example shows how to define a relationship
       between a message to send and an environment variable. The
       symbol is first defined, and then an environment variable is
       created. The first step consists in overloading the definition
       domain of the ``f9`` field to link the environment variable.

       >>> from netzob.all import *
       >>>
       >>> # Symbol definition
       >>> f7 = Field(domain=String("master"), name="F7")
       >>> f8 = Field(domain=String(">"), name="F8")
       >>> f9 = Field(domain=String(), name="F9")
       >>> s3 = Symbol(fields=[f7, f8, f9])
       >>>
       >>> # Environment variables definition
       >>> memory = Memory()
       >>> env1 = Data(String(), name="env1")
       >>> memory.memorize(env1, String("John").value)
       >>>
       >>> # Overloading f9 field definition to link the environment variable
       >>> f9.domain = Value(env1)
       >>>
       >>> # Symbol specialization
       >>> next(s3.specialize(memory=memory))
       b'master>John'

    """

    @public_api
    def __init__(self):
        """Constructor of Memory"""
        self.memory = dict()
        self.__memoryAccessCB = None

    @public_api
    @typeCheck(AbstractVariable)
    def memorize(self, variable, value):
        """Memorizes the provided variable value.

        :param variable: The variable for which we want to memorize a value.
        :param value: The value to memorize.
        :type variable: :class:`Variable <netzob.Model.Vocabulary.Domaine.Variables.AbstractVariable.AbstractVariable>`, required
        :type value: :class:`bitarray <bitarray>` or :class:`bytes`, required

        >>> from netzob.all import *
        >>> variable = Data(String(), name="var1")
        >>> memory = Memory()
        >>> memory.memorize(variable, String("hello").value)
        >>> print(memory)
        Data (String(nbChars=(0,8192))) from field 'None': b'hello'
        >>> memory.memorize(variable, b"test")
        >>> print(memory)
        Data (String(nbChars=(0,8192))) from field 'None': b'test'

        """
        if isinstance(value, bitarray):
            self.memory[variable] = value
        elif isinstance(value, bytes):
            b_value = bitarray()
            b_value.frombytes(value)
            self.memory[variable] = b_value
        else:
            raise TypeError("value parameter of memorize() method should a bitarray or a bytes, not a '{}'".format(type(value)))

    @public_api
    @typeCheck(AbstractVariable)
    def hasValue(self, variable):
        """Returns true if the memory contains a value for the provided variable.

        :param variable: The variable to look for in the memory.
        :type variable: :class:`Variable <netzob.Model.Vocabulary.Domaine.Variables.AbstractVariable.AbstractVariable>`, required
        :return: ``True`` if the memory contains a value for the variable.
        :rtype: :class:`bool`

        >>> from netzob.all import *
        >>> variable = Data(String(), name="var1")
        >>> memory = Memory()
        >>> memory.memorize(variable, String("hello").value)
        >>> memory.hasValue(variable)
        True
        >>> variable2 = Data(String(), name="var2")
        >>> memory.hasValue(variable2)
        False

        """
        return variable in list(self.memory.keys())

    @public_api
    @typeCheck(AbstractVariable)
    def getValue(self, variable):
        """Returns the value memorized for the provided variable.

        :param variable: The variable for which we want to retrieve the value in memory.
        :type variable: :class:`Variable <netzob.Model.Vocabulary.Domaine.Variables.AbstractVariable.AbstractVariable>`, required
        :return: The value in memory.
        :rtype: :class:`bitarray <bitarray>`

        >>> from netzob.all import *
        >>> variable = Data(String(), name="var1")
        >>> memory = Memory()
        >>> memory.memorize(variable, String("hello").value)
        >>> memory.getValue(variable).tobytes()
        b'hello'

        """
        return self.memory[variable]

    @public_api
    @typeCheck(str)
    def getVariable(self, name):
        """Returns the variable memorized which has the provided name.

        :param name: The name for which we want to retrieve the variable in memory.
        :type name: :class:`str`, required
        :return: The variable in memory.
        :rtype: :class:`Variable <netzob.Model.Vocabulary.Domaine.Variables.AbstractVariable.AbstractVariable>`

        >>> from netzob.all import *
        >>> variable = Data(String(), name="var1")
        >>> memory = Memory()
        >>> memory.memorize(variable, String("hello").value)
        >>> print(memory.getVariable("var1"))
        Data (String(nbChars=(0,8192)))

        """

        for variable in self.memory.keys():
            if variable.name == name:
                return variable
        return None

    @public_api
    @typeCheck(AbstractVariable)
    def forget(self, variable):
        """Forgets any memorized value of the provided variable

        :param variable: The variable for which we want to forget the value in memory.
        :type variable: :class:`Variable <netzob.Model.Vocabulary.Domaine.Variables.AbstractVariable.AbstractVariable>`, required

        >>> from netzob.all import *
        >>> variable = Data(String(), name="var1")
        >>> memory = Memory()
        >>> memory.memorize(variable, String("hello").value)
        >>> memory.hasValue(variable)
        True
        >>> memory.forget(variable)
        >>> memory.hasValue(variable)
        False
        """
        if variable in list(self.memory.keys()):
            self.memory.pop(variable, None)

    @public_api
    def copy(self):
        """Copy the current memory in a new memory.

        :return: A new memory containing the same entries as the current memory.
        :rtype: :class:`Memory <netzob.Model.Vocabulary.Domain.Variables.Memory.Memory>`

        >>> from netzob.all import *
        >>> d1 = Data(uint8())
        >>> d2 = Data(String())
        >>> m = Memory()
        >>> m.memorize(d1, uint8(100).value)
        >>> m.memorize(d2, String("hello").value)
        >>> m.getValue(d1)
        bitarray('01100100')
        >>> m2 = m.copy()
        >>> m2.getValue(d1)
        bitarray('01100100')
        >>> m.getValue(d1).bytereverse()
        >>> m.getValue(d1)
        bitarray('00100110')
        >>> m2.getValue(d1)
        bitarray('01100100')

        """
        clonedMemory = Memory()
        for k in list(self.memory.keys()):
            clonedMemory.memory[k] = self.memory[k].copy()
        return clonedMemory

    @public_api
    def clear(self):
        """Clear the current memory.
        """
        self.memory.clear()

    @public_api
    def save(self):
        """Clear the current memory.
        """
        return self.memory.copy()

    @public_api
    def restore(self, memory):
        """Clear the current memory.
        """
        self.memory = memory

    def __str__(self):
        result = []
        for var, value in list(self.memory.items()):
            result.append("{} from field '{}': {}".format(
                var, var.field, TypeConverter.convert(value, BitArray, Raw)))
        return '\n'.join(result)

    def __len__(self):
        return len(self.memory)

    @property
    def memory(self):
        """The content of the memory is stored in this :class:`dict` object.

        :type: :class:`dict`
        """
        return self.__memory

    @memory.setter  # type: ignore
    def memory(self, memory):
        self.__memory = dict()
        for k, v in list(memory.items()):
            self.__memory[k] = v
