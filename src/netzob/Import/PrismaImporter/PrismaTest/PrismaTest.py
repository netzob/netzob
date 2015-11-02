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
import time
from socket import error as socket_error

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+

from netzob.Import.PrismaImporter.PrismaImporter import PrismaImporter
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger
from netzob.Common.Models.Vocabulary.Messages.RawMessage import RawMessage

@NetzobLogger
class PrismaTest(object):
    """ Prisma testing unit; just loads files from hardcoded path and fires up an instance of xbmc and communicates
    """
    def __init__(self):
        self.pi = PrismaImporter()

    def run(self, init=False):
        try:
            l = self.pi.getLayer()
            l.reInit()
            try:
                l.openChannel()
            except socket_error:
                try:
                    # maybe channel still blocked?
                    l.closeChannel()
                    time.sleep(.1)
                    l.openChannel()
                except socket_error:
                    # probably killed target -> restart it
                    print 'watch out, target may be gone?! Trying to restart..'
                    # set States to not active
                    for state in self.pi.States:
                        # just in case..
                        state.active = False
                    time.sleep(11)
                    os.system("/home/dsmp/work/xbmc/bin/kodi &")
                    time.sleep(7.5)
            s = self.pi.getInitial()
            sPre = None
            while sPre != s:
                sPre = s
                s = s.executeAsInitiator(l)
                # if s == 'cycle':
                #     self._logger.critical('cycle detected')
                #     time.sleep(3)
                #     l.closeChannel()
                #     return True
                if 'END' in s.name:
                    # session ended gracefully
                    self._logger.critical('session gracefully ended')
                    l.closeChannel()
                    time.sleep(3)
                    return True
            self._logger.critical('session aborted')
            time.sleep(3)
            l.closeChannel()
            return True
        # probably one cycle ended in the target not responding
        # causing an exception to be thrown
        # causing us to catch it
        except Exception:
            return True

    def toast(self, count=0):
        self.fuzzyLearn(count)

    def adjustPort(self):
        c = self.pi.getLayer().channel
        c.localPort += 1
        if c.localPort > 60000:
            c.localPort = 11337
        return

    def fuzzyLearn(self, count=0):
        ret = True
        init = True
        self.pi.getLayer().reInit()
        while ret:
            ret = self.run(init)
            init = False
            count += 1
            # self.adjustPort()
            if not count % 100:
                self._logger.critical('=== {} === \r\n\r\n'.format(count))
                self.dot(count)
            # find good value here
            if count == 200000:
                ret = False

    def dot(self, count):
        try:
            os.makedirs('{}/graphs2'.format(self.pi.getPath()))
        except OSError:
            pass
        dot = self.pi.getAutomaton().generateDotCode()
        f = open('{}/graphs2/{}'.format(self.pi.getPath(), count), 'w')
        f.write(dot)
        f.close()
        return

    def test(self, dot=True, check=False):
        if self.pi.isInitialized():
            return
        self.pi.setPath('/data/pulsar/models/1ActionMerge')
        self.pi.setDestinationIp('127.0.0.1')
        self.pi.setDestinationPort(36666)
        self.pi.setSourceIp('127.0.0.1')
        self.pi.setSourcePort(51337)

        print self.pi.isInitialized()
        # enhance maybe is a poor idea (at least at learning lvl)
        self.pi.create(enhance=False)
        # there seems to be a problem specializing some Symbols?
        if check:
            self._logger.info('testing generated Symbols')
            for sym in self.pi.Symbols.values():
                remake(sym)
        if dot:
            self.dot('initial')
        return


def remake(sym, rerun=False):
        if sym.role == 'client':
            try:
                sym.getCells()
                sym.specialize(noRules=True)
            except Exception:
                if rerun:
                    print 'deleting entire symbol {}'.format(sym.name)
                    # self._logger.error('problem with symbol No.{} --> removing it'.format(sym.name))
                else:
                    sym.messages = [RawMessage(sym.specialize())]
                    remake(sym, True)


