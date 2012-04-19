# -* - coding: utf-8 -*-

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
import logging
import socket
import select

from bitarray import bitarray

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.MMSTD.Actors.AbstractActor import AbstractActor


#+---------------------------------------------------------------------------+
#| InstanciatedNetworkServer:
#|     Definition of an instanciated network server
#+---------------------------------------------------------------------------+
class InstanciatedNetworkServer(AbstractActor):

    def __init__(self, socket):
        AbstractActor.__init__(self, True, True)
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Common.MMSTD.Actors.Network.InstanciatedNetworkServer.py')
        self.socket = socket
        self.inputMessages = []
        self.outputMessages = []
#
#    def createNewServer(self):
#        host = "localhost"
#        protocol = "TCP"
#        port = 6666
#        from netzob.Common.MMSTD.Actors.Network.NetworkServer import NetworkServer
#        return NetworkServer(host, protocol, port)

    def open(self):
        self.log.warn("Impossible to open an InstanciatedNetworkServer")
        return False

    def close(self):
        self.log.debug("Closing the socket")
        if self.socket == None:
            self.log.warn("No need to close the socket since it's not even open")
            return True
        self.log.debug("Shuting down the socket of the instanciated network server")
        try:
            self.socket.shutdown(socket.SHUT_RDWR)
        except:
            self.log.warn("Error while shuting down a socket")
        self.socket.close()

        return True

    def read(self, timeout):
        self.log.debug("Reading from the socket some data (timeout = " + str(timeout))
        result = bitarray(endian='big')

        chars = []
        try:
            if timeout > 0:
                ready = select.select([self.socket], [], [], timeout)
                if ready[0]:
                    chars = self.socket.recv(4096)
            else:
                ready = select.select([self.socket], [], [])
                self.log.debug("ready = " + str(ready[0]))
                if ready[0]:
                    chars = self.socket.recv(4096)
        except:
            self.log.debug("Impossible to read from the network socket")
            return None

        if (len(chars) == 0):
            return result
        result.fromstring(chars)

#        self.inputMessages.append(receivedData)
        self.log.debug("Received : " + str(result) + "(" + result.tostring() + ")")
        return result

    def write(self, message):
        self.log.debug("Writing to the socket")
        self.outputMessages.append(message)
        self.socket.send(message.tostring())

        self.log.debug("Write down !")

    def getInputMessages(self):
        return self.inputMessages

    def getOutputMessages(self):
        return self.outputMessages

    def isOpen(self):
        return self.open

    #+-----------------------------------------------------------------------+
    #| GETTERS AND SETTERS
    #+-----------------------------------------------------------------------+
    def getPort(self):
        return self.port

    def setPort(self, port):
        self.port = port
