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
#|             ANSSI,   https://www.ssi.gouv.fr                              |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| File contributors :                                                       |
#|       - Georges Bossert <georges.bossert (a) supelec.fr>                  |
#|       - Frédéric Guihéry <frederic.guihery (a) amossys.fr>                |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Standard library imports                                                  |
#+---------------------------------------------------------------------------+
from typing import Iterator  # noqa: F401

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, public_api
from netzob.Model.Vocabulary.AbstractField import AbstractField, GenerationException
from netzob.Model.Vocabulary.Types.Raw import Raw
from netzob.Model.Vocabulary.Domain.Variables.Leafs.Data import Data
from netzob.Model.Vocabulary.Domain.DomainFactory import DomainFactory


class InvalidDomainException(Exception):
    pass


class Field(AbstractField):
    r"""The Field class is used in the definition of a Symbol structure.

    A Field describes a chunk of a Symbol and is specified by a
    definition domain, representing the set of values the field
    accepts.

    The Field constructor expects some parameters:

    :param domain: The definition domain of the field (i.e. the set of values
                   the field accepts). If not specified, the default definition
                   domain will be ``Raw()``, meaning it accepts any values.
                   When this parameter is a list of fields, the constructor set
                   ``self.fields=domain`` and ``self.domain=None``. Otherwise, it sets the :attr:`domain` attribute. During this later operation, a normalization is done in order to convert the provided domain into a :class:`Variable <netzob.Model.Vocabulary.Domain.Variables.AbstractVariable.AbstractVariable>`.
    :param name: The name of the field. If not specified, the
                 default name will be "Field".
    :param isPseudoField: A flag indicating if the field is a
                          pseudo field, meaning it is used
                          internally to help the computation
                          of the value of another field, but does
                          not directly produce data. The default value is False.
    :type domain: :class:`Variable <netzob.Model.Vocabulary.Domain.Variables.AbstractVariable.AbstractVariable>`,
                  :class:`~netzob.Model.Vocabulary.Types.AbstractType.AbstractType`,
                  :class:`bytes`, :class:`str`, :class:`int`, :class:`bitarray <bitarray.bitarray>`,
                  or :class:`list` of :class:`~netzob.Model.Vocabulary.Field.Field`, optional
    :type name: :class:`str`, optional
    :type isPseudoField: :class:`bool`, optional


    The Field class provides the following public variables:

    :var domain: The definition domain of the field (i.e. the
                 set of values the field accepts). Only applicable when the current field has a definition domain. Setting this attribute will clean the list of sub-fields (i.e. the :attr:`fields` attribute will be set to ``[]``).
                 ``None`` when ``self.fields`` is set.
    :var name: The name of the field.
    :var description: The description of the field.
    :var fields: The sorted list of sub-fields. Only applicable when the current field has sub-fields. Setting this attribute will clean the definition domain of the current field.
    :var parent: The parent element.
    :var isPseudoField: A flag indicating if the field is a
                        pseudo field, meaning it is used
                        internally to help the computation
                        of the value of another field, but does
                        not directly produce data.
    :vartype domain: :class:`Variable <netzob.Model.Vocabulary.Domain.Variables.AbstractVariable.AbstractVariable>`
    :vartype name: :class:`str`
    :vartype description: :class:`str`
    :vartype fields: list[~netzob.Model.Vocabulary.Field.Field]
    :vartype parent: ~typing.Union[~netzob.Model.Vocabulary.Field.Field,
                     ~netzob.Model.Vocabulary.Symbol.Symbol]
    :vartype isPseudoField: :class:`bool`


    **Fields hierarchy**

    A field can be composed of sub-fields. This is useful for example
    to separate a header, composed of multiple fields, from its
    payload. The parent field can be seen as a facility to access
    a group of fields.

    In the following example, the ``fheader`` field is a parent field
    for a group of sub-fields. The parent field does not contain any
    concrete data, contrary to its sub-fields.

    >>> from netzob.all import *
    >>> fh0 = Field(name='fh0')
    >>> fh1 = Field(name='fh1')
    >>> fheader = Field([fh0, fh1], name='fheader')

    More generally, a field is part of a tree whose root is a symbol
    and whose all other nodes are fields. Hence, a field
    always has a parent which can be another field or a symbol if it
    is the root.


    **Field definition domain**

    The value that can take a field is defined by its definition
    domain. The definition domain of a field can take multiple forms,
    in order to easily express basic types (such as Integer or String)
    or to model complex data structures (such as alternatives,
    repetitions or sequences).

    The following examples present the different forms that make it possible to
    express the same field content (i.e. an Integer with a constant
    value of 10):

    >>> from netzob.all import *
    >>> f = Field(Data(Integer(10)))
    >>> f = Field(Integer(10))
    >>> f = Field(10)

    If these fields are equivalent, this is because the first
    parameter of the Field constructor is :attr:`domain`, thus its
    name can be omitted. Besides, the domain parameter will be parsed
    by a factory, which accepts either the canonical form of a
    definition domain (such as `domain=Data(Integer(10))`) or a
    shortened form (such as `domain=Integer(10)`, or even
    `domain=10`). In the later case, this means that it is possible to
    use a Python native type that will be automatically converted to its equivalent in
    Netzob type. Supported Python native types are :class:`bytes` (converted in :class:`Raw <netzob.Model.Vocabulary.Types.Raw.Raw>`), :class:`str` (converted in :class:`String <netzob.Model.Vocabulary.Types.String.String>`), :class:`int` (converted in :class:`Integer <netzob.Model.Vocabulary.Types.Integer.Integer>`) and :class:`bitarray <bitarray.bitarray>` (converted in :class:`BitArray <netzob.Model.Vocabulary.Types.BitArray.BitArray>`).

    .. ifconfig:: scope in ('netzob')

       A domain may be composed of basic types, or complex data
       structures. The following examples show how to express data
       structures composed of 1) an alternative between the integers `10`
       and `20`, 2) a repetition of the string `a`, and 3) an aggregate
       (or concatenation) of the strings `aa` and `bb`:

       >>> from netzob.all import *
       >>> f = Field(Alt([10, 20]))
       >>> f = Field(Repeat("a", nbRepeat=(4,8)))
       >>> f = Field(Agg(["aa", "bb"]))


    **Relationships between fields**

    A field can have its value related to the content of another
    field. Such relationships may be specified through specific domain
    objects, such as
    :class:`~netzob.Model.Vocabulary.Domain.Variables.Leafs.Size.Size` or
    :class:`~netzob.Model.Vocabulary.Domain.Variables.Leafs.Value.Value` classes.

    The following example describes a size relationship with a String
    field:

    >>> from netzob.all import *
    >>> f0 = Field(String("test"))
    >>> f1 = Field(Size(f0))
    >>> fheader = Field([f0, f1])
    
    **Pseudo fields**

    Sometimes, a specific field can be needed to express a complex
    data structure that depends on external data. This is the purpose
    of the `isPseudoField` flag. This flag indicates that the current
    field is only used for the computation of the value of another
    field, but does not produce real content during
    specialization. The following example shows a pseudo field that
    contains external data, and a real field whose content is the
    size of the external data:

    >>> from netzob.all import *
    >>> f_pseudo = Field(domain="An external data", isPseudoField=True)
    >>> f_real = Field(domain=Size(f_pseudo))
    >>> fheader = Field([f_pseudo, f_real])

    A real example of a pseudo field is found in the UDP checksum,
    which relies on a pseudo IP header for its computation.


    .. ifconfig:: scope in ('netzob')

       **Encoding functions applied to fields**

       Encoding functions represent functions which apply to modify the
       encoding of a data. The following example shows the use of the
       :class:`Base64EncodingFunction <netzob.Model.Vocabulary.Functions.EncodingFunctions.Base64EncodingFunction.Base64EncodingFunction>`
       function to automatically decode base64 strings in the `f1` field:

       >>> from netzob.all import *
       >>> m1 = "hello YWxs"
       >>> m2 = "hello bXkgbG9yZA=="
       >>> m3 = "hello d29ybGQ="
       >>> messages = [RawMessage(m1), RawMessage(m2), RawMessage(m3)]
       >>> f0 = Field(name="f0", domain=String("hello "))
       >>> f1 = Field(name="f1", domain=String(nbChars=(0, 20)))
       >>> s = Symbol(fields=[f0, f1], messages=messages)
       >>> print(s.str_data())
       f0       | f1            
       -------- | --------------
       'hello ' | 'YWxs'        
       'hello ' | 'bXkgbG9yZA=='
       'hello ' | 'd29ybGQ='    
       -------- | --------------
       >>> f1.addEncodingFunction(Base64EncodingFunction(encode_data = False))
       >>> print(s.str_data())
       f0       | f1       
       -------- | ---------
       'hello ' | 'all'    
       'hello ' | 'my lord'
       'hello ' | 'world'  
       -------- | ---------


    .. ifconfig:: scope in ('netzob')

       **Field examples**

       Here are examples of fields:

       * a field containing the integer value 100

         >>> f = Field(100)

       * a field containing a specific binary: '1000' = 8 in decimal

         >>> f = Field(0b1000)

       * a field containing a raw value of 8 bits (1 byte)

         >>> f = Field(Raw(nbBytes=8))

       * a field with a specific raw value

         >>> f = Field(Raw(b'\x00\x01\x02\x03'))

       * a field representing a random IPv4:

         >>> f = Field(IPv4())

       * a field representing a random String of 6 characters length:

         >>> f = Field(String(nbChars=6))

       * a field representing a random String with length between 5 and 20 characters:

         >>> payloadField = Field(String(nbChars=(5, 20)))

       * a field whose value is the size of the payloadField:

         >>> f = Field([Size(payloadField)])

       * a field representing an alternative between two different strings, either "john" or "kurt":

         >>> f = Field(["john", "kurt"])

       * a field representing a decimal (10) or a String of 16 chars:

         >>> f = Field([10, String(nbChars=(16))])

    """

    @public_api
    def __init__(self, domain=None, name="Field", isPseudoField=False):
        super(Field, self).__init__(name)

        # Handle each possibility for the domain parameter
        if domain is None:  # Check if domain is not defined
            self.domain = Raw()
        elif isinstance(domain, list):  # Check if domain is a list of fields

            # Check if each domain element is of type Field
            is_domain_list_of_fields = True
            for elt in domain:
                if not isinstance(elt, Field):
                    is_domain_list_of_fields = False
                    break

            if is_domain_list_of_fields:
                self.fields = domain
                self.domain = None
            else:
                self.domain = domain  # Domain will be normalized is such case
        else:
            self.domain = domain  # Domain will be normalized is such case

        self.isPseudoField = isPseudoField

    @public_api
    def copy(self, map_objects=None):
        """Copy the current object as well as all its dependencies.

        :return: A new object of the same type.
        :rtype: :class:`Field <netzob.Model.Vocabulary.Field.Field>`

        """

        if map_objects is None:
            map_objects = {}
        if self in map_objects:
            return map_objects[self]

        new_field = Field(domain=None, name=self.name, isPseudoField=self.isPseudoField)
        map_objects[self] = new_field

        if len(self.fields) > 0:
            new_domain = []
            for f in self.fields:
                if f in map_objects.keys():
                    new_domain.append(map_objects[f])
                else:
                    new_sub_field = f.copy(map_objects)
                    new_domain.append(new_sub_field)
            new_field.fields = new_domain
            new_field.domain = None
        else:
            if self.domain in map_objects.keys():
                new_domain = map_objects[self.domain]
            else:
                new_domain = self.domain.copy(map_objects)
            new_field.domain = new_domain

        return new_field

    @public_api
    def str_structure(self, preset=None, deepness=0):
        """Returns a string which denotes the current field definition
        using a tree display.

        :return: The current field represented as a string.
        :rtype: :class:`str`

        :param preset: The configuration used to parameterize values in fields and variables.
        :type preset: :class:`Preset <netzob.Model.Vocabulary.Preset.Preset>`, optional

        >>> from netzob.all import *
        >>> f1 = Field(String(), name="field1")
        >>> f2 = Field(Integer(interval=(10, 100)), name="field2")
        >>> f3 = Field(Raw(nbBytes=14), name="field3")
        >>> field = Field([f1, f2, f3], name="Main field")
        >>> print(field.str_structure())
        Main field
        |--  field1
             |--   Data (String(nbChars=(0,8192)))
        |--  field2
             |--   Data (Integer(10,100))
        |--  field3
             |--   Data (Raw(nbBytes=14))

        """
        tab = ["|--  " for x in range(deepness)]
        tab.append(str(self.name))
        lines = [''.join(tab)]
        if len(self.fields) == 0:
            lines.append(self.domain.str_structure(preset, deepness + 1))
        for f in self.fields:
            lines.append(f.str_structure(preset, deepness + 1))
        return '\n'.join(lines)

    def getVariables(self):
        r"""Returns the list of all underlying variables.

        :return: the list of variables
        :rtype: :class:`list` of :class:`Variable <netzob.Model.Vocabulary.Domain.Variables.AbstractVariable.AbstractVariable`.

        >>> from netzob.all import *
        >>> v1 = Data(uint8(), name='v1')
        >>> v2 = Data(uint8(), name='v2')
        >>> v_agg = Agg([v1, v2], name='v_agg')
        >>> f1 = Field(v_agg)
        >>> variables = f1.getVariables()
        >>> len(variables)
        3

        """
        return self.domain.getVariables()

    @public_api
    def specialize(self, preset=None, memory=None) -> Iterator[bytes]:
        r"""The :meth:`specialize()` method is intended to produce concrete
        :class:`bytes` data based on the field model. This method
        returns a Python generator that in turn provides data
        :class:`bytes` object at each call to ``next(generator)``.

        :param preset: The configuration used to parameterize values in fields and variables.
        :param memory: A memory used to store variable values during
                       specialization and abstraction of successive
                       fields, especially to handle inter-symbol
                       relationships. If None, a temporary memory is
                       created by default and used internally during the scope of the
                       specialization process.
        :type preset: :class:`Preset <netzob.Model.Vocabulary.Preset.Preset>`, optional
        :type memory: :class:`Memory <netzob.Model.Vocabulary.Domain.Variables.Memory.Memory>`, optional
        :return: A generator that provides data :class:`bytes` at each call to ``next(generator)``.
        :rtype: :class:`Generator[bytes]`
        :raises: :class:`GenerationException <netzob.Model.Vocabulary.AbstractField.GenerationException>` if an error occurs while specializing the field.

        The following example shows the :meth:`specialize()` method used for a
        field which contains a string with a constant value.

        >>> from netzob.all import *
        >>> f = Field(String("hello"))
        >>> next(f.specialize())
        b'hello'

        The following example shows the :meth:`specialize()` method used for a
        field which contains a string with a variable value.

        >>> from netzob.all import *
        >>> f = Field(String(nbChars=4))
        >>> len(next(f.specialize()))
        4

        """
        self._logger.debug("Specializes field {0}".format(self.name))

        # Sanity check
        if self.__domain is None and len(self.fields) == 0:
            raise InvalidDomainException("No domain or sub-fields are defined.")

        # We normalize the sub_fields variables
        from netzob.Model.Vocabulary.Domain.Variables.Leafs.AbstractRelationVariableLeaf import AbstractRelationVariableLeaf
        if len(self.fields) > 0:
            for field in self.getLeafFields(includePseudoFields=True):
                if field.domain is not None and isinstance(field.domain, AbstractRelationVariableLeaf):
                    self._logger.debug("Normalize field targets for field '{}'".format(field.name))
                    field.domain.normalize_targets()

        from netzob.Model.Vocabulary.Domain.Specializer.FieldSpecializer import FieldSpecializer
        fs = FieldSpecializer(self, preset=preset, memory=memory)

        specializing_paths = fs.specialize()
        return self._inner_specialize(specializing_paths)

    def _inner_specialize(self, specializing_paths):
        for specializing_path in specializing_paths:
            data = specializing_path.getData(self.domain)
            if len(data) % 8 != 0:
                raise GenerationException("specialize() produced {} bits, which is not aligned on 8 bits. You should review the field model.".format(len(data)))
            yield data.tobytes()

    @public_api
    def count(self, preset=None):
        r"""The :meth:`count` method computes the expected number of unique
        messages produced, considering the initial field model and the
        preset configuration.

        The :meth:`count` method expects the following parameters:

        :param preset: The configuration used to parameterize values in fields and variables. This configuration will impact the expected number of unique messages the field would produce.
        :type preset: :class:`Preset <netzob.Model.Vocabulary.Preset.Preset>`, optional
        :return: The number of unique values the field specialization can produce.
        :rtype: :class:`int`

        .. note::
           The theoretical value returned by :meth:`~count`
           may be huge. Therefore, we force the returned value to be
           :attr:`MAXIMUM_POSSIBLE_VALUES` (86400000000), if the
           theoretical result is beyond this threshold. This limit
           corresponds to 1 day of data generation based on a generation
           bandwith of 1 million per second.

        >>> # Field definition
        >>> from netzob.all import *
        >>> from netzob.Fuzzing.Generators.DeterministGenerator import DeterministGenerator
        >>> f1 = Field(uint16(interval=(50, 1000)))
        >>> f2 = Field(uint8())
        >>> f3 = Field(uint8())
        >>> f = Field([f1, f2, f3])
        >>>
        >>> # Count the expected number of unique produced messages
        >>> f.count()  #  Here, the following computation is done: 951*256*256 (f1 is able to produce 1000-50+1=951 possible values, based on its interval)
        62324736
        >>>
        >>> # Specify a preset configuration for field 'f2'
        >>> preset = Preset(f)
        >>> preset[f2] = 42
        >>> f.count(preset)  # Here, the following computation is done: 951*1*256 (as the f2 field value is set to 42, f2 can now produce only 1 possible value)
        243456
        >>>
        >>> # Specify a preset configuration for field 'f3' by activating fuzzing
        >>> preset.fuzz(f3, generator='determinist')
        >>>
        >>> f.count(preset)  # Here, the following computation is done: 951*1*29 (29 corresponds to the number of possible values generated by the determinist generator)
        27579

        """
        count = 1
        if len(self.fields) > 0:
            for field in self.fields:
                count *= field.count(preset=preset)
        else:
            count = self.domain.count(preset=preset)
        return count

    @property
    def domain(self):
        """This defines the definition domain of a field.

        This definition domain is made of a list of typed values which can optionally have a static value.
        More information on the available types and their specificities are available on their documentations.

        :type: a :class:`list` of :class:`object` -- By object we refer to a primitive object (:class:`int`, :class:`str`, :class:`hex`, :class:`binary`) and netzob types objects inherited from :class:`AbstractType <netzob.Model.Vocabulary.Types.AbstractType.AbstractType>`
        :raises: :class:`InvalidDomainException <netzob.Model.Vocabulary.Field.InvalidDomainException>` if domain invalid.
        """

        return self.__domain

    @domain.setter  # type: ignore
    def domain(self, domain):
        if domain is None:
            self.__domain = Data(Raw())
            self.__domain.field = self
        else:
            # Normalize the domain
            normalizedDomain = DomainFactory.normalizeDomain(domain)

            # Link the domain variables with the current field
            normalizedDomain.field = self

            self.__domain = normalizedDomain

    @property
    def messages(self):
        """A list containing all the messages that the parents of this field have.
        In reality, a field doesn't have messages, it just returns the messages of its symbol

        :type: a :class:`list` of :class:`AbstractMessage <netzob.Model.Vocabulary.Messages.AbstractMessage.AbstractMessage>`
        """
        messages = []
        try:
            messages.extend(self.getSymbol().messages)
        except Exception as e:
            self._logger.warning(
                "The field is attached to no symbol and so it has no messages: {0}".
                format(e))

        return messages

    @property
    def isPseudoField(self):
        """A flag indicating if the field is a pseudo field, meaning it is
        used internally to help for the computation of the value of
        another field, but does not directly produce data.

        :type: :class:`bool`

        """

        return self.__isPseudoField

    @isPseudoField.setter  # type: ignore
    @typeCheck(bool)
    def isPseudoField(self, isPseudoField):
        if isPseudoField is None:
            isPseudoField = False
        self.__isPseudoField = isPseudoField


