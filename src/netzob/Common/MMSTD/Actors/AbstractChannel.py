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
from netzob.Common.MMSTD.Dictionary.Variables.DataVariable import DataVariable
from netzob.Common.MMSTD.Dictionary.DataTypes.WordType import WordType
from netzob.Common.MMSTD.Dictionary.DataTypes.IPv4WordType import IPv4WordType
from netzob.Common.MMSTD.Dictionary.DataTypes.IntegerType import IntegerType
from netzob.Common.Type.TypeConvertor import TypeConvertor
from netzob.Common.Property import Property
from netzob.Common.Type.Format import Format

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+


#+---------------------------------------------------------------------------+
#| AbstractChannel:
#|     Abstract class of a communication channel
#+---------------------------------------------------------------------------+
class AbstractChannel():

    varID_L4_PROTOCOL = "L4_PROTOCOL"
    varID_BIND_IP = "BIND_IP"
    varID_BIND_PORT = "BIND_PORT"
    varID_TARGET_IP = "TARGET_IP"
    varID_TARGET_PORT = "TARGET_PORT"

    def __init__(self, idChannel, isServer, instanciated, memory, protocol, bind_ip, bind_port, target_ip, target_port):
        self.id = idChannel
        self.log = logging.getLogger(__name__)
        self.Terminated = False
        self.is_server = isServer
        self.active = False
        self.instanciated = instanciated
        self.memory = memory

        self.originalProtocol = protocol
        self.originalBindIp = bind_ip
        self.originalBindPort = bind_port
        self.originalTargetIp = target_ip
        self.originalTargetPort = target_port

        self.configureMemory()

    def configureMemory(self):
        """Presets the meta-variables of the channel with specified values"""

        self.varL4Protocol = DataVariable(AbstractChannel.varID_L4_PROTOCOL, AbstractChannel.varID_L4_PROTOCOL, True, True, WordType(True, 0, 5), self.originalProtocol)
        self.varBindIP = DataVariable(AbstractChannel.varID_BIND_IP, AbstractChannel.varID_BIND_IP, True, True, IPv4WordType(True, 7, 15), self.originalBindIp)
        self.varBindPort = DataVariable(AbstractChannel.varID_BIND_PORT, AbstractChannel.varID_BIND_PORT, True, True, IntegerType(True, 0, 5), self.originalBindPort)
        self.varTargetIP = DataVariable(AbstractChannel.varID_TARGET_IP, AbstractChannel.varID_TARGET_IP, True, True, IPv4WordType(True), self.originalTargetIp)
        self.varTargetPort = DataVariable(AbstractChannel.varID_TARGET_PORT, AbstractChannel.varID_TARGET_PORT, True, True, IntegerType(True, 0, 5), self.originalTargetPort)

        self.memory.forget(self.varL4Protocol)
        self.memory.memorize(self.varL4Protocol)

        self.memory.forget(self.varBindIP)
        self.memory.memorize(self.varBindIP)

        self.memory.forget(self.varBindPort)
        self.memory.memorize(self.varBindPort)

        self.memory.forget(self.varTargetIP)
        self.memory.memorize(self.varTargetIP)

        self.memory.forget(self.varTargetPort)
        self.memory.memorize(self.varTargetPort)

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

    def getProtocol(self):
        """Return in string the value of the protocol retrieved from the current memory"""
        binProtocol = self.memory.recall(self.varL4Protocol)
        if binProtocol == None:
            self.log.warn("Impossible to find the memorized value of the protocol")
            return None
        return TypeConvertor.netzobRawToString(TypeConvertor.bin2hexstring(binProtocol))

    def getBindIP(self):
        """Returns in string the value of the bind IP retrieved from memory"""
        binIP = self.memory.recall(self.varBindIP)
        if binIP == None:
            self.log.warn("Impossible to find the memorized value of the Bind IP")
            return None
        return TypeConvertor.netzobRawToString(TypeConvertor.bin2hexstring(binIP))

    def getBindPort(self):
        """Returns in int the value of the bind Port retrieved from memory"""
        binPort = self.memory.recall(self.varBindPort)
        if binPort == None:
            self.log.warn("Impossible to find the memorized value of the Bind Port")
            return None
        return TypeConvertor.bin2int(binPort)

    def getTargetIP(self):
        """Returns in string the value of the target IP retrieved from memory"""
        binIP = self.memory.recall(self.varTargetIP)
        if binIP == None:
            self.log.warn("Impossible to find the memorized value of the Target IP")
            return None
        return TypeConvertor.netzobRawToString(TypeConvertor.bin2hexstring(binIP))

    def getTargetPort(self):
        """Returns in int the value of the bind Port retrieved from memory"""
        binPort = self.memory.recall(self.varTargetPort)
        if binPort == None:
            self.log.warn("Impossible to find the memorized value of the Target Port")
            return None
        return TypeConvertor.bin2int(binPort)

    def getOriginalL4Protocol(self):
        return self.originalProtocol

    def getOriginalBindIP(self):
        return self.originalBindIp

    def getOriginalBindPort(self):
        return self.originalBindPort

    def getOriginalTargetIP(self):
        return self.originalTargetIp

    def getOriginalTargetPort(self):
        return self.originalTargetPort

    def getMemory(self):
        return self.memory

    def getProperties(self):
        properties = []
        properties.append(Property("Protocol", Format.STRING, self.originalProtocol))
        properties.append(Property("Bind IP", Format.STRING, self.originalBindIp))
        properties.append(Property("Bind Port", Format.DECIMAL, self.originalBindPort))
        properties.append(Property("Target IP", Format.STRING, self.originalTargetIp))
        properties.append(Property("Target Port", Format.DECIMAL, self.originalTargetPort))
        return properties

    #+-----------------------------------------------------------------------+
    #| Load
    #+-----------------------------------------------------------------------+
    @staticmethod
    def loadFromXML(rootElement, namespace, version, memory):
        # Computes which type is it
        if rootElement.get("{http://www.w3.org/2001/XMLSchema-instance}type", "abstract") == "abstract":
            raise NameError("The parsed xml doesn't represent a valid type of actor.")

        if rootElement.get("{http://www.w3.org/2001/XMLSchema-instance}type", "abstract") == "netzob:ClientNetworkChannel":
            from netzob.Common.MMSTD.Actors.NetworkChannels.NetworkClient import NetworkClient

            return NetworkClient.loadFromXML(rootElement, namespace, version, memory)
        elif rootElement.get("{http://www.w3.org/2001/XMLSchema-instance}type", "abstract") == "netzob:ServerNetworkChannel":
            from netzob.Common.MMSTD.Actors.NetworkChannels.NetworkServer import NetworkServer

            return NetworkServer.loadFromXML(rootElement, namespace, version, memory)
        else:
            logging.warn("The parsed type of channel ({0}) is unknown.".format(rootElement.get("{http://www.w3.org/2001/XMLSchema-instance}type", "abstract")))

        return None
