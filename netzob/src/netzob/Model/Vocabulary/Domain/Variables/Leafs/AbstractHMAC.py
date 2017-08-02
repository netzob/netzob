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
class AbstractHMAC(AbstractRelationVariableLeaf, metaclass=abc.ABCMeta):
    r"""
    **Abstract class**.
    The AbstractHMAC class comes with a list of concrete HMAC relationships
    between fields. Some implementations are available in the package
    :mod:`netzob.Model.Vocabulary.Domain.Variables.Leafs.Hmacs`.
    Currently available hash functions for HMAC are:
    :class:`HMAC_MD5 <netzob.Model.Vocabulary.Domain.Variables.Leafs.Hmacs.HMAC_MD5.HMAC_MD5>`,
    :class:`HMAC_SHA1 <netzob.Model.Vocabulary.Domain.Variables.Leafs.Hmacs.HMAC_SHA1.HMAC_SHA1>`,
    :class:`HMAC_SHA1_96 <netzob.Model.Vocabulary.Domain.Variables.Leafs.Hmacs.HMAC_SHA1_96.HMAC_SHA1_96>`,
    :class:`HMAC_SHA224 <netzob.Model.Vocabulary.Domain.Variables.Leafs.Hmacs.HMAC_SHA2_224.HMAC_SHA2_224>`,
    :class:`HMAC_SHA256 <netzob.Model.Vocabulary.Domain.Variables.Leafs.Hmacs.HMAC_SHA2_256.HMAC_SHA2_256>`,
    :class:`HMAC_SHA384 <netzob.Model.Vocabulary.Domain.Variables.Leafs.Hmacs.HMAC_SHA2_384.HMAC_SHA2_384>` and
    :class:`HMAC_SHA512 <netzob.Model.Vocabulary.Domain.Variables.Leafs.Hmacs.HMAC_SHA2_512.HMAC_SHA2_512>`.

    The AbstractHMAC constructor expects some parameters:

    :param targets: The targeted fields of the relationship.
    :param key: The cryptographic key used in the hmac computation.
    :param dataType: Specify that the produced value should be
                     represented according to this dataType.
                     If None, default value is Raw(nbBytes=1).
    :param name: The name of the Value variable. If None, the name will be generated.
    :type targets: a :class:`list` of :class:`Field <netzob.Model.Vocabulary.Field>`, required
    :type key: :class:`bytes`, required
    :type dataType: :class:`AbstractType <netzob.Model.Vocabulary.Types.AbstractType>`, optional
    :type name: :class:`str`, optional

    This class is abstract and cannot be instanciated.
    The following methods MUST be inherited:

    * :meth:`calculate`
    * :meth:`getBitSize`
    """

    def __init__(self, targets, key, dataType=None, name=None):
        if dataType is None:
            dataType = Raw(nbBytes=self.getByteSize())
        super(AbstractHMAC, self).__init__(self.__class__.__name__,
                                           dataType=dataType,
                                           targets=targets,
                                           name=name)
        self.key = key

    def relationOperation(self, msg):
        """The relationOperation receive a bitarray object and should return a
        bitarray object.

        """
        # The calling function provides a BitArray
        msg = msg.tobytes()

        # Compute HMAC
        result = self.calculate(msg)

        # The calling function expects a BitArray
        result = TypeConverter.convert(result, Raw, BitArray,
                                       src_endianness=Endianness.LITTLE,
                                       dst_endianness=self.dataType.endianness,
                                       src_unitSize=self.dataType.unitSize,
                                       dst_unitSize=self.dataType.unitSize,
                                       src_sign=Sign.UNSIGNED)

        return result

    @property
    def key(self):
        return self.__key

    @key.setter
    @typeCheck(bytes)
    def key(self, key):
        if key is None:
            raise TypeError("key cannot be None")
        self.__key = key

    @abc.abstractmethod
    def calculate(self,
                  msg  # type: bytes
                  ):   # type: bytes
        """
        **Abstract method**.
        The most-specific computation method taking a :attr:`msg` and returning
        its hash value.

        :param msg: input message
        :type msg: :class:`bytes`
        :return: hash value
        :rtype: :class:`bytes`
        """

    @abc.abstractmethod
    def getBitSize(self):  # type int
        """
        **Abstract method**.
        Get the bit size of the hash'ed message.

        :return: the output unit size
        :type: :class:`int`
        """

    def getByteSize(self):
        return int(self.getBitSize() / 8)
