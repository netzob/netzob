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
import hmac
import hashlib

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Model.Vocabulary.Domain.Variables.Leafs.AbstractHMAC import AbstractHMAC
from netzob.Model.Vocabulary.Domain.Variables.Leafs.Hashes.SHA2_256 import SHA2_256


class HMAC_SHA2_256(AbstractHMAC):
    r"""This class implements the HMAC_SHA2_256.

    The constructor expects some parameters:

    :param targets: The targeted fields of the relationship.
    :param key: The cryptographic key used in the hmac computation.
    :type targets: a :class:`list` of :class:`Field <netzob.Model.Vocabulary.Field>`, required
    :type key: :class:`bytes`, required

    The following example shows how to create a HMAC relation with
    another field:

    >>> from netzob.all import *
    >>> import binascii
    >>> f1 = Field(Raw(b'\xaa\xbb'))
    >>> f2 = Field(HMAC_SHA2_256([f1], key=b'1234'))
    >>> s = Symbol(fields = [f1, f2])
    >>> binascii.hexlify(next(s.specialize()))
    b'aabbd798c3319e6f2ad48c313deb0eee1c9a9b704c3964d8195e66b10a47583b9c07'
    """

    def calculate(self, msg):
        return hmac.new(self.key, msg=msg, digestmod=hashlib.sha256).digest()

    getBitSize = SHA2_256.getBitSize
