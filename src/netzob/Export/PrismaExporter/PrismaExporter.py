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

import os

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+


class PrismaExporter(object):
    """ Exporter receives PrismaImporter-Object and writes it to file in the well-known PRISMA-format
    """
    def __init__(self, pi):
        self.pi = pi
        return

    def toFile(self, path=None):
        """ Writes current Prisma-Object to specified path (if provided)
            OR sub-directory of the previous import-directory

            !!! CAUTION: deletes files in specified path !!!
        """
        if path:
            var = raw_input("CAUTION, process deletes files in {}. Proceed: [y/N] ".format(path))
            if 'y' in var or 'Y' in var:
                pass
            else:
                print('Aborting..')
                return
        pi = self.pi
        if not path:
            path = '{}/NetzobEnhanced'.format(pi.getPath())
        print('writing to:{}'.format(path))
        # make workDir
        try:
            os.makedirs(path)
        except OSError:
            # kill files, be careful here!
            fl = [f for f in os.listdir(path)]
            for f in fl:
                if 'markov' in f or 'template' in f or 'rule' in f:
                    os.remove(os.path.join(path, f))
        toDo = [pi.getInitial()]
        done = []
        symbols = {}
        while toDo:
            current = toDo.pop()
            for t in current.transitions:
                transSyms = '# '
                for s in t.outputSymbols:
                    symbols.update({s.name: (s, current.name)})
                    transSyms += s.name + ' '
                transSyms += '\n'
                nxt = t.endState
                # print '{}->{}'.format(current.name, nxt.name)
                f = open(os.path.join(path, 'nE.markovModel'), 'a')
                f.write('{}->{},1 '.format(current.name, nxt.name))
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


