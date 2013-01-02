# -*- coding: utf-8 -*-

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
#| Standard library imports
#+---------------------------------------------------------------------------+
from locale import gettext as _

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+


class PropertyList(object):
    """This class allow to store Property items that are internally
    stored in a dict(). Items are accessible like any other list or
    dict."""

    def __init__(self):
        self._properties = {}

    def append(self, prop):
        self._properties.update({prop.getName(): prop})

    def keys(self):
        return self._properties.keys()

    def __getitem__(self, name):
        try:
            return self._properties[name]
        except KeyError:
            raise KeyError("Unknown property: {0}".format(name))

    def __setitem__(self, name, value):
        self._properties.update({name: value})

    def __iter__(self):
        for i in self._properties:
            yield self._properties[i]

    def __contains__(self, key):
        return key in self._properties

    def keys(self):
        'PropertyList.keys() -> list of keys in PropertyList'
        return list(self._properties)

    def values(self):
        'PropertyList.values() -> list of values in PropertyList'
        for key in self:
            print key

        return [self[key.getName()] for key in self]

    def clear(self):
        self._properties.clear()
