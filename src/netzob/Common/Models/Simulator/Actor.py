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
import threading

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger
from netzob.Common.Models.Grammar.States.AbstractState import AbstractState
from netzob.Common.Models.Simulator.Channels.AbstractChannel import AbstractChannel


@NetzobLogger
class Actor(threading.Thread):
    """An actor is an instance of a traffic generator which given a grammar and a vocabular
    can generate and parse messages from a specified channel.

    For instance we can create two very simple network Actors which communicate together through
    a TCP channel and exchanges their names until one stops.
    The two actors are Alice and Bob. Alice is the initiator of the communication meaning she sends the input symbols
    while Bob answers with the output symbols of the grammar.
    The grammar is very simple, we first open the channel, and allow Alice to send random time "alice> hello". Bob answers everytime "bob> hello".
    It's Alice which decide to stop the communication.

    The communication happens over a TCP:8888 connection.

    >>> from netzob import *
    >>> # First we create the symbols
    >>> aliceSymbol = Symbol(name="Alice-Hello", fields=[Field("alice>hello")])
    >>> bobSymbol = Symbol(name="Bob-Hello", fields=[Field("bob>hello")])

    >>> # Create the grammar
    >>> s0 = State(name="S0")
    >>> s1 = State(name="S1")
    >>> s2 = State(name="S2")
    >>> openTransition = OpenChannelTransition(startState=s0, endState=s1, name="Open")
    >>> mainTransition = Transition(startState=s1, endState=s1, inputSymbol=aliceSymbol, outputSymbols=[bobSymbol], name="hello")
    >>> closeTransition = CloseChannelTransition(startState=s1, endState=s2, name="Close")

    >>> # create first actor: Alice the initiator of the communicatio
    >>> alice = Actor(initialState = s0, initiator = True, channel = TCPServer(listeningIP="127.0.0.1", listeningPort=8888))
    >>> bob = Actor(initialState = s0, initiator = False, channel = TCPClient(listeningIP="127.0.0.1", listeningPort=8888))

    >>> # start alice
    >>> alice.start()

    >>> # start bob
    >>> bob.start()

    >>> # wait alice and bob are no more alive
    >>> while alice.alive or bob.alive: time.sleep(5)
    >>> print "OK"



    """

    def __init__(self, initialState, initiator, channel):
        """
        Constructor of an actor

        :parameter initialState: the initial state where the actor will begin
        :type initialState: :class:`netzob.Common.Models.Grammar.States.AbstractState.AbstractState`
        :parameter initiator: indicates if the actor initiates the communication and emits the input symbol
        :type name: :class:`boolean`
        :parameter channel: the channel on which the communication will happen
        :type channel: :class:`netzob.Common.Models.Simulator.Channels.AbstractChannel.AbstractChannel`

        """
        self.initialState = initialState
        self.initiator = initiator
        self.channel = channel
        self.__stopEvent = threading.Event()

    def run(self):
        """Entry point of an actor executed when the thread is started."""

        currentState = self.initialState
        while not self.__stopEvent.isSet():
            try:
                if self.initiator:
                    currentState = currentState.executeAsInitiator(self.abstractionLayer)
                else:
                    currentState = currentState.executeAsNoInitiator(self.abstractionLayer)

                if currentState is None:
                    self._logger.warning("The execution of transition did not returned a state")
                    self.stop()

            except Exception:
                self._logger.warning("Exception raised when on the execution of state {0}.".format(currentState.name))
                self.stop()

        self._logger.info("Actor {0} has finished to execute".format(self.name))

    def stop(self):
        """Stop the current thread.

        This operation is not immediate because
        we try to stop the thread as cleanly as possible.

        To illustrate its usage, we create an infinite actor
        and stop it afterward

        >>> import time
        >>> from netzob import *
        >>> aliceSymbol = Symbol(name="Alice-Hello", fields=[Field("alice>hello")])

        >>> # Create the grammar
        >>> s0 = State(name="S0")
        >>> s1 = State(name="S1")
        >>> openTransition = OpenChannelTransition(startState=s0, endState=s1, name="Open")
        >>> mainTransition = Transition(startState=s1, endState=s1, inputSymbol=aliceSymbol, outputSymbols=[aliceSymbol], name="hello")

        >>> # create first actor: Alice the initiator of the communicatio
        >>> alice = Actor(initialState = s0, initiator = True, channel = TCPServer(listeningIP="127.0.0.1", listeningPort=8888))
        >>> bob = Actor(initialState = s0, initiator = True, channel = TCPClient(targetIP="127.0.0.1", targetPort=8888))

        >>> alice.start()
        >>> bob.start()

        >>> time.sleep(5)
        >>> bob.stop()
        >>> alice.stop()

        """
        self._logger.debug("Actor {0} has been requested to stop".format(self.name))
        self.__stopEvent.set()

    def isActive(self):
        """Computes if the current actor is active i.e. the grammar
        didn't stop to execute.

        :return: True is the actor has not finished
        :rtype: :class:`bool`
        """
        return self.__stopEvent.is_set()

    @property
    def initialState(self):
        """The initial state where the actor starts in the grammar.

        :type: :class:`netzob.Common.Models.Grammar.States.AbstractState.AbstractState`
        """
        return self.__initialsState

    @initialState.setter
    @typeCheck(AbstractState)
    def initialState(self, initialState):
        if initialState is None:
            raise TypeError("Initial state cannot be None")
        self.__initialState = initialState

    @property
    def initiator(self):
        """The actor is initiator means it starts to communicate
        and emits the input symbol registered on the transitions

        :type: :class:`bool`
        """
        return self.__initiator

    @initiator.setter
    @typeCheck(bool)
    def initiator(self, initiator):
        if initiator is None:
            raise TypeError("Initiator  cannot be None")
        self.__initiator = initiator

    @property
    def channel(self):
        """The communication channel on which the actor will communicate

        :type: :class:`netzob.Common.Models.Simulator.Channels.AbstractChannel.AbstractChannel`
        """
        return self.__channel

    @channel.setter
    @typeCheck(AbstractChannel)
    def channel(self, channel):
        if channel is None:
            raise TypeError("Channel cannot be None")
        self.__channel = channel
