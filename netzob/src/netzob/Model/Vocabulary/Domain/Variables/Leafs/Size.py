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

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger, public_api
from netzob.Model.Vocabulary.Domain.Variables.Leafs.AbstractVariableLeaf import AbstractVariableLeaf
from netzob.Model.Vocabulary.Domain.Variables.Leafs.AbstractRelationVariableLeaf import AbstractRelationVariableLeaf, RelationDependencyException
from netzob.Model.Vocabulary.Domain.Variables.Nodes.AbstractVariableNode import AbstractVariableNode
from netzob.Model.Vocabulary.Domain.Variables.Nodes.Agg import Agg
from netzob.Model.Vocabulary.Types.AbstractType import AbstractType
from netzob.Model.Vocabulary.Types.TypeConverter import TypeConverter
from netzob.Model.Vocabulary.Types.BitArray import BitArray
from netzob.Model.Vocabulary.Types.Raw import Raw
from netzob.Model.Vocabulary.Types.Integer import Integer, uint8
from netzob.Model.Vocabulary.Domain.GenericPath import GenericPath


@NetzobLogger
class Size(AbstractRelationVariableLeaf):
    r"""The Size class is a variable whose content is the size of other field values.

    It is possible to define a field so that its value is equal to the
    size of another field, or group of fields (potentially including
    itself).

    By default, the computed size expresses an amount of bytes. It is
    possible to change this behavior by using the ``factor``
    and ``offset`` parameters.

    The Size constructor expects some parameters:

    :param targets: The targeted objects of the relationship. If a :class:`~netzob.Model.Vocabulary.Field.Field` is provided, it will be normalized by the associated :class:`Variable <netzob.Model.Vocabulary.Domain.Variables.AbstractVariable.AbstractVariable>`.
    :param dataType: Specify that the produced value should be
                     represented according to this dataType. If None, default
                     value is Raw(nbBytes=1).
    :param factor: Specify that the initial size value (always
                   expressed in bits) should be multiplied by this
                   factor. The default value is ``1.0/8``. For example, to
                   express a size in bytes, the factor should be ``1.0/8``,
                   whereas to express a size in bits, the factor should be
                   ``1.0``.
    :param offset: Specify that an offset value should be added to
                   the final size value (after applying the factor
                   parameter). The default value is 0.
    :param name: The name of the variable. If None, the name
                 will be generated.
    :type targets: a :class:`~netzob.Model.Vocabulary.Field.Field` or a :class:`Variable <netzob.Model.Vocabulary.Domain.Variables.AbstractVariable.AbstractVariable>` or a :class:`list` of :class:`~netzob.Model.Vocabulary.Field.Field` or :class:`Variable <netzob.Model.Vocabulary.Domain.Variables.AbstractVariable.AbstractVariable>`, required
    :type dataType: :class:`~netzob.Model.Vocabulary.Types.AbstractType.AbstractType`, optional
    :type factor: :class:`float`, optional
    :type offset: :class:`int`, optional
    :type name: :class:`str`, optional


    The Size class provides the following public variables:

    :var targets: The list of variables that are required before computing
                   the value of this relation
    :var dataType: The type of the data.
    :var factor: Defines the multiplication factor to apply to the targeted
                 length.
    :var offset: Defines the offset to apply to the computed length.
    :vartype targets: a list of
                      :class:`Variable <netzob.Model.Vocabulary.Domain.Variables.AbstractVariable.AbstractVariable>`
    :vartype dataType: :class:`~netzob.Model.Vocabulary.Types.AbstractType.AbstractType`
    :vartype factor: :class:`float`
    :vartype offset: :class:`int`


    The following example shows how to define a size field with a
    Raw dataType:

    >>> from netzob.all import *
    >>> f0 = Field(String(nbChars=10))
    >>> f1 = Field(String(";"))
    >>> f2 = Field(Size([f0], dataType=Raw(nbBytes=1)))
    >>> f = Field([f0, f1, f2])
    >>> data = next(f.specialize())
    >>> data[-1] == 10
    True

    The following example shows how to define a size field with a
    Raw dataType, along with specifying the ``factor`` and ``offset`` parameters.

    >>> from netzob.all import *
    >>> f0 = Field(String(nbChars=(4,10)))
    >>> f1 = Field(String(";"))
    >>> f2 = Field(Size([f0, f1], dataType=Raw(nbBytes=1), factor=1./8, offset=4))
    >>> f = Field([f0, f1, f2])
    >>> data = next(f.specialize())
    >>> data[-1] > (4*8*1./8 + 4) # == 4 bytes minimum * 8 bits * a factor of 1./8 + an offset of 4
    True

    In this example, the *f2* field is a size field where its value is
    equal to the size of the concatenated values of fields *f0* and
    *f1*. The *dataType* parameter specifies that the produced value
    should be represented as a ``Raw``. The *factor* parameter
    specifies that the initial size value (always expressed in bits)
    should be multiplied by ``1.0/8`` (in order to retrieve the amount of
    bytes). The *offset* parameter specifies that the final size value
    should be computed by adding 4 bytes.

    The following example shows how to define a size field so that its
    value depends on a list of non-consecutive fields:

    >>> from netzob.all import *
    >>> f1 = Field(String("="))
    >>> f2 = Field(String("#"))
    >>> f4 = Field(String("%"))
    >>> f5 = Field(Raw(b"_"))
    >>> f3 = Field(Size([f1, f2, f4, f5]))
    >>> f = Field([f1, f2, f3, f4, f5])
    >>> next(f.specialize())
    b'=#\x04%_'

    In the following example, a size field is declared after its
    targeted field. This shows that the field order does not impact
    the relationship computations.

    >>> from netzob.all import *
    >>> f0 = Field(String(nbChars=(1,4)), name='f0')
    >>> f1 = Field(String(";"), name='f1')
    >>> f2 = Field(Size(f0), name='f2')
    >>> f = Field([f0, f1, f2])
    >>> 3 <= len(next(f.specialize())) <= 6
    True


    In the following example, a size field is declared before the
    targeted field:

    >>> from netzob.all import *
    >>> f2 = Field(String(nbChars=(1,4)), name="f2")
    >>> f1 = Field(String(";"), name="f1", )
    >>> f0 = Field(Size(f2), name="f0")
    >>> f = Field([f0, f1, f2])
    >>> d = next(f.specialize())
    >>> 3 <= len(d) <= 6
    True


    **Size field with fields and variables as target**

    The following examples show the specialization process of a Size
    field whose targets are both fields and variables:

    >>> from netzob.all import *
    >>> d = Data(String(nbChars=20))
    >>> f0 = Field(domain=d)
    >>> f1 = Field(String(";"))
    >>> f2 = Field(Size([d, f1]))
    >>> f = Field([f0, f1, f2])
    >>> res = next(f.specialize())
    >>> b'\x15' in res
    True

    >>> from netzob.all import *
    >>> d = Data(String(nbChars=20))
    >>> f2 = Field(domain=d)
    >>> f1 = Field(String(";"))
    >>> f0 = Field(Size([f1, d]))
    >>> f = Field([f0, f1, f2])
    >>> res = next(f.specialize())
    >>> b'\x15' in res
    True


    **Size field which targets itself**

    The following example shows a Size field whose targets contain
    itsef. In such case, the domain datatype (here, an ``uint16``) is
    used to compute the size of the length field (here, the datatype
    occupies 2 bytes).

    >>> from netzob.all import *
    >>> f0 = Field(uint8(0), name="f0")
    >>> f1 = Field(uint8(0), name="f1")
    >>> f2 = Field(name="len")
    >>> f3 = Field(uint32(0), name="f3")
    >>> f4 = Field(Raw(nbBytes=(0,28)), name="f4")
    >>> f2.domain = Size([f0, f1, f2, f3, f4], dataType=uint16())
    >>> symbol = Symbol([f0, f1, f2, f3, f4])
    >>> data = next(symbol.specialize())
    >>> data
    b'\x00\x00\x00\x15\x00\x00\x00\x00z\x12\x10\xfe\x9a$)L\xc4\xbfL91'
    >>> symbol.abstract(data)
    OrderedDict([('f0', b'\x00'), ('f1', b'\x00'), ('len', b'\x00\x15'), ('f3', b'\x00\x00\x00\x00'), ('f4', b'z\x12\x10\xfe\x9a$)L\xc4\xbfL91')])

    """

    @public_api
    def __init__(self,
                 targets,
                 dataType=None,
                 factor=1. / 8,
                 offset=0,
                 name=None):

        if dataType is None:
            dataType = uint8()
        elif not isinstance(dataType, Integer):
            max_buffer_size = 1 << dataType.size[1]
            unitsize = AbstractType.computeUnitSize(max_buffer_size)
            dataType.unitSize = unitsize

        super(Size, self).__init__(self.__class__.__name__, dataType=dataType, targets=targets, name=name)
        self.factor = factor
        self.offset = offset

    @public_api
    def copy(self, map_objects=None):
        """Copy the current object as well as all its dependencies.

        :return: A new object of the same type.
        :rtype: :class:`Size <netzob.Model.Vocabulary.Domain.Variables.Leafs.Size.Size>`

        """
        if map_objects is None:
            map_objects = {}
        if self in map_objects:
            return map_objects[self]

        new_size = Size([], dataType=self.dataType, factor=self.factor, offset=self.offset, name=self.name)
        map_objects[self] = new_size

        new_targets = []
        for target in self.targets:
            if target in map_objects.keys():
                new_targets.append(map_objects[target])
            else:
                new_target = target.copy(map_objects)
                new_targets.append(new_target)

        new_size.targets = new_targets
        return new_size

    def __computeExpectedValue_stage1(self, targets, parsingPath, remainingVariables, preset=None):
        """
        Compute the total size of targets
        """
        size = 0

        from netzob.Fuzzing.Mutators.DomainMutator import FuzzingMode
        for variable in targets:

            if preset is not None and preset.get(variable) is not None and preset.get(variable).mode == FuzzingMode.FIXED:
                remainingVariables.append(variable)

            elif parsingPath.hasData(variable) or variable is self:
                remainingVariables.append(variable)

            # variable is a leaf
            elif isinstance(variable, AbstractVariableLeaf):
                try:
                    size += variable.getFixedBitSize()
                except ValueError:
                    remainingVariables.append(variable)

            # variable is a node
            elif isinstance(variable, AbstractVariableNode):
                if isinstance(variable, Agg):
                    size += self.__computeExpectedValue_stage1(
                        variable.children, parsingPath, remainingVariables)
                else:
                    error_message = "The following variable has no value: '{}' for field '{}'".format(variable, variable.field)
                    self._logger.debug(error_message)
                    raise RelationDependencyException(error_message, variable)
            else:
                remainingVariables.append(variable)

        return size

    def __computeExpectedValue_stage2(self, parsingPath, remainingVariables):
        """
        Compute the size of remaining variables
        """
        size = 0

        for variable in remainingVariables:

            # Retrieve variable value
            if variable is self:
                value = self.dataType.generate()
            else:
                if parsingPath.hasData(variable):
                    value = parsingPath.getData(variable)
                else:
                    error_message = "The following variable has no value: '{}' for field '{}'".format(variable, variable.field)
                    self._logger.debug(error_message)
                    raise RelationDependencyException(error_message, variable)

            if value is None:
                break

            # Retrieve length of variable value
            size += len(value)

        return size

    @typeCheck(GenericPath)
    def computeExpectedValue(self, parsingPath, preset=None):
        self._logger.debug("Compute expected value for Size variable '{}' from field '{}'".format(self, self.field))

        # first checks the pointed fields all have a value
        remainingVariables = []

        size = self.__computeExpectedValue_stage1(self.targets, parsingPath, remainingVariables, preset=preset)
        size += self.__computeExpectedValue_stage2(parsingPath, remainingVariables)
        size = int(size * self.factor + self.offset)

        # Check if we can encode the size in the Size field structure
        max_size = (1 << self.dataType.unitSize.value)
        if size > max_size:
            error_message = "The computed size (which is '{}') cannot be encoded in the current Size field".format(size)
            if self.field is not None and len(self.field.name) > 0:
                error_message = error_message + " '{}' (which can encode at most a value of '{}').".format(self.field.name, max_size)
            else:
                error_message = error_message + " (which can encode at most a value of '{}').".format(max_size)
            error_message = error_message + " You should consider using a bigger dataType."
            self._logger.debug(error_message)
            raise ValueError(error_message)

        b = TypeConverter.convert(size, Integer, BitArray,
                                  src_unitSize=self.dataType.unitSize,
                                  dst_unitSize=self.dataType.unitSize,
                                  src_sign=self.dataType.sign,
                                  dst_sign=self.dataType.sign,
                                  src_endianness=self.dataType.endianness,
                                  dst_endianness=self.dataType.endianness)

        # add heading '0'
        while len(b) < self.dataType.size[0]:
            b.insert(0, False)

        # in some cases (when unitSize and size are not equal), it may require to delete some '0' in front
        while len(b) > self.dataType.size[1]:
            b.remove(0)

        self._logger.debug("Computed value for {}: '{}'".format(self, b.tobytes()))
        return b

    def __str__(self):
        """The str method."""
        return "Size({0}) - Type:{1}".format(
            str([v.name for v in self.targets]), self.dataType)

    @property
    def dataType(self):
        """
        Property (getter.setter  # type: ignore).
        The datatype used to encode the result of the computed size.

        :type: :class:`AbstractType <netzob.Model.Vocabulary.Types.AbstractType.AbstractType>`
        """
        return self.__dataType

    @dataType.setter  # type: ignore
    @typeCheck(AbstractType)
    def dataType(self, dataType):
        if dataType is None:
            raise TypeError("Datatype cannot be None")
        size = dataType.unitSize
        if size is None:
            raise ValueError(
                "The datatype of a Size field must declare its unitSize")
        self.__dataType = dataType

    @property
    def factor(self):
        """
        Property (getter.setter  # type: ignore).
        Defines the multiplication factor to apply to the targeted length
        (in bits).

        :type: :class:`float`
        """
        return self.__factor

    @factor.setter  # type: ignore
    @typeCheck(float)
    def factor(self, factor):
        if factor is None:
            raise TypeError("Factor cannot be None, use 1.0 for the identity.")
        self.__factor = factor

    @property
    def offset(self):
        """
        Property (getter.setter  # type: ignore).
        Defines the offset to apply to the computed length.
        computed size = (factor*size(targetField)+offset)

        :type: :class:`int`
        """
        return self.__offset

    @offset.setter  # type: ignore
    @typeCheck((int, float))
    def offset(self, offset):
        if offset is None:
            raise TypeError(
                "Offset cannot be None, use 0 if no offset should be applied.")
        self.__offset = offset


