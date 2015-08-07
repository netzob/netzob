__author__ = 'dsmp'

import os

import time
from socket import error as socket_error

from netzob.Import.PrismaImporter.PrismaImporter import PrismaImporter


class PrismaTest(object):
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
                    if not init:
                        self.pi.getLayer().sesSym[-2].append('CRASH')
                        self.pi.getLayer().sesSta[-2].append('CRASH')
                    time.sleep(11)
                    err = os.system("/home/dsmp/work/xbmc/bin/kodi &")
                    time.sleep(7.5)
                    if err == 0:
                        return True
            s = self.pi.getInitial()
            sPre = None
            while sPre != s:
                sPre = s
                s = s.executeAsInitiator(l)
            l.closeChannel()
            return True
        # probably one cycle ended in the target not responding
        # causing an excaption to be thrown
        # causing us to catch it
        except Exception, e:
            return True

    def fuzzyLearn(self):
        ret = True
        init = True
        while ret:
            ret = self.run(init)
            init = False

    def test(self, full=False):
        self.pi.setPath('/home/dsmp/work/pulsar/src/models/evo1')
        self.pi.setDestinationIp('127.0.0.1')
        self.pi.setDestinationPort(36666)
        self.pi.setSourceIp('127.0.0.1')
        self.pi.setSourcePort(51337)

        print self.pi.isInitialized()

        self.pi.create(enhance=True)
        dot = self.pi.getAutomaton().generateDotCode()
        f = open('prismaDot', 'w')
        f.write(dot)
        f.close()

        return
