#!/usr/bin/env python

from .Rule import Rule


class CopyRule(Rule):
    def __init__(self, hist, ruleHist, srcID, srcField, dstID, dstField, typ, ptype, content):
        Rule.__init__(self, hist, ruleHist, srcID, srcField, dstID, dstField)
        self.typ = typ
        self.ptype = ptype
        self.content = content

    def __str__(self):
        return 'ID {!s} {!s} {!s} {!s} {!s}'.format(self.hist, self.srcID, self.srcField, self.dstID, self.dstField)

    def __repr__(self):
        return '{!r} {!r} {!r} {!r} {!r} {!r} {!r}'.format(self.hist, self.srcID, self.srcField, self.dstID,
                                                           self.dstField, self.ptype, self.content)

