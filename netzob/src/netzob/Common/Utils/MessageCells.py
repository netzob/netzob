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
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| File contributors :                                                       |
#|       - Georges Bossert <gbossert (a) miskin.fr>                          |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Standard library imports                                                  |
#+---------------------------------------------------------------------------+
from collections import OrderedDict

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import NetzobLogger


@NetzobLogger
class MessageCells(OrderedDict):
    """
    This data structure overwrites the notion of OrderedDict to support additionnal attributes
    such as 'headers'. This data structure has been created for the `AbstractField.getMessageCells` method

    >>> from netzob.all import *
    >>> m = MessageCells()
    >>> m[1] = "a"
    >>> m[2] = "b"
    >>> m[1] = m[2]
    >>> list(m.items())
    [(1, 'b'), (2, 'b')]
    >>> m.fields = [Field(name="f1"), Field(name="f2")]
    >>> [f.name for f in m.fields]
    ['f1', 'f2']

    """

    def __init__(self):
        super().__init__()
        self.fields = []

    @property
    def fields(self):
        """Fields that participate in the message cells columns"""
        return self.__fields

    @fields.setter
    def fields(self, fields):
        self.__fields = []
        for f in fields:
            self.__fields.append(f)
            
