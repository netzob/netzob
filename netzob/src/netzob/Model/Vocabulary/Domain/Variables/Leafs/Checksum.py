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
#|       - Frédéric Guihéry <frederic.guihery (a) amossys.fr>                |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Standard library imports                                                  |
#+---------------------------------------------------------------------------+
import random
from PyCRC.CRC16 import CRC16 as _CRC16
from PyCRC.CRC16DNP import CRC16DNP as _CRC16DNP
from PyCRC.CRC16Kermit import CRC16Kermit as _CRC16Kermit
from PyCRC.CRC16SICK import CRC16SICK as _CRC16SICK
from PyCRC.CRC32 import CRC32 as _CRC32
from PyCRC.CRCCCITT import CRCCCITT as _CRCCCITT

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+
from bitarray import bitarray
import binascii

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger
from netzob.Model.Vocabulary import partialclass
from netzob.Model.Vocabulary.Domain.Variables.Leafs.AbstractRelationVariableLeaf import AbstractRelationVariableLeaf
from netzob.Model.Vocabulary.AbstractField import AbstractField
from netzob.Model.Vocabulary.Types.HexaString import HexaString
from netzob.Model.Vocabulary.Types.AbstractType import AbstractType, Endianness, Sign, UnitSize
from netzob.Model.Vocabulary.Types.TypeConverter import TypeConverter
from netzob.Model.Vocabulary.Types.BitArray import BitArray
from netzob.Model.Vocabulary.Types.Raw import Raw
from netzob.Model.Vocabulary.Types.Integer import Integer


