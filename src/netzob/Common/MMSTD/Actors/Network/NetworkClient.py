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
import socket
import select
import logging
from bitarray import bitarray

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.MMSTD.Actors.AbstractActor import AbstractActor


#+---------------------------------------------------------------------------+
#| NetworkClient:
#|     Definition of a network client
#+---------------------------------------------------------------------------+
class NetworkClient(AbstractActor):

    def __init__(self, host, protocol, port, sport):
        AbstractActor.__init__(self, False, False)
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Common.MMSTD.Actors.Network.NetworkClient.py')
        self.port = port
        self.sport = sport
        self.host = host
        self.protocol = protocol
        self.socket = None
        self.inputMessages = []
        self.outputMessages = []

    def open(self):
        try:
            if (self.protocol == "UDP"):
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            else:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind(('', self.sport))
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            self.socket.connect((self.host, self.port))
            self.socket.setblocking(True)
        except socket.error, msg:
            self.log.warn("Opening the network connection has failed : " + str(msg))
            self.socket = None

        if self.socket == None:
            self.log.warn("Impossible to open the socket created in the NetworkClient")
            return False

#        self.inputFile = self.socket.makefile('r', -1)
        self.outputFile = self.socket.makefile('w', -1)
        return True

    def close(self):
        self.log.debug("Closing the network client")
        self.stop()
        try:
            self.socket.shutdown(socket.SHUT_RDWR)
        except socket.error, msg:
            self.log.debug("Error appeared while shuting down the socket." + str(msg))

        try:
            self.socket.close()
#            self.socket.shutdown(socket.SHUT_RDWR)
        except socket.error, msg:
            self.log.debug("Error appeared while closing down the socket." + str(msg))

        return True

    def read(self, timeout):
        chars = []
        try:
            if timeout > 0:
                self.log.debug("Reading from the socket with a timeout of " + str(timeout))
                ready = select.select([self.socket], [], [], timeout)
                if ready[0]:
                    chars = self.socket.recv(4096)
            else:
                self.log.debug("Reading from the socket without any timeout")
                ready = select.select([self.socket], [], [])
                if ready[0]:
                    chars = self.socket.recv(4096)
        except:
            self.log.debug("Impossible to read from the network socket")
            return None
        result = bitarray(endian='big')
        self.log.debug("Read finished")
        if (len(chars) == 0):
            return result
        result.fromstring(chars)

        self.log.debug("Received : " + str(result))
        return result

    def write(self, message):
        self.log.debug("Write down !")
        self.outputMessages.append(message)
        try:
            self.outputFile.write(message.tostring())
            self.outputFile.flush()
        except:
            self.log.warn("An error occured while trying to write on the communication channel")

    def getInputMessages(self):
        return self.inputMessages

    def getOutputMessages(self):
        return self.outputMessages

    def getGeneratedInstances(self):
        return []

    def stop(self):
        self.log.debug("Stopping the thread of the network client")
        AbstractActor.stop(self)

    #+-----------------------------------------------------------------------+
    #| GETTERS AND SETTERS
    #+-----------------------------------------------------------------------+
    def getPort(self):
        return self.port

    def setPort(self, port):
        self.port = port
