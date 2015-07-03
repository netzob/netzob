#!/usr/bin/env python

#from PrismaState import PrismaState as P

class MarkovModel(object):

    def __init__(self):
        self.model = {}

    def __str__(self):
        s = ''
        for key in self.model:
            for value in self.model[key]:
                s += str(value) + ', '
        return s[:-2]

    def __getitem__(self,key):
        return self.model[key]

    def keys(self):
        return self.model.keys()

    def __iter__(self):
        return self.model.items().__iter__()

    def add(self,mtrans):
        if mtrans.curState not in self.model:
            self.model[mtrans.curState] = []
        self.model[mtrans.curState].append(mtrans.nextState)

