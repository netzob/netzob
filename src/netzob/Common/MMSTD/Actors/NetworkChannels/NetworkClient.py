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
#| Standard library imports                                                  |
#+---------------------------------------------------------------------------+
from bitarray import bitarray
from gettext import gettext as _
import logging
from lxml.etree import ElementTree
from lxml import etree

import select
import socket

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+

from netzob.Common.Type.TypeConvertor import TypeConvertor
from netzob.Common.MMSTD.Actors.AbstractChannel import AbstractChannel


#+---------------------------------------------------------------------------+
#| NetworkClient:
#|     Definition of a network client
#+---------------------------------------------------------------------------+
class NetworkClient(AbstractChannel):

    def __init__(self, id, memory, protocol, bind_ip, bind_port, target_ip, target_port):
        AbstractChannel.__init__(self, id, False, False, memory, protocol, bind_ip, bind_port, target_ip, target_port)
        # create logger with the given configuration
        self.log = logging.getLogger(__name__)
        self.socket = None
        self.inputMessages = []
        self.outputMessages = []

    def open(self):
        try:
            if (self.getProtocol() == "UDP"):
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            else:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            if self.getBindIP() is not None or self.getBindPort() is not None:
                self.socket.bind((self.getBindIP(), self.getBindPort()))

            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

            targetIp = self.getTargetIP()
            targetPort = self.getTargetPort()
            self.log.debug("Try to connect on {0}:{1}".format(targetIp, targetPort))
            self.socket.connect((targetIp, targetPort))
            self.socket.setblocking(True)

            self.log.debug("NetworkClient has initiated a connection with {0}:{1}".format(targetIp, targetPort))
        except socket.error, msg:
            self.log.warn("Opening the network connection on {0}:{1} has failed : {2}".format(targetIp, targetPort, msg))
            self.socket = None

        if self.socket is None:
            self.log.warn("Impossible to open the socket")
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
            self.log.debug("Error appeared while shutting down the socket." + str(msg))

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
        result = TypeConvertor.string2bin("".join(chars), "big")
        self.log.debug("Read finished")
        if (len(chars) == 0):
            return result
        self.log.debug("Received : {0}".format(TypeConvertor.bin2strhex(result)))
        return result

    def write(self, message):
        self.log.debug("Write down !")
        self.outputMessages.append(message)

        try:
            self.outputFile.write(TypeConvertor.binB2string(message))
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

    #+-----------------------------------------------------------------------+
    #| GETTERS AND SETTERS
    #+-----------------------------------------------------------------------+
    def getPort(self):
        return self.port

    def setPort(self, port):
        self.port = port

    def save(self, root, namespace):
        """Save in the XML tree the actor definition"""
        xmlActor = etree.SubElement(root, "{" + namespace + "}communicationChannel")
        xmlActor.set("{http://www.w3.org/2001/XMLSchema-instance}type", "netzob:ClientNetworkChannel")
        xmlActor.set('id', str(self.getID()))

        xmlL4Protocol = etree.SubElement(xmlActor, "{" + namespace + "}l4_protocol")
        if self.getOriginalL4Protocol() is not None:
            xmlL4Protocol.text = self.getOriginalL4Protocol()
        else:
            xmlL4Protocol.text = ""

        xmlBindIp = etree.SubElement(xmlActor, "{" + namespace + "}bind_ip")
        if self.getOriginalBindIP() is not None:
            xmlBindIp.text = self.getOriginalBindIP()
        else:
            xmlBindIp.text = ""

        xmlBindPort = etree.SubElement(xmlActor, "{" + namespace + "}bind_port")
        if self.getOriginalBindPort() is not None:
            xmlBindPort.text = str(self.getOriginalBindPort())
        else:
            xmlBindPort.text = ""

        xmlTargetIp = etree.SubElement(xmlActor, "{" + namespace + "}target_ip")
        if self.getOriginalTargetIP() is not None:
            xmlTargetIp.text = self.getOriginalTargetIP()
        else:
            xmlTargetIp.text = ""

        xmlTragetPort = etree.SubElement(xmlActor, "{" + namespace + "}target_port")
        if self.getOriginalTargetPort() is not None:
            xmlTragetPort.text = str(self.getOriginalTargetPort())
        else:
            xmlTragetPort.text = ""

    @staticmethod
    def loadFromXML(rootElement, namespace, version, memory):
        # Then we verify its an IPC Message
        if rootElement.get("{http://www.w3.org/2001/XMLSchema-instance}type", "abstract") != "netzob:ClientNetworkChannel":
            raise NameError("The parsed xml doesn't represent a valid network client channel.")

        idChannel = rootElement.get('id')

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
        actor = NetworkClient(idChannel, memory, l4_protocol, bind_ip, bind_port, target_ip, target_port)
        return actor
