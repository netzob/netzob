#!/usr/bin/env python

from .Rule import Rule

class DataRule(Rule):

    def __init__(self,hist,srcID,srcField,dstID,dstField,data):
        Rule.__init__(self,hist,srcID,srcField,dstID,dstField)
        self.data = data

    def __repr__(self):
        return '{!r} {!r} {!r} {!r} {!r} {!r}'.format(self.hist,self.srcID,self.srcField, self.dstID, self.dstField,self.data)

