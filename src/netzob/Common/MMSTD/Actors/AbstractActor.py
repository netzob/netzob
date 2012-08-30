# -*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|          01001110 01100101 01110100 01111010 01101111 01100010            |
#|                                                                           |
#|               Netzob : Inferring communication protocols                  |
#+---------------------------------------------------------------------------+
#| Copyright (C) 2011 Georges Bossert and Frédéric Guihéry                   |
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
#| Standard library imports
#+---------------------------------------------------------------------------+
from gettext import gettext as _
import logging

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+


#+---------------------------------------------------------------------------+
#| AbstractActor:
#|     Definition of an actor
#+---------------------------------------------------------------------------+
class AbstractActor():

    def __init__(self, idActor, nameActor, isServer, instanciated, protocol, bindIP, bindPort, targetIP, targetPort):
        self.id = idActor
        self.name = nameActor
#        Thread.__init__(self)
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Common.MMSTD.Actors.AbstractActor.py')
        self.Terminated = False
        self.is_server = isServer
        self.active = False
        self.instanciated = instanciated
        self.protocol = protocol
        self.bindIP = bindIP
        self.bindPort = bindPort
        self.targetIP = targetIP
        self.targetPort = targetPort

    def isAnInstanciated(self):
        return self.instanciated

    def stop(self):
        self.Terminated = True

    def isServer(self):
        return self.is_server

    def isActive(self):
        return self.active

    def getID(self):
        return self.id

    def getName(self):
        return self.name

    def getL4Protocol(self):
        return self.protocol

    def getBindIP(self):
        return self.bindIP

    def getBindPort(self):
        return self.bindPort

    def getTargetIP(self):
        return self.targetIP

    def getTargetPort(self):
        return self.targetPort

    #+-----------------------------------------------------------------------+
    #| Load
    #+-----------------------------------------------------------------------+
    @staticmethod
    def loadFromXML(rootElement, namespace, version):
        # Computes which type is it
        if rootElement.get("{http://www.w3.org/2001/XMLSchema-instance}type", "abstract") == "abstract":
            raise NameError("The parsed xml doesn't represent a valid type of actor.")

        if rootElement.get("{http://www.w3.org/2001/XMLSchema-instance}type", "abstract") == "netzob:ClientNetworkActor":
            from netzob.Common.MMSTD.Actors.Network.NetworkClient import NetworkClient

            return NetworkClient.loadFromXML(rootElement, namespace, version)
        elif rootElement.get("{http://www.w3.org/2001/XMLSchema-instance}type", "abstract") == "netzob:ServerNetworkActor":
            from netzob.Common.MMSTD.Actors.Network.NetworkServer import NetworkServer

            return NetworkServer.loadFromXML(rootElement, namespace, version)
        else:
            logging.warn("The parsed type of Actor ({0}) is unknown.".format(rootElement.get("{http://www.w3.org/2001/XMLSchema-instance}type", "abstract")))

        return None
