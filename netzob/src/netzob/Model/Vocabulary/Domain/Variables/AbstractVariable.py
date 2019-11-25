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
import abc

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+
from bitarray import bitarray

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck
from netzob.Model.Vocabulary.Domain.Variables.Scope import Scope
from netzob.Common.Utils.Decorators import public_api


class AbstractVariable(object):
    """A variable participates in the definition domain of a field.

    The AbstractVariable class defines the API of a variable, which can be a leaf or a node variable.
    """

    @public_api
    def __init__(self, varType, name=None, scope=None):
        """Constructor

        :param varType: the type of the variable. we highly recommend using the __class_.__name__
        :type varType: :class:`str`
        :keyword name: the optional name of the variable
        :raise: :class:`TypeError` if parameters type are not valid

        """
        if name is not None:
            self.name = name
        else:
            self.name = str(varType)

        self.__varType = varType
        if scope is None:
            scope = Scope.NONE
        self.scope = scope

        # Parent field
        self.field = None

        # Parent variable
        self.parent = None

    @public_api
    @abc.abstractmethod
    def copy(self, map_objects=None):
        """Clone the current object as well as all its dependencies. This
        method returns a new object of the same type.

        """
        raise NotImplementedError("Method clone() is not implemented")

    @abc.abstractmethod
    def specialize(self, originalSpecializingPath, preset=None):
        """Specializes the current variable."""
        raise NotImplementedError("Method specialize() is not implemented")

    @abc.abstractmethod
    def count(self, preset=None):
        raise NotImplementedError("Method count() is not implemented")

    @public_api
    @abc.abstractmethod
    def isnode(self):
        """Tells if the current variable is a node variable, which means it as children.

       :return: Return ``True`` if the current variable is a node variable.
       :rtype: :class:`bool`

        """
        raise NotImplementedError("Method isnode() is not implemented")

    def is_same_symbol(self, variable):
        """Tells if the current variable and the variable in parameter are
        part of the same symbol.

        """
        if self.field is None or self.field.getAncestor() is None:
            return False
        if variable.field is None or variable.field.getAncestor() is None:
            return False
        return self.field.getAncestor() == variable.field.getAncestor()

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

    #+---------------------------------------------------------------------------+
    #| Special Functions                                                         |
    #+---------------------------------------------------------------------------+
    def __key(self):
        return id(self)

    def __eq__(x, y):
        return x.__key() == y.__key()

    def __hash__(self):
        return self.__key()

    def __str__(self):
        """The str method, mostly for debugging purpose."""
        return "{0}".format(self.name)

    #+---------------------------------------------------------------------------+
    #| Properties                                                                |
    #+---------------------------------------------------------------------------+
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
    def scope(self):
        """The scope of the variable.

        :type: :class:`object`
        """
        return self.__scope

    @scope.setter  # type: ignore
    def scope(self, scope):
        if scope is None:
            raise ValueError("scope cannot be None")
        self.__scope = scope

    @property
    def field(self):
        return self.__field

    @field.setter  # type: ignore
    def field(self, field):
        self.__field = field

    @property
    def parent(self):
        return self.__parent

    @parent.setter  # type: ignore
    def parent(self, parent):
        self.__parent = parent
