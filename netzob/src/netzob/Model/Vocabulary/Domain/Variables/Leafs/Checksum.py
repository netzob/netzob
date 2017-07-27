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
import abc

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Model.Vocabulary.Domain.Variables.Leafs.AbstractRelationVariableLeaf import AbstractRelationVariableLeaf
from netzob.Model.Vocabulary.Types.AbstractType import AbstractType, Endianness, Sign
from netzob.Model.Vocabulary.Types.BitArray import BitArray
from netzob.Model.Vocabulary.Types.Raw import Raw
from netzob.Model.Vocabulary.Types.TypeConverter import TypeConverter
from netzob.Model.Vocabulary.Types.Integer import Integer


class Checksum(AbstractRelationVariableLeaf, metaclass=abc.ABCMeta):
    r"""The Checksum class implements a list of checksum relationships between fields.

    The Checksum constructor expects some parameters:

    :param targets: The targeted fields of the relationship.
    :param dataType: Specify that the produced value should be
                     represented according to this dataType.
                     If None, default value is Raw(nbBytes=2), as generally
                     the checksum is on 16bits.
    :param name: The name of the Value variable. If None, the name will be generated.
    :type targets: a :class:`list` of :class:`Field <netzob.Model.Vocabulary.Field>`, required
    :type dataType: :class:`AbstractType <netzob.Model.Vocabulary.Types.AbstractType>`, optional
    :type name: :class:`str`, optional


    Currently supported checksum functions are:

    * CRC16 (default checksum function)
    * CRC16DNP
    * CRC16Kermit
    * CRC16SICK
    * CRC32
    * CRCCCITT
    * InternetChecksum (this checksum is used in ICMP, UDP, IP, TCP protocols, as specified in RFC 1071)


    **Complete example with ICMP**

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

    >>> chksumField.domain = InternetChecksum([headerField, dataField],
    ...                                       dataType=Raw(nbBytes=2))
    >>> s = Symbol(fields = [headerField, dataField])
    >>> msgs = [RawMessage(s.specialize()) for i in range(1)]
    >>> s.messages = msgs
    >>> s.addEncodingFunction(TypeEncodingFunction(HexaString))
    >>> print(s.str_data())  # doctest: +ELLIPSIS
    Type | Code | Checksum | Identifier | Sequence Number | Timestamp          | Payload    ...
    ---- | ---- | -------- | ---------- | --------------- | ------------------ | -----------...
    '08' | '00' | '1607'   | '1d22'     | '0007'          | 'a8f3f65300000000' | '60b5060000...
    ---- | ---- | -------- | ---------- | --------------- | ------------------ | -----------...

    """

    def __init__(self, targets, dataType=None, name=None):
        if dataType is None:
            dataType = Raw(nbBytes=self.getByteSize())
            # The computed checksum is generally on 16 bits
        super(Checksum, self).__init__(self.__class__.__name__,
                                       dataType=dataType,
                                       targets=targets,
                                       name=name)

    def relationOperation(self, msg):
        """The relationOperation receive a bitarray object and should return a
        bitarray object.

        """
        # Convert bitarray input into bytes
        msg = msg.tobytes()

        # Compute checksum
        result = self.calculate(msg)

        # Convert the result in a BitArray (be carefull with the src_unitSize)
        result = TypeConverter.convert(result, Integer, BitArray,
                    src_endianness=Endianness.LITTLE,
                    dst_endianness=self.dataType.endianness,
                    src_unitSize=AbstractType.getUnitSizeEnum(self.getBitSize()),
                    dst_unitSize=self.dataType.unitSize,
                    src_sign=Sign.UNSIGNED)

        return result

    @abc.abstractmethod
    def calculate(self, msg: bytes) -> int:
        """
        The most-specific computation method taking a :attr:`msg` and returning
        its checksum value.

        :param msg: input message
        :type msg: :class:`bytes`
        :return: checksum value
        :rtype: :class:`int`
        """

    @abc.abstractmethod
    def getBitSize(self) -> int:
        """
        Get the unit size of the checksum'ed message.

        :return: the output unit size
        :type: :class:`int`
        """

    def getByteSize(self):
        return int(self.getBitSize() / 8)
