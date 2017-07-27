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
from netzob.Model.Vocabulary.Types.AbstractType import Endianness, Sign
from netzob.Model.Vocabulary.Types.BitArray import BitArray
from netzob.Model.Vocabulary.Types.TypeConverter import TypeConverter
from netzob.Model.Vocabulary.Types.Raw import Raw


class Hash(AbstractRelationVariableLeaf, metaclass=abc.ABCMeta):
    r"""The Hash class implements a list of hash relationships between fields.

    The Hash constructor expects some parameters:

    :param targets: The targeted fields of the relationship.
    :param dataType: Specify that the produced value should be
                     represented according to this dataType.
                     If None, default value is Raw(nbBytes=1).
    :param name: The name of the Value variable. If None, the name will be generated.
    :type targets: a :class:`list` of :class:`Field <netzob.Model.Vocabulary.Field>`, required
    :type dataType: :class:`AbstractType <netzob.Model.Vocabulary.Types.AbstractType>`, optional
    :type name: :class:`str`, optional

    Supported hash functions are:

    * md5 (default hash function)
    * sha1
    * sha1-96
    * sha224
    * sha256
    * sha384
    * sha512
    """

    def __init__(self, targets, dataType=None, name=None):
        if dataType is None:
            dataType = Raw(nbBytes=self.getByteSize())
        super(Hash, self).__init__(self.__class__.__name__,
                                   dataType=dataType,
                                   targets=targets,
                                   name=name)

    def relationOperation(self, msg):
        """The relationOperation receive a bitarray object and should return a
        bitarray object.

        """
        # The calling function provides a BitArray
        msg = msg.tobytes()

        # Compute hash
        result = self.calculate(msg)

        # Convert the result in a BitArray (be carefull with the src_unitSize)
        result = TypeConverter.convert(result, Raw, BitArray,
                                       src_endianness=Endianness.LITTLE,
                                       dst_endianness=self.dataType.endianness,
                                       src_unitSize=self.dataType.unitSize,
                                       dst_unitSize=self.dataType.unitSize,
                                       src_sign=Sign.UNSIGNED)

        return result

    @abc.abstractmethod
    def calculate(self, msg: bytes) -> bytes:
        """
        The most-specific computation method taking a :attr:`msg` and returning
        its hash value.

        :param msg: input message
        :type msg: :class:`bytes`
        :return: hash value
        :rtype: :class:`bytes`
        """

    @abc.abstractmethod
    def getBitSize(self) -> int:
        """
        Get the bit size of the hash'ed message.

        :return: the output unit size
        :type: :class:`int`
        """

    def getByteSize(self):
        return int(self.getBitSize() / 8)
