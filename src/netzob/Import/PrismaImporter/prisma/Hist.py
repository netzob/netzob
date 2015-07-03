#!/usr/bin/env python

#from PrismaState import PrismaState as P

class Hist(object):

    def __init__(self, prePreTempID, preTempID, curTempID):
        self.prePreTempID = prePreTempID
        self.preTempID = preTempID
        self.curTempID = curTempID

    def update(self, ID):
        return Hist(self.preTempID, self.curTempID, ID)

    def __str__(self):
        return str(self.prePreTempID) + ';' + str(self.preTempID) + ';' + str(self.curTempID)

    #remove later
    def __repr__(self):
        return 'Hist({!r},{!r},{!r})'.format(self.prePreTempID, self.preTempID, self.curTempID)

    def __hash__(self):
        return hash(str(self.prePreTempID)) ^ hash(str(self.preTempID)) ^ hash(str(self.curTempID))

    def __eq__(self,obj):
        return isinstance(obj,Hist) and obj.prePreTempID == self.prePreTempID and obj.preTempID == self.preTempID and obj.curTempID == self.curTempID

    def assembleHist(self,flag=False):
        allHist = []
        for ID1 in self.prePreTempID:
            for ID2 in self.preTempID:
                for ID3 in self.curTempID:
                    if flag == False:
                        allHist.append(Hist([ID1], [ID2], [ID3]))
                    else:
                        allHist.append(Hist(ID1, ID2, ID3))
        return allHist

    def getID(self,pos):
        if pos == -3:
            return self.prePreTempID
        if pos == -2:
            return self.preTempID
        return self.curTempID

    def differByPre(self,obj):
        return isinstance(obj,Hist) and obj.prePreTempID == self.prePreTempID and obj.curTempID == self.curTempID and obj.preTempID != self.preTempID
            