def _test():
    r"""

    # Test field specialization

    >>> from netzob.all import *
    >>> f = Field(String("hello"))
    >>> next(f.specialize())
    b'hello'


    # Test field specialization with sub-fields

    >>> from netzob.all import *
    >>> f1 = Field(String("hello"))
    >>> f2 = Field(String(" john"))
    >>> f = Field([f1, f2])
    >>> next(f.specialize())
    b'hello john'


    # Test field specialization with fuzzing

    >>> from netzob.all import *
    >>> f = Field(String("hello"))
    >>> preset = Preset(f)
    >>> preset.fuzz(f)
    >>> next(f.specialize(preset))
    b'System("ls -al /")\x00                                                                                                                                                                                                                                             '
    """


def _test_field_integer():
    r"""

    # test field can define integer: signed and unsigned, represented in little/big endian and represented on 8/16/24/32/64 bit

    >>> from netzob.all import *

    >>> i1 = Integer(1, unitSize=UnitSize.SIZE_8, sign=Sign.UNSIGNED)
    >>> i2 = Integer(255, unitSize=UnitSize.SIZE_8, sign=Sign.UNSIGNED)
    >>> i3 = Integer(-2, unitSize=UnitSize.SIZE_8, sign=Sign.SIGNED)
    >>> i4 = Integer(255, unitSize=UnitSize.SIZE_16, endianness=Endianness.BIG)
    >>> i5 = Integer(255, unitSize=UnitSize.SIZE_16, endianness=Endianness.LITTLE)
    >>> i6 = Integer(255, unitSize=UnitSize.SIZE_24)
    >>> i7 = Integer(255, unitSize=UnitSize.SIZE_32)
    >>> i8 = Integer(255, unitSize=UnitSize.SIZE_64)

    >>> field = Field(domain=[i1, i2, i3, i4, i5, i6, i7, i8])
    >>> s = Symbol([field])
    >>> list = []
    >>> for _ in range(40):
    ...     list.append(next(s.specialize()))

    # i1
    >>> b'\x01' in list
    True

    # i2
    >>> b'\xff' in list
    True

    # i3
    >>> b'\xfe' in list
    True

    # i4
    >>> b'\x00\xff' in list
    True

    # i5
    >>> b'\xff\x00' in list
    True

    # i6
    >>> b'\x00\x00\xff' in list
    True

    # i7
    >>> b'\x00\x00\x00\xff' in list
    True

    # i8
    >>> b'\x00\x00\x00\x00\x00\x00\x00\xff' in list
    True

    """


