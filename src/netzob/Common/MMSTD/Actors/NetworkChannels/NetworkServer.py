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
import SocketServer
SocketServer.TCPServer.allow_reuse_address = True
import threading
import time
import uuid
import select
from lxml.etree import ElementTree
from lxml import etree

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.MMSTD.Actors.AbstractChannel import AbstractChannel
from netzob.Common.MMSTD.Actors.MMSTDVisitor import MMSTDVisitor
from netzob.Common.MMSTD.Dictionary.AbstractionLayer import AbstractionLayer
from netzob.Common.MMSTD.MMSTD import MMSTD
from netzob.Common.MMSTD.Actors.NetworkChannels.InstanciatedNetworkServer import InstanciatedNetworkServer
from netzob.Common.MMSTD.Dictionary.Memory import Memory


#+---------------------------------------------------------------------------+
#| Container
#+---------------------------------------------------------------------------+
class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):

    def __init__(self, connectionInfos, TCPConnectionHandler):
        SocketServer.TCPServer.__init__(self, connectionInfos, TCPConnectionHandler)
        self.instances = []
        self.allow_reuse_address = True
        self.multipleConnectionAllowed = True
        self.memory = None
        self.bindIP = None
        self.bindPort = None
        self.targetIP = None
        self.targetPort = None

    def getVocabulary(self):
        return self.vocabulary

    def getMemory(self):
        return self.memory

    def getBindIP(self):
        return self.bindIP

    def setBindIP(self, bindIP):
        self.bindIP = bindIP

    def getBindPort(self):
        return self.bindPort

    def setBindPort(self, port):
        self.bindPort = port

    def getTargetIP(self):
        return self.targetIP

    def setTargetIP(self, targetIP):
        self.targetIP = targetIP

    def getTargetPort(self):
        return self.targetPort

    def setTargetPort(self, targetPort):
        self.targetPort = targetPort

    def getInitialState(self):
        return self.initialState

    def isMaster(self):
        return self.master

    def setVocabulary(self, vocabulary):
        self.vocabulary = vocabulary

    def setMemory(self, memory):
        self.memory = memory

    def setInitialState(self, initialState):
        self.initialState = initialState

    def setMaster(self, master):
        self.master = master

    def addGeneratedInstance(self, instance):
        self.instances.append(instance)

    def removeGeneratedInstance(self, instance):
        self.instances.remove(instance)

    def getGeneratedInstances(self):
        return self.instances

    def setCBWhenAClientConnects(self, cb):
        self.cbClientConnected = cb

    def setCBWhenAClientDisconnects(self, cb):
        self.cbClientDisconnected = cb

    def setCBWhenInputSymbol(self, cb):
        self.cbInputSymbol = cb

    def setCBWhenOutputSymbol(self, cb):
        self.cbOutputSymbol = cb

    def notifyAClientIsConnected(self):
        self.cbClientConnected()

    def notifyAClientIsDisconnected(self):
        self.cbClientDisconnected()

    def getCBInputSymbol(self):
        return self.cbInputSymbol

    def getCBOutputSymbol(self):
        return self.cbOutputSymbol

    def setMultipleConnectionIsAllowed(self, multipleConnectionAllowed):
        self.multipleConnectionAllowed = multipleConnectionAllowed

    def isMultipleConnectionAllowed(self):
        return self.multipleConnectionAllowed

#    def shutdown(self):
#        logging.info("shutingdown")
#        SocketServer.TCPServer.shutdown(self)


