#-*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|          01001110 01100101 01110100 01111010 01101111 01100010            |
#|                                                                           |
#|               Netzob : Inferring communication protocols                  |
#+---------------------------------------------------------------------------+
#| Copyright (C) 2011-2014 Georges Bossert and Frédéric Guihéry              |
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
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger


@NetzobLogger
class Flag(object):
    r"""A flag represents an identified named bit in a field.


    For example, HTTP2 header packet defines 4 flags (ENDSTREAM, ENDHEADERS, PADDED end PRIORITY).
    One can use the Flag class to model these flags
    
    >>> from netzob.all import *
    >>> FLAG_ENDSTREAM = Flag(name = "End stream", position = 0)
    >>> FLAG_ENDHEADERS = Flag(name = "End headers", position = 2)
    >>> FLAG_PADDED = Flag(name = "Padded", position = 3)
    >>> FLAG_PRIORITY = Flag(name = "Priority", position = 5)    
    >>> flags = [FLAG_ENDSTREAM, FLAG_ENDHEADERS, FLAG_PADDED, FLAG_PRIORITY]
    >>> f0 = Field(name="Flags", domain=Raw(nbBytes=1, endianness=AbstractType.ENDIAN_LITTLE), flags = flags)
    >>> m_endstream = RawMessage("\x01")
    >>> m_endheaders = RawMessage("\x04")
    >>> m_padded = RawMessage("\x08")
    >>> m_priority = RawMessage("\x20")
    >>> s = Symbol(fields=[f0], messages = [m_endstream, m_endheaders, m_padded, m_priority])
    >>> s.addEncodingFunction(TypeEncodingFunction(BitArray))
    >>> print s
    Flags               
    --------------------
    bitarray('00000001')
    bitarray('00000100')
    bitarray('00001000')
    bitarray('00100000')
    --------------------
    >>> print f0.getFlagValues()[0][FLAG_ENDSTREAM]
    True
    >>> print f0.getFlagValues()[0][FLAG_ENDHEADERS]
    False
    >>> print f0.getFlagValues()[1][FLAG_ENDHEADERS]
    True
    >>> print f0.getFlagValues()[1][FLAG_ENDSTREAM]
    False
    >>> print f0.getFlagValues()[2][FLAG_PADDED]
    True
    >>> print f0.getFlagValues()[2][FLAG_PRIORITY]
    False
    >>> print f0.getFlagValues()[3][FLAG_PRIORITY]
    True
    >>> print f0.getFlagValues()[3][FLAG_ENDSTREAM]
    False
    >>> # flag values can also be retrieved at the symbol level
    >>> print s.getFlagValues()[3][FLAG_PRIORITY]
    True
    
    """

    def __init__(self, name, position):
        self.name = name
        self.position = position

    def __str__(self):
        return self.name
    def __repr__(self):
        return self.__str__()

    @property
    def name(self):
        """Flag's name, cannot be None

        :type: :class:`str`
        :raises: :class:`TypeError`
        """

        return self.__name

    @name.setter
    @typeCheck(str)
    def name(self, name):
        if name is None:
            raise ValueError("Flag's name is Mandatory")
        self.__name = name

    @property
    def position(self):
        """Flag's position, cannot be Noneand must be >= 0

        :type: :class:`int`
        :raises: :class:`TypeError`
        """

        return self.__position

    @position.setter
    @typeCheck(int)
    def position(self, position):
        if position is None:
            raise ValueError("Flag's position is Mandatory")
        if position < 0:
            raise ValueError("Flag's position must be >= 0")
        self.__position = position
