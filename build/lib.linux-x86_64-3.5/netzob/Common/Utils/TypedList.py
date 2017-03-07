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
import collections

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+


class TypedList(collections.MutableSequence):
    """A strong typed list based on collections.MutableSequence.

    The idea is to verify members type when editing the list. By using this
    class instead of the typical list, we enforce members type.

    >>> typedList = TypedList(str)
    >>> typedList.append("toto")
    >>> typedList.extend(["titi", "tata"])
    >>> len(typedList)
    3
    >>> typedList[1]
    'titi'
    >>> typedList.append(3)
    Traceback (most recent call last):
    TypeError: Invalid type for argument, expecting: <type 'str'>
    >>> typedList.extend(["tutu", 5])
    Traceback (most recent call last):
    TypeError: Invalid type for argument, expecting: <type 'str'>
    """

    def __init__(self, membersTypes, *args):
        self.membersTypes = membersTypes
        self.list = list()
        self.extend(list(args))

    def check(self, v):
        if not isinstance(v, self.membersTypes):
            raise TypeError("Invalid type for argument, expecting: {0}, received : {1}".format(self.membersTypes, v.__class__.__name__))

    def __len__(self):
        return len(self.list)

    def __getitem__(self, i):
        return self.list[i]

    def __delitem__(self, i):
        del self.list[i]

    def __setitem__(self, i, v):
        self.check(v)
        self.list[i] = v

    def insert(self, i, v):
        self.check(v)
        self.list.insert(i, v)

    def __str__(self):
        return str(',\n'.join([str(x) for x in self.list]))

    def __repr__(self):
        return repr(self.list)
