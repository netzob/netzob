#!/usr/bin/env python

class PrismaState(object):

    def __init__(self, hist):
        self.hist = hist

    def __str__(self):
        return (len(self.hist)*'{}|')[:-1].format(*self.hist)

    def __repr__(self):
        return 'PrismaState('+(len(self.hist)*'{!r}|')[:-1].format(*self.hist)+')'
        #return 'PrismaState('+(len(self.hist)*'{r!}|')[:-1].format(*self.hist)+')'

    #direction: state -> obj
    def validTransition(self,obj):
        return isinstance(obj,PrismaState) and obj.hist[:-1] == self.hist[1:]

    def __eq__(self, obj):
        return isinstance(obj,PrismaState) and obj.hist == self.hist 

    def __hash__(self):
        h = hash(self.hist[0])
        for i in self.hist[1:]:
            h ^= hash(i)
        return h

    def getCurState(self):
        return self.hist[-1]
