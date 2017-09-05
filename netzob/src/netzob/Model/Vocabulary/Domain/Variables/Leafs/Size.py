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
    r"""The Size class is a variable whose content is the size of other field values.

    It is possible to define a field so that its value is equal to the
    size of another field, or group of fields (potentially including
    itself).

    By default, the computed size expresses an amount of bytes. It is
    possible to change this behavior by using the parameters ``factor``
    and ``offset``.

    The Size constructor expects some parameters:

    :param targets: The targeted fields of the relationship.
    :param dataType: Specify that the produced value should be
                     represented according to this dataType. If None, default
                     value is Raw(nbBytes=1).
    :param factor: Specify that the initial size value (always
                   expressed in bits) should be divided by this
                   factor. The default value is 1./8. For example, to express a size in bytes,
                   the factor should be ``1./8``, whereas to express a size in bits, the factor should be ``1.``.
    :param offset: Specify that an offset value should be added to
                   the final size value (after applying the factor
                   parameter). The default value is 0.
    :param name: The name of the variable. If None, the name
                 will be generated.
    :type targets: a :class:`list` of :class:`Field <netzob.Model.Vocabulary.Field>`, required
    :type dataType: :class:`AbstractType <netzob.Model.Vocabulary.Types.AbstractType>`, optional
    :type factor: :class:`float`, optional
    :type offset: :class:`int`, optional
    :type name: :class:`str`, optional


    The Size class provides the following public variables:

    :var dataType: The type of the data.
    :var factor: Defines the multiplication factor to apply on the targeted length.
    :var offset: Defines the offset to apply on the computed length.
    :vartype dataType: :class:`AbstractType <netzob.Model.Vocabulary.Types.AbstractType>`
    :vartype factor: :type: :class:`float`
    :vartype offset: :type: :class:`int`


    The following example shows how to define a size field with a
    Raw dataType:

    >>> from netzob.all import *
    >>> f0 = Field(String(nbChars=10))
    >>> f1 = Field(String(";"))
    >>> f2 = Field(Size([f0], dataType=Raw(nbBytes=1)))
    >>> f = Field([f0, f1, f2])
    >>> data = f.specialize()
    >>> data[-1] == 10
    True

    The following example shows how to define a size field with a
    Raw dataType, along with specifying the ``factor`` and ``offset`` parameters.

    >>> from netzob.all import *
    >>> f0 = Field(String(nbChars=(4,10)))
    >>> f1 = Field(String(";"))
    >>> f2 = Field(Size([f0, f1], dataType=Raw(nbBytes=1), factor=1./8, offset=4))
    >>> f = Field([f0, f1, f2])
    >>> data = f.specialize()
    >>> data[-1] > (4*8*1./8 + 4) # == 4 bytes minimum * 8 bits * a factor of 1./8 + an offset of 4
    True

    In this example, the field *f2* is a size field where its value is
    equal to the size of the concatenated values of fields *f0* and
    *f1*. The *dataType* parameter specifies that the produced value
    should be represented as a ``Raw``. The *factor* parameter
    specifies that the initial size value (always expressed in bits)
    should be divided by 8 (in order to retrieve the amount of
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
    >>> f.specialize()
    b'=#\x04%_'

    In the following example, a size field is declared after its
    targeted field. This shows that the field order does not impact
    the relationship computations.

    >>> from netzob.all import *
    >>> f0 = Field(String(nbChars=(1,4)), name='f0')
    >>> f1 = Field(String(";"), name='f1')
    >>> f2 = Field(Size(f0), name='f2')
    >>> f = Field([f0, f1, f2])
    >>> 3 <= len(f.specialize()) <= 6
    True


    .. ifconfig:: scope in ('netzob')

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
       >>> Symbol.abstract(data, [s])  # doctest: +IGNORE_EXCEPTION_DETAIL
       (Unknown Symbol b'john;\x03', OrderedDict())

    In the following example, a size field is declared before the
    targeted field:

    >>> from netzob.all import *
    >>> f2 = Field(String(nbChars=(1,4)), name="f2")
    >>> f1 = Field(String(";"), name="f1", )
    >>> f0 = Field(Size(f2), name="f0")
    >>> f = Field([f0, f1, f2])
    >>> 3 <= len(f.specialize()) <= 6
    True


    .. ifconfig:: scope in ('netzob')

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
       >>> Symbol.abstract(data, [s])  # doctest: +IGNORE_EXCEPTION_DETAIL
       (Unknown Symbol b'\x03;john', OrderedDict())


    **Size field with fields and variables as target**

    The following examples show the specialization process of a Size
    field whose targets are both fields and variables:

    >>> from netzob.all import *
    >>> d = Data(String(nbChars=20))
    >>> f0 = Field(domain=d)
    >>> f1 = Field(String(";"))
    >>> f2 = Field(Size([d, f1]))
    >>> f = Field([f0, f1, f2])
    >>> res = f.specialize()
    >>> b'\x15' in res
    True

    >>> from netzob.all import *
    >>> d = Data(String(nbChars=20))
    >>> f2 = Field(domain=d)
    >>> f1 = Field(String(";"))
    >>> f0 = Field(Size([f1, d]))
    >>> f = Field([f0, f1, f2])
    >>> res = f.specialize()
    >>> b'\x15' in res
    True

    """

    def __init__(self,
                 targets,
                 dataType=None,
                 factor=1./8,
                 offset=0,
                 name=None):
        super(Size, self).__init__(self.__class__.__name__, dataType=dataType, targets=targets, name=name)
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
                if parsingPath.hasData(variable):
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
                value = parsingPath.getData(variable)

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
        """
        Property (getter/setter).
        The datatype used to encode the result of the computed size.

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
        """
        Property (getter/setter).
        Defines the multiplication factor to apply on the targeted length
        (in bits).

        :type: :class:`float`
        """
        return self.__factor

    @factor.setter
    @typeCheck(float)
    def factor(self, factor):
        if factor is None:
            raise TypeError("Factor cannot be None, use 1.0 for the identity.")
        self.__factor = factor

    @property
    def offset(self):
        """
        Property (getter/setter).
        Defines the offset to apply on the computed length.
        computed size = (factor*size(targetField)+offset)

        :type: :class:`int`
        """
        return self.__offset

    @offset.setter
    @typeCheck(int)
    def offset(self, offset):
        if offset is None:
            raise TypeError(
                "Offset cannot be None, use 0 if no offset should be applied.")
        self.__offset = offset

    def _test(self):
        r"""
        The following example shows a real example with an IP header with
        two Size fields:

        >>> from netzob.all import *
        >>> # Fields
        >>> ip_ver      = Field(name='Version', domain=BitArray(value=bitarray('0100')))
        >>> ip_ihl      = Field(name='Header length', domain=BitArray('0000'))
        >>> ip_tos      = Field(name='TOS', domain=Data(dataType=BitArray(nbBits=8),
        ...                     originalValue=bitarray('00000000'), svas=SVAS.PERSISTENT))
        >>> ip_tot_len  = Field(name='Total length', domain=BitArray('0000000000000000'))
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
        >>> ip_checksum = Field(name='Checksum', domain=BitArray('0000000000000000'))
        >>> ip_saddr    = Field(name='Source address', domain=IPv4("127.0.0.1"))
        >>> ip_daddr    = Field(name='Destination address', domain=IPv4("127.0.0.1"))
        >>> ip_payload  = Field(name='Payload', domain=BitArray('0000000000000000'))
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

        The following examples show the specialization process of a Size
        field:

        >>> from netzob.all import *
        >>> f0 = Field(String(nbChars=20))
        >>> f1 = Field(String(";"))
        >>> f2 = Field(Size(f0))
        >>> f = Field([f0, f1, f2])
        >>> res = f.specialize()
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
        >>> b"CMDauthentify#\x11" in s.specialize()
        True

        """
