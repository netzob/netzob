from netzob.Common.Models.Vocabulary.Field import Field
from netzob.Common.Models.Vocabulary.Domain.DomainFactory import DomainFactory
from netzob.Common.Utils.NetzobRegex import NetzobStaticRegex
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger

import random
from urllib import unquote


@NetzobLogger
class PrismaField(Field):
    def __init__(self, domain=None, name='PrismaField', layer=None):
        self.__domain = None
        self.regex = None
        super(PrismaField, self).__init__(domain, name, layer)
        self.rules = {}
        # self.type = 'rule'

    def _isStatic(self):
        """Returns True if the field denotes a static content"""
        return isinstance(self.regex, NetzobStaticRegex)

    @property
    def domain(self):
        if not self.type:
            return self.__domain
        hist = self.parent.horizon2ID()
        rule = self.rules[hist]
        ruleType = getType(rule)
        if ruleType == 'data':
            data = random.choice(rule.data)
            return DomainFactory.normalizeDomain(unquote(data))
        elif ruleType == 'exact':
            # get the right Symbol to read from
            srcSym = self.parent.horizon[int(rule.srcID)]
            self.domain = srcSym.fields[srcSym.absoluteFields[int(rule.srcField)]].domain
            return self.domain
        elif ruleType == 'copy':
            srcSym = self.parent.horizon[int(rule.srcID)]
            value = srcSym.fields[srcSym.absoluteFields[int(rule.srcField)]].getValues()
            # manipulate value here according to rule
            return self.domain
        self._logger.critical('cannot happen')

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
        # needs further refinement
        return 'copy'
    return 'exact'
