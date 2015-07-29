#!/usr/bin/env python

# from PrismaState import PrismaState as P

class Hist(object):
    #def __init__(self, prePreTempID, preTempID, curTempID):
    #    self.prePreTempID = prePreTempID
    #    self.preTempID = preTempID
    #    self.curTempID = curTempID

    def __init__(self, hist=None, updateID=None):
        if updateID != None:
            self.theHist = hist.theHist[1:] + [updateID]
        elif hist != None:
            self.theHist = hist
            #self.prePreTempID = self.theHist[-3]
            #self.preTempID = self.theHist[-2]
            #self.curTempID = self.theHist[-1]

    def update(self, ID):
        return Hist(self, updateID=ID)

    def getID(self, depth=-1):
        return self.theHist[depth]

    def __str__(self):
        s = ''
        for i in self.theHist:
            s += str(i) + ' ; '
        return s[:-3]
        #return str(self.prePreTempID) + ';' + str(self.preTempID) + ';' + str(self.curTempID)

    #remove later
    def __repr__(self):
        #return 'Hist({!r},{!r},{!r})'.format(self.prePreTempID, self.preTempID, self.curTempID)
        rep = ''
        for i in self.theHist:
            rep += str(i) + ';'
        return 'Hist(' + rep[:-1] + ')'

    def __hash__(self):
        #return hash(str(self.prePreTempID)) ^ hash(str(self.preTempID)) ^ hash(str(self.curTempID))
        h = hash(self.theHist[0][0])
        for i in self.theHist[1:]:
            h ^= hash(i[0])
        return h

    def __eq__(self, obj):
        #return isinstance(obj,Hist) and obj.prePreTempID == self.prePreTempID and obj.preTempID == self.preTempID and obj.curTempID == self.curTempID
        return isinstance(obj, Hist) and obj.theHist == self.theHist

    def assembleHist(self, lenHist, flag=False):
        allHist = [Hist(lenHist * [-3])]
        remain = self.theHist
        while len(remain) != 0:
            allHist = crossProd(remain[0], allHist)
            remain = remain[1:]
        return allHist


def crossProd(longList, allHist):
    histContain = []
    for ID in longList:
        for hists in allHist:
            histContain.append(hists.update([ID]))
    return histContain
