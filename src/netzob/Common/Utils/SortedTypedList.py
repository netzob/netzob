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
from bintrees import AVLTree

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import NetzobLogger
from netzob.Common.Utils.SortableObject import SortableObject


@NetzobLogger
class SortedTypedList(object):
    """This data structure allows to sort and maintain sorted
    a list of objects inheriting from :class:`netzob.Common.Utils.SortableObject.SortableObject`.
    It uses an AVLTree proposed by :mod:`bintrees` to represent elements in the list.

    :TODO: The inner object __tree stores the given element using an AVLTree. Thus
    exposing new methods only requires the creation of a wrapper method in this class.

    >>> from netzob import *
    >>> from netzob.Common.Utils.SortedTypedList import SortedTypedList
    >>> msg1 = RawMessage("msg1", date=25.0)
    >>> msg2 = RawMessage("msg2", date=2.0)
    >>> msg3 = RawMessage("msg3", date=1456487548.0)
    >>> l = SortedTypedList(RawMessage, [msg2, msg3, msg1])
    >>> print l.values()[0]
    2.0 None>>None msg2

    >>> msg4 = RawMessage("msg4", date=145548.0)
    >>> l.add(msg4)
    >>> msg5 = RawMessage("msg5", date=14.0)
    >>> msg6 = RawMessage("msg6", date=1745645548.0)
    >>> l.addAll([msg5, msg6])
    >>> print l.values()[5]
    1745645548.0 None>>None msg6

    """

    def __init__(self, membersTypes, elements=None):
        self.membersTypes = membersTypes
        self.__tree = AVLTree()
        if elements is not None and len(elements) > 0:
            self._extend(elements)

    def add(self, element):
        """Insert in the proper place the specified element.

        :type: any object that comply with the typed of the current list and inherits from :class:`netzob.Common.Utils.SortableObject.SortableObject`.
        :raises: a TypeError if element is None or if its type doesn't comply with
                 the definition of the list.
        """
        if element is None:
            raise TypeError("Element cannot be None")
        self._extend([element])

    def addAll(self, elements):
        """Insert in their proper place all the specified element.

        :type: a list of any object that comply with the typed of the current list and inherits from :class:`netzob.Common.Utils.SortableObject.SortableObject`.
        :raises: a TypeError if element is None or if its type doesn't comply with
                 the definition of the list.
        """
        if elements is None:
            raise TypeError("Element cannot be None")
        self._extend(elements)

    def values(self):
        """Return a list sorted with the values of the current SortedTypedList.
        :warning: modifying this list has no effect on the SortedTypedList.

        :rtype: :mod:list
        """

        l = []
        for x in self.__tree.values():
            l.append(x)
        return l

    def clear(self):
        """remove all items from the list.
        It's a O(n) operation"""
        self.__tree.clear()

    def _extend(self, elements):
        """Add all the elements in the current list.

        :parameter elements: a list of :class:`netzob.Common.Utils.SortableObject.SortableObject` to insert.
        :raises: TypeError if something is wrong with the given elements
        """
        for e in elements:
            self._check(e)

        d = dict()
        for e in elements:
            d[e.priority()] = e
        self.__tree.update(d)

    def _check(self, v):
        if not isinstance(v, self.membersTypes):
            raise TypeError("Invalid type for argument, expecting: {0}, received : {1}".format(self.membersTypes, v.__class__.__name__))
        if not isinstance(v, SortableObject):
            raise TypeError("Objects inserted in a SortedTypedList must inherits from SortableObject class")

    def __str__(self):
        return ', \n'.join([str(v) for k, v in self.__tree.items()])

    def __repr__(self):
        return repr(self.__tree)
