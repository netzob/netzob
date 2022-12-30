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
#|       - Alexandre Pigné <alexandre.pigne (a) amossys.fr>                  |
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


class Constant(object):
    """
    Descriptor of a constant value

    >>> from netzob.all import *
    >>> default = Constant(1)
    >>> str(default)
    Traceback (most recent call last):
    NameError: Constant is unbound
    >>> class Foo:
    ...    A = default
    >>> str(default)
    'A'
    >>> Foo.A
    1
    >>> type(Foo.A)
    <class 'int'>
    >>> Foo.A += 1
    >>> Foo.A
    2
    >>> default
    Constant(1)
    """

    def __init__(self, value):
        self.__name = None
        self.__value = value

    def __str__(self):
        if self.__name is None:
            raise NameError("Constant is unbound")
        return self.__name

    def __repr__(self):
        return "Constant({!r})".format(self.__value)

    def __get__(self, obj, owner):
        return self.__value

    def __set__(self, obj, value):
        self.__value = value

    def __set_name__(self, obj, name):
        self.__name = name
