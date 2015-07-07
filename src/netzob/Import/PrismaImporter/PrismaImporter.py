import prisma
import copy
import os

from netzob.Common.Models.Vocabulary.Symbol import Symbol
from netzob.Common.Models.Vocabulary.Field import Field
from netzob.Common.Models.Vocabulary.Messages.RawMessage import RawMessage
from netzob.Common.Models.Grammar.States.State import State
from netzob.Common.Models.Grammar.Transitions.Transition import Transition


class PrismaImporter(object):
    def __init__(self):
        print("Hello Netzob, this is Prisma...\nI'm gonna take over...\nDon't make it harder than necessary.")
        self.rules = None
        self.model = None
        self.templates = None
        self.Symbols = None
        self.brokenStates = None
        self.States = []
        pass

    def getPrisma(self, path):
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
        symbolContainer = {}
        for ID, temp in self.templates.IDtoTemp.items():
        # Symbol(map(lambda y: Field(y),x.content))
            if 'UAC' in temp.state.getCurState():
                src = 'client'
                dst = 'server'
            else:
                src = 'server'
                dst = 'client'
            fields = map(lambda x: Field(sanitizeRule(x)), temp.content)
            if fields == []:
                continue
                # fields = [Field('')]
            s = Symbol(fields, [])
            s = Symbol(fields, [RawMessage(s.specialize(), destination=dst, source=src)])
            symbolContainer.update({ID: s})
        self.Symbols = symbolContainer

        # get INITIAL state
        for k in self.model.model.keys():
            if k.curState == 'START':
                break
        # create States beginning at initial
        cpy = copy.deepcopy(self.model)
        self.brokenStates = self.createStates(k)
        self.model = cpy
        for state in self.brokenStates:
            self.States.append(self.createTransitions(state))

    def createStates(self, prismaState):
        if 'END' in prismaState.getCurState():
            return [[State(prismaState.getName())]]
        if prismaState not in self.model.model.keys():
            return
        curState = State(prismaState.getName())
        nextStates = []
        for nx in self.model.model[prismaState]:
            nextStates.append(nx)

        print(curState, nextStates)

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

    def createTransitions(self, state):
        if len(state) < 2:
            return state[0]
        trans = []
        state, nextStates = state
        for nx in nextStates:
            for s in self.brokenStates:
                if s[0].name == nx.getName():
                    trans.append(Transition(state, s[0]))
        if trans != []:
            state.__transitions = trans
        return state


def sanitizeRule(x):
    if x == '':
        return 'dsmp'
    return x
