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
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger
from netzob.Model.Vocabulary.Domain.Variables.Leafs.HMAC import HMAC
from netzob.Model.Vocabulary.Types.AbstractType import Endianness, Sign
from netzob.Model.Vocabulary.Types.TypeConverter import TypeConverter
from netzob.Model.Vocabulary.Types.BitArray import BitArray
from netzob.Model.Vocabulary.Types.Raw import Raw


@NetzobLogger
class HMAC_MD5(HMAC):
    r"""This class implements the HMAC_MD5.

    The constructor expects some parameters:

    :param targets: The targeted fields of the relationship.
    :param key: The cryptographic key used in the hmac computation.
    :param dataType: Specify that the produced value should be
                     represented according to this dataType.
                     If None, default value is Raw(nbBytes=1).
    :param name: The name of the Value variable. If None, the name will be generated.
    :type targets: a :class:`list` of :class:`AbstractField <netzob.Model.Vocabulary.AbstractField>`, required
    :type key: :class:`bytes`, required
    :type dataType: :class:`AbstractType <netzob.Model.Vocabulary.Types.AbstractType>`, optional
    :type name: :class:`str`, optional

    The following examples show how to create a HMAC relation with
    another field:

    >>> from netzob.all import *
    >>> f1 = Field(Raw(b'\xaa\xbb'))
    >>> f2 = Field(HMAC_MD5([f1], key=b'1234'))
    >>> s = Symbol(fields = [f1, f2])
    >>> binascii.hexlify(s.specialize())
    b'aabbb71c98baa40dc8a49361816d5dc1eb25'

    """

    def __init__(self, targets, key, dataType=None, name=None):
        super(HMAC_MD5, self).__init__(self.__class__.__name__,
                                       targets=targets,
                                       key=key,
                                       dataType=dataType,
                                       name=name)

    def relationOperation(self, msg):

        # The calling function provides a BitArray
        msg = msg.tobytes()

        # Compute HMAC
        result = hmac.new(self.key, msg=msg, digestmod=hashlib.md5).digest()

        # The calling function expects a BitArray
        result = TypeConverter.convert(result, Raw, BitArray,
                                       src_endianness=Endianness.LITTLE,
                                       dst_endianness=self.dataType.endianness,
                                       src_unitSize=self.dataType.unitSize,
                                       dst_unitSize=self.dataType.unitSize,
                                       src_sign=Sign.UNSIGNED)

        return result