class ThreadedUDPServer(SocketServer.ThreadingMixIn, SocketServer.UDPServer):

    def __init__(self, connectionInfos, UDPConnectionHandler):
        SocketServer.UDPServer.__init__(self, connectionInfos, UDPConnectionHandler)
        self.instances = []
        self.allow_reuse_address = True
        self.multipleConnectionAllowed = True
        self.memory = None
        self.bindIP = None
        self.bindPort = None
        self.targetIP = None
        self.targetPort = None

    def getVocabulary(self):
        return self.vocabulary

    def getMemory(self):
        return self.memory

    def getInitialState(self):
        return self.initialState

    def isMaster(self):
        return self.master

    def setVocabulary(self, vocabulary):
        self.vocabulary = vocabulary

    def setMemory(self, memory):
        self.memory = memory

    def getBindIP(self):
        return self.bindIP

    def setBindIP(self, bindIP):
        self.bindIP = bindIP

    def getBindPort(self):
        return self.bindPort

    def setBindPort(self, port):
        self.bindPort = port

    def getTargetIP(self):
        return self.targetIP

    def setTargetIP(self, targetIP):
        self.targetIP = targetIP

    def getTargetPort(self):
        return self.targetPort

    def setTargetPort(self, targetPort):
        self.targetPort = targetPort

    def setInitialState(self, initialState):
        self.initialState = initialState

    def setMaster(self, master):
        self.master = master

    def addGeneratedInstance(self, instance):
        self.instances.append(instance)

    def removeGeneratedInstance(self, instance):
        self.instances.remove(instance)

    def getGeneratedInstances(self):
        return self.instances

    def setCBWhenAClientConnects(self, cb):
        self.cbClientConnected = cb

    def setCBWhenAClientDisconnects(self, cb):
        self.cbClientDisconnected = cb

    def setCBWhenInputSymbol(self, cb):
        self.cbInputSymbol = cb

    def setCBWhenOutputSymbol(self, cb):
        self.cbOutputSymbol = cb

    def notifyAClientIsConnected(self):
        self.cbClientConnected()

    def notifyAClientIsDisconnected(self):
        self.cbClientDisconnected()

    def getCBInputSymbol(self):
        return self.cbInputSymbol

    def getCBOutputSymbol(self):
        return self.cbOutputSymbol

    def setMultipleConnectionIsAllowed(self, multipleConnectionAllowed):
        self.multipleConnectionAllowed = multipleConnectionAllowed

    def isMultipleConnectionAllowed(self):
        return self.multipleConnectionAllowed


class TCPConnectionHandler(SocketServer.BaseRequestHandler):

    def __init__(self, request, client_address, server):
        server.allow_reuse_address = True
        SocketServer.BaseRequestHandler.__init__(self, request, client_address, server)
        self.subVisitor = None

    def handle(self):
        self.log = logging.getLogger(__name__)

        if not self.server.isMultipleConnectionAllowed() and len(self.server.getGeneratedInstances()) > 0:
#            self.log.warn("We do not adress this client, another one already connected")
            return
        self.log.info("A client has just initiated a connection on the server.")
        self.server.notifyAClientIsConnected()

        initialState = self.server.getInitialState()
        vocabulary = self.server.getVocabulary()
        isMaster = self.server.isMaster()

        # we create a sub automata
        automata = MMSTD(initialState, vocabulary)

        # and duplicate the memory for this instance
        duplicatedMemory = self.server.getMemory().duplicate()

        # We create an instantiated network server
        instanciatedNetworkServer = InstanciatedNetworkServer(uuid.uuid4(), duplicatedMemory, "TCP", self.request, self.server.getBindIP(), self.server.getBindPort(), self.server.getTargetIP(), self.server.getTargetPort())

        # Create the input and output abstraction layer
        abstractionLayer = AbstractionLayer(instanciatedNetworkServer, vocabulary, Memory(), self.server.getCBInputSymbol(), self.server.getCBOutputSymbol())
        # abstractionLayer = AbstractionLayer(instanciatedNetworkServer, vocabulary, Memory(vocabulary.getVariables()), self.server.getCBInputSymbol(), self.server.getCBOutputSymbol())

        # And we create an MMSTD visitor for this
        anID = str(uuid.uuid4())
        self.subVisitor = MMSTDVisitor(anID, "Instance-" + anID, automata, isMaster, abstractionLayer)

        self.log.info("An MMSTDVistor has been instantiated and assigned to the current network client.")
        self.subVisitor.start()

        # save it
        self.server.addGeneratedInstance(self.subVisitor)

        finish = not self.subVisitor.isAlive()

        while (not finish):
            try:
                ready = select.select([self.request], [], [], 1)
                time.sleep(0.1)
                finish = not self.subVisitor.isAlive()
            except:
                self.log.warn("The socket is not anymore opened !")
                finish = True
