#!/usr/bin/env python

#from PrismaState import PrismaState as P

class MarkovTransition(object):

    def __init__(self,curState,nextState):
        if not curState.validTransition(nextState):
            raise RuntimeError('invalid transition')
        self.curState = curState
        self.nextState = nextState

    def __str__(self):
        return str(self.curState) + ' -> ' + str(self.nextState)

    #remove later
    def __repr__(self):
        return 'Transition({!r},{!r})'.format(self.curState,self.nextState)

    def __hash__(self):
        return hash(self.nextState) ^ hash(self.curState)

    def __eq__(self,obj):
        return isinstance(obj,MarkovTransition) and obj.curState == self.curState and obj.nextState == self.nextState