def _test_field_bitarray():
    r"""

    # test field representation on bit array data with variable length

    >>> from netzob.all import *

    >>> next(Field(BitArray('00000000')).specialize())
    b'\x00'
    >>> next(Field(BitArray('00000001')).specialize())
    b'\x01'
    >>> next(Field(BitArray('00000010')).specialize())
    b'\x02'
    >>> next(Field(BitArray('00000100')).specialize())
    b'\x04'
    >>> next(Field(BitArray('11111111')).specialize())
    b'\xff'
    >>> next(Field(BitArray('1111111100000000')).specialize())
    b'\xff\x00'

    >>> len(next(Field(BitArray(nbBits=32)).specialize()))
    4
    >>> len(next(Field(BitArray(nbBits=64)).specialize()))
    8

    """


def _test_field_string():
    r"""

    # test field representation on string data (ASCII & Unicode) (output is hex of UTF-8 encoding)

    >>> from netzob.all import *

    >>> next(Field(domain=String('abcdef')).specialize())
    b'abcdef'
    >>> next(Field(domain=String('Ω')).specialize())
    b'\xce\xa9'
    >>> next(Field(domain=String('abcdefΩ')).specialize())
    b'abcdef\xce\xa9'

    >>> next(Field(domain=String('abcdef', eos=['123'])).specialize())
    b'abcdef123'

    """


