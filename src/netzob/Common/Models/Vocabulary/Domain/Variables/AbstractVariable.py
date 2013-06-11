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
import abc
import logging
import uuid

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck


class AbstractVariable(object):
    """A variable participates in the definition domain of a field.

    This class is abstract and so should not be instanciated directly.
    """

    __metaclass__ = abc.ABCMeta

    def __init__(self, varType, varId=None):
        """Constructor

        :param varType: the type of the variable. we highly recommend to use the __class_.__name__
        :type varType: :class:`str`
        :keywork varId: the id of the variable
        :type varId: :class:`uuid.UUID`
        :raise: :class:`TypeError` if parameters type are not valid

        """
        self.__logger = logging.getLogger(__name__)
        self.__varType = varType
        if varId is None:
            self.id = uuid.uuid4()
        else:
            self.id = varId

    @property
    def id(self):
        return self.__id

    @id.setter
    @typeCheck(uuid.UUID)
    def id(self, varId):
        self.__id = varId

    @property
    def varType(self):
        """The type of the variable (Read-only).

        :type: `str`
        :raises: :class:`AttributeError` on write attempt
        """
        return self.__varType

    @varType.setter
    def varType(self, varType):
        raise AttributeError("Not allowed to modify the variable type")