def _test_size():
    r"""
    The following example shows a real example with an IP header with
    two Size fields:

    >>> from netzob.all import *
    >>> # Fields
    >>> ip_ver      = Field(name='Version', domain=BitArray(value=bitarray('0100')))
    >>> ip_ihl      = Field(name='Header length', domain=bitarray('0000'))
    >>> ip_tos      = Field(name='TOS', domain=Data(dataType=BitArray('00000000'), scope=Scope.SESSION))
    >>> ip_tot_len  = Field(name='Total length', domain=bitarray('0000000000000000'))
    >>> ip_id       = Field(name='Identification number', domain=BitArray(nbBits=16))
    >>> ip_flags    = Field(name='Flags', domain=Data(dataType=BitArray('000'), scope=Scope.SESSION))
    >>> ip_frag_off = Field(name='Fragment offset',
    ...                     domain=Data(dataType=BitArray('0000000000000'), scope=Scope.SESSION))
    >>> ip_ttl      = Field(name='TTL', domain=Data(dataType=BitArray('10000000'), scope=Scope.SESSION))
    >>> ip_proto    = Field(name='Protocol', domain=uint8be(6))
    >>> ip_checksum = Field(name='Checksum', domain=bitarray('0000000000000000'))
    >>> ip_saddr    = Field(name='Source address', domain=IPv4("127.0.0.1"))
    >>> ip_daddr    = Field(name='Destination address', domain=IPv4("127.0.0.1"))
    >>> ip_payload  = Field(name='Payload', domain=bitarray('0000000000000000'))
    >>> # Domains
    >>> ip_ihl.domain = Size([ip_ver, ip_ihl, ip_tos, ip_tot_len, ip_id, ip_flags,
    ...                       ip_frag_off, ip_ttl, ip_proto, ip_checksum, ip_saddr, ip_daddr],
    ...                      dataType=BitArray(nbBits=4), factor=1./32)
    >>> ip_tot_len.domain = Size([ip_ver, ip_ihl, ip_tos, ip_tot_len, ip_id, ip_flags,
    ...                           ip_frag_off, ip_ttl, ip_proto, ip_checksum, ip_saddr,
    ...                           ip_daddr, ip_payload],
    ...                          dataType=Raw(nbBytes=2), factor=1./8)
    >>> # Symbol
    >>> packet = Symbol(name='IP layer', fields=[
    ...    ip_ver, ip_ihl, ip_tos, ip_tot_len, ip_id, ip_flags, ip_frag_off,
    ...    ip_ttl, ip_proto, ip_checksum, ip_saddr, ip_daddr, ip_payload])
    >>> data = next(packet.specialize())
    >>> hex(data[0])
    ... # This corresponds to the first byte of the IP layer. '5' means 5*32 bits,
    ... # which is the size of the default IP header.
    '0x45'
    >>> hex(data[3])
    ... # This corresponds to the third byte of the IP layer. '0x16' means 22 octets,
    ... # which is the size of the default IP header + 2 octets of payload.
    '0x16'


    The following examples show the specialization process of a Size
    field:

    >>> from netzob.all import *
    >>> f0 = Field(String(nbChars=20))
    >>> f1 = Field(String(";"))
    >>> f2 = Field(Size(f0))
    >>> f = Field([f0, f1, f2])
    >>> res = next(f.specialize())
    >>> b'\x14' in res
    True

    >>> from netzob.all import *
    >>> f0 = Field(String("CMDauthentify"), name="f0")
    >>> f1 = Field(String('#'), name="sep")
    >>> f2 = Field(name="f2")
    >>> f3 = Field(name="size field")
    >>> f4 = Field(Raw(b"\x00\x00\x00\x00"), name="f4")
    >>> f5 = Field(Raw(nbBytes=11))
    >>> f6 = Field(Raw(b'wd'), name="f6")
    >>> f7 = Field(Raw(nbBytes=(0, 1)))
    >>> f3.domain = Size([f4, f5, f6])
    >>> f2.fields = [f3, f4, f5, f6, f7]
    >>> s = Symbol(fields=[f0, f1, f2])
    >>> b"CMDauthentify#\x11" in next(s.specialize())
    True

    # We check that a Size datatype cannot be constant

    >>> f1 = Field(uint8(0))
    >>> f2 = Field(Size([f1], dataType=uint16(0)))
    Traceback (most recent call last):
    ...
    Exception: Relation dataType should not have a constant value: 'Integer(0)'.



    # Example with UDP inner relationships (2 Size fields with a CRC)

    >>> from netzob.all import *
    >>> # UDP header fields
    >>> udp_sport = Field(uint16(), "udp.sport")
    >>> udp_dport = Field(uint16(), "udp.dport")
    >>> udp_length = Field(bitarray('0000000000000000'), "udp.length")
    >>> udp_checksum = Field(bitarray('0000000000000000'), "udp.checksum")
    >>> udp_payload = Field(Raw(), "udp.payload")
    >>>
    >>> udp_header = [udp_sport, udp_dport, udp_length, udp_checksum, udp_payload]
    >>>
    >>> # Update UDP length field
    >>> udp_length.domain = Size(udp_header, dataType=uint16(), factor=1./8)
    >>>
    >>> # Pseudo IP header to compute the UDP checksum
    >>> pseudo_ip_src = Field(IPv4(), "udp.pseudoIP.saddr")
    >>> pseudo_ip_dst = Field(IPv4(), "udp.pseudoIP.daddr")
    >>> pseudo_ip_proto = Field(Raw(b'\x00\x11'), "udp.pseudoIP.proto")
    >>> pseudo_ip_length = Field(Size(udp_header, dataType=uint16(), factor=1./8), "udp.pseudoIP.length")
    >>>
    >>> pseudo_ip_header = Field(name="udp.pseudoIP", isPseudoField=True)
    >>> pseudo_ip_header.fields = [pseudo_ip_src, pseudo_ip_dst, pseudo_ip_proto, pseudo_ip_length]
    >>>
    >>> udp_checksum.domain = InternetChecksum([pseudo_ip_header] + udp_header, dataType=Raw(nbBytes=2, unitSize=UnitSize.SIZE_16))
    >>>
    >>> # UDP symbol
    >>> symbol_udp = Symbol(name="udp", fields=(udp_header + [pseudo_ip_header]))
    >>>
    >>> #
    >>> preset = Preset(symbol_udp)
    >>> preset["udp.payload"] = b"test AAAAAAAA"
    >>> data = next(symbol_udp.specialize(preset))
    >>>
    >>> symbol_udp.abstract(data)  # doctest: +ELLIPSIS
    OrderedDict([('udp.sport', b'...'), ('udp.dport', b'...'), ('udp.length', b'\x00\x15'), ('udp.checksum', b'...'), ('udp.payload', b'test AAAAAAAA')])

    """


