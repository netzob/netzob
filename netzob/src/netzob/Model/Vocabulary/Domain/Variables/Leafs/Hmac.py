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
from netzob.Model.Vocabulary.Types.AbstractType import AbstractType, Endianness, Sign
from netzob.Model.Vocabulary.Types.TypeConverter import TypeConverter
from netzob.Model.Vocabulary.Types.BitArray import BitArray
from netzob.Model.Vocabulary.Types.Raw import Raw
from netzob.Model.Vocabulary.Types.Integer import Integer


@NetzobLogger
class Hmac(AbstractRelationVariableLeaf):
    r"""The Hmac class implements a list of hmac relationships between fields.

    The Hmac constructor expects some parameters:

    :param fields: The targeted fields of the relationship.
    :param key: The cryptographic key used in the hmac computation.
    :param hashName: The underlying hash function (see below
                     for the list of supported functions). Default
                     value is md5.
    :param dataType: Specify that the produced value should be
                     represented according to this dataType.
    :param name: The name of the Value variable. If None, the name will be generated.
    :type field: a :class:`list` of :class:`AbstractField <netzob.Model.Vocabulary.AbstractField>`, required
    :type key: :class:`bytes`, required
    :type hashName: :class:`str`, optional
    :type dataType: :class:`AbstractType <netzob.Model.Vocabulary.Types.AbstractType>`, optional
    :type name: :class:`str`, optional

    Supported hash functions for hmac are:

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
    >>> f1 = Field(Raw(b'\xaa\xbb'))
    >>> f2 = Field(Hmac([f1], key=b'1234'))
    >>> s = Symbol(fields = [f1, f2])
    >>> binascii.hexlify(s.specialize())
    b'aabbb71c98baa40dc8a49361816d5dc1eb25'

    >>> f2 = Field(Hmac([f1], key=b'1234', hashName='md5'))
    >>> s = Symbol(fields = [f1, f2])
    >>> binascii.hexlify(s.specialize())
    b'aabbb71c98baa40dc8a49361816d5dc1eb25'

    >>> f2 = Field(Hmac([f1], key=b'1234', hashName='sha1'))
    >>> s = Symbol(fields = [f1, f2])
    >>> binascii.hexlify(s.specialize())
    b'aabb1c8c88e4ccf41d1b33814bfbb8e487611e97e699'

    >>> f2 = Field(Hmac([f1], key=b'1234', hashName='sha1-96'))
    >>> s = Symbol(fields = [f1, f2])
    >>> binascii.hexlify(s.specialize())
    b'aabb1c8c88e4ccf41d1b33814bfb'

    >>> f2 = Field(Hmac([f1], key=b'1234', hashName='sha224'))
    >>> s = Symbol(fields = [f1, f2])
    >>> binascii.hexlify(s.specialize())
    b'aabb99950845aec2ba54e4c426baa74667d27feb6f55c807a2302f6ceb54'

    >>> f2 = Field(Hmac([f1], key=b'1234', hashName='sha256'))
    >>> s = Symbol(fields = [f1, f2])
    >>> binascii.hexlify(s.specialize())
    b'aabbd798c3319e6f2ad48c313deb0eee1c9a9b704c3964d8195e66b10a47583b9c07'

    >>> f2 = Field(Hmac([f1], key=b'1234', hashName='sha384'))
    >>> s = Symbol(fields = [f1, f2])
    >>> binascii.hexlify(s.specialize())  # doctest: +ELLIPSIS
    b'aabb76b3535033802e3234386d1f45aa74e443d21651a798c194769b9af1808cd29d2...'

    >>> f2 = Field(Hmac([f1], key=b'1234', hashName='sha512'))
    >>> s = Symbol(fields = [f1, f2])
    >>> binascii.hexlify(s.specialize())  # doctest: +ELLIPSIS
    b'aabb76ef5cd30cf5dcd93cb8b5c6f65f894e4453b51fc055d7cb05746f342f561b4c4...'

    """

    def __init__(self, fields, key, hashName='md5', dataType=None, name=None):
        super(Hmac, self).__init__(self.__class__.__name__,
                                   dataType=dataType,
                                   fieldDependencies=fields,
                                   name=name)
        self.key = key
        self.hashName = hashName

    def relationOperation(self, msg):

        # The calling function provides a BitArray
        msg = msg.tobytes()
        
        self._logger.debug("Computing hash of '{0}'".format(
            TypeConverter.convert(msg, Raw, HexaString)))

        if self.hashName == "md5":
            result = hmac.new(self.key, msg=msg, digestmod=hashlib.md5).digest()
        elif self.hashName == "sha1":
            result = hmac.new(self.key, msg=msg, digestmod=hashlib.sha1).digest()
        elif self.hashName == "sha1-96":
            result = hmac.new(self.key, msg=msg, digestmod=hashlib.sha1).digest()[:int(96/8)]
        elif self.hashName == "sha224":
            result = hmac.new(self.key, msg=msg, digestmod=hashlib.sha224).digest()
        elif self.hashName == "sha256":
            result = hmac.new(self.key, msg=msg, digestmod=hashlib.sha256).digest()
        elif self.hashName == "sha384":
            result = hmac.new(self.key, msg=msg, digestmod=hashlib.sha384).digest()
        elif self.hashName == "sha512":
            result = hmac.new(self.key, msg=msg, digestmod=hashlib.sha512).digest()
        else:
            raise Exception("Hmac function not implemented: 'hmac-{}'".format(self.hashName))

        # The calling function expects a BitArray
        result = TypeConverter.convert(result, Raw, BitArray,
                                       src_endianness=Endianness.LITTLE,
                                       dst_endianness=self.dataType.endianness,
                                       src_unitSize=self.dataType.unitSize,
                                       dst_unitSize=self.dataType.unitSize,
                                       src_sign=Sign.UNSIGNED)

        return result

    @property
    def hashName(self):
        return self.__hashName

    @hashName.setter
    @typeCheck(str)
    def hashName(self, hashName):
        if hashName is None:
            raise TypeError("hashName cannot be None")
        algorithms_supported = list(hashlib.algorithms_guaranteed)
        algorithms_supported.append("sha1-96")
        if hashName not in algorithms_supported:
            raise ValueError(
                "The hashName must be one of: '{}'".format(hashlib.algorithms_guaranteed))
        self.__hashName = hashName

    @property
    def key(self):
        return self.__key

    @key.setter
    @typeCheck(bytes)
    def key(self, key):
        if key is None:
            raise TypeError("key cannot be None")
        self.__key = key


hmac_md5     = partialclass(Hmac, hashName="md5")
hmac_sha1    = partialclass(Hmac, hashName="sha1")
hmac_sha1_96 = partialclass(Hmac, hashName="sha1-96")
hmac_sha224  = partialclass(Hmac, hashName="sha224")
hmac_sha256  = partialclass(Hmac, hashName="sha256")
hmac_sha384  = partialclass(Hmac, hashName="sha384")
hmac_sha512  = partialclass(Hmac, hashName="sha512")
