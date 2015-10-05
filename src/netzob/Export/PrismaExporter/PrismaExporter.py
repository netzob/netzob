__author__ = 'dsmp'

import os


class PrismaExporter(object):
    def __init__(self, pi):
        self.pi = pi
        return

    def toFile(self):
        pi = self.pi
        path = '{}/NetzobEnhanced'.format(pi.getPath())
        print('writing to:{}'.format(path))
        # make workDir
        try:
            os.makedirs(path)
        except OSError:
            # kill all, be careful here!
            fl = [f for f in os.listdir(path)]
            for f in fl:
                os.remove(os.path.join(path, f))
        toDo = [pi.getInitial()]
        done = []
        symbols = {}
        while toDo:
            current = toDo.pop()
            for t in current.transitions:
                # # is start?
                # if current == pi.getInitial():
                #     pass
                # # maybe transition invalidated
                # if len(t.outputSymbols) < 1:
                #     continue
                # get left (not deleted) Symbols
                transSyms = '#'
                for s in t.outputSymbols:
                    symbols.update({s.name: (s, current.name)})
                    transSyms += s.name + ' '
                transSyms += '\n'
                nxt = t.endState
                # print '{}->{}'.format(current.name, nxt.name)
                f = open(os.path.join(path, 'nE.markovModel'), 'a')
                f.write('{}->{},1\n'.format(current.name, nxt.name))
                f.write(transSyms)
                f.close()
                if nxt not in done:
                    toDo.append(nxt)
            done.append(current)
        t = open(os.path.join(path, 'nE.templates'), 'a')
        r = open(os.path.join(path, 'nE.rules'), 'a')
        for s, p in symbols.values():
            t.write(s.toFile(p, self.pi))
            for ruleList in s.rules.values():
                for rule in ruleList:
                    r.write(rule.toFile())
            for ruleList in s.dataRules.values():
                for rule in ruleList:
                    r.write(rule.toFile())
            for ruleList in s.copyRules.values():
                for rule in ruleList:
                    r.write(rule.toFile())
        t.close()
        r.close()


