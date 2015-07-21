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

    def modelEnhancer(self, depth=0):
        import copy
        goOn = False
        # for k,v in self.model.items():
        #     print(k, '--> ', v)
        # print()
        cpy = copy.deepcopy(self.model)
        for key in cpy.keys():
            for value in self.model[key]:
                if 'END' in value.getCurState():
                    # print('removing value ', value, 'from key', key)
                    self.model[key].remove(value)
            if self.model[key] == []:
                del self.model[key]
                # print('removing key ',key, 'because it is empty')
                cpyDash = copy.deepcopy(self.model)
                for otherKey in cpyDash.keys():
                    if key in self.model[otherKey]:
                        goOn = True
                        # print('removing from key', otherKey, 'value', key)
                        self.model[otherKey].remove(key)
        if goOn:
            self.modelEnhancer(depth+1)

