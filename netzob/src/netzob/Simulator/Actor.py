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
import threading

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger
from netzob.Model.Grammar.States.AbstractState import AbstractState
from netzob.Model.Grammar.Automata import Automata
from netzob.Simulator.AbstractionLayer import AbstractionLayer


@NetzobLogger
class Actor(threading.Thread):
    """An actor is an instance of a traffic generator which, given a
    grammar and a vocabular, can visit the underlying automaton, and
    generate and parse messages from a specified abstraction layer.

    The Actor constructor expects some parameters:

    :param automata: The automaton the actor will visit.
    :param initiator: This flag indicates if the actor initiates the
                      communication and emits the input symbol, or
                      waits for another peer to initiate the
                      connection. Default value is True.
    :param abstractionLayer: The underlying abstraction layer used to abstract and specialize symbols.
    :type automata: :class:`Automata <netzob.Model.Grammar.Automata.Automata>`, required
    :type initiator: :class:`boolean`, required
    :type abstractionLayer: :class:`AbstractionLayer <netzob.Simulator.AbstractionLayer.AbstractionLayer>`, required


    **Complete example**

    For instance we can create two very simple network Actors which
    communicate together through a TCP channel and exchange their
    names until one stops.

    The two actors are Alice and Bob. Alice is the initiator of the
    communication meaning she sends the input symbols while Bob
    answers with the output symbols of the grammar. The grammar is
    very simple, we first open the channel, and allow Alice to send
    random time "alice> hello". Bob answers everytime "bob> hello".
    It's Alice who decides to stop the communication.

    >>> from netzob.all import *
    >>> import time

    >>> # First we create the symbols
    >>> aliceSymbol = Symbol(name="Alice-Hello", fields=[Field("alice>hello")])
    >>> bobSymbol = Symbol(name="Bob-Hello", fields=[Field("bob>hello")])
    >>> symbolList = [aliceSymbol, bobSymbol]

    >>> # Create the grammar
    >>> s0 = State(name="S0")
    >>> s1 = State(name="S1")
    >>> s2 = State(name="S2")
    >>> openTransition = OpenChannelTransition(startState=s0, endState=s1, name="Open")
    >>> mainTransition = Transition(startState=s1,
    ...                             endState=s1,
    ...                             inputSymbol=aliceSymbol,
    ...                             outputSymbols=[bobSymbol], name="hello")
    >>> closeTransition = CloseChannelTransition(startState=s1, endState=s2, name="Close")
    >>> automata = Automata(s0, symbolList)

    >>> # Create actors: Alice (a server) and Bob (a client)
    >>> channel = UDPServer(localIP="127.0.0.1", localPort=8887)
    >>> abstractionLayer = AbstractionLayer(channel, symbolList)
    >>> alice = Actor(automata = automata, initiator = False, abstractionLayer=abstractionLayer)

    >>> channel = UDPClient(remoteIP="127.0.0.1", remotePort=8887)
    >>> abstractionLayer = AbstractionLayer(channel, symbolList)
    >>> bob = Actor(automata = automata, initiator = True, abstractionLayer=abstractionLayer)

    >>> alice.start()
    >>> bob.start()

    >>> time.sleep(2)

    >>> bob.stop()
    >>> alice.stop()

    """

    def __init__(self, automata, initiator, abstractionLayer):
        super(Actor, self).__init__()
        self.automata = automata
        self.initiator = initiator
        self.abstractionLayer = abstractionLayer
        self.__stopEvent = threading.Event()

    def run(self):
        """Start the visit of the automaton from its initial state."""

        currentState = self.automata.initialState
        while not self.__stopEvent.isSet():
            try:
                self._logger.debug("Current state: {0}.".format(currentState))
                if self.initiator:
                    currentState = currentState.executeAsInitiator(
                        self.abstractionLayer)
                else:
                    currentState = currentState.executeAsNotInitiator(
                        self.abstractionLayer)

                if currentState is None:
                    self._logger.warning(
                        "The execution of transition did not returned a state")
                    self.stop()

            except Exception as e:
                self._logger.warning(
                    "Exception raised when on the execution of state {0}.".
                    format(currentState.name))
                self._logger.warning("Exception error: {0}".format(str(e)))

                self.stop()

        self._logger.debug(
            "Actor {0} has finished to execute".format(self.name))

    def stop(self):
        """Stop the visit of the automaton.

        This operation is not immediate because we try to stop the
        thread as cleanly as possible.

        """
        self.__stopEvent.set()
        try:
            self.abstractionLayer.closeChannel()
        except Exception as e:
            self._logger.error(e)

    def isActive(self):
        """Tell if the current actor is active (i.e. if the automaton
        visit is still processing).

        :return: True is the actor has not finished.
        :rtype: :class:`bool`
        """
        return not self.__stopEvent.is_set()

    @property
    def automata(self):
        return self.__automata

    @automata.setter
    @typeCheck(Automata)
    def automata(self, automata):
        if automata is None:
            raise TypeError("Automata cannot be None")
        self.__automata = automata

    @property
    def initiator(self):
        return self.__initiator

    @initiator.setter
    @typeCheck(bool)
    def initiator(self, initiator):
        if initiator is None:
            raise TypeError("Initiator  cannot be None")
        self.__initiator = initiator

    @property
    def abstractionLayer(self):
        return self.__abstractionLayer

    @abstractionLayer.setter
    @typeCheck(AbstractionLayer)
    def abstractionLayer(self, abstractionLayer):
        if abstractionLayer is None:
            raise TypeError("AbstractionLayer cannot be None")
        self.__abstractionLayer = abstractionLayer