def _test_abstraction():
    r"""

    In the following example, a size field is declared after its
    targeted field, and a message that does not correspond to the
    expected model is then parsed. As the data does not match the
    expected symbol, the returned symbol is unknown:

    >>> from netzob.all import *
    >>> f0 = Field(String(nbChars=(1,10)), name='f0')
    >>> f1 = Field(String(";"), name='f1')
    >>> f2 = Field(Size(f0), name='f2')
    >>> s  = Symbol(fields=[f0, f1, f2])
    >>> data = b"john;\x03"
    >>> s.abstract(data)  # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    ...
    netzob.Model.Vocabulary.AbstractField.AbstractionException: With the symbol/field 'Symbol', cannot abstract the data: 'b'john;\x03''. Error: 'No parsing path returned while parsing 'b'john;\x03'''


    In the following example, a size field is declared before its
    targeted field, and a message that does not correspond to the
    expected model is then parsed. As the data does not match the
    expected symbol, the returned symbol is unknown:

    >>> from netzob.all import *
    >>> f2 = Field(String(nbChars=(1,10)), name="f2")
    >>> f1 = Field(String(";"), name="f1", )
    >>> f0 = Field(Size(f2), name="f0")
    >>> s  = Symbol(fields=[f0, f1, f2])
    >>> data = b"\x03;john"
    >>> s.abstract(data)  # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    ...
    netzob.Model.Vocabulary.AbstractField.AbstractionException: With the symbol/field 'Symbol', cannot abstract the data: 'b'\x03;john''. Error: 'No parsing path returned while parsing 'b'\x03;john'''

    """


