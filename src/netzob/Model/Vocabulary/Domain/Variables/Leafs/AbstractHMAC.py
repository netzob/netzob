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
from netzob.Common.Utils.Decorators import NetzobLogger, public_api
from netzob.Model.Vocabulary.Domain.Variables.Leafs.AbstractRelationVariableLeaf import AbstractRelationVariableLeaf
from netzob.Model.Vocabulary.Types.AbstractType import Endianness, Sign
from netzob.Model.Vocabulary.Types.TypeConverter import TypeConverter
from netzob.Model.Vocabulary.Types.BitArray import BitArray
from netzob.Model.Vocabulary.Types.Raw import Raw


@NetzobLogger
class AbstractHMAC(AbstractRelationVariableLeaf, metaclass=abc.ABCMeta):
    r"""The AbstractHMAC interface specifies the methods to implement
    in order to create a new HMAC relationship.

    If the relationship targets itself, it will initialize the initial
    value of the HMAC field to 0x00.

    The following methods have to be implemented:

    * :meth:`calculate`
    * :meth:`getBitSize`
    """

    ## Interface methods ##

    @abc.abstractmethod
    def calculate(self, data):
        # type: (bytes) -> bytes
        """This is a computation method that takes a :attr:`data` and returns
        its HMAC value.

        :param data: The input data on which to compute the HMAC relationship.
        :type data: :class:`bytes`, required
        :return: The HMAC value.
        :rtype: :class:`bytes`

        """

    @abc.abstractmethod
    def getBitSize(self):  # type int
        """This method should return the unit size in bits of the produced
        HMAC (such as ``160`` bits).

        :return: The output unit size in bits.
        :type: :class:`int`

        """


    ## Internal methods ##

    @public_api
    def __init__(self, targets, key, dataType=None, name=None):
        if dataType is None:
            dataType = Raw(nbBytes=self.getByteSize())
        super(AbstractHMAC, self).__init__(self.__class__.__name__,
                                           dataType=dataType,
                                           targets=targets,
                                           name=name)
        self.key = key

    @public_api
    def copy(self, map_objects=None):
        """Copy the current object as well as all its dependencies.

        :return: A new object of the same type.
        :rtype: :class:`AbstractHMAC <netzob.Model.Vocabulary.Domain.Variables.Leafs.AbstractHMAC.AbstractHMAC>`

        """
        if map_objects is None:
            map_objects = {}
        if self in map_objects:
            return map_objects[self]

        new_hmac = self.__class__([], key=self.key, dataType=self.dataType, name=self.name)
        map_objects[self] = new_hmac

        new_targets = []
        for target in self.targets:
            if target in map_objects.keys():
                new_targets.append(map_objects[target])
            else:
                new_target = target.copy(map_objects)
                new_targets.append(new_target)

        new_hmac.targets = new_targets
        return new_hmac

    def getByteSize(self):
        return int(self.getBitSize() / 8)

    def relationOperation(self, data):
        """The relationOperation receive a bitarray object and should return a
        bitarray object.

        """
        # The calling function provides a BitArray
        data = data.tobytes()

        # Compute HMAC
        result = self.calculate(data)

        # The calling function expects a BitArray
        result = TypeConverter.convert(result, Raw, BitArray,
                                       src_endianness=Endianness.LITTLE,
                                       dst_endianness=self.dataType.endianness,
                                       src_unitSize=self.dataType.unitSize,
                                       dst_unitSize=self.dataType.unitSize,
                                       src_sign=Sign.UNSIGNED)

        return result
