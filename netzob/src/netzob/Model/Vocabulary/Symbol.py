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
# |       - Georges Bossert <georges.bossert (a) supelec.fr>                  |
# |       - Frédéric Guihéry <frederic.guihery (a) amossys.fr>                |
# +---------------------------------------------------------------------------+

# +---------------------------------------------------------------------------+
# | Standard library imports                                                  |
# +---------------------------------------------------------------------------+
try:
    from typing import Dict, List  # noqa: F401
except ImportError:
    pass

# +---------------------------------------------------------------------------+
# | Related third party imports                                               |
# +---------------------------------------------------------------------------+

# +---------------------------------------------------------------------------+
# | Local application imports                                                 |
# +---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, public_api, NetzobLogger
from netzob.Model.Vocabulary.AbstractField import AbstractField, GenerationException
from netzob.Common.Utils.TypedList import TypedList
from netzob.Model.Vocabulary.Messages.AbstractMessage import AbstractMessage
from netzob.Model.Vocabulary.Field import Field
from netzob.Model.Vocabulary.Domain.Variables.Memory import Memory


@NetzobLogger
class Symbol(AbstractField):
    r"""The Symbol class is a main component of the Netzob protocol model.

    A symbol represents an abstraction of all messages of the same
    type from a protocol perspective. A symbol structure is made of
    fields.

    The Symbol constructor expects some parameters:

    :param fields: The fields that participate in the symbol
                   definition, in the wire order. May be ``None`` (thus, a generic :class:`Field <netzob.Model.Vocabulary.Field.Field>`
                   instance would be defined), especially when using Symbols
                   for reverse engineering (i.e. fields identification).
    :param messages: The messages that are associated with the
                     symbol. May be ``None`` (thus, an empty :class:`list`
                     would be defined), especially when
                     modeling a protocol from scratch (i.e. the
                     fields are already known).
    :param name: The name of the symbol. If not specified, the
                 default name will be "Symbol".
    :type fields: a :class:`list` of :class:`Field <netzob.Model.Vocabulary.Field.Field>`, optional
    :type messages: a :class:`list` of :class:`AbstractMessage <netzob.Model.Vocabulary.Messages.AbstractMessage.AbstractMessage>`, optional
    :type name: :class:`str`, optional


    The Symbol class provides the following public variables:

    :var fields: The sorted list of sub-fields.
    :var name: The name of the symbol.
    :var description: The description of the symbol.
    :vartype fields: a :class:`list` of :class:`Field <netzob.Model.Vocabulary.Field.Field>`
    :vartype name: :class:`str`
    :vartype description: :class:`str`


    **Usage of Symbol for protocol modeling**

    The Symbol class may be used to model a protocol from scratch, by
    specifying its structure in terms of fields:

    >>> from netzob.all import *
    >>> f0 = Field("aaaa")
    >>> f1 = Field(" # ")
    >>> f2 = Field("bbbbbb")
    >>> symbol = Symbol(fields=[f0, f1, f2])
    >>> for f in symbol.fields:
    ...     print("{} - {}".format(f, f.domain))
    Field - Data (String('aaaa'))
    Field - Data (String(' # '))
    Field - Data (String('bbbbbb'))

    .. ifconfig:: scope in ('netzob')

       **Usage of Symbol for protocol dissecting**

       The Symbol class may be used to dissect a list of messages
       according to the fields structure:

       >>> from netzob.all import *
       >>> f0 = Field("hello", name="f0")
       >>> f1 = Field(String(nbChars=(0, 10)), name="f1")
       >>> m1 = RawMessage("hello world")
       >>> m2 = RawMessage("hello earth")
       >>> symbol = Symbol(fields=[f0, f1], messages=[m1, m2])
       >>> print(symbol.str_data())
       f0      | f1      
       ------- | --------
       'hello' | ' world'
       'hello' | ' earth'
       ------- | --------


    .. ifconfig:: scope in ('netzob')

       **Usage of Symbol for protocol reverse engineering**

       The Symbol class may be used is to do reverse engineering on a
       list of captured messages of unknown/undocumented protocols:

       >>> from netzob.all import *
       >>> m1 = RawMessage("hello aaaa")
       >>> m2 = RawMessage("hello bbbb")
       >>> symbol = Symbol(messages=[m1, m2])
       >>> Format.splitStatic(symbol)
       >>> print(symbol.str_data())
       Field-0  | Field-1
       -------- | -------
       'hello ' | 'aaaa' 
       'hello ' | 'bbbb' 
       -------- | -------

    """

    @public_api
    def __init__(self, fields=None, messages=None, name="Symbol"):
        # type: (List[Field], List[AbstractMessage], str) -> None
        super(Symbol, self).__init__(name)
        self.__messages = TypedList(AbstractMessage)
        if messages is None:
            messages = []
        self.messages = messages
        if fields is None:
            # create a default empty field
            fields = [Field()]
        self.fields = fields

    @public_api
    def copy(self, map_objects=None):
        """Copy the current object as well as all its dependencies. This
        method returns a new object of the same type.

        :return: A new object of the same type.
        :rtype: :class:`Symbol <netzob.Model.Vocabulary.Symbol.Symbol>`

        """

        # map_objects is a dict that contains already copied instances. This allows to copy objects, such as fields, that contains relationships with already copied elements.

        if map_objects is None:
            map_objects = {}
        if self in map_objects:
            return map_objects[self]

        new_symbol = Symbol(fields=[], messages=self.messages, name=self.name)
        map_objects[self] = new_symbol

        new_fields = []
        for f in self.fields:
            if f in map_objects.keys():
                new_fields.append(map_objects[f])
            else:
                new_field = f.copy(map_objects)
                new_fields.append(new_field)

        new_symbol.fields = new_fields
        return new_symbol

    def __eq__(self, other):
        if not isinstance(other, Symbol):
            return False
        if other is None:
            return False
        return self.name == other.name

    def __ne__(self, other):
        if other is None:
            return True
        if not isinstance(other, Symbol):
            return True
        return other.name != self.name

    def __key(self):
        return id(self)

    def __hash__(self):
        return id(self)

    @public_api
    def str_structure(self, preset=None, deepness=0):
        r"""Returns a string which denotes the current symbol definition
        using a tree display.

        :param preset: The configuration used to parameterize values in fields and variables.
        :type preset: :class:`Preset <netzob.Model.Vocabulary.Preset.Preset>`, optional
        :return: The current symbol represented as a string.
        :rtype: :class:`str`


        This example shows the rendering of a symbol with multiple
        fields.

        >>> from netzob.all import *
        >>> f1 = Field(String(), name="field1")
        >>> f2 = Field(Integer(interval=(10, 100)), name="field2")
        >>> f3 = Field(Raw(nbBytes=14), name="field3")
        >>> symbol = Symbol([f1, f2, f3], name="symbol_name")
        >>> print(symbol.str_structure())
        symbol_name
        |--  field1
             |--   Data (String(nbChars=(0,8192)))
        |--  field2
             |--   Data (Integer(10,100))
        |--  field3
             |--   Data (Raw(nbBytes=14))
        >>> print(f1.str_structure())
        field1
        |--   Data (String(nbChars=(0,8192)))


        This example shows the rendering of a symbol where a Preset
        configuration has been applied on several variables (the
        :meth:`fuzz` method is explained in the fuzzing section).

        >>> from netzob.all import *
        >>> field1 = Field(Raw(nbBytes=1), name="field 1")
        >>> v1 = Data(uint8(), name='v1')
        >>> v2 = Data(uint8())
        >>> var_agg = Agg([v1, v2])
        >>> field2 = Field(var_agg, name="field 2")
        >>> field3 = Field(Raw(nbBytes=1), name="field 3")
        >>> symbol = Symbol(name="symbol 1", fields=[field1, field2, field3])
        >>> preset = Preset(symbol)
        >>> preset[field1] = b'\x42'
        >>> preset.fuzz('v1', mode=FuzzingMode.MUTATE)
        >>> preset.fuzz(field3)
        >>> print(symbol.str_structure(preset))
        symbol 1
        |--  field 1
             |--   Data (Raw(nbBytes=1)) [FuzzingMode.FIXED (b'B')]
        |--  field 2
             |--   Agg
                   |--   Data (Integer(0,255)) [FuzzingMode.MUTATE]
                   |--   Data (Integer(0,255))
        |--  field 3
             |--   Data (Raw(nbBytes=1)) [FuzzingMode.GENERATE]

        """
        tab = ["|--  " for x in range(deepness)]
        tab.append(str(self.name))
        lines = [''.join(tab)]
        for f in self.fields:
            lines.append(f.str_structure(preset, deepness + 1))
        return '\n'.join(lines)

    @public_api
    def specialize(self,
                   preset=None,
                   memory=None):
        r"""The :meth:`specialize()` method is intended to produce concrete
        :class:`bytes` data based on the symbol model and the current :class:`Preset <netzob.Model.Vocabulary.Preset.Preset>` configuration. This method
        returns a Python generator that in turn provides data
        :class:`bytes` object at each call to ``next(generator)``.

        The specialize() method expects some parameters:

        :param preset: The configuration used to parameterize values in fields and variables.
        :param memory: A memory used to store variable values during
                       specialization and abstraction of successive
                       symbols, especially to handle inter-symbol
                       relationships. If None, a temporary memory is
                       created by default and used internally during the scope of the
                       specialization process.
        :type preset: :class:`Preset <netzob.Model.Vocabulary.Preset.Preset>`, optional
        :type memory: :class:`Memory <netzob.Model.Vocabulary.Domain.Variables.Memory.Memory>`, optional
        :return: A generator that provides data :class:`bytes` at each call to ``next(generator)``.
        :rtype: :class:`Generator[bytes]`
        :raises: :class:`GenerationException <netzob.Model.Vocabulary.AbstractField.GenerationException>` if an error occurs while specializing the field.

        The following example shows the :meth:`specialize()` method used for a
        field which contains a String field and a Size field.

        >>> from netzob.all import *
        >>> f1 = Field(domain=String('hello'))
        >>> f2 = Field(domain=String(' '))
        >>> f3 = Field(domain=String('John'))
        >>> s = Symbol(fields=[f1, f2, f3])
        >>> next(s.specialize())
        b'hello John'

        """

        from netzob.Model.Vocabulary.Domain.Specializer.MessageSpecializer import MessageSpecializer
        msg = MessageSpecializer(preset=preset, memory=memory)

        specializing_paths = msg.specializeSymbol(self)
        return self._inner_specialize(specializing_paths)

    def _inner_specialize(self, specializing_paths):
        for specializing_path in specializing_paths:
            data = specializing_path.generatedContent
            if len(data) % 8 != 0:
                raise GenerationException("specialize() produced {} bits, which is not aligned on 8 bits. You should review the symbol model.".format(len(data)))
            yield data.tobytes()

    @public_api
    def count(self, preset=None):
        r"""The :meth:`count` method computes the expected number of unique
        messages produced, considering the initial symbol model and the
        preset configuration of fields.

        The :meth:`count` method expects the following parameters:

        :param preset: The configuration used to parameterize values in fields and variables. This configuration will impact the expected number of unique messages the symbol would produce.
        :type preset: :class:`Preset <netzob.Model.Vocabulary.Preset.Preset>`, optional
        :return: The number of unique values the symbol specialization can produce.
        :rtype: :class:`int`

        .. note::
           The theoretical value returned by :meth:`~count`
           may be huge. Therefore, we force the returned value to be
           :attr:`MAXIMUM_POSSIBLE_VALUES` (86400000000), if the
           theoretical result is beyond this threshold. This limit
           corresponds to 1 day of data generation based on a generation
           bandwith of 1 million per second.

        >>> # Symbol definition
        >>> from netzob.all import *
        >>> from netzob.Fuzzing.Generators.DeterministGenerator import DeterministGenerator
        >>> f1 = Field(uint16(interval=(50, 1000)))
        >>> f2 = Field(uint8())
        >>> f3 = Field(uint8())
        >>> symbol = Symbol(fields=[f1, f2, f3])
        >>>
        >>> # Count the expected number of unique produced messages
        >>> symbol.count()  #  Here, the following computation is done: 951*256*256 (f1 is able to produce 1000-50+1=951 possible values, based on its interval)
        62324736
        >>>
        >>> # Specify a preset configuration for field 'f2'
        >>> preset = Preset(symbol)
        >>> preset[f2] = 42
        >>> symbol.count(preset)  # Here, the following computation is done: 951*1*256 (as the f2 field value is set to 42, f2 can now produce only 1 possible value)
        243456
        >>>
        >>> # Specify a preset configuration for field 'f3' by activating fuzzing
        >>> preset.fuzz(f3, generator='determinist')
        >>>
        >>> symbol.count(preset)  # Here, the following computation is done: 951*1*29 (29 corresponds to the number of possible values generated by the determinist generator)
        27579

        """

        count = 1
        for field in self.fields:
            count *= field.count(preset=preset)
        return count

    def clearMessages(self):
        """Delete all the messages attached to the current symbol"""
        while (len(self.__messages) > 0):
            self.__messages.pop()

    # Properties

    @property
    def messages(self):
        """A list containing all the messages that this symbol represent.

        :type : a :class:`list` of :class:`AbstractMessage <netzob.Model.Vocabulary.Messages.AbstractMessage.AbstractMessage>`
        """
        return self.__messages

    @messages.setter  # type: ignore
    def messages(self, messages):
        if messages is None:
            messages = []

        # First it checks the specified messages are all AbstractMessages
        for msg in messages:
            if not isinstance(msg, AbstractMessage):
                raise TypeError(
                    "Cannot add messages of type {0} in the session, only AbstractMessages are allowed.".
                    format(type(msg)))

        self.clearMessages()
        for msg in messages:
            self.__messages.append(msg)

    def __repr__(self):
        return self.name

    def __getitem__(self, field_name):
        """
        Get a field from its name in the field database.

        :param field_name: the name of the :class:`Field <netzob.Model.Vocabulary.Field.Field>` object
        :type field_name: :class:`str`
        :raise KeyError: when the field has not been found
        """
        return self.getField(field_name)


