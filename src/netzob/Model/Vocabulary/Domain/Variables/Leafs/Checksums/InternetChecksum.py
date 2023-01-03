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

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Model.Vocabulary.Domain.Variables.Leafs.Checksums.CRC16 import CRC16


class InternetChecksum(CRC16):
    r"""This class implements the InternetChecksum function, as used in
    ICMP, UDP, IP, TCP protocols, as specified in :rfc:`1071`.

    The following example shows how to create a checksum relation with
    another field:

    >>> from netzob.all import *
    >>> import binascii
    >>> f1 = Field(Raw(b'\xaa\xbb'))
    >>> f2 = Field(InternetChecksum([f1]))
    >>> s = Symbol(fields = [f1, f2])
    >>> binascii.hexlify(next(s.specialize()))
    b'aabb5544'

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
    >>> msgs = [RawMessage(next(s.specialize()))]
    >>> s.messages = msgs
    >>> s.addEncodingFunction(TypeEncodingFunction(HexaString))
    >>> print(s.str_data())  # doctest: +ELLIPSIS
    Type | Code | Checksum | Identifier | Sequence Number | Timestamp          | Payload    ...
    ---- | ---- | -------- | ---------- | --------------- | ------------------ | -----------...
    '08' | '00' | '1607'   | '1d22'     | '0007'          | 'a8f3f65300000000' | '60b5060000...
    ---- | ---- | -------- | ---------- | --------------- | ------------------ | -----------...

    """

    def calculate(self, msg):

        # Compute checksum
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
        return ~s & 0xffff
