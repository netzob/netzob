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

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck


class AbstractState(object, metaclass=abc.ABCMeta):
    """This class represents the interface of the abstract state. Every
    kind of state usable in the grammar of a protocol should inherit
    from this abstract class.

    The AbstractState constructor expects some parameters:

    :param name: The name of the state. The default value is `None`.
    :type name: :class:`str`, optional

    """

    def __init__(self, name=None):
        self.__id = uuid.uuid4()
        self.name = name
        self.active = False
        self.__cbk = None

    def __str__(self):
        return str(self.name)

    # Execution abstract methods

    @abc.abstractmethod
    def executeAsInitiator(self, abstractionLayer):
        pass

    @abc.abstractmethod
    def executeAsNotInitiator(self, abstractionLayer):
        pass

    # Properties

    @property
    def id(self):
        """Unique identifier of the state

        :type: :class:`uuid.UUID`
        :raise: TypeError if not valid
        """
        return self.__id

    @id.setter
    @typeCheck(uuid.UUID)
    def id(self, _id):
        if id is None:
            raise TypeError("id cannot be None")
        self.__id = _id

    @property
    def name(self):
        """Optional Name of the state

        :type: str
        :raise: TypeError is not an str
        """
        return self.__name

    @name.setter
    @typeCheck(str)
    def name(self, name):
        if name is None:
            name = "State"

        self.__name = name

    @property
    def active(self):
        """Represents the current execution status of the state.
        If a state is active, it means none of its transitions has yet
        been fully executed and that its the current state.

        :type: :class:`bool`
        """
        return self.__active

    @active.setter
    @typeCheck(bool)
    def active(self, active):
        if active is None:
            raise TypeError("The active info cannot be None")
        self.__active = active

    @property
    def cbk(self):
        """Function called during state execution.

        If a callback function is defined, we call it in order to
        execute an external program that may change the selected
        transition.

        The callable function should have the following prototype: 

        ``def cbk_function(possibleTransitions, selectedTransitionIndex):``

        Where:

        * ``possibleTransitions`` corresponds to the :class:`list` of possible transitions (:class:`Transition <netzob.Model.Grammar.Transitions.Transition.Transition>`) from the current state.
        * ``selectedTransitionIndex`` corresponds to the original selected transition index.

        The callback function should return an integer corresponding
        to the selected transition (that could have changed by the
        executed program).

        :type: :class:`func`
        :raise: TypeError if cbk is not a callable function

        """
        return self.__cbk

    @cbk.setter
    def cbk(self, cbk):
        if not callable(cbk):
            raise TypeError("'cbk' should be a callable function")
        self.__cbk = cbk