def _test_field_padding():
    r"""
    # test field with Padding

    >>> from netzob.all import *

    >>> f_str = Field(String("abcdef"))
    >>> f_pad = Field(Padding(f_str, data=String('*'), modulo=64))
    >>> a = next(Field([f_str, f_pad]).specialize())
    >>> a
    b'abcdef**'
    >>> len(a) * 8
    64
    >>> f_pad = Field(Padding(f_str, data=String('*'), modulo=128))
    >>> len(next(Field([f_str, f_pad]).specialize())) * 8
    128
    >>> f_pad = Field(Padding(f_str, data=String('*'), modulo=256))
    >>> len(next(Field([f_str, f_pad]).specialize())) * 8
    256

    """


def _test_field_padding_callback():
    r"""
    # test field with Padding with the use of a callback function that determine the data value

    >>> from netzob.all import *
    >>> f0 = Field(Raw(nbBytes=10))
    >>> f1 = Field(Raw(b"##"))
    >>> def cbk_data(current_length, modulo):
    ...     length_to_pad = modulo - (current_length % modulo)  # Length in bits
    ...     length_to_pad = int(length_to_pad / 8)  # Length in bytes
    ...     res_bytes = b"".join([t.to_bytes(1, byteorder='big') for t in list(range(length_to_pad))])
    ...     res_bits = bitarray(endian='big')
    ...     res_bits.frombytes(res_bytes)
    ...     return res_bits
    >>> f2 = Field(Padding([f0, f1], data=cbk_data, modulo=128))
    >>> f = Field([f0, f1, f2])
    >>> d = next(f.specialize())
    >>> d[12:]
    b'\x00\x01\x02\x03'
    >>> len(d) * 8
    128

    """


