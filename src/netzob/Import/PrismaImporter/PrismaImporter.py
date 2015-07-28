import prisma
import copy
import os

from netzob.Common.Models.Vocabulary.Symbol import Symbol
from netzob.Common.Models.Vocabulary.EmptySymbol import EmptySymbol
from netzob.Common.Models.Vocabulary.Field import Field
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
                self.rules = rules
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
            if k.curState == 'START':
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
            fields = map(lambda x: Field(sanitizeRule(unquote(x))), temp.content)
            if not fields:
                continue
            s = Symbol(fields, [])
            mess = RawMessage(s.specialize(), destination=dst, source=src)
            s = Symbol(name=str(ID), fields=fields, messages=[mess])
            symbolContainer.update({ID: s})
        return symbolContainer

    def createStates(self, prismaState):
        if 'END' in prismaState.getCurState():
            return [[State(prismaState.getName())]]
        if prismaState not in self.model.model.keys():
            return
        curState = State(prismaState.getName())
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
                if s[0].name == nx.getName():
                    temps = self.getTemplates(state.name)
                    trans.append(PrismaTransition(state, s[0], outputSymbols=temps, inputSymbol=EmptySymbol(), name='tr'))
        if trans:
            state.__transitions = trans
        return state

    def getTemplates(self, stateName):
        temps = []
        for pState in self.templates.stateToID.keys():
            if pState.getName() == stateName:
                for ID in self.templates.stateToID[pState]:
                    if ID not in self.Symbols.keys():
                        continue
                    s = self.Symbols[ID]
                    if s not in temps:
                        temps.append(s)
        return temps

    def computeRules(self):
        # handle normal rules
        for rule in self.rules[0].rules.values():
            pass
        # handle copy rules
        for rule in self.rules[1].rules.values():
            pass
        # handle data rules
        for rule in self.rules[2].rules.values():
            pass
        pass

    def computeABSfields(self):
        for template in self.templates.IDtoTemp.values():
            if template.fields:
                self.absoluteFields.update({template.ID: template.fields})

    def test(self, full=False):
        self.getPrisma('/home/dsmp/work/p2p/samples/airplay1st', enhance=False)
        # self.getPrisma('/home/dasmoep/work/git/p2p/samples/airplay1st', enhance=True)
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
            if 'START|START' in start.name:
                self.Start = start
                break

        self.auto = Automata(start, self.Symbols.values())
        dot = self.auto.generateDotCode()
        f = open('prismaDot', 'w')
        f.write(dot)
        f.close()
        print 'dotcode written to file "prismaDot"'

        chan = TCPClient('127.0.0.1', 36666, '127.0.0.1', 41337)
        self.PrismaLayer = PrismaLayer(chan, self.Symbols.values(), 3)  # 3 being the HORIZON LENGTH +1

        return


# what to do about ruleFields?
def sanitizeRule(x):
    if x == '':
        return ASCII(nbChars=(0, 100))
        # return 'dsmp'
    return x

