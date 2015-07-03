#!/usr/bin/env python

class Template(object):

    def __init__(self,ID,state,count,fields,ntokens,content):
        self.ID = ID
        self.state = state
        self.count = count
        self.fields = fields
        self.content = content
        self.length = ntokens
        #in which context is template observed?
        self.hists = None

    def __str__(self):
        return 'ID {!s} {!s} {!s} {!s}'.format(self.ID,self.state,self.count, self.fields)#str(self.ID) +' '+ self.state

    def __repr__(self):
        return 'ID {!r} {!r}'.format(self.ID,self.state)

    def __hash__(self):
        return self.ID

    def __eq__(self,temp):
        return isinstance(temp,Template) and temp.ID == self.ID