def _test_field_multi_type():
    r"""
    # test field with several different types

    >>> from netzob.all import *
    >>> f_int = Field([42, Integer(43)])
    >>> f_str = Field(["abc", String("def")])
    >>> f_bit = Field([BitArray('11111111'), Raw(b'##')])
    >>> f_f = Field([f_int, f_str, f_bit])
    >>> f = Field([f_f])
    >>> b = next(f.specialize())
    >>> for _ in range(10):
    ...     b += next(f.specialize())

    >>> b.find(b'\x2A') != -1 # 42 in hexa
    True
    >>> b.find(b'\x2B') != -1 # 43 in hexa
    True
    >>> b.find(b'abc') != -1
    True
    >>> b.find(b'def') != -1
    True
    >>> b.find(b'\xff') != -1 # BitArray('11111111')
    True
    >>> b.find(b'##') != -1
    True

    """


def _test_inaccessible_variable_during_specialization_agg():
    r"""

    >>> from netzob.all import *
    >>> Conf.apply()
    >>> length = Field(uint8be(), "icmp.length")
    >>> payloadVar = Data(Raw(nbBytes=(1, 10)))
    >>> paddingVar = Padding([payloadVar],
    ...                       data=Raw(b"\x00"),
    ...                       modulo=32,
    ...                       once=False)
    >>> field_payload_padding = Field(Agg([payloadVar, paddingVar]), "icmp.payload")
    >>> length.domain = Size([field_payload_padding],
    ...                      dataType=uint8be())
    ...                      #factor=1./32)
    >>> checksum = Field(InternetChecksum([paddingVar],
    ...                                   dataType=Raw(nbBytes=2,
    ...                                   unitSize=UnitSize.SIZE_16)),
    ...                  "icmp.checksum")
    >>> s = Symbol(
    ...     [checksum, length, field_payload_padding],
    ...     name="unreach")
    >>> print(next(s.specialize()))
    b'\xff\xff\x04\xdb\x00\x00\x00'
    >>> preset = Preset(s)
    >>> preset['icmp.payload'] = b'PAYLOAD\x00'
    >>> print(next(s.specialize(preset=preset)))
    Traceback (most recent call last):
    ...
    netzob.Model.Vocabulary.Domain.Variables.Leafs.AbstractRelationVariableLeaf.InaccessibleVariableException: The following variable is inaccessible: 'Padding(['Data']) - Type:Raw(b'\x00')' for field 'icmp.payload'. This may be because a parent field or variable is preset.


    >>> from netzob.all import *
    >>> Conf.apply()
    >>> v_raw1 = Data(Raw(nbBytes=2))
    >>> v_raw2 = Data(Raw(nbBytes=4))
    >>> v_agg = Agg([v_raw1, v_raw2])
    >>> f1 = Field(v_agg)
    >>> f2 = Field(Value(v_agg))
    >>> s = Symbol([f1, f2])
    >>> next(s.specialize())
    b'\xdb\xf7i\xec\xfb\x8e\xdb\xf7i\xec\xfb\x8e'
    >>> preset = Preset(s)
    >>> preset[v_agg] = b"aa"
    >>> next(s.specialize(preset))
    b'aaaa'


    >>> from netzob.all import *
    >>> Conf.apply()
    >>> v_raw1 = Data(Raw(nbBytes=2))
    >>> v_raw2 = Data(Raw(nbBytes=4))
    >>> v_agg = Agg([v_raw1, v_raw2])
    >>> f1 = Field(v_agg)
    >>> f2 = Field(Value(v_raw1))
    >>> s = Symbol([f1, f2])
    >>> next(s.specialize())
    b'\xdb\xf7i\xec\xfb\x8e\xdb\xf7'
    >>> preset = Preset(s)
    >>> preset[v_agg] = b"aa"
    >>> next(s.specialize(preset))
    Traceback (most recent call last):
    ...
    netzob.Model.Vocabulary.Domain.Variables.Leafs.AbstractRelationVariableLeaf.InaccessibleVariableException: The following variable is inaccessible: 'Data (Raw(nbBytes=2))' for field 'Field'. This may be because a parent field or variable is preset.

    """


