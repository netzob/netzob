import prisma
import copy
import os

from netzob.Common.Models.Vocabulary.Symbol import Symbol
from netzob.Common.Models.Vocabulary.EmptySymbol import EmptySymbol
from netzob.Common.Models.Vocabulary.Field import Field
from netzob.Common.Models.Vocabulary.Session import Session
from netzob.Common.Models.Vocabulary.Messages.RawMessage import RawMessage
from netzob.Common.Models.Grammar.States.State import State
from netzob.Common.Models.Grammar.Transitions.PrismaTransition import PrismaTransition
from netzob.Common.Models.Grammar.Automata import Automata
from netzob.Common.Models.Types.ASCII import ASCII

import string
from urllib import unquote

from netzob.Common.Models.Simulator.AbstractionLayer import AbstractionLayer
from netzob.Common.Models.Simulator.Channels.TCPClient import TCPClient


class PrismaImporter(object):
    def __init__(self):
        print("Hello Netzob, this is Prisma...\nI'm gonna take over...\nDon't make it harder than necessary.\n")
        self.rules = None
        self.model = None
        self.templates = None
        self.Messages = []
        self.Symbols = None
        self.brokenStates = None
        self.States = []

        # debug stuff
        self.connectedStates = None
        self.Session = None
        self.absSess = None
        self.auto = None
        self.dot = None
        pass

    def getPrisma(self, path, enhance=False):
        templates, model, rules = None, None, None
        for files in os.listdir(path):
            if 'template' in files:
                f = open('{0}/{1}'.format(path, files), 'r')
                templates = prisma.templateParse(f)
                self.templates = templates
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
            if rules != None and model != None and templates != None:
                break
        if rules == None or model == None or templates == None:
            print("Big Problem: Couldn't find some of the files")
            return -1
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
            # Symbol(map(lambda y: Field(y),x.content))
            if 'UAC' in temp.state.getCurState():
                src = 'client'
                dst = 'server'
            else:
                src = 'server'
                dst = 'client'
            # mess with contentEncoding
            # cont = unquote(temp.content)
            # escCont = ''.join(c for c in cont if c in string.printable)
            # if not cont == escCont:
            #     # model as hex
            #     pass
            # else:
            fields = map(lambda x: Field(sanitizeRule(unquote(x))), temp.content)
            if fields == []:
                continue
                # fields = [Field('')]
            s = Symbol(fields, [])
            mess = RawMessage(s.specialize(), destination=dst, source=src)
            self.Messages.append(mess)
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
                    # trans.append(PrismaTransition(state, s[0], outputSymbols=temps, inputSymbol=empty, name='tr'))
                    if 'UAC' in state.name.split('|')[-1]:
                        trans.append(PrismaTransition(state, s[0], outputSymbols=temps, inputSymbol=EmptySymbol(), name='tr'))
                    else:
                        # if state.name == 'START|START':
                        #     print 'yeah'
                        #     trans.append(PrismaTransition(state, s[0], inputSymbol=EmptySymbol(), name='tr'))
                        # for ID in temps:
                        #     trans.append(PrismaTransition(state, s[0], inputSymbol=EmptySymbol(), outputSymbols=[ID], name='tr'))
                        trans.append(PrismaTransition(state, s[0], inputSymbol=EmptySymbol(), outputSymbols=temps, name='tr'))
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

    def test(self, full=False):
        self.getPrisma('/home/dsmp/work/p2p/samples/airplay1st')
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
                break

        self.auto = Automata(start, self.Symbols.values())
        dot = self.auto.generateDotCode()
        f = open('prismaDot', 'w')
        f.write(dot)
        f.close()
        print 'dotcode written to file "prismaDot"'

        chan = TCPClient('127.0.0.1', 36666, '127.0.0.1', 41337)
        absl = AbstractionLayer(chan, self.Symbols.values())
        absl.openChannel()
        # state = start

        return absl

        if full:
            # make Session of observed Messages
            sess = Session(self.Messages)
            self.Session = sess
            # make somehow abstraction of this Session
            # e.g. find matching Symbol for each Message
            absSess = sess.abstract(self.Symbols.values())
            self.absSess = absSess
            # make Automaton and dotCode
            dotcode = []
            auto = []
            auto.append(Automata.generateChainedStatesAutomata(absSess, self.Symbols.values()))
            dotcode.append(auto[-1].generateDotCode())
            auto.append(Automata.generateOneStateAutomata(absSess, self.Symbols.values()))
            dotcode.append(auto[-1].generateDotCode())
            auto.append(Automata.generatePTAAutomata([absSess], self.Symbols.values()))
            dotcode.append(auto[-1].generateDotCode())
            self.auto = auto
            self.dot = dotcode
            # save this to testFiles
            for i in range(3):
                f = open('dot{}'.format(i), 'w')
                f.write(dotcode[i])
                f.close()
            return start
        return start


def sanitizeRule(x):
    if x == '':
        return ASCII(nbChars=(0, 100))
        # return 'dsmp'
    return x