def _test_many_relation_abstractions():
    r"""
    >>> from netzob.all import *
    >>> eth_length = Field(bitarray('0000000000000000'), "eth.length")
    >>>
    >>> eth_llc = Field(Raw(nbBytes=3), "eth.llc")  # IEEE 802.2 header
    >>>
    >>> eth_payload = Field(Raw(), name="eth.payload")
    >>>
    >>> eth_padding = Field(Padding([eth_length, eth_llc, eth_payload],
    ...                              data=Raw(nbBytes=1),
    ...                              modulo=8*60),
    ...                      "eth.padding")
    >>>
    >>> eth_crc_802_3 = Field(bitarray('00000000000000000000000000000000'), "eth.crc")
    >>> eth_crc_802_3.domain = CRC32([eth_length,
    ...                               eth_llc,
    ...                               eth_payload,
    ...                               eth_padding],
    ...                              dataType=Raw(nbBytes=4,
    ...                                           unitSize=UnitSize.SIZE_32))
    >>>
    >>> eth_length.domain = Size([eth_llc, eth_payload],
    ...                           dataType=uint16(), factor=1./8)
    >>>
    >>> symbol = Symbol(name="ethernet_802_3",
    ...                  fields=[eth_length,
    ...                          eth_llc,
    ...                          eth_payload,
    ...                          eth_padding,
    ...                          eth_crc_802_3])
    >>> preset = Preset(symbol)
    >>> preset['eth.payload'] = b"PAYLOAD"
    >>> print(symbol.str_structure())
    ethernet_802_3
    |--  eth.length
         |--   Size(['eth.llc', 'eth.payload']) - Type:Integer(0,65535)
    |--  eth.llc
         |--   Data (Raw(nbBytes=3))
    |--  eth.payload
         |--   Data (Raw(nbBytes=(0,8192)))
    |--  eth.padding
         |--   Padding(['eth.length', 'eth.llc', 'eth.payload']) - Type:Raw(nbBytes=1)
    |--  eth.crc
         |--   Relation(['eth.length', 'eth.llc', 'eth.payload', 'eth.padding']) - Type:Raw(nbBytes=4)
    >>> data = next(symbol.specialize(preset))
    >>> symbol.abstract(data)  # doctest: +ELLIPSIS
    OrderedDict([('eth.length', b'\x00\n'), ('eth.llc', b'...'), ('eth.payload', b'PAYLOAD'), ('eth.padding', b'...'), ('eth.crc', ...)])


    # Test abstraction of ARP message

    >>> data = b"\x00\x01\x08\x00\x06\x04\x00\x02\x00\x22\x4d\x56\x4d\xac\xc0\xa8\xc8\xab\x84\x8f\x69\xc9\x28\x91\xc0\xa8\xc8\xe2"

    >>> arp_hrd = Field(uint16(), "arp.hrd") # Hardware address space (1 for Ethernet)
    >>> arp_pro = Field(uint16(), "arp.pro") # Protocol address space (2048 for IP)
    >>> arp_hln = Field(uint8(), "arp.hln")  # byte length of each hardware address
    >>> arp_pln = Field(uint8(), "arp.pln")  # byte length of each protocol address
    >>> arp_op = Field(uint16(), "arp.op")   # opcode (1 for request, 2 for reply)

    >>> arp_ip_sha = Field(Raw(nbBytes=6), "arp.sha")
    >>> arp_ip_spa = Field(Raw(nbBytes=4), "arp.spa")
    >>> arp_ip_tha = Field(Raw(nbBytes=6), "arp.tha")
    >>> arp_ip_tpa = Field(Raw(nbBytes=4), "arp.tpa")

    >>> arp_ip_symbol = Symbol(name="arp.ip", fields=([
    ...     arp_hrd, arp_pro, arp_hln, arp_pln, arp_op,
    ...     arp_ip_sha, arp_ip_spa, arp_ip_tha, arp_ip_tpa]))

    >>> arp_ip_symbol.abstract(data)
    OrderedDict([('arp.hrd', b'\x00\x01'), ('arp.pro', b'\x08\x00'), ('arp.hln', b'\x06'), ('arp.pln', b'\x04'), ('arp.op', b'\x00\x02'), ('arp.sha', b'\x00"MVM\xac'), ('arp.spa', b'\xc0\xa8\xc8\xab'), ('arp.tha', b'\x84\x8fi\xc9(\x91'), ('arp.tpa', b'\xc0\xa8\xc8\xe2')])


    # Test Symbol cloning

    >>> f1 = Field(Raw())
    >>> f2 = Field(Size(f1))
    >>> f3 = Field(Value(f2))
    >>> f4 = Field(CRC16([f2]))
    >>> f5 = Field(MD5([f2]))
    >>> f6 = Field(HMAC_MD5([f2], key="\x00"))
    >>> v1 = Data(int8(2))
    >>> f7 = Field(Agg([Raw(), v1]))
    >>> f8 = Field(Alt([Raw(), Raw()]))
    >>> f9 = Field(Repeat(Raw(), nbRepeat=1))
    >>> f10 = Field(Repeat(Raw(), nbRepeat=v1))
    >>> f11 = Field(Opt(Raw()))
    >>> s = Symbol([f1, f2, f3, f4, f5, f6, f7, f8, f9, f10, f11])
    >>> print(s.str_structure())
    Symbol
    |--  Field
         |--   Data (Raw(nbBytes=(0,8192)))
    |--  Field
         |--   Size(['Field']) - Type:Integer(0,255)
    |--  Field
         |--   Value(Field)
    |--  Field
         |--   Relation(['Field']) - Type:Raw(nbBytes=2)
    |--  Field
         |--   Relation(['Field']) - Type:Raw(nbBytes=16)
    |--  Field
         |--   Relation(['Field']) - Type:Raw(nbBytes=16)
    |--  Field
         |--   Agg
               |--   Data (Raw(nbBytes=(0,8192)))
               |--   Data (Integer(2))
    |--  Field
         |--   Alt
               |--   Data (Raw(nbBytes=(0,8192)))
               |--   Data (Raw(nbBytes=(0,8192)))
    |--  Field
         |--   Repeat
               |--   Data (Raw(nbBytes=(0,8192)))
    |--  Field
         |--   Repeat
               |--   Data (Raw(nbBytes=(0,8192)))
    |--  Field
         |--   Opt
               |--   Data (Raw(nbBytes=(0,8192)))
    >>> ids = set()
    >>> for f in s.getLeafFields():
    ...     ids.add(id(f))
    ...     ids.add(id(f.domain))
    ...     if f.domain.isnode():
    ...         for v in f.domain.children:
    ...             ids.add(id(v))
    
    >>> s_bis = s.copy()
    >>> print(s_bis.str_structure())
    Symbol
    |--  Field
         |--   Data (Raw(nbBytes=(0,8192)))
    |--  Field
         |--   Size(['Field']) - Type:Integer(0,255)
    |--  Field
         |--   Value(Field)
    |--  Field
         |--   Relation(['Field']) - Type:Raw(nbBytes=2)
    |--  Field
         |--   Relation(['Field']) - Type:Raw(nbBytes=16)
    |--  Field
         |--   Relation(['Field']) - Type:Raw(nbBytes=16)
    |--  Field
         |--   Agg
               |--   Data (Raw(nbBytes=(0,8192)))
               |--   Data (Integer(2))
    |--  Field
         |--   Alt
               |--   Data (Raw(nbBytes=(0,8192)))
               |--   Data (Raw(nbBytes=(0,8192)))
    |--  Field
         |--   Repeat
               |--   Data (Raw(nbBytes=(0,8192)))
    |--  Field
         |--   Repeat
               |--   Data (Raw(nbBytes=(0,8192)))
    |--  Field
         |--   Opt
               |--   Data (Raw(nbBytes=(0,8192)))
    >>> ids_bis = set()
    >>> for f in s_bis.getLeafFields():
    ...     ids_bis.add(id(f))
    ...     ids_bis.add(id(f.domain))
    ...     if f.domain.isnode():
    ...         for v in f.domain.children:
    ...             ids_bis.add(id(v))
    >>> ids.intersection(ids_bis)
    set()


    """
