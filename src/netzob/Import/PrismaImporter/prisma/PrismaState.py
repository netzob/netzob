#!/usr/bin/env python

class PrismaState(object):

    def __init__(self,preState,curState):
        self.preState = preState
        self.curState = curState

    def __str__(self):
        return self.preState + '|' + self.curState

    def __repr__(self):
        return 'PrismaState({!r},{!r})'.format(self.preState,self.curState)

    def validTransition(self,obj):
        return isinstance(obj,PrismaState) and obj.preState == self.curState

    def __eq__(self, obj):
        return isinstance(obj,PrismaState) and obj.preState == self.preState and obj.curState == self.curState

    def __hash__(self):
        return hash(self.preState) ^ hash(self.curState)

    def getCurState(self):
        return self.curState
