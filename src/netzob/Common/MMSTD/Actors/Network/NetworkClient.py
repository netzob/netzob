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
from gettext import gettext as _
import socket
import select
import logging
from bitarray import bitarray
from lxml.etree import ElementTree
from lxml import etree
#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.MMSTD.Actors.AbstractActor import AbstractActor


#+---------------------------------------------------------------------------+
#| NetworkClient:
#|     Definition of a network client
#+---------------------------------------------------------------------------+
class NetworkClient(AbstractActor):

    def __init__(self, id, name, protocol, bindIP, bindPort, targetIP, targetPort):
        AbstractActor.__init__(self, id, name, False, False, protocol, bindIP, bindPort, targetIP, targetPort)
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Common.MMSTD.Actors.Network.NetworkClient.py')
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

        if self.socket is None:
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

    def save(self, root, namespace):
        """Save in the XML tree the actor definition"""
        xmlActor = etree.SubElement(root, "{" + namespace + "}actor")
        xmlActor.set("{http://www.w3.org/2001/XMLSchema-instance}type", "netzob:ClientNetworkActor")
        xmlActor.set('id', str(self.getID()))
        xmlActor.set('name', str(self.getName()))

        xmlL4Protocol = etree.SubElement(xmlActor, "{" + namespace + "}l4_protocol")
        if self.getL4Protocol() is not None:
            xmlL4Protocol.text = self.getL4Protocol()
        else:
            xmlL4Protocol.text = ""

        xmlBindIp = etree.SubElement(xmlActor, "{" + namespace + "}bind_ip")
        if self.getBindIP() is not None:
            xmlBindIp.text = self.getBindIP()
        else:
            xmlBindIp.text = ""

        xmlBindPort = etree.SubElement(xmlActor, "{" + namespace + "}bind_port")
        if self.getBindPort() is not None:
            xmlBindPort.text = str(self.getBindPort())
        else:
            xmlBindPort.text = ""

        xmlTargetIp = etree.SubElement(xmlActor, "{" + namespace + "}target_ip")
        if self.getTargetIP() is not None:
            xmlTargetIp.text = self.getTargetIP()
        else:
            xmlTargetIp.text = ""

        xmlTragetPort = etree.SubElement(xmlActor, "{" + namespace + "}target_port")
        if self.getTargetPort() is not None:
            xmlTargetIp.text = str(self.getTargetPort())
        else:
            xmlTargetIp.text = ""

    @staticmethod
    def loadFromXML(rootElement, namespace, version):
        # Then we verify its an IPC Message
        if rootElement.get("{http://www.w3.org/2001/XMLSchema-instance}type", "abstract") != "netzob:ClientNetworkActor":
            raise NameError("The parsed xml doesn't represent a a network client.")

        idActor = rootElement.get('id')
        nameActor = rootElement.get('name')

        # Parse the data field and transform it into a byte array
        l4_protocol = rootElement.find("{" + namespace + "}l4_protocol").text
        if l4_protocol != "UDP" and l4_protocol != "TCP":
            logging.warning("Invalid L4 protocol.")
            return None

        bind_ip = rootElement.find("{" + namespace + "}bind_ip").text
        if bind_ip is None or len(bind_ip) == 0:
            bind_ip = None

        bind_port = None
        tmp = rootElement.find("{" + namespace + "}bind_port").text
        if tmp is not None and len(tmp) > 0:
            try:
                bind_port = int(tmp)
            except:
                logging.warn("Invalid bind port.")
                return None

        target_ip = rootElement.find("{" + namespace + "}target_ip").text
        if target_ip is None or len(target_ip) == 0:
            target_ip = None

        target_port = None
        tmp = rootElement.find("{" + namespace + "}target_port").text
        if tmp is not None and len(tmp) > 0:
            try:
                target_port = int(tmp)
            except:
                logging.warn("Invalid target port")
                return None

        # create the actor
        actor = NetworkClient(idActor, nameActor, l4_protocol, bind_ip, bind_port, target_ip, target_port)
        return actor
