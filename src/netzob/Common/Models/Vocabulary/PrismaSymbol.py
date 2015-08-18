__author__ = 'dsmp'

from netzob.Common.Models.Vocabulary.Symbol import Symbol
from netzob.Common.Models.Vocabulary.AbstractField import AbstractField
from netzob.Import.PrismaImporter.prisma.Hist import Hist
from netzob.Common.Models.Vocabulary.Field import Field
from netzob.Common.Models.Vocabulary.Messages.RawMessage import RawMessage
from netzob.Common.Utils.TypedList import TypedList
from netzob.Common.Models.Vocabulary.Messages.AbstractMessage import AbstractMessage
from netzob.Common.Models.Types.Raw import Raw
from netzob.Common.Models.Types.BitArray import BitArray
from netzob.Common.Models.Types.TypeConverter import TypeConverter
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger

import random
from urllib import unquote


@NetzobLogger
class PrismaSymbol(AbstractField):

    def __init__(self, pi=None, absFields=[], fields=None, messages=None, name="Symbol",
                 rules={}, copyRules={}, dataRules={}, horizon=[None], role=None):

        super(PrismaSymbol, self).__init__(name, None, True)
        self.__messages = TypedList(AbstractMessage)

        # self.__messages = TypedList(AbstractMessage)
        # super(PrismaSymbol, self).__init__(fields, messages, name)
        self.pi = pi
        self.horizon = horizon
        self.rules = rules
        self.copyRules = copyRules
        self.dataRules = dataRules
        self.absoluteFields = absFields

        self.role = role
        self.faulty = 0.0
        self.emitted = 0

        if messages is None:
            messages = []
        self.msg = messages
        if fields is None:
            # create a default empty field
            fields = [Field()]
        self.fields = fields

    # def copy(self):
    #     return PrismaSymbol(pi=self.pi, absFields=self.absoluteFields, fields=self.fields, messages=self.messages,
    #                         rules=self.rules, copyRules=self.copyRules, dataRules=self.dataRules, role=self.role,
    #                         name=self.name)

    def setHorizon(self, horizon):
        self.horizon = horizon

    def horizon2ID(self):
        return Hist(map(lambda x: [int(x.name)], self.horizon[-3:]))

    def updateHorizon(self, nextSymbol):
        self.horizon = self.horizon[1:] + [nextSymbol]

    def applyRules(self):
        self._logger.critical('rules for sym{}'.format(self.name))
        if not self.horizon[-1]:
            return
        hor = self.horizon2ID()
        ruleFlag = False
        if hor in self.dataRules:
            self._logger.critical('found data rules')
            ruleFlag = True
            for rule in self.dataRules[hor]:
                data = random.choice(rule.data)
                # self._logger.info('from data pool {} chose {}'.format(rule.data, data))
                # self._logger.critical('unquoted: {}'.format(unquote(data)))
                f = Field(str(unquote(data)).strip())
                # self._logger.critical('domain: {}'.format(f.domain))
                self.fields[self.absoluteFields[int(rule.dstField)]].domain = f.domain
                # self.messages = [RawMessage(self.specialize(noRules=True))]
            self.messages = [RawMessage(self.specialize(noRules=True))]
            try:
                # self._logger.critical('message: {}'.format(self.specialize(noRules=True)))
                self.getCells()
                # self.fields[int(rule.dstField)].getValues()[0]
                self._logger.critical('success')
            except Exception as e:
                self._logger.critical('DataRule breaks Cells')
        if hor in self.rules:
            self._logger.critical('found exact rule')
            ruleFlag = True
            for rule in self.rules[hor]:
                srcSym = self.horizon[int(rule.srcID)]
                try:
                    print self.fields[self.absoluteFields[int(rule.dstField)]].domain
                    self.fields[self.absoluteFields[int(rule.dstField)]].domain = srcSym.fields[srcSym.absoluteFields[int(rule.srcField)]].domain
                    print self.fields[self.absoluteFields[int(rule.dstField)]].domain
                    self.messages = [RawMessage(self.specialize(noRules=True))]
                    self._logger.critical('success')
                except Exception:
                    self._logger.critical('error in exactRule')
        if hor in self.copyRules:
            self._logger.info('found copy rules')
            ruleFlag = True
            for rule in self.copyRules[hor]:
                srcSym = self.horizon[int(rule.srcID)]
                if 'Seq' in rule.typ:
                    self._logger.critical('Sequential')
                    try:
                        base = int(srcSym.fields[srcSym.absoluteFields[int(rule.srcField)]].getValues()[0])
                    except ValueError:
                        self._logger.critical("couldn't cast base to int")
                        self._logger.critical("baseValue:{}".format(srcSym.fields[srcSym.absoluteFields[int(rule.srcField)]].getValues()[0]))
                        self._logger.critical("setting it to 1")
                        base = 1
                    try:
                        inc = int(rule.content)
                    except ValueError:
                        self._logger.critical("couldn't cast increment to int")
                        self._logger.critical("baseValue:{}".format(srcSym.fields[srcSym.absoluteFields[int(rule.srcField)]].getValues()[0]))
                        inc = 1
                    new = base + inc
                    f = Field(str(new))
                    self.fields[self.absoluteFields[int(rule.dstField)]].domain = f.domain
                    self.messages = [RawMessage(self.specialize(noRules=True))]
                    self._logger.critical('success')
                elif 'Comp' in rule.typ:
                    self._logger.critical('CopyComplete')
                    flag = False
                    if 'PREFIX' in rule.ptype:
                        try:
                            f = Field(srcSym.fields[srcSym.absoluteFields[int(rule.srcField)]].getValues()[0] + random.choice(rule.content))
                            flag = True
                        except Exception:
                            self._logger.critical('error in copyCompletePREFIX at sym{}'.format(self.name))
                    else:
                        try:
                            # srcSym.fields[srcSym.absoluteFields[int(rule.srcField)]].getValues()[0]
                            f = Field(random.choice(rule.content) + srcSym.fields[srcSym.absoluteFields[int(rule.srcField)]].getValues()[0])
                            flag = True
                        except Exception as e:
                            self._logger.critical('error in copyCompleteSUFFIX at sym{}'.format(self.name))
                            # self._logger.critical('prefix: {}'.format(rule.content))
                            # self._logger.critical('prefix: {}'.format(random.choice(rule.content)))
                            # self._logger.critical('srcField: {}'.format(int(rule.srcField)))
                            # self._logger.critical('srcID: {}'.format(int(rule.srcID)))
                            # self._logger.critical('srcSym: {}'.format(srcSym.name))
                            # self._logger.critical('srcDomain: {}'.format(srcSym.fields[srcSym.absoluteFields[int(rule.srcField)]].domain))
                            # self._logger.critical('along here')
                            # self._logger.critical('srcValue: {}'.format(srcSym.fields[srcSym.absoluteFields[int(rule.srcField)]].getValues()))
                    if flag:
                        self.fields[self.absoluteFields[int(rule.dstField)]].domain = f.domain
                        self.messages = [RawMessage(self.specialize(noRules=True))]
                        self._logger.critical('success')
                else:  # 'Part' in rule.typ
                    self._logger.critical('CopyPartial')
                    split = srcSym.fields[srcSym.absoluteFields[int(rule.srcField)]].getValues()[0].split(rule.content, 1)
                    if len(split) != 2:
                        self._logger.critical('error in SPLIT of copyPartial')
                        continue
                    flag = False
                    if 'PREFIX' in rule.ptype:
                        try:
                            f = Field(split[0])
                            flag = True
                        except Exception:
                            self._logger.critical('error in copyPartial')
                    else:
                        try:
                            f = Field(split[1])
                            flag = True
                        except Exception:
                            self._logger.critical('error in copyPartial')
                    if flag:
                        self.fields[self.absoluteFields[int(rule.dstField)]].domain = f.domain
                        self.messages = [RawMessage(self.specialize(noRules=True))]
                        self._logger.critical('success')
        # if ruleFlag:
        #     self.messages = [RawMessage(self.specialize(noRules=True))]
        if not ruleFlag:
            # heuristically approach:
            # put always same string in rule fields iff horizon does not match
            # maybe reason about what string fits best
            # tried 'AAAAAAAAAAAAA'
            f = Field('1')
            for ind in self.absoluteFields:
                self.fields[ind].domain = f.domain
            self.messages = [RawMessage(self.specialize(noRules=True))]
            for field in self.fields:
                if field.name == 'broken':
                    field.domain = Field(f.getValues()[0]).domain
                    self.messages = [RawMessage(self.specialize(noRules=True))]
            self._logger.warning('No Rules for this context')
            self.messages = [RawMessage(self.specialize(noRules=True))]

    def specialize(self, memory=None, noRules=False, data=False):
        if not noRules:
            self._logger.error('specializing sym{}'.format(self.name))
        if not noRules and self.horizon != [None]:
            self.applyRules()
        from netzob.Common.Models.Vocabulary.Domain.Specializer.MessageSpecializer import MessageSpecializer
        try:
            msg = MessageSpecializer(memory=memory)
            spePath = msg.specializeSymbol(self)
            if not noRules:
                self._logger.info('getting message just fine')
        except Exception:
            self._logger.critical('something wrong with getting message from symbol')

        if spePath is not None:
            try:
                message = TypeConverter.convert(spePath.generatedContent, BitArray, Raw)
                return message
            except Exception:
                self._logger.critical('something wrong with converting message')

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

    def toFile(self, parent):
        ntokens = len(self.fields)
        fields = ''
        if self.absoluteFields:
            fields = ','.join(map(lambda x: str(x), self.absoluteFields))
        # build strings like this one:
        # TEMPLATE id:4 state:None.UAC|None.UAC count:2 ntokens:64 fields:2,8,20,24
        sym = 'TEMPLATE id:{} state:{} count:1 ntokens:{} fields:{}\n'.format(self.name, parent, ntokens, fields)
        # grep content from exactly what we loaded earlier
        # hell this is stupid :s
        temp = self.pi.templates[int(self.name)]
        for c in temp.content:
            sym += '{}\n'.format(c)
        return sym