#-*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|          01001110 01100101 01110100 01111010 01101111 01100010            |
#|                                                                           |
#|               Netzob : Inferring communication protocols                  |
#+---------------------------------------------------------------------------+
#| Copyright (C) 2015 Christian Bruns                                        |
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
#|       - Christian Bruns <christian.bruns1 (a) stud.uni-goettingen.de>     |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Standard library imports                                                  |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+

import random

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+

from netzob.Common.Models.Grammar.States.State import State
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger

@NetzobLogger
class PrismaState(State):
    """ Performs like original State; incorporates features of invalidating a Transitions Symbol (if it is to faulty)
        and even the Transition itself, if it has no Symbols left. Also removes itself, if no Transitions are left.

    """
    def __init__(self, name=None):
        super(PrismaState, self).__init__(name=name)
        self.active = False
        self.trans = []
        self.usedTransitions = []
        self.invalid = False

    def executeAsInitiator(self, abstractionLayer):
        if abstractionLayer is None:
            raise TypeError("AbstractionLayer cannot be None")

        self.active = True

        # Pick the next transition
        nextTransition = self.pickNextTransition()
        if nextTransition is None:
            self.active = False
            raise Exception("No transition to execute, we stop here.")

        # Execute picked transition as an initiator
        try:
            nextState = nextTransition.executeAsInitiator(abstractionLayer)
        except Exception, e:
            self.active = False
            raise e

        if nextState is None:
            self.active = False
            raise Exception("The execution of transition {0} on state {1} did not return the next state.".format(str(nextTransition), self.name))

        self.active = False
        return nextState

    def pickNextTransition(self):
        """ Advanced picking method; incorporates features of deleting Symbols from Transitions, Transitions from
            current State and current State itself. Picks Transitions cyclically.

        :return: the Transition to be executed
        """
        flag = True
        while flag:
            pos = list(set(self.trans)-set(self.usedTransitions))
            c = random.choice(pos)
            # is endState invalid?
            if c.endState.invalid:
                # remove transition to it
                self.trans.remove(c)
            else:
                flag = False
                self.usedTransitions.append(c)
        if c.invalid:
            self.trans.remove(c)
            if len(self.trans) == 0:
                self.invalid = True
                if self.name.split('|')[-1] == 'START':
                    exit()
        # if c in self.trans:
        if len(self.trans) <= len(self.usedTransitions):
            self.usedTransitions = []
        return c

    def setTransitions(self, transitions):
        self.trans = transitions

    @property
    def transitions(self):
        return self.trans
