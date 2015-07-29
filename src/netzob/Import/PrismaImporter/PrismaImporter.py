import prisma
import copy
import os

from netzob.Common.Models.Vocabulary.PrismaSymbol import PrismaSymbol
from netzob.Common.Models.Vocabulary.EmptySymbol import EmptySymbol
from netzob.Common.Models.Vocabulary.PrismaField import PrismaField
from netzob.Common.Models.Vocabulary.Messages.RawMessage import RawMessage
from netzob.Common.Models.Grammar.States.State import State
from netzob.Common.Models.Grammar.Transitions.PrismaTransition import PrismaTransition
from netzob.Common.Models.Grammar.Automata import Automata
from netzob.Common.Models.Types.ASCII import ASCII

from urllib import unquote

from netzob.Common.Models.Simulator.PrismaLayer import PrismaLayer
from netzob.Common.Models.Simulator.Channels.TCPClient import TCPClient


class PrismaImporter(object):
    def __init__(self):
        print("Hello Netzob, this is Prisma...\nI'm gonna take over...\nDon't make it harder than necessary.\n")
        self.rules = None
        self.model = None
        self.templates = None
        self.absoluteFields = {}
        self.brokenStates = None
        self.horizonLength = None

        # Symbols and States
        self.Symbols = None
        self.States = []
        self.Rules = {}
        self.copyRules = {}
        self.dataRules = {}

        # automaton, abstractionLayer, initialState
        self.Automaton = None
        self.PrismaLayer = None
        self.Start = None

    def getPrisma(self, path, enhance=False):
        templates, model, rules = None, None, None
        for files in os.listdir(path):
            if 'template' in files:
                f = open('{0}/{1}'.format(path, files), 'r')
                templates = prisma.templateParse(f)
                self.templates = templates
                self.computeABSfields()
                f.close()
                print('read templates')
            if 'markov' in files:
                f = open('{0}/{1}'.format(path, files), 'r')
                model = prisma.markovParse(f)
                self.model = model
                f.close()
                if enhance:
                    self.model.modelEnhancer()
                print('read model')
            if 'rules' in files:
                f = open('{0}/{1}'.format(path, files), 'r')
                rules = prisma.ruleParse(f)
                self.horizonLength = rules[-1]
                self.rules = rules[:-1]
                f.close()
                print('read rules')
            if rules and model and templates:
                break
        if not rules or not model or not templates:
            print("Big Problem: Couldn't find some of the files")
            return -1
        self.computeRules()
        return

    def convertPrisma2Netzob(self):
        self.Symbols = self.createSymbols()

        # get INITIAL state
        for k in self.model.model.keys():
            if k.getCurState() == 'START':
                break
        # create States beginning at initial
        cpy = copy.deepcopy(self.model)
        self.brokenStates = self.createStates(k)
        self.model = cpy
        for state in self.brokenStates:
            self.States.append(self.createPrismaTransitions(state))

    def createSymbols(self):
        symbolContainer = {}
        for ID, temp in self.templates.IDtoTemp.items():
            if 'UAC' in temp.state.getCurState():
                src = 'client'
                dst = 'server'
            else:
                src = 'server'
                dst = 'client'
            fields = map(lambda x: PrismaField(sanitizeRule(unquote(x))), temp.content)
            if not fields:
                continue
            s = PrismaSymbol(fields=fields)
            mess = RawMessage(s.specialize(), destination=dst, source=src)
            absFields = rules = cpyR = datR = None
            if ID in self.absoluteFields:
                absFields = self.absoluteFields[ID]
            if ID in self.Rules:
                rules = self.Rules[ID]
                rules = genDict(rules)
            if ID in self.copyRules:
                cpyR = self.copyRules[ID]
                cpyR = genDict(cpyR)
            if ID in self.dataRules:
                datR = self.dataRules[ID]
                datR = genDict(datR)
            s = PrismaSymbol(absFields=absFields, name=str(ID), fields=fields, messages=[mess],
                             rules=rules, copyRules=cpyR, dataRules=datR)
            symbolContainer.update({ID: s})
        return symbolContainer

    def createStates(self, prismaState):
        if 'END' in prismaState.getCurState():
            return [[State(getName(prismaState))]]
        if prismaState not in self.model.model.keys():
            return
        curState = State(getName(prismaState))
        nextStates = []
        for nx in self.model.model[prismaState]:
            nextStates.append(nx)

        # recurse
        moreStates = []
        backup = self.model.model[prismaState]
        del self.model.model[prismaState]
        for nx in backup:
            s = self.createStates(nx)
            if s is not None:
                moreStates += s

        moreStates.append([curState, nextStates])
        return moreStates

    def createPrismaTransitions(self, state):
        if len(state) < 2:
            return state[0]
        trans = []
        state, nextStates = state
        for nx in nextStates:
            for s in self.brokenStates:
                if s[0].name ==getName(nx):
                    temps = self.getTemplates(state.name)
                    trans.append(PrismaTransition(state, s[0], outputSymbols=temps, inputSymbol=EmptySymbol(), name='tr'))
        if trans:
            state.__transitions = trans
        return state

    def getTemplates(self, stateName):
        temps = []
        for pState in self.templates.stateToID.keys():
            if getName(pState) == stateName:
                for ID in self.templates.stateToID[pState]:
                    if ID not in self.Symbols.keys():
                        continue
                    s = self.Symbols[ID]
                    if s not in temps:
                        temps.append(s)
        return temps

    def computeRules(self):
        # handle normal rules
        for ruleList in self.rules[0].rules.values():
            for rule in ruleList:
                ID = rule.dstID[0]
                if ID not in self.Rules.keys():
                    self.Rules.update({ID: []})
                self.Rules[ID].append(rule)
        # handle copy rules
        seen = []
        for ruleList in self.rules[1].rules.values():
            seen.append(rule)
            for rule in ruleList:
                ID = rule.dstID[0]
                if ID not in self.copyRules.keys():
                    self.copyRules.update({ID: []})
                self.copyRules[ID].append(rule)
        # handle data rules
        for ruleList in self.rules[2].rules.values():
            for rule in ruleList:
                ID = rule.dstID[0]
                if ID not in self.dataRules.keys():
                    self.dataRules.update({ID: []})
                self.dataRules[ID].append(rule)
        return seen

    def computeABSfields(self):
        for template in self.templates.IDtoTemp.values():
            if template.fields:
                self.absoluteFields.update({template.ID: template.fields})

    def test(self, full=False):
        # self.getPrisma('/home/dsmp/work/p2p/samples/airplay1st', enhance=False)
        # self.getPrisma('/home/dasmoep/work/git/p2p/samples/airplay1st', enhance=True)
        self.getPrisma('/home/dsmp/Desktop/mynetzob/src/netzob/Import/PrismaImporter/samples/airplay1st', enhance=False)
        self.convertPrisma2Netzob()

        for s in self.States:
            for t in s.transitions:
                if t.endState not in self.States:
                    print(t.startState.name, '->', t.endState.name)

        for s in self.States:
            for t in s.transitions:
                print(t.startState.name, '->', t.endState.name, 'as', t.ROLE, 'by')
                for osy in t.outputSymbols:
                    print(osy.name,)
                print

        for start in self.States:
            if start.name == '|'.join(self.horizonLength*['START']):
                self.Start = start
                break

        self.Automaton = Automata(start, self.Symbols.values())
        dot = self.Automaton.generateDotCode()
        f = open('prismaDot', 'w')
        f.write(dot)
        f.close()
        print 'dotcode written to file "prismaDot"'

        chan = TCPClient('127.0.0.1', 36666, '127.0.0.1', 41337)
        self.PrismaLayer = PrismaLayer(chan, self.Symbols.values(), self.horizonLength+1)

        # for s in self.Symbols.values():
        #     s.messages = [RawMessage(s.specialize())]

        #  # test rules
        #  s = self.Symbols[14]
        #  ss = self.Symbols[5]
        #  sss = self.Symbols[19]

        # s.setHorizon([s, ss, s])
        # ss.setHorizon([ss, sss, ss])
        # # for SeqRule
        # # f = PrismaField('41')
        # # for PartRule
        # f = PrismaField('PREFIX%3Fgetexe%3Dgo.exeSUFFIX')
        # f.parent = ss
        # ss.fields[8] = f
        # ss.messages = [RawMessage(ss.specialize())]
        # ss.applyRules()
        # print ss.specialize()
        return


# what to do about ruleFields?
def sanitizeRule(x):
    if x == '':
        return ASCII(nbChars=(0, 100))
        # return 'dsmp'
    return x

def getName(prismaState):
    s = ''
    for i in range(len(prismaState.hist)):
        s += '|'+prismaState.hist[i]
    return s[1:]

def genDict(ruleList):
    d = {}
    for rule in ruleList:
        if rule.ruleHist not in d:
            d.update({rule.ruleHist: []})
        d[rule.ruleHist].append(rule)
    return d
