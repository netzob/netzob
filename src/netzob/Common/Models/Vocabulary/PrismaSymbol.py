__author__ = 'dsmp'

from netzob.Common.Models.Vocabulary.Symbol import Symbol


class PrismaSymbol(Symbol):
    def __init__(self, absFields=None, fields=None, messages=None, name="Symbol"):
        super(PrismaSymbol, self).__init__(fields, messages, name)
        self.horizon = None
        self.rules = None
        self.absoluteFields = absFields

    def setHorizon(self, horizon):
        self.horizon = horizon