@NetzobLogger
class Checksum(AbstractRelationVariableLeaf):
    r"""The Checksum class implements a list of checksum relationships between fields.

    The Checksum constructor expects some parameters:

    :param targets: The targeted fields of the relationship.
    :param checksumName: The underlying checksum function (see below
                         for the list of supported functions). Default
                         value is CRC16.
    :param dataType: Specify that the produced value should be
                     represented according to this dataType.
                     If None, default value is Raw(nbBytes=2), as generally
                     the checksum is on 16bits.
    :param name: The name of the Value variable. If None, the name will be generated.
    :type targets: a :class:`list` of :class:`AbstractField <netzob.Model.Vocabulary.AbstractField>`, required
    :type checksumName: :class:`str`, optional
    :type dataType: :class:`AbstractType <netzob.Model.Vocabulary.Types.AbstractType>`, optional
    :type name: :class:`str`, optional

    Supported checksum functions are:

    * CRC16 (default checksum function)
    * CRC16DNP
    * CRC16Kermit
    * CRC16SICK
    * CRC32
    * CRCCCITT
    * InternetChecksum (this checksum is used in ICMP, UDP, IP, TCP protocols, as specified in RFC 1071)


    The following examples show how to create a checksum relation with
    another field, with different checksum functions:

    >>> from netzob.all import *
    >>> f1 = Field(Raw(b'\xaa\xbb'))
    >>> f2 = Field(Checksum([f1]))
    >>> s = Symbol(fields = [f1, f2])
    >>> binascii.hexlify(s.specialize())
    b'aabb3ed3'

    >>> f2 = Field(Checksum([f1], 'CRC16'))
    >>> s = Symbol(fields = [f1, f2])
    >>> binascii.hexlify(s.specialize())
    b'aabb3ed3'

    >>> f2 = Field(Checksum([f1], 'CRC16DNP'))
    >>> s = Symbol(fields = [f1, f2])
    >>> binascii.hexlify(s.specialize())
    b'aabbfb9b'

    >>> f2 = Field(Checksum([f1], 'CRC16Kermit'))
    >>> s = Symbol(fields = [f1, f2])
    >>> binascii.hexlify(s.specialize())
    b'aabb59d7'

    >>> f2 = Field(Checksum([f1], 'CRC16SICK'))
    >>> s = Symbol(fields = [f1, f2])
    >>> binascii.hexlify(s.specialize())
    b'aabbabef'

    >>> f2 = Field(Checksum([f1], 'CRC32'))
    >>> s = Symbol(fields = [f1, f2])
    >>> binascii.hexlify(s.specialize())
    b'aabb982c8249'

    >>> f2 = Field(Checksum([f1], 'CRCCCITT'))
    >>> s = Symbol(fields = [f1, f2])
    >>> binascii.hexlify(s.specialize())
    b'aabb05e4'

    >>> f2 = Field(Checksum([f1], 'InternetChecksum'))
    >>> s = Symbol(fields = [f1, f2])
    >>> s.specialize()
    b'\xaa\xbbUD'


    **Checksum Shortcut Definitions**

    This class also provides shortcuts to define checksum
    relationships. The following shortcuts are available:

    * CRC16(fields)            -> Checksum(fields, checksumName='CRC16')
    * CRC16DNP(fields)         -> Checksum(fields, checksumName='CRC16DNP')
    * CRC16Kermit(fields)      -> Checksum(fields, checksumName='CRC16Kermit')
    * CRC16Sick(fields)        -> Checksum(fields, checksumName='CRC16Sick')
    * CRC32(fields)            -> Checksum(fields, checksumName='CRC32')
    * CRCCCITT(fields)         -> Checksum(fields, checksumName='CRCCCITT')
    * InternetChecksum(fields) -> Checksum(fields, checksumName='InternetChecksum')


    **Complete Example with ICMP**

    The following example illustrates the creation of an ICMP Echo request packet
    with a valid checksum computed on-the-fly.

    >>> from netzob.all import *
    >>> typeField = Field(name="Type", domain=Raw(b'\x08'))
    >>> codeField = Field(name="Code", domain=Raw(b'\x00'))
    >>> chksumField = Field(name="Checksum")
    >>> identField = Field(name="Identifier", domain=Raw(b'\x1d\x22'))
    >>> seqField = Field(name="Sequence Number", domain=Raw(b'\x00\x07'))
    >>> timeField = Field(name="Timestamp", domain=Raw(b'\xa8\xf3\xf6\x53\x00\x00\x00\x00'))
    >>> headerField = Field(name="header")
    >>> headerField.fields = [typeField, codeField, chksumField,
    ...                       identField, seqField, timeField]
    >>> dataField = Field(name="Payload", domain=Raw(b'\x60\xb5\x06\x00\x00\x00\x00\x00\x10\
    ... \x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f\x20\x21\x22\x23\x24\x25\
    ... \x26\x27\x28\x29\x2a\x2b\x2c\x2d\x2e\x2f\x30\x31\x32\x33\x34\x35\x36\x37'))

    >>> chksumField.domain = Checksum([headerField, dataField], 'InternetChecksum',
    ...                               dataType=Raw(nbBytes=2))
    >>> s = Symbol(fields = [headerField, dataField])
    >>> msgs = [RawMessage(s.specialize()) for i in range(1)]
    >>> s.messages = msgs
    >>> s.addEncodingFunction(TypeEncodingFunction(HexaString))
    >>> print(s)  # doctest: +ELLIPSIS
    Type | Code | Checksum | Identifier | Sequence Number | Timestamp          | Payload    ...
    ---- | ---- | -------- | ---------- | --------------- | ------------------ | -----------...
    '08' | '00' | '1607'   | '1d22'     | '0007'          | 'a8f3f65300000000' | '60b5060000...
    ---- | ---- | -------- | ---------- | --------------- | ------------------ | -----------...

    """

    def __init__(self, targets, checksumName='CRC16', dataType=None, name=None):
        if dataType is None:
            dataType = Raw(nbBytes=2)  # The computed checksum is generally on 16 bits
        super(Checksum, self).__init__(self.__class__.__name__,
                                   dataType=dataType,
                                   targets=targets,
                                   name=name)
        self.checksumName = checksumName

    def relationOperation(self, msg):

        msg = msg.tobytes()

        self._logger.debug("Computing checksum of '{0}'".format(
            TypeConverter.convert(msg, Raw, HexaString)))

        if self.checksumName == "CRC16":
            result = _CRC16().calculate(msg)
        elif self.checksumName == "CRC16DNP":
            result = _CRC16DNP().calculate(msg)
        elif self.checksumName == "CRC16Kermit":
            result = _CRC16Kermit().calculate(msg)
        elif self.checksumName == "CRC16SICK":
            result = _CRC16SICK().calculate(msg)
        elif self.checksumName == "CRC32":
            result = _CRC32().calculate(msg)
        elif self.checksumName == "CRCCCITT":
            result = _CRCCCITT().calculate(msg)
        elif self.checksumName == "InternetChecksum":

            def carry_around_add(a, b):
                c = a + b
                return (c & 0xffff) + (c >> 16)

            s = 0
            for i in range(0, len(msg), 2):
                if i + 1 >= len(msg):
                    w = msg[i] & 0xFF
                else:
                    w = msg[i] + (msg[i + 1] << 8)
                s = carry_around_add(s, w)
            result = ~s & 0xffff

        else:
            raise Exception("Checksum function not implemented: '{}'".format(self.checksumName))

        # Convert the result in a BitArray (be carefull with the src_unitSize)
        if self.checksumName == "CRC32":
            result = TypeConverter.convert(result, Integer, BitArray,
                                           src_endianness=Endianness.LITTLE,
                                           dst_endianness=self.dataType.endianness,
                                           src_unitSize=UnitSize.SIZE_32,
                                           dst_unitSize=self.dataType.unitSize,
                                           src_sign=Sign.UNSIGNED)

        else:
            result = TypeConverter.convert(result, Integer, BitArray,
                                           src_endianness=Endianness.LITTLE,
                                           dst_endianness=self.dataType.endianness,
                                           src_unitSize=UnitSize.SIZE_16,
                                           dst_unitSize=self.dataType.unitSize,
                                           src_sign=Sign.UNSIGNED)

        return result

    @property
    def checksumName(self):
        return self.__checksumName

    @checksumName.setter
    @typeCheck(str)
    def checksumName(self, checksumName):
        if checksumName is None:
            raise TypeError("checksumName cannot be None")
        self.__checksumName = checksumName


CRC16            = partialclass(Checksum, checksumName="CRC16")
CRC16DNP         = partialclass(Checksum, checksumName="CRC16DNP")
CRC16Kermit      = partialclass(Checksum, checksumName="CRC16Kermit")
CRC16Sick        = partialclass(Checksum, checksumName="CRC16Sick")
CRC32            = partialclass(Checksum, checksumName="CRC32")
CRCCCITT         = partialclass(Checksum, checksumName="CRCCCITT")
InternetChecksum = partialclass(Checksum, checksumName="InternetChecksum")
