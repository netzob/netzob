#-*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|          01001110 01100101 01110100 01111010 01101111 01100010            |
#|                                                                           |
#|               Netzob : Inferring communication protocols                  |
#+---------------------------------------------------------------------------+
#| Copyright (C) 2011-2016 Georges Bossert and Frédéric Guihéry              |
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
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| File contributors :                                                       |
#|       - Georges Bossert <georges.bossert (a) supelec.fr>                  |
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
from netzob.Common.Utils.Decorators import NetzobLogger
from netzob.Model.Types.TypeConverter import TypeConverter
from netzob.Model.Types.BitArray import BitArray
from netzob.Model.Vocabulary.Functions.EncodingFunction import EncodingFunction
from netzob.Model.Types.AbstractType import AbstractType


@NetzobLogger
class TypeEncodingFunction(EncodingFunction):
    r"""This encoding function allows to specify the type and its attributes
    such as the endianness, the sign and the unitsize that will be used to encode
    the specified data.

    >>> from netzob.all import *
    >>> f = Field(name="f0", domain=Agg(["There are ", Integer(10), " solutions."]))
    >>> m = RawMessage(b"There are " + TypeConverter.convert(10, Integer, Raw) + b" solutions.")
    >>> s = Symbol(fields=[f], messages=[m], name="Symbol")
    >>> s.addEncodingFunction(TypeEncodingFunction(HexaString))
    >>> print(s)
    f0                                            
    ----------------------------------------------
    '546865726520617265200a20736f6c7574696f6e732e'
    ----------------------------------------------

    >>> m=RawMessage(b'hello\x00\x00\x00\x01')
    >>> f1=Field(ASCII("hello"))
    >>> f2=Field(Integer(unitSize=AbstractType.UNITSIZE_32))
    >>> s = Symbol(fields=[f1,f2], messages=[m])
    >>> print(s)
    Field   | Field             
    ------- | ------------------
    'hello' | '\x00\x00\x00\x01'
    ------- | ------------------

    >>> f2.addEncodingFunction(TypeEncodingFunction(Integer, unitSize=AbstractType.UNITSIZE_32, endianness=AbstractType.ENDIAN_LITTLE))
    >>> print(s)
    Field   | Field   
    ------- | --------
    'hello' | 16777216
    ------- | --------

    >>> f2=Field(Integer(unitSize=AbstractType.UNITSIZE_32))
    >>> f2.addEncodingFunction(TypeEncodingFunction(Integer, unitSize=AbstractType.UNITSIZE_32, endianness=AbstractType.ENDIAN_BIG))
    >>> s = Symbol(fields=[f1,f2], messages=[m])
    >>> print(s)
    Field   | Field
    ------- | -----
    'hello' | 1    
    ------- | -----

    """
    def __init__(self, _type, unitSize=None, endianness=None, sign=None):
        """Creates a new encoding function that will encode
        the data with the specified types and following its attributes. If an attribute
        is not specified (or set to None), it takes its default value defined in :class:`netzob.Model.Types.AbstractType.AbstractType`.

        :parameter _type: the type that will be used to encode
        :type _type: :class:`type`
        :keyword unitSize: the unitsize of the expected result. Values must be one of AbstractType.UNITSIZE_*
        :type unitSize: str
        :keyword endianness: the endianness of the expected result. Values must be AbstractType.ENDIAN_BIG or AbstractType.ENDIAN_LITTLE
        :type endianness: str
        :keyword sign: the sign of the expected result. Values must be AbstractType.SIGN_SIGNED or AbstractType.SIGN_UNSIGNED
        :type sign: str
        """
        self.type = _type
        if unitSize is None:
            unitSize = AbstractType.defaultUnitSize()
        self.unitSize = unitSize

        if endianness is None:
            endianness = AbstractType.defaultEndianness()
        self.endianness = endianness

        if sign is None:
            sign = AbstractType.defaultSign()
        self.sign = sign

    def encode(self, data):
        self._logger.debug(data)
        return TypeConverter.convert(data, BitArray, self.type, dst_unitSize=self.unitSize, dst_endianness=self.endianness, dst_sign=self.sign)

    def priority(self):
        """Returns the priority of the current encoding filter."""
        return 100

    @property
    def type(self):
        return self.__type

    @type.setter
    def type(self, _type):
        if _type is None:
            raise TypeError("Type cannot be None")
        if _type not in AbstractType.supportedTypes():
            raise TypeError("The type is not supported, please refer to the list of supported type in AbstractType.supportedTypes()")
        self.__type = _type

    @property
    def unitSize(self):
        return self.__unitSize

    @unitSize.setter
    def unitSize(self, unitSize):
        if unitSize is None:
            raise TypeError("Unitsize cannot be None.")
        if unitSize not in AbstractType.supportedUnitSizes():
            raise ValueError("This unitSize is not supported, please refer to the list of supported type in AbstractType.supportedUnitSizes()")
        self.__unitSize = unitSize

    @property
    def endianness(self):
        return self.__endianness

    @endianness.setter
    def endianness(self, endianness):
        if endianness is None:
            raise TypeError("Endianness cannot be None.")
        if endianness not in AbstractType.supportedEndianness():
            raise ValueError("This endianness is not supported, please refer to the list of supported type in AbstractType.supportedEndianness()")
        self.__endianness = endianness

    @property
    def sign(self):
        return self.__sign

    @sign.setter
    def sign(self, sign):
        if sign is None:
            raise TypeError("Sign cannot be None.")
        if sign not in AbstractType.supportedSign():
            raise ValueError("This sign is not supported, please refer to the list of supported type in AbstractType.supportedSign()")
        self.__sign = sign

