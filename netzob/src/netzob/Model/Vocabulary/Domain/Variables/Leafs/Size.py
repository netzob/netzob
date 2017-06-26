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
from bitarray import bitarray

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger
from netzob.Model.Vocabulary.Domain.Variables.Leafs.AbstractRelationVariableLeaf import AbstractRelationVariableLeaf
from netzob.Model.Vocabulary.AbstractField import AbstractField
from netzob.Model.Vocabulary.Types.String import String
from netzob.Model.Vocabulary.Types.AbstractType import AbstractType, Endianness, Sign, UnitSize
from netzob.Model.Vocabulary.Types.TypeConverter import TypeConverter
from netzob.Model.Vocabulary.Types.BitArray import BitArray
from netzob.Model.Vocabulary.Types.Raw import Raw
from netzob.Model.Vocabulary.Types.Integer import Integer
from netzob.Model.Vocabulary.Domain.Variables.Leafs.Data import Data
from netzob.Model.Vocabulary.Domain.GenericPath import GenericPath
from netzob.Model.Vocabulary.Domain.Specializer.SpecializingPath import SpecializingPath
from netzob.Model.Vocabulary.Domain.Parser.ParsingPath import ParsingPath


@NetzobLogger
class Size(AbstractRelationVariableLeaf):
    r"""The Size class is a variable which content is the size of another field value.

    Netzob can define a field so that its value is equal to the
    size of another field, or group of fields (potentially including
    itself).

    The Size constructor expects some parameters:

    :param targets: The targeted fields of the relationship.
    :param dataType: Specify that the produced value should be
                     represented according to this dataType. If None, default
                     value is Raw(nbBytes=1).
    :param factor: Specify that the initial size value (always
                       expressed in bits) should be divided by this
                       factor. For example, to express a size in bytes,
                       the factor should be 1./8.
    :param offset: Specify that the final size value
                       should be shifted according to the offset value.
    :param name: The name of the Value variable. If None, the name
                     will be generated.
    :type targets: a :class:`list` of :class:`AbstractField <netzob.Model.Vocabulary.AbstractField>`, required
    :type dataType: :class:`AbstractType <netzob.Model.Vocabulary.Types.AbstractType>`, optional
    :type factor: :class:`int`, optional
    :type offset: :class:`int`, optional
    :type name: :class:`str`, optional


    The following example shows how to define a size field with an
    String dataType:

    >>> from netzob.all import *
    >>> f0 = Field(String(nbChars=(1,10)))
    >>> f1 = Field(String(";"))
    >>> f2 = Field(Size([f0, f1], dataType=String(nbChars=2), factor=1./8, offset=16))
    >>> s  = Symbol(fields=[f0, f1, f2])

    In this example, the field *f2* is a size field where its value is
    equal to the size of the concatenated values of fields *f0* and
    *f1*. The *dataType* parameter specifies that the produced value
    should be represented as a String string. The *factor* parameter
    specifies that the initial size value (always expressed in bits)
    should be divided by 8 (in order to retrieve the amount of
    bytes). The *offset* parameter specifies that the final size value
    should be computed minus 16 bytes.

    The following example shows how to define a size field so that its
    value depends on a list of non-consecutive fields:

    >>> f1 = Field(String("="))
    >>> f2 = Field(String("#"))
    >>> f4 = Field(String("%"))
    >>> f5 = Field(Raw(b"_"))
    >>> f3 = Field(Size([f1, f2, f4, f5]))
    >>> s  = Symbol(fields=[f1, f2, f3, f4, f5])
    >>> print(repr(s.specialize()))
    b'=#\x04%_'

    In the following example, a size field is declared after its field.

    >>> f0 = Field(String(nbChars=(1,10)))
    >>> f1 = Field(String(";"))
    >>> f2 = Field(Size(f0))
    >>> s  = Symbol(fields=[f0, f1, f2])
    >>> msg1  = RawMessage(b"netzob;\x06")
    >>> mp = MessageParser()
    >>> print(mp.parseMessage(msg1, s))
    [bitarray('011011100110010101110100011110100110111101100010'), bitarray('00111011'), bitarray('00000110')]

    In the following example, a size field is declared after its
    targeted field. A message that does not correspond to the expected
    model is then parsed, thus creating an exception:

    >>> msg2  = RawMessage(b"netzob;\x03")
    >>> mp = MessageParser()
    >>> print(mp.parseMessage(msg2, s))  # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
      ...
    InvalidParsingPathException: No parsing path returned while parsing 'b'netzob;\x03''


    In the following example, a size field is declared before the
    targeted field:

    >>> f2 = Field(String(nbChars=(1,10)), name="f2")
    >>> f1 = Field(String(";"), name="f1", )
    >>> f0 = Field(Size(f2), name="f0")
    >>> s  = Symbol(fields=[f0, f1, f2])

    >>> msg1  = RawMessage(b"\x06;netzob")
    >>> mp = MessageParser()
    >>> print(mp.parseMessage(msg1, s))
    [bitarray('00000110'), bitarray('00111011'), bitarray('011011100110010101110100011110100110111101100010')]

    In the following example, a size field is declared before its
    targeted field. A message that does not correspond to the expected model is
    then parsed, thus creating an exception:

    >>> msg2  = RawMessage(b"\x03;netzob")
    >>> mp = MessageParser()
    >>> print(mp.parseMessage(msg2, s))  # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
      ...
    InvalidParsingPathException: No parsing path returned while parsing 'b'\x03;netzob''


    **Size field with fields and variables as target**

    The following examples show the specialization process of a Size
    field whose targets are both fields and variables:

    >>> d = Data(String(nbChars=20))
    >>> f0 = Field(domain=d)
    >>> f1 = Field(String(";"))
    >>> f2 = Field(Size([d, f1]))
    >>> s = Symbol(fields=[f0, f1, f2])
    >>> res = s.specialize()
    >>> b'\x15' in res
    True

    >>> d = Data(String(nbChars=20))
    >>> f2 = Field(domain=d)
    >>> f1 = Field(String(";"))
    >>> f0 = Field(Size([f1, d]))
    >>> s = Symbol(fields=[f0, f1, f2])
    >>> res = s.specialize()
    >>> b'\x15' in res
    True


    **Size field specialization**

    The following examples show the specialization process of a Size
    field:
    
    >>> f0 = Field(String(nbChars=20))
    >>> f1 = Field(String(";"))
    >>> f2 = Field(Size(f0))
    >>> s = Symbol(fields=[f0, f1, f2])
    >>> res = s.specialize()
    >>> b'\x14' in res
    True

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
    >>> b"CMDauthentify#\x11" in s.specialize()
    True

    The following example shows a real example with an IP header with
    two Size fields:

    >>> # Fields
    >>> ip_ver      = Field(name='Version', domain=BitArray(value=bitarray('0100')))
    >>> ip_ihl      = Field(name='Header length', domain=BitArray(bitarray('0000')))
    >>> ip_tos      = Field(name='TOS', domain=Data(dataType=BitArray(nbBits=8),
    ...                     originalValue=bitarray('00000000'), svas=SVAS.PERSISTENT))
    >>> ip_tot_len  = Field(name='Total length', domain=BitArray(bitarray('0000000000000000')))
    >>> ip_id       = Field(name='Identification number', domain=BitArray(nbBits=16))
    >>> ip_flags    = Field(name='Flags', domain=Data(dataType=BitArray(nbBits=3),
    ...                     originalValue=bitarray('000'), svas=SVAS.PERSISTENT))
    >>> ip_frag_off = Field(name='Fragment offset',
    ...                     domain=Data(dataType=BitArray(nbBits=13),
    ...                     originalValue=bitarray('0000000000000'), svas=SVAS.PERSISTENT))
    >>> ip_ttl      = Field(name='TTL', domain=Data(dataType=BitArray(nbBits=8),
    ...                     originalValue=bitarray('10000000'), svas=SVAS.PERSISTENT))
    >>> ip_proto    = Field(name='Protocol',
    ...                     domain=Integer(value=6, unitSize=UnitSize.SIZE_8,
    ...                                    endianness=Endianness.BIG,
    ...                                    sign=Sign.UNSIGNED))
    >>> ip_checksum = Field(name='Checksum', domain=BitArray(bitarray('0000000000000000')))
    >>> ip_saddr    = Field(name='Source address', domain=IPv4("127.0.0.1"))
    >>> ip_daddr    = Field(name='Destination address', domain=IPv4("127.0.0.1"))
    >>> ip_payload  = Field(name='Payload', domain=BitArray(bitarray('0000000000000000')))
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
    >>> data = packet.specialize()
    >>> repr(hex(data[0]))
    ... # This corresponds to the first octect of the IP layer. '5' means 5*32 bits,
    ... # which is the size of the default IP header.
    "'0x45'"
    >>> repr(hex(data[3]))
    ... # This corresponds to the third octect of the IP layer. '0x16' means 22 octets,
    ... # which is the size of the default IP header + 2 octets of payload.
    "'0x16'"

    """

    def __init__(self,
                 targets,
                 dataType=None,
                 factor=1./8,
                 offset=0,
                 name=None):
        super(Size, self).__init__(self.__class__.__name__, targets=targets, name=name)
        if dataType is None:
            dataType = Raw(nbBytes=1)
        self.dataType = dataType
        self.factor = factor
        self.offset = offset

    def __key(self):
        return (self.dataType, self.factor, self.offset)

    def __eq__(x, y):
        try:
            return x.__key() == y.__key()
        except:
            return False

    def __hash__(self):
        return hash(self.__key())

    @typeCheck(GenericPath)
    def computeExpectedValue(self, parsingPath):
        self._logger.debug("Compute expected value for Size variable")

        # first checks the pointed fields all have a value
        hasNeededData = True
        size = 0
        remainingVariables = []

        for variable in self.targets:

            if variable == self:
                remainingVariables.append(variable)
            else:

                # Retrieve the size of the targeted variable, if it not a Data and has a fixed size
                if not isinstance(variable, Data):
                    if hasattr(variable, "dataType"):
                        minSize, maxSize = variable.dataType.size
                        if maxSize is not None and minSize == maxSize:
                            size += minSize
                            continue
                        else:
                            raise Exception("The following targeted variable must have a fixed size: {0}".format(variable.name))

                # Else, retrieve its value if it exists
                if parsingPath.isDataAvailableForVariable(variable):
                    remainingVariables.append(variable)
                else:
                    self._logger.debug("Cannot compute the relation, because the following target variable has no value: '{0}'".format(variable))
                    hasNeededData = False
                    break

        if not hasNeededData:
            raise Exception("Expected value cannot be computed, some dependencies are missing for domain {0}".format(self))

        for variable in remainingVariables:

            # Retrieve variable value
            if variable is self:
                value = self.dataType.generate()
            else:
                value = parsingPath.getDataAssignedToVariable(variable)

            if value is None:
                break

            # Retrieve length of variable value
            size += len(value)

        size = int(size * self.factor + self.offset)
        size_raw = TypeConverter.convert(size,
                                         Integer,
                                         Raw,
                                         src_unitSize=self.dataType.unitSize,
                                         dst_unitSize=self.dataType.unitSize,
                                         src_sign=self.dataType.sign,
                                         dst_sign=self.dataType.sign)
        b = TypeConverter.convert(size_raw, Raw, BitArray)

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
        """The datatype used to encode the result of the computed size.

        :type: :class:`AbstractType <netzob.Model.Vocabulary.Types.AbstractType.AbstractType>`
        """

        return self.__dataType

    @dataType.setter
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
