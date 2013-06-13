#-*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|          01001110 01100101 01110100 01111010 01101111 01100010            |
#|                                                                           |
#|               Netzob : Inferring communication protocols                  |
#+---------------------------------------------------------------------------+
#| Copyright (C) 2011 Georges Bossert and Frédéric Guihéry                   |
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
import logging
import uuid

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck
from netzob.Common.Models.Types.AbstractType import AbstractType
from netzob.Common.Models.Vocabulary.Domain.Variables.Leafs.AbstractVariableLeaf import AbstractVariableLeaf


class Data(AbstractVariableLeaf):
    """Represents a data, meaning a portion of content in the final
    message.

    For instance:

    >>> from netzob import *
    >>> f = Field()
    >>> f.domain = Data(dataType=ASCII, value="zoby", name="pseudo")
    >>> print f.domain.varType
    Data
    >>> print f.domain.currentValue
    zoby
    >>> print f.domain.dataType.__name__
    ASCII
    >>> print f.domain.name
    pseudo

    >>> f = Field(ASCII("hello zoby"))
    >>> print f.domain.varType
    Data
    >>> print f.domain.currentValue
    hello zoby


    """

    def __init__(self, dataType, value=None, name=None, size=(None, None)):
        """The constructor of a data variable

        :param dataType: the type of the data.
        :type dataType: :class:`netzob.Common.Models.Types.AbstractType.AbstractType`
        :keyword value: the value of the data (can be None)
        :type value: :class:`object`
        :keyword name: the name of the data, if None name will be generated
        :type name: :class:`str`
        :keyword size: the size of the data (minSize, maxSize) in bits, per default its (None, None)
        :type size: a tupple of int
        :raises: :class:`TypeError` or :class:`ValueError` if parameters are not valid.

        """

        super(Data, self).__init__(self.__class__.__name__)
        self.__logger = logging.getLogger(__name__)

        self.dataType = dataType
        self.currentValue = value
        if name is None:
            name = str(uuid.uuid4())
        self.name = name
        self.size = size

    @property
    def dataType(self):
        """The type of the data.

        :type: :class:`netzob.Common.Models.Types.AbstractType.AbstractType`
        :raises: :class:`TypeError` or :class:`ValueError` if not valid.
        """
        return self.__dataType

    @dataType.setter
    @typeCheck(type)
    def dataType(self, dataType):
        if dataType is None:
            raise ValueError("dataType cannot be None")
        if not AbstractType.__subclasscheck__(dataType):
            raise ValueError("The specified type must inherit from the AbstractType class.")

        self.__dataType = dataType

    @property
    def currentValue(self):
        """The current value of the data.

        :type: :class:`object`
        """
        return self.__currentValue

    @currentValue.setter
    def currentValue(self, currentValue):
        self.__currentValue = currentValue

    @property
    def name(self):
        """The name of the data.

        :type: :class:`object`
        """
        return self.__name

    @name.setter
    @typeCheck(str)
    def name(self, name):
        if name is None:
            raise ValueError("name cannot be None")
        name = name.strip()
        if len(name) == 0:
            raise ValueError("name must be defined even after being trimmed (len>0)")
        self.__name = name

    @property
    def size(self):
        """The size of the data.
        size = (sizeMin, sizeMax)

        :type: a tupple of int


        >>> from netzob import *
        >>> data = Data(dataType=ASCII, value="zoby", name="pseudo", size=None)

        >>> data = Data(dataType=ASCII, value="zoby", name="pseudo", size=(-1, None))
        Traceback (most recent call last):
        ...
        ValueError: Minimum size must be greater than 0

        >>> data = Data(dataType=ASCII, value="zoby", name="pseudo", size=(5, 2))
        Traceback (most recent call last):
        ...
        ValueError: Maximum must be greater than the minimum
        """
        return self.__size

    @size.setter
    def size(self, size):
        if size is None:
            size = (None, None)

        if isinstance(size, tuple):
            minSize, maxSize = size

            if minSize is not None and not isinstance(minSize, int):
                raise TypeError("Size must be defined with a tuple of int")
            if maxSize is not None and not isinstance(maxSize, int):
                raise TypeError("Size must be defined with a tuple of int")

            if minSize is None:
                minSize = 0

            if minSize < 0:
                raise ValueError("Minimum size must be greater than 0")
            if maxSize is not None and maxSize <= minSize:
                raise ValueError("Maximum must be greater than the minimum")

            self.__size = (minSize, maxSize)
        else:
            raise TypeError("Size must be defined by a tuple an int or with None")

        self.__size = size
