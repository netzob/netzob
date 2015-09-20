import prisma
import copy
import os
from urllib import unquote

from netzob.Common.Models.Vocabulary.PrismaSymbol import PrismaSymbol
from netzob.Common.Models.Vocabulary.Symbol import Symbol
from netzob.Common.Models.Vocabulary.EmptySymbol import EmptySymbol
from netzob.Common.Models.Vocabulary.PrismaField import PrismaField
from netzob.Common.Models.Vocabulary.Messages.RawMessage import RawMessage
from netzob.Common.Models.Grammar.States.State import State
from netzob.Common.Models.Grammar.Transitions.PrismaTransition import PrismaTransition
from netzob.Common.Models.Grammar.Automata import Automata
from netzob.Common.Models.Types.ASCII import ASCII
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger

from netzob.Common.Models.Simulator.PrismaLayer import PrismaLayer
from netzob.Common.Models.Simulator.Channels.TCPClient import TCPClient


@NetzobLogger
class PrismaImporter(object):
    def __init__(self):
        print("\nHello Netzob, this is Prisma...\nI'm gonna take over...\nDon't make it harder than necessary.\n")
        # of no greater use later on
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

        # essential attributes
        self.__initialized = False
        # where the PRISMA fiels live
        self.__path = None
        # who talks to whom?!
        self.__destinationIP = None
        self.__destinationPort = None
        self.__sourceIP = None
        self.__sourcePort = None

        # automaton, abstractionLayer, initialState
        # everything needed for communication
        self.__Automaton = None
        self.__PrismaLayer = None
        self.__Start = None
        return

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

        # get initial state
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
            s = self.createSymbol(ID)
            # if 'UAC' in temp.state.getCurState():
            #     src = 'client'
            #     dst = 'server'
            # else:
            #     src = 'server'
            #     dst = 'client'
            # numRuleFields = 1
            # if temp.fields:
            #     numRuleFields = len(temp.fields)
            # maxEntropy = min(1000/(8*numRuleFields), 17)
            # maxEntropy = max(maxEntropy, 1)
            # fields = map(lambda x: PrismaField(*sanitizeRule(unquote(x), src, maxEntropy)), temp.content)
            # if not fields:
            #     continue
            # s = PrismaSymbol(fields=fields, name=str(ID), role=src)
            # if src == 'server':
            #     s.messages = [RawMessage(s.specialize(), destination=dst, source=src)]
            # absFields = []
            # rules = cpyR = datR = {}
            # if ID in self.absoluteFields:
            #     s.absoluteFields = self.absoluteFields[ID]
            # if ID in self.Rules:
            #     rules = self.Rules[ID]
            #     s.rules = genDict(rules)
            # if ID in self.copyRules:
            #     cpyR = self.copyRules[ID]
            #     s.copyRules = genDict(cpyR)
            # if ID in self.dataRules:
            #     datR = self.dataRules[ID]
            #     s.dataRules = genDict(datR)
            # # s = PrismaSymbol(pi=self, absFields=absFields, name=str(ID), fields=fields, messages=[msg],
            # #                  rules=rules, copyRules=cpyR, dataRules=datR, role=src)
            # # try:
            # #     s.getCells()
            # # except Exception:
            # #     self._logger.critical('cannot crack sym{} at {}'.format(s.name, maxEntropy))
            symbolContainer.update({ID: s})
        return symbolContainer

    def createSymbol(self, ID, role=None):
        temp = self.templates.IDtoTemp[ID]
        if 'UAC' in temp.state.getCurState():
            src = 'client'
            dst = 'server'
        else:
            src = 'server'
            dst = 'client'
        numRuleFields = 1
        if temp.fields:
            numRuleFields = len(temp.fields)
        maxEntropy = min(1000/(8*numRuleFields), 17)
        maxEntropy = max(maxEntropy, 1)
        fields = map(lambda x: PrismaField(*sanitizeRule(unquote(x), src, maxEntropy)), temp.content)
        # if not fields:
        #     return
        s = PrismaSymbol(fields=fields, name=str(ID), role=src)
        if src == 'server':
            s.messages = [RawMessage(s.specialize(), destination=dst, source=src)]
        absFields = []
        rules = cpyR = datR = {}
        if ID in self.absoluteFields:
            s.absoluteFields = self.absoluteFields[ID]
        if ID in self.Rules:
            rules = self.Rules[ID]
            s.rules = genDict(rules)
        if ID in self.copyRules:
            cpyR = self.copyRules[ID]
            s.copyRules = genDict(cpyR)
        if ID in self.dataRules:
            datR = self.dataRules[ID]
            s.dataRules = genDict(datR)
        s.buildFields()
        # temp = self.templates.IDtoTemp[ID]
        # if role == 'client':
        #     src = 'client'
        #     dst = 'server'
        # else:
        #     src = 'server'
        #     dst = 'client'
        # numRuleFields = 1
        # if temp.fields:
        #     numRuleFields = len(temp.fields)
        # maxEntropy = min(1000/(8*numRuleFields), 17)
        # maxEntropy = max(maxEntropy, 1)
        # fields = map(lambda x: PrismaField(*sanitizeRule(unquote(x), src, maxEntropy)), temp.content)
        # if not fields:
        #     return None
        # s = PrismaSymbol(fields=fields, name=str(ID))
        # if src == 'server':
        #     msg = RawMessage(s.specialize(), destination=dst, source=src)
        # absFields = []
        # rules = cpyR = datR = {}
        # if ID in self.absoluteFields:
        #     absFields = self.absoluteFields[ID]
        # if ID in self.Rules:
        #     rules = self.Rules[ID]
        #     rules = genDict(rules)
        # if ID in self.copyRules:
        #     cpyR = self.copyRules[ID]
        #     cpyR = genDict(cpyR)
        # if ID in self.dataRules:
        #     datR = self.dataRules[ID]
        #     datR = genDict(datR)
        # s = PrismaSymbol(pi=self, absFields=absFields, name=str(ID), fields=fields, messages=[msg],
        #                  rules=rules, copyRules=cpyR, dataRules=datR, role=src)
        # # try:
        # #     s.getCells()
        # # except Exception:
        # #     self._logger.critical('cannot crack sym{} at {}'.format(s.name, maxEntropy))
        return s

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
        # are you initialState?
        if state.name == '|'.join(self.horizonLength*['START']):
            self.__Start = state
        for nx in nextStates:
            for s in self.brokenStates:
                if s[0].name == getName(nx):
                    # make each transition its own set of symbols
                    temps = self.getTemplates(state.name)
                    trans.append(PrismaTransition(state, s[0], outputSymbols=temps, inputSymbol=EmptySymbol(),
                                                  name='{}-->{}'.format(state.name, s[0].name)))
        if trans:
            state.__transitions = trans
            state.trans = trans
        return state

    def getTemplates(self, stateName):
        temps = []
        for pState in self.templates.stateToID.keys():
            if getName(pState) == stateName:
                for ID in self.templates.stateToID[pState]:
                    # if ID not in self.Symbols.keys():
                    #     continue
                    # s = self.Symbols[ID]
                    if 'UAC' in stateName:
                        role = 'client'
                    else:
                        role = 'server'
                    s = self.createSymbol(ID, role)
                    if s:
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
            for rule in ruleList:
                seen.append(rule)
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

    def create(self, enhance=False):
        if not self.isInitialized():
            print 'Information missing.'
            return
        # read files from location
        print 'reading from location {}'.format(self.getPath())
        self.getPrisma(self.getPath(), enhance)
        # build netzob structures
        print 'building Netzob structures'
        self.convertPrisma2Netzob()
        self.__setAutomaton(Automata(self.__Start, self.Symbols.values()))
        print 'setting up CHANNEL from {}:{} to {}:{}'.format(self.getSourceIp(), self.getSourcePort(), self.getDestinationIp(), self.getDestinationPort())
        chan = TCPClient(self.getDestinationIp(), self.getDestinationPort(), self.getSourceIp(), self.getSourcePort())
        self.__setLayer(PrismaLayer(chan, self.Symbols.values(), self.horizonLength+1))
        print 'ready for takeoff\n'

    #getter 'n' setter
    def isInitialized(self):
        return self.__initialized

    def __setInitialized(self):
        if self.__path and self.__sourceIP and self.__sourcePort and self.__destinationIP and self.__destinationPort:
            self.__initialized = not self.__initialized

    def setPath(self, path):
        self.__path = path
        self.__setInitialized()

    def getPath(self):
        return self.__path

    def getSourceIp(self):
        return self.__sourceIP

    def setSourceIp(self, ip):
        if not ipchecker(ip):
            raise ValueError
        self.__sourceIP = ip
        self.__setInitialized()

    def getDestinationIp(self):
        return self.__destinationIP

    def setDestinationIp(self, ip):
        if not ipchecker(ip):
            raise ValueError
        self.__destinationIP = ip
        self.__setInitialized()

    def getSourcePort(self):
        return self.__sourcePort

    def setSourcePort(self, port):
        if not numchecker(port):
            raise ValueError
        self.__sourcePort = port
        self.__setInitialized()

    def getDestinationPort(self):
        return self.__destinationPort

    def setDestinationPort(self, port):
        if not numchecker(port):
            raise ValueError
        self.__destinationPort = port
        self.__setInitialized()

    def __setAutomaton(self, Automaton):
        self.__Automaton = Automaton

    def getAutomaton(self):
        return self.__Automaton

    def __setLayer(self, PrismaLayer):
        self.__PrismaLayer = PrismaLayer

    def getLayer(self):
        return self.__PrismaLayer

    def getInitial(self):
        return self.__Start


# what to do about ruleFields?
def sanitizeRule(x, role, maxEntropy):
    if x == '':
        return [ASCII(nbChars=(1, maxEntropy))]
    # this is a nightmare
    # be a little bit more cool if some received message does not
    # fits a template; a plan never survives first contact with reality
    if role == 'server':
        l = len(x)
        if 'port' in x or 'Port' in x:
            return [ASCII(nbChars=(l-10, l+10)), x], 'broken'
        # are you an integer field?
        b = numchecker(x, False)
        if b:
            # if so, model it as a field with no content in a variable size
            # will match many integers then
            # note: for RECEIVING only!
            return [ASCII(nbChars=(1, l+2))]
    return [x]


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


def ipchecker(ip):
    try:
        split = ip.split('.')
        if len(split) != 4:
            return False
        for i in split:
            b = numchecker(i)
            if not b:
                return False
        return True
    except (SyntaxError, AttributeError):
        print "IP should look like '127.0.0.1'"
        return False


def numchecker(num, port=True):
    try:
        int(num)
        return True
    except ValueError:
        if port:
            print 'You know how a port looks like..'
        return False