#        instanciatedNetworkServer.close()

        self.subVisitor.join(None)

        self.server.notifyAClientIsDisconnected()
#        self.server.shutdown_request(self.request)
#        self.server.close_request(self.request)
#        self.server.shutdown()

        self.log.warn("End of the execution of the TCP Connection handler")
#    def finish(self):
#        self.log.info("Closing the NetworkServer since the client is disconnected")
#        SocketServer.BaseRequestHandler.finish(self)
#        self.subVisitor.stop()


class UDPConnectionHandler(SocketServer.DatagramRequestHandler):

    def __init__(self, request, client_address, server):
        server.allow_reuse_address = True
        self.client_address = client_address
        SocketServer.BaseRequestHandler.__init__(self, request, client_address, server)
        self.subVisitor = None

    def handle(self):

        self.server.notifyAClientIsConnected()

        self.log = logging.getLogger('netzob.Common.MMSTD.Actors.Network.NetworkServer_ConnectionHandler.py')

        if not self.server.isMultipleConnectionAllowed() and len(self.server.getGeneratedInstances()) > 0:
            return
        self.log.info("A client has just initiated a connection on the server.")
        self.server.notifyAClientIsConnected()

        initialState = self.server.getInitialState()
        vocabulary = self.server.getVocabulary()
        isMaster = self.server.isMaster()

        # we create a sub automata
        automata = MMSTD(initialState, vocabulary)

        # and duplicate the memory for this instance
        duplicatedMemory = self.server.getMemory().duplicate()

        # set client IP and Port source as the target IP:Port through memory
        targetIP = self.client_address[0]
        targetPort = self.client_address[1]
        self.server.setTargetIP(targetIP)
        self.server.setTargetPort(targetPort)

        # We create an instantiated network server
        instanciatedNetworkServer = InstanciatedNetworkServer(uuid.uuid4(), duplicatedMemory, "UDP", self.request, self.server.getBindIP(), self.server.getBindPort(), self.server.getTargetIP(), self.server.getTargetPort())

        # Create the input and output abstraction layer
        abstractionLayer = AbstractionLayer(instanciatedNetworkServer, vocabulary, Memory(), self.server.getCBInputSymbol(), self.server.getCBOutputSymbol())
        # abstractionLayer = AbstractionLayer(instanciatedNetworkServer, vocabulary, Memory(vocabulary.getVariables()), self.server.getCBInputSymbol(), self.server.getCBOutputSymbol())

        # And we create an MMSTD visitor for this
        anID = str(uuid.uuid4())
        self.subVisitor = MMSTDVisitor(anID, "Instance-" + anID, automata, isMaster, abstractionLayer)

        self.log.info("An MMSTDVistor has been instantiated and assigned to the current network client.")
        self.subVisitor.start()

        # save it
        self.server.addGeneratedInstance(self.subVisitor)

        finish = not self.subVisitor.isAlive()

        while (not finish):
            try:
                ready = select.select([self.request], [], [], 1)
                time.sleep(0.1)
                finish = not self.subVisitor.isAlive()
            except:
                self.log.warn("The socket is not opened anymore!")
                finish = True

        self.subVisitor.join(None)

        self.server.notifyAClientIsDisconnected()

        self.log.warn("End of the execution of the UDP Connection handler")