def _test_inaccessible_variable_during_specialization_alt():
    r"""

    >>> from netzob.all import *
    >>> Conf.apply()
    >>> v_raw1 = Data(Raw(nbBytes=2))
    >>> v_raw2 = Data(Raw(nbBytes=4))
    >>> v_alt = Alt([v_raw1, v_raw2])
    >>> f1 = Field(v_alt)
    >>> f2 = Field(Value(v_alt))
    >>> s = Symbol([f1, f2])
    >>> next(s.specialize())
    b'\xf7\x07\xf7\x07'
    >>> preset = Preset(s)
    >>> preset[v_alt] = b"aa"
    >>> next(s.specialize(preset))
    b'aaaa'

    >>> from netzob.all import *
    >>> Conf.apply()
    >>> v_raw1 = Data(Raw(nbBytes=2))
    >>> v_raw2 = Data(Raw(nbBytes=4))
    >>> v_alt = Alt([v_raw1, v_raw2])
    >>> f1 = Field(v_alt)
    >>> f2 = Field(Value(v_raw1))
    >>> s = Symbol([f1, f2])
    >>> next(s.specialize())
    b'\xf7\x07\xf7\x07'
    >>> preset = Preset(s)
    >>> preset[v_alt] = b"aa"
    >>> next(s.specialize(preset))
    Traceback (most recent call last):
    ...
    netzob.Model.Vocabulary.Domain.Variables.Leafs.AbstractRelationVariableLeaf.InaccessibleVariableException: The following variable is inaccessible: 'Data (Raw(nbBytes=2))' for field 'Field'. This may be because a parent field or variable is preset.

    """


