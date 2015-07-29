__author__ = 'dsmp'

from netzob.Common.Models.Vocabulary.Field import Field


class PrismaField(Field):
    def __init__(self, domain=None, name="Field", layer=False):
        super(PrismaField, self).__init__(domain, name, layer)