#+---------------------------------------------------------------------------+
#| NetworkServer:
#|     Definition of a server which follows the definition of the provided
#|     automata.
#+---------------------------------------------------------------------------+
class NetworkServer(AbstractChannel):

    def __init__(self, id, memory, protocol, bind_ip, bind_port, target_ip, target_port):
        AbstractChannel.__init__(self, id, True, False, memory, protocol, bind_ip, bind_port, target_ip, target_port)
        # create logger with the given configuration
        self.log = logging.getLogger(__name__)

        self.server = None
        self.instantiatedServers = []
        self.allowMultipleClients = True

    def openServer(self, vocabulary, initialState, master, cb_whenAClientConnects, cb_whenAClientDisconnects, cb_registerInputSymbol, cb_registerOutputSymbol):
        # Instantiates the server
        maxNumberOfAttempts = 3
        nbAttempts = 0
        error = False
        finish = False
        while not finish:
            finish = True
            try:
                if self.getProtocol() == "UDP":
                    self.log.info("Configure an UDP Network Server to listen on " + self.getBindIP() + ":" + str(self.getBindPort()) + ".")
                    self.server = ThreadedUDPServer((self.getBindIP(), self.getBindPort()), UDPConnectionHandler)
                else:
                    self.log.info("Configure a TCP Network Server to listen on " + str(self.getBindIP()) + ":" + str(self.getBindPort()) + ".")
                    self.server = ThreadedTCPServer((self.getBindIP(), self.getBindPort()), TCPConnectionHandler)
            except Exception as e:
                self.log.warn("Impossible to open a server, attempts = " + str(nbAttempts) + "/" + str(maxNumberOfAttempts))
                self.log.warn("Error reason: {0}".format(e))
                finish = False
                nbAttempts += 1
                if nbAttempts > maxNumberOfAttempts:
                    finish = True
                    error = True
            time.sleep(5)

        if not error:
            self.server.setCBWhenAClientConnects(cb_whenAClientConnects)
            self.server.setCBWhenAClientDisconnects(cb_whenAClientDisconnects)
            self.server.setCBWhenInputSymbol(cb_registerInputSymbol)
            self.server.setCBWhenOutputSymbol(cb_registerOutputSymbol)
            self.server.allow_reuse_address = True
            self.server.setVocabulary(vocabulary)
            self.server.setInitialState(initialState)
            self.server.setMaster(master)
            self.server.setMemory(self.getMemory())
            self.server.setTargetIP(self.getTargetIP())
            self.server.setTargetPort(self.getTargetPort())
            self.server.setBindIP(self.getBindIP())
            self.server.setBindPort(self.getBindPort())

            self.server.setMultipleConnectionIsAllowed(self.allowMultipleClients)
            self.server_thread = threading.Thread(target=self.server.serve_forever)
            self.server_thread.daemon = True
            self.log.info("Start the server")
            self.server_thread.start()
        else:
            self.log.warn("The server cannot be started")

    def close(self):
        self.log.info("Shutdown down the server")
        self.server.server_close()
        self.server.shutdown()

        self.log.info("The thread which hosts the server has finished")

        self.log.info("The server has been shutted down")

    def getInputMessages(self):
        return []

    def getOutputMessages(self):
        return []

    def setAllowMultipleClients(self, allowMultipleClients):
        self.allowMultipleClients = allowMultipleClients

    def getGeneratedInstances(self):
        if self.server is None:
            return []
        return self.server.getGeneratedInstances()

    def stop(self):
        self.log.debug("Stopping the thread of the network server")

        self.close()
        #AbstractActor.stop(self)

    def write(self, message):
        self.log.warning("Oups, a network server cannot send message, only instanciated can")

    #+-----------------------------------------------------------------------+
    #| GETTERS AND SETTERS
    #+-----------------------------------------------------------------------+
    def save(self, root, namespace):
        """Save in the XML tree the actor definition"""
        xmlActor = etree.SubElement(root, "{" + namespace + "}communicationChannel")
        xmlActor.set("{http://www.w3.org/2001/XMLSchema-instance}type", "netzob:ServerNetworkChannel")
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

        xmlTargetPort = etree.SubElement(xmlActor, "{" + namespace + "}target_port")
        if self.getOriginalTargetPort() is not None:
            xmlTargetPort.text = str(self.getOriginalTargetPort())
        else:
            xmlTargetPort.text = ""

    @staticmethod
    def loadFromXML(rootElement, namespace, version, memory):
        # Then we verify its an IPC Message
        if rootElement.get("{http://www.w3.org/2001/XMLSchema-instance}type", "abstract") != "netzob:ServerNetworkChannel":
            raise NameError("The parsed xml doesn't represent a network server.")

        idActor = rootElement.get('id')

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
        actor = NetworkServer(idActor, memory, l4_protocol, bind_ip, bind_port, target_ip, target_port)
        return actor
