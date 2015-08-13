__author__ = 'dsmp'

from netzob.Common.Models.Grammar.States.State import State
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger

import random
import copy


@NetzobLogger
class PrismaState(State):
    def __init__(self, name=None):
        super(PrismaState, self).__init__(name=name)
        self.active = False
        self.trans = []
        self.usedTransitions = []
        self.invalid = False

    def executeAsInitiator(self, abstractionLayer):
        if abstractionLayer is None:
            raise TypeError("AbstractionLayer cannot be None")

        self._logger.debug("Execute state {0} as an initiator".format(self.name))

        self.active = True

        # Pick the next transition
        nextTransition = self.pickNextTransition()
        self._logger.info("Next transition: {0}.".format(nextTransition))

        if nextTransition is None:
            self.active = False
            raise Exception("No transition to execute, we stop here.")

        # Execute picked transition as an initiator
        try:
            nextState = nextTransition.executeAsInitiator(abstractionLayer)
            self._logger.info("Transition '{0}' leads to state: {1}.".format(str(nextTransition), str(nextState)))
        except Exception, e:
            self.active = False
            raise e

        if nextState is None:
            self.active = False
            raise Exception("The execution of transition {0} on state {1} did not return the next state.".format(str(nextTransition), self.name))

        self.active = False
        return nextState

    def pickNextTransition(self):
        # if len(self.transitions) == 1:
        #     return self.transitions[0]

        flag = True
        while flag:
            self._logger.info("picking transition")
            pos = list(set(self.trans)-set(self.usedTransitions))
            c = random.choice(pos)
            # is endState invalid?
            if c.endState.invalid:
                self._logger.critical("picked transition's endState invalid, removing {}".format(c.name))
                # remove transition to it
                self.trans.remove(c)
            else:
                flag = False
                self.usedTransitions.append(c)
        if c.invalid:
            self._logger.critical("picked transition invalid, removing {}".format(c.name))
            # self.memorizedTransitions.remove(c)
            self.trans.remove(c)
            if len(self.trans) == 0:
                self._logger.critical("invalidating state: {}".format(self.name))
                self.invalid = True
                if self.name.split('|')[-1] == 'START':
                    exit()
        # if c in self.trans:
        # self.usedTransitions.append(c)
        if len(self.trans) <= len(self.usedTransitions):
            self._logger.info("resetting transitions")
            self.usedTransitions = []
        return c

    def setTransitions(self, transitions):
        self.trans = transitions

    @property
    def transitions(self):
        return self.trans
