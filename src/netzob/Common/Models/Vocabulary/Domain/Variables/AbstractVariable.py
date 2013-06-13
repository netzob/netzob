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

    def __init__(self, varType, varId=None, name=None):
        """Constructor

        :param varType: the type of the variable. we highly recommend to use the __class_.__name__
        :type varType: :class:`str`
        :keywork varId: the id of the variable
        :type varId: :class:`uuid.UUID`
        :keyword name: the optional name of the variable, if not set its the varId
        :raise: :class:`TypeError` if parameters type are not valid

        """
        self.__logger = logging.getLogger(__name__)
        if varId is None:
            self.id = uuid.uuid4()
        else:
            self.id = varId

        if name is not None:
            self.name = name
        else:
            self.name = str(self.id)

        self.__varType = varType
        self.learnable = False
        self.mutable = False

    #+---------------------------------------------------------------------------+
    #| Generic methods for variables                                             |
    #+---------------------------------------------------------------------------+
    @abc.abstractmethod
    def isDefined(self, processingToken):
        """Tells if the variable is defined (i.e. has a value for a leaf, enough leaf have values for a node...)

        :type processingToken: :class:`netzob.Common.Models.Vocabulary.Domain.Variables.VariableProcessingTokens.AbstractVariableProcessingToken.AbstractVariableProcessingToken
        :param processingToken: a token which contains all critical information on this access.
        :rtype: boolean
        :return: True if the variable is defined.
        """
        raise NotImplementedError("The current variable does not implement 'isDefined'.")

    #+---------------------------------------------------------------------------+
    #| Visitor abstract method                                                   |
    #+---------------------------------------------------------------------------+
    @abc.abstractmethod
    def read(self, readingToken):
        """Grants a reading access to the variable. The value of readingToken is read bit by bit.

        :param readingToken: a token which contains all critical information on this reading access.
        :type readingToken: :class:`netzob.Common.Models.Vocabulary.Domain.Variables.VariableProcessingToken.VariableReadingToken.VariableReadingToken`
        """
        raise NotImplementedError("The current variable does not implement 'read'.")

    @abc.abstractmethod
    def write(self, writingToken):
        """Grants a writing access to the variable.
        A value is written according to encountered node variable rules and is stored in the provided writingToken.

        :param writingToken: a token which contains all critical information on this writing access.
        :type writingToken: :class:`netzob.Common.Models.Vocabulary.Domain.Variables.VariableProcessingToken.VariableWritingToken.VariableWritingToken`
        """
        raise NotImplementedError("The current variable does not implement 'write'.")

    #+---------------------------------------------------------------------------+
    #| Special Functions                                                         |
    #+---------------------------------------------------------------------------+
    def __str__(self):
        """The toString method, mostly for debugging purpose."""
        return "Variable {0} (mutable: {1}, learnable: {2})".format(self.name, str(self.mutable), str(self.learnable))

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
    def learnable(self):
        """tells if the variable can learned a value, initialized itself or not.

        >>> from netzob import *
        >>> alt = Alt()
        >>> alt.learnable
        False
        >>> alt.learnable = True
        >>> alt.learnable
        True
        >>> alt.learnable = "dqsqdsq"
        Traceback (most recent call last):
        ...
        TypeError: Invalid type for arguments, expecting: bool and received str
        >>> alt.learnable = None
        Traceback (most recent call last):
        ...
        TypeError: Learnable cannot be None
        >>> alt.learnable
        True

        :type:bool
        """
        return self.__learnable

    @learnable.setter
    @typeCheck(bool)
    def learnable(self, learnable):
        if learnable is None:
            raise TypeError("Learnable cannot be None")
        self.__learnable = learnable

    @property
    def mutable(self):
        """Tells if the variable can be modified or not.

        >>> from netzob import *
        >>> agg = Agg()
        >>> agg.mutable
        False
        >>> agg.mutable = True
        >>> agg.mutable
        True
        >>> agg.mutable = "dqsqdsq"
        Traceback (most recent call last):
        ...
        TypeError: Invalid type for arguments, expecting: bool and received str
        >>> agg.mutable = None
        Traceback (most recent call last):
        ...
        TypeError: Mutable cannot be None
        >>> agg.mutable
        True

        :type:bool
        """
        return self.__mutable

    @mutable.setter
    @typeCheck(bool)
    def mutable(self, mutable):
        if mutable is None:
            raise TypeError("Mutable cannot be None")
        self.__mutable = mutable
