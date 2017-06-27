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
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger
from netzob.Model.Vocabulary.Domain.Variables.Leafs.AbstractRelationVariableLeaf import AbstractRelationVariableLeaf
from netzob.Model.Vocabulary.Types.AbstractType import Endianness, Sign
from netzob.Model.Vocabulary.Types.TypeConverter import TypeConverter
from netzob.Model.Vocabulary.Types.BitArray import BitArray
from netzob.Model.Vocabulary.Types.Raw import Raw


@NetzobLogger
class HMAC(AbstractRelationVariableLeaf):
    r"""The HMAC class implements the HMAC relationships between fields.

    The Hmac constructor expects some parameters:

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

    Currently supported hash functions for HMAC are:

    * md5
    * sha1
    * sha1-96
    * sha224
    * sha256
    * sha384
    * sha512


    The following examples show how to create a hmac relation with
    another field, with different hash functions:

    >>> from netzob.all import *
    >>> import binascii
    >>> f1 = Field(Raw(b'\xaa\xbb'))
    >>> f2 = Field(HMAC_MD5([f1], key=b'1234'))
    >>> s = Symbol(fields = [f1, f2])
    >>> binascii.hexlify(s.specialize())
    b'aabbb71c98baa40dc8a49361816d5dc1eb25'

    >>> f2 = Field(HMAC_SHA1([f1], key=b'1234'))
    >>> s = Symbol(fields = [f1, f2])
    >>> binascii.hexlify(s.specialize())
    b'aabb1c8c88e4ccf41d1b33814bfbb8e487611e97e699'

    >>> f2 = Field(HMAC_SHA1_96([f1], key=b'1234'))
    >>> s = Symbol(fields = [f1, f2])
    >>> binascii.hexlify(s.specialize())
    b'aabb1c8c88e4ccf41d1b33814bfb'

    >>> f2 = Field(HMAC_SHA2_224([f1], key=b'1234'))
    >>> s = Symbol(fields = [f1, f2])
    >>> binascii.hexlify(s.specialize())
    b'aabb99950845aec2ba54e4c426baa74667d27feb6f55c807a2302f6ceb54'

    >>> f2 = Field(HMAC_SHA2_256([f1], key=b'1234'))
    >>> s = Symbol(fields = [f1, f2])
    >>> binascii.hexlify(s.specialize())
    b'aabbd798c3319e6f2ad48c313deb0eee1c9a9b704c3964d8195e66b10a47583b9c07'

    >>> f2 = Field(HMAC_SHA2_384([f1], key=b'1234'))
    >>> s = Symbol(fields = [f1, f2])
    >>> binascii.hexlify(s.specialize())  # doctest: +ELLIPSIS
    b'aabb76b3535033802e3234386d1f45aa74e443d21651a798c194769b9af1808cd29d2...'

    >>> f2 = Field(HMAC_SHA2_512([f1], key=b'1234'))
    >>> s = Symbol(fields = [f1, f2])
    >>> binascii.hexlify(s.specialize())  # doctest: +ELLIPSIS
    b'aabb76ef5cd30cf5dcd93cb8b5c6f65f894e4453b51fc055d7cb05746f342f561b4c4...'

    """

    def __init__(self, varType, targets, key, dataType=None, name=None):
        super(HMAC, self).__init__(varType,
                                   dataType=dataType,
                                   targets=targets,
                                   name=name)
        self.key = key

    @abc.abstractmethod
    def relationOperation(self, msg):
        """The relationOperation receive a bitarray object and should return a
        bitarray object.

        """
        raise NotImplementedError("Internal Error: 'relationOperation' method not implemented")

    @property
    def key(self):
        return self.__key

    @key.setter
    @typeCheck(bytes)
    def key(self, key):
        if key is None:
            raise TypeError("key cannot be None")
        self.__key = key
