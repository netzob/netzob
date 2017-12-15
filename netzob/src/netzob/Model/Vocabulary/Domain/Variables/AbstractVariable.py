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
#|       - Georges Bossert <georges.bossert (a) supelec.fr>                  |
#|       - Frédéric Guihéry <frederic.guihery (a) amossys.fr>                |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Standard library imports                                                  |
#+---------------------------------------------------------------------------+
import uuid
import abc
from typing import Iterable

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+
from bitarray import bitarray

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck
from netzob.Model.Vocabulary.Domain.Variables.SVAS import SVAS


class AbstractVariable(object):
    """A variable participates in the definition domain of a field.

    This class is abstract and so should not be instantiated directly.
    """

    def __init__(self, varType, varId=None, name=None, svas=None):
        """Constructor

        :param varType: the type of the variable. we highly recommend using the __class_.__name__
        :type varType: :class:`str`
        :keywork varId: the id of the variable
        :type varId: :class:`uuid.UUID`
        :keyword name: the optional name of the variable, if not set its the varId
        :raise: :class:`TypeError` if parameters type are not valid

        """
        if varId is None:
            self.id = uuid.uuid4()
        else:
            self.id = varId

        if name is not None:
            self.name = name
        else:
            self.name = str(self.id)

        self.__varType = varType
        if svas is None:
            svas = SVAS.EPHEMERAL
        self.svas = svas

        # Parent field
        self.field = None

    @abc.abstractmethod
    def specialize(self, originalSpecializingPath, fuzz=None):
        """Specializes the current variable."""
        raise NotImplementedError("Method specialize() is not implemented")

    @abc.abstractmethod
    def count(self, fuzz=None):
        raise NotImplementedError("Method count() is not implemented")

    @abc.abstractmethod
    def isnode(self):
        """Tells if the current variable is a node variable, which means it as children."""
        raise NotImplementedError("Method isnode() is not implemented")

    def getFixedBitSize(self):
        """Provide the length of a theoretical value that would be generated.
        It is not the length of an effective value but a prediction of its
        length in case this latter is fixed.

        :return: the theoretical length of a value generated from the underlying type
        :rtype: int
        :raise: ValueError in case the length is dynamic or could not be predicted
        """
        self._logger.debug("Determine the deterministic size of the value of "
                           "the variable")
        raise ValueError("Cannot determine a fixed size for variable '{}'"
                         .format(self))

    def check_may_miss_dependencies(self, variables):
        # type: (Iterable[AbstractVariable]) -> bool
        """
        Verify that this variable **may** fail to process against some variable
        (both specialization or abstraction).

        :param variables: an iterable of variables
        :type variables: Iterable[~netzob.Model.Vocabulary.Domain.Variables.AbstractVariable.AbstractVariable]
        :return: ``True`` if the result is not empty or no variable have been
                 passed as argument, else ``False``.
        :rtype: bool
        """
        return True

    #+---------------------------------------------------------------------------+
    #| Special Functions                                                         |
    #+---------------------------------------------------------------------------+
    def __key(self):
        return (self.id)

    def __eq__(x, y):
        try:
            return x.__key() == y.__key()
        except Exception as e:
            raise e

    def __hash__(self):
        return hash(self.__key())

    def __str__(self):
        """The str method, mostly for debugging purpose."""
        return "{0}".format(self.varType)

    #+---------------------------------------------------------------------------+
    #| Properties                                                                |
    #+---------------------------------------------------------------------------+
    @property
    def id(self):
        return self.__id

    @id.setter  # type: ignore
    @typeCheck(uuid.UUID)
    def id(self, varId):
        self.__id = varId

    @property
    def varType(self):
        """The type of the variable (Read-only).

        :type: :class:`str`
        :raises: :class:`AttributeError` on write attempt
        """
        return self.__varType

    @varType.setter  # type: ignore
    def varType(self, varType):
        raise AttributeError("Not allowed to modify the variable type")

    @property
    def name(self):
        """The name of the variable.

        :type: :class:`object`
        """
        return self.__name

    @name.setter  # type: ignore
    @typeCheck(str)
    def name(self, name):
        if name is None:
            raise ValueError("name cannot be None")
        name = name.strip()
        if len(name) == 0:
            raise ValueError(
                "name must be defined even after being trimmed (len>0)")
        self.__name = name

    @property
    def svas(self):
        """The svas of the variable.

        :type: :class:`object`
        """
        return self.__svas

    @svas.setter  # type: ignore
    def svas(self, svas):
        if svas is None:
            raise ValueError("svas cannot be None")
        self.__svas = svas

    @property
    def field(self):
        return self.__field

    @field.setter  # type: ignore
    def field(self, field):
        self.__field = field
