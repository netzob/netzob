# -*- coding: utf-8 -*-

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
#| Standard library imports
#+---------------------------------------------------------------------------+
import uuid

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger


@NetzobLogger
class ApplicativeData(object):
    """An applicative data represents an information used over the application
    that generated the captured flows. It can be the player name or the user email address
    if these informations are used somehow by the protocol.

    An applicative data can be created out of any information.
    >>> from netzob.all import *
    >>> app = ApplicativeData("Username", ASCII("toto"))
    >>> print(app.name)
    Username

    >>> app1 = ApplicativeData("Email", ASCII("contact@netzob.org"))
    >>> print(app1.value)
    ASCII=contact@netzob.org ((0, 144))

    """

    def __init__(self, name, value, _id=None):
        self.name = name
        self.value = value
        if _id is None:
            _id = uuid.uuid4()
        self.id = _id

    @property
    def name(self):
        """The name of the applicative data.

        :type: :mod:`str`
        """
        return self.__name

    @name.setter
    @typeCheck(str)
    def name(self, name):
        if name is None:
            raise TypeError("Name cannot be None")
        self.__name = name

    @property
    def id(self):
        """The unique id of the applicative data.

        :type: :class:`uuid.UUID`
        """
        return self.__id

    @id.setter
    @typeCheck(uuid.UUID)
    def id(self, _id):
        if _id is None:
            raise TypeError("Id cannot be None")
        self.__id = _id

    @property
    def value(self):
        """The value of the applicative data.

        :type: object
        """
        return self.__value

    @value.setter
    def value(self, value):
        if value is None:
            raise TypeError("Value cannot be None")
        self.__value = value

    def __str__(self):
        """Redefine the string representation of the current
        applicative Data.

        :return: the string representation of the applicative data
        :rtype: str
        """
        return "Applicative Data: {0}={1})".format(self.name, self.value)

