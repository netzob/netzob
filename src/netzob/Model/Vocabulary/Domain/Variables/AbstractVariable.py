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
import abc
import uuid

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

    This class is abstract and so should not be instanciated directly.
    """

    def __init__(self, varType, varId=None, name=None, svas=None):
        """Constructor

        :param varType: the type of the variable. we highly recommend to use the __class_.__name__
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
        # A list containing all variables which value is bind to the value of this variable.
        self.__boundedVariables = []
        # An integer list which contain the index of each segment this variable is responsible for (they have been created from its)
        self.__tokenChoppedIndexes = []
        # The variables just above the current variable in the tree representation.
        self.__fathers = []


    #+---------------------------------------------------------------------------+
    #| Special Functions                                                         |
    #+---------------------------------------------------------------------------+
    def __key(self):
        return (self.id)

    def __eq__(x, y):
        return x.__key() == y.__key()

    def __hash__(self):
        return hash(self.__key())

    def __str__(self):
        """The str method, mostly for debugging purpose."""
        return "{0}".format(self.varType)

    # @abc.abstractmethod
    # def _str_debug(self, deepness=0):
    #     """Returns a string which denotes
    #     the current domain definition using a tree display"""

    #+---------------------------------------------------------------------------+
    #| Properties                                                                |
    #+---------------------------------------------------------------------------+
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

    @property
    def name(self):
        """The name of the variable.

        :type: :class:`object`
        """
        return self.__name

    @name.setter
    @typeCheck(str)
    def name(self, name):
        if name is None:
            raise ValueError("name cannot be None")
        name = name.strip()
        if len(name) == 0:
            raise ValueError("name must be defined even after being trimmed (len>0)")
        self.__name = name

    @property
    def svas(self):
        """The svas of the variable.

        :type: :class:`object`
        """
        return self.__svas

    @svas.setter
    def svas(self, svas):
        if svas is None:
            raise ValueError("svas cannot be None")
        self.__svas = svas

        

    # @property
    # def learnable(self):
    #     """tells if the variable can learned a value, initialized itself or not.

    #     >>> from netzob.all import *
    #     >>> alt = Alt()
    #     >>> alt.learnable
    #     False
    #     >>> alt.learnable = True
    #     >>> alt.learnable
    #     True
    #     >>> alt.learnable = "dqsqdsq"
    #     Traceback (most recent call last):
    #     ...
    #     TypeError: Invalid type for arguments, expecting: bool and received str
    #     >>> alt.learnable = None
    #     Traceback (most recent call last):
    #     ...
    #     TypeError: Learnable cannot be None
    #     >>> alt.learnable
    #     True

    #     :type:bool
    #     """
    #     return self.__learnable

    # @learnable.setter
    # @typeCheck(bool)
    # def learnable(self, learnable):
    #     if learnable is None:
    #         raise TypeError("Learnable cannot be None")
    #     self.__learnable = learnable

    # @property
    # def mutable(self):
    #     """Tells if the variable can be modified or not.

    #     >>> from netzob.all import *
    #     >>> agg = Agg()
    #     >>> agg.mutable
    #     False
    #     >>> agg.mutable = True
    #     >>> agg.mutable
    #     True
    #     >>> agg.mutable = "dqsqdsq"
    #     Traceback (most recent call last):
    #     ...
    #     TypeError: Invalid type for arguments, expecting: bool and received str
    #     >>> agg.mutable = None
    #     Traceback (most recent call last):
    #     ...
    #     TypeError: Mutable cannot be None
    #     >>> agg.mutable
    #     True

    #     :type:bool
    #     """
    #     return self.__mutable

    # @mutable.setter
    # @typeCheck(bool)
    # def mutable(self, mutable):
    #     if mutable is None:
    #         raise TypeError("Mutable cannot be None")
    #     self.__mutable = mutable

    # @property
    # def boundedVariables(self):
    #     """A list containing all variables which value is bind to the value of this variable.

    #     >>> from netzob.all import *
    #     >>> d1 = Data(ASCII())
    #     >>> len(d1.boundedVariables)
    #     0
    #     >>> d2 = Data(Integer())
    #     >>> len(d2.boundedVariables)
    #     0
    #     >>> d3 = Data(Raw())
    #     >>> len(d3.boundedVariables)
    #     0
    #     >>> d1.boundedVariables.append(d2)
    #     >>> d1.boundedVariables.append(d3)
    #     >>> len(d1.boundedVariables)
    #     2

    #     :type: list of :class:`netzob.Model.Vocabulary.Domain.Variables.AbstractVariable.AbstractVariable`
    #     :raise: TypeError if parameter is not valid
    #     """
    #     return self.__boundedVariables

    # @boundedVariables.setter
    # def boundedVariables(self, boundedVariables):
    #     for bound in boundedVariables:
    #         if not isinstance(bound, AbstractVariable):
    #             raise TypeError("BoundedVariables must be AbstractVariables")

    #     self.__boundedVariables = []
    #     for bound in boundedVariables:
    #         self.__boundedVariables.append(bound)

    # @property
    # def tokenChoppedIndex(self):
    #     """An integer list which contain the index of each segment
    #     this variable is responsible for (they have been created from its)

    #     .. warning:: use the method addTokenChoppedIndex() to add an index.

    #     :type: list of int
    #     """
    #     return self.__tokenChoppedIndexes

    # @tokenChoppedIndex.setter
    # def tokenChoppedIndex(self, tokenChoppedIndex):
    #     for index in tokenChoppedIndex:
    #         if not isinstance(index, int):
    #             raise TypeError("tokenChoppedIndex must be a list of int")
    #     self.__tokenChoppedIndexes = []
    #     for index in tokenChoppedIndex:
    #         self.__tokenChoppedIndexes.append(index)

    # @property
    # def fathers(self):
    #     """ The variables just above the current variable in the tree representation.

    #     :type: list of :class:`netzob.Model.Vocabulary.Domain.Variables.AbstractVariable.AbstractVariables
    #     """
    #     return self.__fathers

    # @fathers.setter
    # def fathers(self, fathers):
    #     self.__fathers = []
    #     for father in fathers:
    #         self.__fathers.append(father)
