__author__ = 'dsmp'

from netzob.Common.Models.Vocabulary.Symbol import Symbol
from netzob.Import.PrismaImporter.prisma.Hist import Hist
from netzob.Common.Models.Vocabulary.Field import Field
from netzob.Common.Models.Vocabulary.Messages.RawMessage import RawMessage
from netzob.Common.Utils.TypedList import TypedList
from netzob.Common.Models.Vocabulary.Messages.AbstractMessage import AbstractMessage
from netzob.Common.Models.Types.Raw import Raw
from netzob.Common.Models.Types.BitArray import BitArray
from netzob.Common.Models.Types.TypeConverter import TypeConverter

import random
from urllib import unquote


class PrismaSymbol(Symbol):

    def __init__(self, absFields=[], fields=None, messages=None, name="Symbol", rules={}, copyRules={}, dataRules={}):
        self.__messages = TypedList(AbstractMessage)
        super(PrismaSymbol, self).__init__(fields, messages, name)
        self.horizon = None
        self.rules = rules
        self.copyRules = copyRules
        self.dataRules = dataRules
        self.absoluteFields = absFields

        if messages is None:
            messages = []
        self.messages = messages
        if fields is None:
            # create a default empty field
            fields = [Field()]
        self.fields = fields

    def setHorizon(self, horizon):
        self.horizon = horizon

    def horizon2ID(self):
        return Hist(map(lambda x: [int(x.name)], self.horizon))

    def applyRules(self):
        if not self.horizon:
            print 'nothing to do'
            return
        hor = self.horizon2ID()
        print 'checking horizon {}'.format(hor)
        ruleFlag = False
        if hor in self.dataRules:
            print 'found data rules'
            ruleFlag = True
            for rule in self.dataRules[hor]:
                data = random.choice(rule.data)
                print 'from data pool {} chose {}'.format(rule.data, data)
                f = Field(unquote(data))
                # f.parent = self
                self.fields[self.absoluteFields[rule.dstField]].domain = f.domain
        if hor in self.rules:
            print 'normal rule'
            ruleFlag = True
            for rule in self.rules[hor]:
                srcSym = self.horizon[rule.srcID]
                self.fields[self.absoluteFields[rule.dstField]].domain = srcSym.fields[srcSym.absoluteFields[rule.srcField]].domain
        if hor in self.copyRules:
            print 'found copy rules'
            ruleFlag = True
            for rule in self.copyRules[hor]:
                srcSym = self.horizon[rule.srcID]
                if 'Seq' in rule.typ:
                    f = Field(str(int(srcSym.fields[srcSym.absoluteFields[rule.srcField]].getValues()[0])
                                        + int(rule.content)))
                    # f.parent = self
                    self.fields[self.absoluteFields[rule.dstField]].domain = f.domain
                elif 'Comp' in rule.typ:
                    if 'PREFIX' in rule.ptype:
                        f = Field(srcSym.fields[srcSym.absoluteFields[rule.srcField]].getValues()[0] +
                                        random.choice(rule.content))
                    else:
                        f = Field(random.choice(rule.content) +
                                        srcSym.fields[srcSym.absoluteFields[rule.srcField]].getValues()[0])
                    # f.parent = self
                    self.fields[self.absoluteFields[rule.dstField]].domain = f.domain
                else:  # 'Part' in rule.typ
                    split = srcSym.fields[srcSym.absoluteFields[rule.srcField]].getValues()[0].split(rule.content, 1)
                    if len(split) != 2:
                        continue
                    if 'PREFIX' in rule.ptype:
                        f = Field(split[0])
                    else:
                        f = Field(split[1])
                    # f.parent = self
                    self.fields[self.absoluteFields[rule.dstField]].domain = f.domain
        if ruleFlag:
            # self.clearMessages()
            self.messages = [RawMessage(self.specialize(noRules=True))]

    def specialize(self, memory=None, noRules=False):
        if self.horizon and not noRules:
            print 'calling for rules'
            self.applyRules()
            print 'applied rules'
        from netzob.Common.Models.Vocabulary.Domain.Specializer.MessageSpecializer import MessageSpecializer
        msg = MessageSpecializer(memory=memory)
        spePath = msg.specializeSymbol(self)

        if spePath is not None:
            return TypeConverter.convert(spePath.generatedContent, BitArray, Raw)

    def clearMessages(self):
        """Delete all the messages attached to the current symbol"""
        while(len(self.__messages) > 0):
            self.__messages.pop()

    # Properties

    @property
    def messages(self):
        """A list containing all the messages that this symbol represent.

        :type : a :class:`list` of :class:`netzob.Common.Models.Vocabulary.Messages.AbstractMessage.AbstractMessage`
        """
        return self.__messages

    @messages.setter
    def messages(self, messages):
        if messages is None:
            messages = []

        # First it checks the specified messages are all AbstractMessages
        for msg in messages:
            if not isinstance(msg, AbstractMessage):
                raise TypeError("Cannot add messages of type {0} in the session, only AbstractMessages are allowed.".format(type(msg)))

        self.clearMessages()
        for msg in messages:
            self.__messages.append(msg)
