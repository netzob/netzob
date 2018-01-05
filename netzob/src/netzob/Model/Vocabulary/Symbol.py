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

# +---------------------------------------------------------------------------+
# | Related third party imports                                               |
# +---------------------------------------------------------------------------+

# +---------------------------------------------------------------------------+
# | Local application imports                                                 |
# +---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, public_api
from netzob.Model.Vocabulary.AbstractField import AbstractField
from netzob.Common.Utils.TypedList import TypedList
from netzob.Model.Vocabulary.Messages.AbstractMessage import AbstractMessage
from netzob.Model.Vocabulary.Field import Field
from netzob.Model.Vocabulary.Domain.Variables.Memory import Memory


class Symbol(AbstractField):
    """The Symbol class is a main component of the Netzob protocol model.

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

    :var name: The name of the symbol.
    :var description: The description of the symbol.
    :var fields: The sorted list of sub-fields.
    :vartype name: :class:`str`
    :vartype description: :class:`str`
    :vartype fields: a :class:`list` of :class:`Field <netzob.Model.Vocabulary.Field.Field>`


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

    def __init__(self, fields=None, messages=None, name="Symbol"):
        super(Symbol, self).__init__(name)
        self.__messages = TypedList(AbstractMessage)
        if messages is None:
            messages = []
        self.messages = messages
        if fields is None:
            # create a default empty field
            fields = [Field()]
        self.fields = fields

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
        return self.__key()

    @public_api
    def specialize(self, presets=None, fuzz=None, memory=None):
        r"""The :meth:`specialize()` method generates a :class:`bytes` sequence whose
        content follows the symbol definition.

        The specialize() method expects some parameters:

        :param presets: A dictionary of keys:values used to preset
                        (parameterize) fields during symbol
                        specialization. Values in this dictionary will
                        override any field definition, constraints or
                        relationship dependencies. The default value is :const:`None`.
        :param fuzz: A fuzzing configuration used during the specialization process. Values
                     in this configuration will override any field
                     definition, constraints, relationship
                     dependencies or parameterized fields. See
                     :class:`Fuzz <netzob.Fuzzing.Fuzz.Fuzz>`
                     for a complete explanation of its use for fuzzing
                     purpose. The default value is :const:`None`.
        :param memory: A memory used to store variable values during
                       specialization and abstraction of successive
                       symbols, especially to handle inter-symbol
                       relationships. If None, a temporary memory is
                       created by default and used internally during the scope of the
                       specialization process.
        :type presets: ~typing.Dict[~typing.Union[str,~netzob.Model.Vocabulary.Field.Field],
                       ~typing.Union[~bitarray.bitarray,bytes,
                       ~netzob.Model.Vocabulary.Types.AbstractType.AbstractType]],
                       optional
        :type fuzz: :class:`Fuzz <netzob.Fuzzing.Fuzz.Fuzz>`, optional
        :type memory: :class:`Memory <netzob.Model.Vocabulary.Domain.Variables.Memory.Memory>`, optional
        :return: The produced content after specializing the symbol.
        :rtype: :class:`bytes`
        :raises: :class:`GenerationException <netzob.Model.Vocabulary.AbstractField.GenerationException>` if an error occurs while specializing the field.

        The following example shows the :meth:`specialize()` method used for a
        field which contains a String field and a Size field.

        >>> from netzob.all import *
        >>> f1 = Field(domain=String(nbChars=5))
        >>> f0 = Field(domain=Size(f1))
        >>> s = Symbol(fields=[f0, f1])
        >>> result = s.specialize()
        >>> result[0]
        5
        >>> len(result)
        6

        **Parameterized specialization of field values** (:attr:`presets` parameter)

        It is possible to preset (parameterize) fields during symbol
        specialization, through a dict passed in the :attr:`presets`
        parameter of the :meth:`~netzob.Model.Vocabulary.Symbol.specialize`
        method. Values in this dictionary will override any field
        definition, constraints or relationship dependencies.

        The presets dictionary accepts a sequence of keys and values,
        where keys correspond to the fields in the symbol that we want
        to override, and values correspond to the overriding
        content. Keys are either expressed as :class:`Field
        <netzob.Model.Vocabulary.Field.Field>` objects or strings
        containing field accessors when field names are used (such as
        in ``f = Field(name="udp.dport")``). Values are either
        expressed as :class:`bitarray <bitarray.bitarray>` (as it is
        the internal type for variables in the Netzob library), as
        :class:`bytes` or in the type of the overridden field
        variable.

        The following code shows the definition of a simplified UDP
        header that will be later used as base example. This UDP
        header is made of one named field containing a destination
        port, and a named field containing a payload:

        >>> from netzob.all import *
        >>> f_dport = Field(name="udp.dport", domain=Integer(unitSize=UnitSize.SIZE_8))
        >>> f_payload = Field(name="udp.payload", domain=Raw(nbBytes=2))
        >>> symbol_udp = Symbol(name="udp", fields=[f_dport, f_payload])

        The three following codes show the same way to express the
        parameterized **values** during specialization of the
        ``udp_dport`` and ``udp_payload`` fields:

        >>> presets = {}
        >>> presets["udp.dport"] = 11              # udp.dport expects an int or an Integer
        >>> presets["udp.payload"] = b"\xaa\xbb"   # udp.payload expects a bytes object or a Raw object
        >>> symbol_udp.specialize(presets=presets)
        b'\x0b\xaa\xbb'

        >>> presets = {}
        >>> presets["udp.dport"] = uint16(11)        # udp.dport expects an int or an Integer
        >>> presets["udp.payload"] = Raw(b"\xaa\xbb") # udp.payload expects a bytes object or a Raw object
        >>> symbol_udp.specialize(presets=presets)
        b'\x00\x0b\xaa\xbb'

        >>> presets = {}
        >>> presets["udp.dport"] = bitarray('00001011', endian='big')
        >>> presets["udp.payload"] = bitarray('1010101010111011', endian='big')
        >>> symbol_udp.specialize(presets=presets)
        b'\x0b\xaa\xbb'

        The previous example shows the use of BitArray as dict
        values. BitArray are always permitted for any parameterized
        field, as it is the internal type for variables in the Netzob
        library.

        The following example shows the same way to express the
        parameterized **keys** during specialization of the fields
        ``udp_dport`` and ``udp_payload``:

        >>> symbol_udp.specialize(presets={f_dport: 11, f_payload: b"\xaa\xbb"})
        b'\x0b\xaa\xbb'
        >>> symbol_udp.specialize(presets={"udp.dport": 11, "udp.payload": b"\xaa\xbb"})
        b'\x0b\xaa\xbb'


        A preset value bypasses all the constraint checks on your field definition.
        In the following example, it can be used to bypass a size field definition.

        >>> from netzob.all import *
        >>> f1 = Field()
        >>> f2 = Field(domain=Raw(nbBytes=(10,15)))
        >>> f1.domain = Size(f2)
        >>> s = Symbol(fields=[f1, f2])
        >>> presetValues = {f1: bitarray('11111111')}
        >>> s.specialize(presets = presetValues)[0]
        255


        **Field Fuzzing**

        It is possible to fuzz fields during symbol specialization,
        through the :attr:`fuzz` parameter of the
        :meth:`~netzob.Model.Vocabulary.Symbol.specialize`
        method. Values in this parameter will override any field
        definition, constraints, relationship dependencies or
        parameterized values.

        For more information regarding the expected :attr:`fuzz`
        parameter content, see the class :class:`Fuzz
        <netzob.Fuzzing.Fuzz.Fuzz>` class.

        """

        from netzob.Model.Vocabulary.Domain.Specializer.MessageSpecializer import MessageSpecializer
        msg = MessageSpecializer(presets=presets, fuzz=fuzz, memory=memory)
        spePath = msg.specializeSymbol(self)

        if spePath is not None:
            return spePath.generatedContent.tobytes()

    @public_api
    def count(self, presets=None, fuzz=None):
        r"""The :meth:`count` method computes the expected number of unique
        messages produced, considering the initial symbol model, the
        preset fields and the fuzzed fields.

        The :meth:`count` method expects the same parameters as the :meth:`specialize` method:

        :param presets: A dictionary of keys:values used to preset
                        (parameterize) fields during symbol
                        specialization. Values in this dictionary will
                        override any field definition, constraints or
                        relationship dependencies. The default value is :const:`None`.
        :param fuzz: A fuzzing configuration used during the specialization process. Values
                     in this configuration will override any field
                     definition, constraints, relationship
                     dependencies or parameterized fields. See
                     :class:`Fuzz <netzob.Fuzzing.Fuzz.Fuzz>`
                     for a complete explanation of its use for fuzzing
                     purpose. The default value is :const:`None`.
        :type presets: ~typing.Dict[~typing.Union[str,~netzob.Model.Vocabulary.Field.Field],
                       ~typing.Union[~bitarray.bitarray,bytes,
                       ~netzob.Model.Vocabulary.Types.AbstractType.AbstractType]],
                       optional
        :type fuzz: :class:`Fuzz <netzob.Fuzzing.Fuzz.Fuzz>`, optional
        :return: The number of unique values the symbol specialization can produce.
        :rtype: a :class:`int`

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
        >>> symbol.count()
        62324736
        >>>
        >>> # Specify a preset for field 'f3'
        >>> presetValues = {f3: bitarray('11111111')}
        >>>
        >>> symbol.count(presets=presetValues)
        243456
        >>>
        >>> # Specify a fuzz configuration for field 'f2'
        >>> fuzz = Fuzz()
        >>> fuzz.set(f2, generator='determinist')
        >>>
        >>> symbol.count(presets=presetValues, fuzz=fuzz)
        27579

        """

        count = 1
        for field in self.fields:
            if presets is not None and field in presets.keys():
                pass
            else:
                count *= field.count(presets=presets, fuzz=fuzz)
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
        field = self.getField(field_name)
        if field is None:
            raise KeyError("Field {} has not been found in {}"
                           .format(field_name, self))
        return field


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
    >>> presets = {'eth.payload': b"PAYLOAD"}
    >>> d = Symbol.abstract(symbol.specialize(presets=presets), [symbol])[1]
    >>> for k in presets:
    ...    assert d[k] == presets[k]


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

    >>> AbstractField.abstract(data, [arp_ip_symbol])
    (arp.ip, OrderedDict([('arp.hrd', b'\x00\x01'), ('arp.pro', b'\x08\x00'), ('arp.hln', b'\x06'), ('arp.pln', b'\x04'), ('arp.op', b'\x00\x02'), ('arp.sha', b'\x00"MVM\xac'), ('arp.spa', b'\xc0\xa8\xc8\xab'), ('arp.tha', b'\x84\x8fi\xc9(\x91'), ('arp.tpa', b'\xc0\xa8\xc8\xe2')]))


    """
