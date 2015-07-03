import prisma
import os

from netzob.Common.Models.Vocabulary.Symbol import Symbol
from netzob.Common.Models.Vocabulary.Field import Field
from netzob.Common.Models.Vocabulary.Messages.RawMessage import RawMessage


class PrismaImporter(object):

    def __init__(self):
        print("Hello Netzob, this is Prisma...\nI'm gonna take over...\nDon't make it harder than necessary.")
        self.rules = None
        self.model = None
        self.templates = None
        self.Symbols = None
        pass

    def getPrisma(self, path):
        templates, model, rules = None, None, None
        for files in os.listdir(path):
            if 'template' in files:
                f = open('{0}/{1}'.format(path,files),'r')
                templates = prisma.templateParse(f)
                self.templates = templates
                f.close()
                print('read templates')
            if 'markov' in files:
                f = open('{0}/{1}'.format(path,files),'r')
                model = prisma.markovParse(f)
                self.model = model
                f.close()
                print('read model')
            if 'rules' in files:
                f = open('{0}/{1}'.format(path,files),'r')
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

        # return symbolContainer

def sanitizeRule(x):
    if x == '':
        return 'dsmp'
    return x
