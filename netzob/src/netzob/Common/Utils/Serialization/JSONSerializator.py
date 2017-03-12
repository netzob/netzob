# -*- coding: utf-8 -*-

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
#| Standard library imports
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+
import inspect

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+


class JSONSerializator(object):
    @staticmethod
    def serialize(obj):
        """Serialize the specified object under a specific
        JSON format.
        It inspects the specified object to search for attributes to
        serialize.

        >>> from netzob.all import *
        >>> msg = RawMessage("hello")
        >>> print(JSONSerializator.serialize(msg))

        It's not possible to serialize a None object

        >>> JSONSerializator.serialize(None)
        Traceback (most recent call last):
        ...
        TypeError: Cannot serialize a None object
    
        :parameter obj: the object to serialize
        :type obj: :class:`object`
        :return: the object serialized in JSON
        :rtype: :class:`str`
        """

        if obj is None:
            raise TypeError("Cannot serialize a None object")

        typeObj = type(obj)
        props = []
        for entry in list(typeObj.__dict__.values()):
            if inspect.isdatadescriptor(entry):
                props.append(entry)

        for prop in props:
            print(prop.fget.__name__, prop.fget)

        return "TEST"
