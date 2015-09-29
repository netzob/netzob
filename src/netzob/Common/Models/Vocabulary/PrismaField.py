from netzob.Common.Models.Vocabulary.Field import Field
from netzob.Common.Models.Vocabulary.Domain.DomainFactory import DomainFactory
from netzob.Common.Utils.NetzobRegex import NetzobStaticRegex
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger
from netzob.Common.Models.Types.Raw import Raw
from netzob.Common.Models.Types.TypeConverter import TypeConverter

from netzob.Common.Models.Types.BitArray import BitArray
from netzob.Common.Models.Types.TypeConverter import TypeConverter

import random
from urllib import unquote


class InvalidDomainException(Exception):
    pass

@NetzobLogger
class PrismaField(Field):
    def __init__(self, domain=None, name='PrismaField', layer=None):
        # self.__domain = None
        self.regex = None
        super(PrismaField, self).__init__(domain, name, layer)
        self.rules = {}

        self.ruleToggle = False

        # self._logger.critical(self.__domain)

        if domain is None:
            domain = Raw(None)
        self.domain = domain

    def _isStatic(self):
        """Returns True if the field denotes a static content"""
        return isinstance(self.regex, NetzobStaticRegex)

    def specialize(self):
        self._logger.debug("Specializes field {0}".format(self.name))
        if self.__domain is None:
            raise InvalidDomainException("The domain is not defined.")

        from netzob.Common.Models.Vocabulary.Domain.Specializer.FieldSpecializer import FieldSpecializer
        fs = FieldSpecializer(self)
        specializingPaths = fs.specialize()

        if len(specializingPaths) < 1:
            raise Exception("Cannot specialize this field")

        specializingPath = specializingPaths[0]

        self._logger.debug("field specializing done: {0}".format(specializingPath))
        if specializingPath is None:
            raise Exception("The specialization of the field {0} returned no result.".format(self.name))

        return TypeConverter.convert(specializingPath.getDataAssignedToVariable(self.domain), BitArray, Raw)

    @property
    def domain(self):
        return self.__domain

    def domainUpdate(self):
        if not self.rules or not self.ruleToggle:
            return self.__domain
        hist = self.parent.horizon2ID()
        rule = self.rules[hist]
        ruleType = getType(rule)
        if ruleType == 'data':
            self._logger.critical('dataRule')
            data = random.choice(rule.data)
            dom = unquote(data)
        elif ruleType == 'exact':
            self._logger.critical('exactRule')
            # get the right Symbol to read from
            srcSym = self.parent.horizon[int(rule.srcID)]
            dom = srcSym.fields[srcSym.absoluteFields[int(rule.srcField)]].getValues()[0]
        else:  # ruleType == 'copy':
            srcSym = self.parent.horizon[int(rule.srcID)]
            # getValues returns list
            # in our case only one value shall be in there
            value = srcSym.fields[srcSym.absoluteFields[int(rule.srcField)]].getValues()[0]
            # manipulate value here according to rule
            if 'Seq' in rule.typ:
                self._logger.critical('seqRule')
                try:
                    base = int(value)
                except ValueError:
                    self._logger.critical('sequential rule: cannot cast value of field to int')
                    base = 1
                try:
                    inc = int(rule.content)
                except ValueError:
                    self._logger.critical('sequential rule: cannot cast rule content to int')
                    inc = 1
                dom = base + inc
            elif 'Comp' in rule.typ:
                self._logger.critical('compRule')
                data = unquote(random.choice(rule.content))
                if 'PREFIX' in rule.ptype:
                    dom = value + data
                elif 'SUFFIX' in rule.ptype:
                    dom = data + value
            elif 'Part' in rule.typ:
                self._logger.critical('partRule')
                value = value.split(rule.content, 1)
                if len(value) != 2:
                    self._logger.critical('partial rule: value not split-able by separator')
                if 'PREFIX' in rule.ptype:
                    dom = value[0]
                elif 'SUFFIX' in rule.ptype:
                    dom = value[1]
            else:
                self._logger.critical('cannot happen')
                dom = 'xY'
        self.domain = dom
        return self.__domain

    @domain.setter
    def domain(self, domain):
        normalizedDomain = DomainFactory.normalizeDomain(domain)
        self._logger.debug("Create Normalized regex for {0}".format(normalizedDomain))
        self.regex = normalizedDomain.buildRegex()
        self.__domain = normalizedDomain


def getType(rule):
    attr = rule.__dict__.keys()
    if 'data' in attr:
        return 'data'
    if 'typ' in attr:
        return 'copy'
    return 'exact'
