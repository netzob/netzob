#!/usr/bin/env python

class TemplateContainer(object):

    def __init__(self):
        self.IDtoTemp = {}
        self.stateToID = {}

    def __str__(self):
        s = ''
        for key in self.IDtoTemp:
            for value in self.IDtoTemp[key]:
                s += str(value) + ', '
        return s[:-2]

    def __getitem__(self,key):
        if isinstance(key,int):
            return self.IDtoTemp[key]
        return self.stateToID[key]

    def __iter__(self):
        return self.IDtoTemp.items().__iter__()

    def keys(self):
        return self.IDtoTemp.keys()

    def add(self,template):
        self.IDtoTemp[template.ID] =  template
        if template.state not in self.stateToID:
            self.stateToID[template.state] = []
        self.stateToID[template.state].append(template.ID)