def _test_inaccessible_variable_during_specialization_repeat():
    r"""

    >>> from netzob.all import *
    >>> Conf.apply()
    >>> v_raw1 = Data(Raw(nbBytes=2))
    >>> v_repeat = Repeat(v_raw1, nbRepeat=2)
    >>> f1 = Field(v_repeat)
    >>> f2 = Field(Value(v_repeat))
    >>> s = Symbol([f1, f2])
    >>> next(s.specialize())
    b'\xf7\x07\xec\xfb\xf7\x07\xec\xfb'
    >>> preset = Preset(s)
    >>> preset[v_repeat] = b"aa"
    >>> next(s.specialize(preset))
    b'aaaa'

    >>> from netzob.all import *
    >>> Conf.apply()
    >>> v_raw1 = Data(Raw(nbBytes=2))
    >>> v_repeat = Repeat(v_raw1, nbRepeat=2)
    >>> f1 = Field(v_repeat)
    >>> f2 = Field(Value(v_raw1))
    >>> s = Symbol([f1, f2])
    >>> next(s.specialize())
    Traceback (most recent call last):
    ...
    TypeError: Value target is a child of a Repeat variable, which is not supported

    """


def _test_field_multiple_targets():
    r"""

    >>> from netzob.all import *
    >>> Conf.apply()
    >>> length = Field(uint8be(), "icmp.length")
    >>> payloadVar = Data(Raw(nbBytes=(1, 10)))
    >>> paddingVar = Padding([payloadVar],
    ...                      data=Raw(b"\x00"),
    ...                      modulo=32,
    ...                      once=False)
    >>> field_payload_padding = Field(Agg([payloadVar, paddingVar]), name='icmp.padding')
    >>> length.domain = Size([field_payload_padding],
    ...                      dataType=uint8be(),
    ...                      factor=1./32)
    >>> checksum = Field(InternetChecksum([field_payload_padding],
    ...                                   dataType=Raw(nbBytes=2,
    ...                                   unitSize=UnitSize.SIZE_16)),
    ...                  "icmp.checksum")
    >>> s = Symbol(
    ...     [checksum, length, field_payload_padding],
    ...     name="unreach")
    >>> data = next(s.specialize())
    >>> data
    b'$\xff\x01\xdb\x00\x00\x00'
    >>> s.abstract(data)
    OrderedDict([('icmp.checksum', b'$\xff'), ('icmp.length', b'\x01'), ('icmp.padding', b'\xdb\x00\x00\x00')])

    """


def _test_field_alt_with_future_dependency():
    r"""

    >>> from netzob.all import *
    >>> Conf.apply()
    >>> v_raw1 = Data(Raw(nbBytes=2))
    >>> v_value = Value(v_raw1)
    >>> v_alt = Alt([v_value])
    >>> f1 = Field(v_alt, name="f1")
    >>> f2 = Field(v_raw1, name="f2")
    >>> s = Symbol([f1, f2])
    >>> d = next(s.specialize())
    >>> d
    b'\xf7\x07\xf7\x07'
    >>> s.abstract(d)
    OrderedDict([('f1', b'\xf7\x07'), ('f2', b'\xf7\x07')])

    """


