from .PrismaState import PrismaState
from .MarkovTransition import MarkovTransition
from .MarkovModel import MarkovModel
from .Template import Template
from .TemplateContainer import TemplateContainer
from .RulesContainer import RulesContainer
from .Rule import Rule
from .DataRule import DataRule
from .CopyRule import CopyRule
from .Hist import Hist


def markovParse(filehandle):
    model = MarkovModel()
    for line in filehandle:
        line = line.split(',', 1)[0]
        left, right = line.split('->')
        curState = PrismaState(left.split('|'))
        nextState = PrismaState(right.split('|'))
        transition = MarkovTransition(curState, nextState)
        model.add(transition)
    return model


def templateParse(filehandle):
    templates = TemplateContainer()
    ntokens = 0
    for line in filehandle:
        if ntokens == 0:
            line = line.split()
            ID = int(line[1].split(':')[1])
            hist = line[2].split(':')[1].split('|')
            state = PrismaState(hist)
            count = int(line[3].split(':')[1])
            fields = line[5].split(':')[1].split(',')
            if fields == ['']:
                fields = []
            else:
                fields = list(map(int, fields))
            ntokens = int(line[4].split(':')[1])
            length = ntokens
            content = []
            if ntokens == 0:
                templates.add(Template(ID, state, count, fields, length, content))
        else:
            content.append(line.strip())
            ntokens -= 1
            if ntokens == 0:
                templates.add(Template(ID, state, count, fields, length, content))
    return templates


def ruleParse(filehandle):
    rules = RulesContainer()
    copyRules = RulesContainer()
    dataRules = RulesContainer()

    dataFlag = 0
    ptypeFlag = 0
    seqFlag = 0

    line1 = filehandle.readline()
    theHistLength = len(list(map(int, line1.split()[1].split(':')[1].split(';')))) - 1
    # print(theHistLength)
    while line1:
        line2 = filehandle.readline()
        if 'DataRule' in line1:
            dataFlag = 1
        if 'Copy' in line1:
            ptypeFlag = 1
        if 'Seq' in line1:
            seqFlag = 1
        line = line1.split()
        #TODO/done
        #dirty fix on mutlimodel stuff...
        hist = list(map(int, line[1].split(':')[1].split(';')))
        hist = [[i] for i in hist]
        #NOTE 
        dstID = hist[-1]
        ruleHist = Hist(hist=hist)
        hist = Hist(hist=hist[:-1])
        srcID = int(line[2].split(':')[1])
        srcField = int(line[3].split(':')[1])
        dstField = int(line[4].split(':')[1])
        if dataFlag == 1:
            data = line2.split(':')[1].split(',')
            data[-1] = data[-1].strip()
            dataRules.add(DataRule(hist, ruleHist, srcID, srcField, dstID, dstField, data))
            dataFlag = 0
        #handle ptype accurate
        elif ptypeFlag == 1:
            line2 = line2.strip().split(':')
            typ = line[5].split(':')[1]
            ptype = line2[1].split()[0].split('_')[2]
            if 'Complete' in line1:
                content = line2[2].split(',')
            else:
                content = line2[2]
            copyRules.add(CopyRule(hist, ruleHist, srcID, srcField, dstID, dstField, typ, ptype, content))
            ptypeFlag = 0
        elif seqFlag == 1:
            typ = line[5].split(':')[1]
            ptype = None
            content = line2.strip().split(':')[1]
            copyRules.add(CopyRule(hist, ruleHist, srcID, srcField, dstID, dstField, typ, ptype, content))
            seqFlag = 0
        else:  #assuming: dataFlag == 0 and ptypeFlag == 0:
            rules.add(Rule(hist, ruleHist, srcID, srcField, dstID, dstField))
        line1 = filehandle.readline()
    return rules, copyRules, dataRules, theHistLength

