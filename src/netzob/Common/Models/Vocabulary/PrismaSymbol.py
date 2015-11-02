#-*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|          01001110 01100101 01110100 01111010 01101111 01100010            |
#|                                                                           |
#|               Netzob : Inferring communication protocols                  |
#+---------------------------------------------------------------------------+
#| Copyright (C) 2015 Christian Bruns                                        |
#| This program is free software: you can redistribute it and/or modify      |
#| it under the terms of the GNU General Public License as published by      |
#| the Free Software Foundation, either version 3 of the License, or         |
#| (at your option) any later version.                                       |
#|                                                                           |
#| This program is distributed in the hope that it will be useful,           |
#| but WITHOUT ANY WARRANTY; without even the implied warranty of            |
#| MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the              |
#| GNU General Public License for more details.                              |
#|                                                                           |
#| You should have received a copy of the GNU General Public License         |
#| along with this program. If not, see <http://www.gnu.org/licenses/>.      |
#+---------------------------------------------------------------------------+
#| @url      : http://www.netzob.org                                         |
#| @contact  : contact@netzob.org                                            |
#| @sponsors : Amossys, http://www.amossys.fr                                |
#|             Supélec, http://www.rennes.supelec.fr/ren/rd/cidre/           |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| File contributors :                                                       |
#|       - Christian Bruns <christian.bruns1 (a) stud.uni-goettingen.de>     |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Standard library imports                                                  |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+

from netzob.Common.Models.Vocabulary.Symbol import Symbol
from netzob.Import.PrismaImporter.PrismaIO.Hist import Hist
from netzob.Common.Models.Vocabulary.Field import Field
from netzob.Common.Models.Vocabulary.Messages.RawMessage import RawMessage
from netzob.Common.Utils.TypedList import TypedList
from netzob.Common.Models.Vocabulary.Messages.AbstractMessage import AbstractMessage
from netzob.Common.Models.Types.Raw import Raw
from netzob.Common.Models.Types.BitArray import BitArray
from netzob.Common.Models.Types.TypeConverter import TypeConverter
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger


@NetzobLogger
class PrismaSymbol(Symbol):
    """ Basically performs like original Symbol; incorporates features of Context (so-called Horizon)
        and context sensitive Rules, which will be applied to its Fields when being specialized

        ToDo: test the correctness of the learned model and remove Symbol from specific Transition if
        it performs badly, e.g. bad emitted-to-faulty ratio (measure this in Transition)
    """

    def __init__(self, fields=None, pi=None, absFields=[], messages=None, name="Symbol",
                 rules={}, copyRules={}, dataRules={}, horizon=[None], role=None):

        self.__messages = TypedList(AbstractMessage)
        super(PrismaSymbol, self).__init__(fields, messages, name)
        self.pi = pi
        self.horizon = horizon
        self.rules = rules
        self.copyRules = copyRules
        self.dataRules = dataRules
        self.absoluteFields = absFields
        # make Symbol aware of its horizons
        self.horizons = []

        self.role = role
        self.faulty = 0.0
        self.emitted = 0

        if messages is None:
            messages = []
        self.messages = messages
        if fields is None:
            # create a default empty field
            fields = [Field()]
        self.fields = fields

    def buildFields(self):
        # attach rules to the fields
        for hist, ruleList in self.dataRules.items():
            self.horizons.append(hist)
            for rule in ruleList:
                field = self.fields[self.absoluteFields[int(rule.dstField)]]
                field.rules[hist] = rule
                field.ruleToggle = True
        for hist, ruleList in self.rules.items():
            self.horizons.append(hist)
            for rule in ruleList:
                field = self.fields[self.absoluteFields[int(rule.dstField)]]
                field.rules[hist] = rule
                field.ruleToggle = True
        for hist, ruleList in self.copyRules.items():
            self.horizons.append(hist)
            for rule in ruleList:
                field = self.fields[self.absoluteFields[int(rule.dstField)]]
                field.rules[hist] = rule
                field.ruleToggle = True
        self.horizons = list(set(self.horizons))

    def setHorizon(self, horizon):
        self.horizon = horizon

    def horizon2ID(self):
        return Hist(map(lambda x: [int(x.name)], self.horizon))

    def updateHorizon(self, nextSymbol):
        self.horizon = self.horizon[1:] + [nextSymbol]

    def specialize(self, memory=None, noRules=False, data=False):
        self.clearMessages()
        from netzob.Common.Models.Vocabulary.Domain.Specializer.MessageSpecializer import MessageSpecializer
        msg = MessageSpecializer(memory=memory)
        spePath = msg.specializeSymbol(self)

        if spePath is not None:
            try:
                message = TypeConverter.convert(spePath.generatedContent, BitArray, Raw)
                self.messages = [RawMessage(message)]
                return message
            except Exception:
                self._logger.critical('something wrong with converting message Sym{}'.format(self.name))

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

    def toFile(self, parent, pi):
        """ Writes Symbol to file in the well-known PRISMA-format

        :param parent: the Prisma-State to which this Symbol belongs
        :param pi: the PrismaImporter-Object to which the Symbol is attached
        :return: the encoding of the Symbol in PRISMA-format
        """
        ntokens = len(self.fields)
        fields = ''
        if self.absoluteFields:
            fields = ','.join(map(lambda x: str(x), self.absoluteFields))
        # build strings like this one:
        # TEMPLATE id:4 state:None.UAC|None.UAC count:2 ntokens:64 fields:2,8,20,24
        sym = 'TEMPLATE id:{} state:{} count:1 ntokens:{} fields:{}\n'.format(self.name, parent, ntokens, fields)
        # grep content from exactly what we loaded earlier
        # hell this is stupid :s
        temp = pi.templates[int(self.name)]
        for c in temp.content:
            sym += '{}\n'.format(c)
        return sym


def getHorizons(rules, copyRules, dataRules):
    horizons = []
    for hor in rules.keys():
        horizons.append(hor)
    for hor in copyRules.keys():
        horizons.append(hor)
    for hor in dataRules.keys():
        horizons.append(hor)
    return list(set(horizons))