def _test_size_contains_itself():
    r"""

    >>> from netzob.all import *
    >>> Conf.apply()

    # In big endian

    >>> from netzob.all import *
    >>> f0 = Field(uint8(0), name="f0")
    >>> f1 = Field(uint8(0), name="f1")
    >>> f2 = Field(name="len")
    >>> f3 = Field(uint32(0), name="f3")
    >>> f4 = Field(Raw(nbBytes=(0,28)), name="f4")
    >>> f2.domain = Size([f0, f1, f2, f3, f4], dataType=uint16())
    >>> symbol = Symbol([f0, f1, f2, f3, f4])
    >>> data = next(symbol.specialize())
    >>> data
    b'\x00\x00\x00\x17\x00\x00\x00\x00\x07i\xec\xfb\x8eR\x11\xfa\xa7&\x7f\xb8\x16\xd7G'
    >>> symbol.abstract(data)
    OrderedDict([('f0', b'\x00'), ('f1', b'\x00'), ('len', b'\x00\x17'), ('f3', b'\x00\x00\x00\x00'), ('f4', b'\x07i\xec\xfb\x8eR\x11\xfa\xa7&\x7f\xb8\x16\xd7G')])


    # In little endian

    >>> from netzob.all import *
    >>> f0 = Field(uint8le(0), name="f0")
    >>> f1 = Field(uint8le(0), name="f1")
    >>> f2 = Field(name="len")
    >>> f3 = Field(uint32le(0), name="f3")
    >>> f4 = Field(Raw(nbBytes=(0,28)), name="f4")
    >>> f2.domain = Size([f0, f1, f2, f3, f4], dataType=uint16le())
    >>> symbol = Symbol([f0, f1, f2, f3, f4])
    >>> data = next(symbol.specialize())
    >>> data
    b'\x00\x00\r\x00\x00\x00\x00\x00\x9b\xb9D\xe9z'
    >>> symbol.abstract(data)
    OrderedDict([('f0', b'\x00'), ('f1', b'\x00'), ('len', b'\r\x00'), ('f3', b'\x00\x00\x00\x00'), ('f4', b'\x9b\xb9D\xe9z')])

    """


def _test_size_default_datatype_value():
    r"""

    >>> from netzob.all import *
    >>> f1 = Field(Raw(nbBytes=1000), "F1")
    >>> f2 = Field(Size([f1]), "F2")
    >>> s = Symbol([f1, f2])
    >>> next(s.specialize()) # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    ValueError: The computed size (which is '1000') cannot be encoded in the current Size field 'F2' (which can encode at most a value of '256'). You should consider using a bigger dataType.

    >>> from netzob.all import *
    >>> f1 = Field(Raw(nbBytes=1000), "F1")
    >>> f2 = Field(Size([f1], dataType=uint8be()), "F2")
    >>> s = Symbol([f1, f2])
    >>> next(s.specialize()) # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    ValueError: The computed size (which is '1000') cannot be encoded in the current Size field 'F2' (which can encode at most a value of '256'). You should consider using a bigger dataType.

    >>> from netzob.all import *
    >>> f1 = Field(Raw(nbBytes=1000), "F1")
    >>> f2 = Field(Size([f1], dataType=uint8be(), factor=1./32), "F2")
    >>> s = Symbol([f1, f2])
    >>> len(next(s.specialize()))
    1001

    """