def _test_field_repeat_with_future_dependency():
    r"""

    >>> from netzob.all import *
    >>> Conf.apply()
    >>> v_raw1 = Data(Raw(nbBytes=2))
    >>> v_value = Value(v_raw1)
    >>> v_repeat = Repeat(v_value, nbRepeat=2)
    >>> f1 = Field(v_repeat, name="f1")
    >>> f2 = Field(v_raw1, name="f2")
    >>> s = Symbol([f1, f2])
    >>> d = next(s.specialize())
    >>> d
    b'\xf7\x07\xf7\x07\xf7\x07'
    >>> s.abstract(d)
    OrderedDict([('f1', b'\xf7\x07\xf7\x07'), ('f2', b'\xf7\x07')])

    >>> from netzob.all import *
    >>> Conf.apply()
    >>> v_raw1 = Data(Raw(nbBytes=(1, 4)))
    >>> v_value = Value(v_raw1)
    >>> v_repeat = Repeat(v_value, nbRepeat=(2, 5))
    >>> f1 = Field(v_repeat, name="f1")
    >>> f2 = Field(v_raw1, name="f2")
    >>> s = Symbol([f1, f2])
    >>> d = next(s.specialize())
    >>> d
    b'\xf7\x07\xf7\x07\xf7\x07\xf7\x07'
    >>> s.abstract(d)  # doctest: +SKIP
    OrderedDict([('f1', b'\xf7\x07\xf7\x07\xf7'), ('f2', b'\x07')])

    >>> from netzob.all import *
    >>> Conf.apply()
    >>> v_raw1 = Data(Raw(nbBytes=2))
    >>> v_size = Size(v_raw1)
    >>> v_repeat = Repeat(v_size, nbRepeat=(2, 5))
    >>> f1 = Field(v_repeat, name="f1")
    >>> f2 = Field(v_raw1, name="f2")
    >>> s = Symbol([f1, f2])
    >>> d = next(s.specialize())
    >>> d
    b'\x02\x02\xf7\x07'
    >>> s.abstract(d)
    OrderedDict([('f1', b'\x02\x02'), ('f2', b'\xf7\x07')])

    >>> from netzob.all import *
    >>> Conf.apply()
    >>> v_raw1 = Data(Raw(nbBytes=(1, 4)))
    >>> v_size = Size(v_raw1)
    >>> v_repeat = Repeat(v_size, nbRepeat=(2, 5))
    >>> f1 = Field(v_repeat, name="f1")
    >>> f2 = Field(v_raw1, name="f2")
    >>> s = Symbol([f1, f2])
    >>> d = next(s.specialize())
    >>> d
    b'\x02\x02\x02\xf7\x07'
    >>> s.abstract(d)  # doctest: +SKIP
    OrderedDict([('f1', b'\x02\x02'), ('f2', b'\xf7\x07')])

    """


def _test_field_with_future_common_target_for_multiple_variables():
    r"""

    >>> from netzob.all import *
    >>> Conf.apply()
    >>> v_raw = Data(Raw(nbBytes=2))
    >>> v_value1 = Value(v_raw)
    >>> v_value2 = Value(v_raw)
    >>> f1 = Field(v_raw, name="f1")
    >>> f2 = Field(v_value1, name="f2")
    >>> f3 = Field(v_value2, name="f3")
    >>> s = Symbol([f2, f3, f1])
    >>> d = next(s.specialize())
    >>> d
    b'\xdb\xf7\xdb\xf7\xdb\xf7'
    >>> s.abstract(d)
    OrderedDict([('f2', b'\xdb\xf7'), ('f3', b'\xdb\xf7'), ('f1', b'\xdb\xf7')])

    >>> from netzob.all import *
    >>> Conf.apply()
    >>> v_raw = Data(Raw(nbBytes=(1, 4)))
    >>> v_value1 = Value(v_raw)
    >>> v_value2 = Value(v_raw)
    >>> f1 = Field(v_raw, name="f1")
    >>> f2 = Field(v_value1, name="f2")
    >>> f3 = Field(v_value2, name="f3")
    >>> s = Symbol([f2, f3, f1])
    >>> d = next(s.specialize())
    >>> d
    b'\x10\xdb\xf7\x10\xdb\xf7\x10\xdb\xf7'
    >>> s.abstract(d)
    OrderedDict([('f2', b'\x10\xdb\xf7'), ('f3', b'\x10\xdb\xf7'), ('f1', b'\x10\xdb\xf7')])

    >>> from netzob.all import *
    >>> Conf.apply()
    >>> v_raw = Data(Raw(nbBytes=2))
    >>> v_value1 = Size(v_raw)
    >>> v_value2 = Size(v_raw)
    >>> f1 = Field(v_raw, name="f1")
    >>> f2 = Field(v_value1, name="f2")
    >>> f3 = Field(v_value2, name="f3")
    >>> s = Symbol([f2, f3, f1])
    >>> d = next(s.specialize())
    >>> d
    b'\x02\x02\xdb\xf7'
    >>> s.abstract(d)
    OrderedDict([('f2', b'\x02'), ('f3', b'\x02'), ('f1', b'\xdb\xf7')])

    >>> from netzob.all import *
    >>> Conf.apply()
    >>> v_raw = Data(Raw(nbBytes=(1, 4)))
    >>> v_value1 = Size(v_raw)
    >>> v_value2 = Size(v_raw)
    >>> f1 = Field(v_raw, name="f1")
    >>> f2 = Field(v_value1, name="f2")
    >>> f3 = Field(v_value2, name="f3")
    >>> s = Symbol([f2, f3, f1])
    >>> d = next(s.specialize())
    >>> d
    b'\x03\x03\x10\xdb\xf7'
    >>> s.abstract(d)
    OrderedDict([('f2', b'\x03'), ('f3', b'\x03'), ('f1', b'\x10\xdb\xf7')])

    >>> from netzob.all import *
    >>> Conf.apply()
    >>> v_raw = Data(Raw(nbBytes=(1, 4)))
    >>> v_value1 = Size(v_raw)
    >>> v_value2 = Size([v_raw, v_value1])
    >>> f1 = Field(v_raw, name="f1")
    >>> f2 = Field(v_value2, name="f2")
    >>> f3 = Field(v_value1, name="f3")
    >>> s = Symbol([f2, f3, f1])
    >>> d = next(s.specialize())
    >>> d
    b'\x04\x03\x10\xdb\xf7'
    >>> s.abstract(d)
    OrderedDict([('f2', b'\x04'), ('f3', b'\x03'), ('f1', b'\x10\xdb\xf7')])

   """
