__author__ = 'dsmp'

import os


class PrismaExporter(object):
    def __init__(self, pi):
        self.pi = pi
        return

    def toFile(self):
        pi = self.pi
        path = '{}/NetzobEnhanced'.format(pi.getPath())
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
                # get left (not deleted) Symbols
                for s in t.outputSymbols:
                    symbols.update({s.name: (s, current.name)})
                nxt = t.endState
                # print '{}->{}'.format(current.name, nxt.name)
                f = open(os.path.join(path, 'nE.markovModel'), 'a')
                f.write('{}->{},1\n'.format(current.name, nxt.name))
                f.close()
                if nxt not in done:
                    toDo.append(nxt)
            done.append(current)
        f = open(os.path.join(path, 'nE.templtaes'), 'a')
        for s, p in symbols.values():
            f.write(s.toFile(p))
        f.close()


