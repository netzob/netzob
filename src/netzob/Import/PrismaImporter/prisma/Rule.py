#!/usr/bin/env python

class Rule(object):

    def __init__(self,hist,srcID,srcField,dstID,dstField):
        self.hist = hist
        self.srcID = srcID
        self.srcField = srcField
        self.dstID = dstID
        self.dstField = dstField

    def __str__(self):
        return 'ID {!s} {!s} {!s} {!s} {!s}'.format(self.hist,self.srcID,self.srcField, self.dstID, self.dstField)

    def __repr__(self):
        return '{!r} {!r} {!r} {!r} {!r}'.format(self.hist,self.srcID,self.srcField, self.dstID, self.dstField)

