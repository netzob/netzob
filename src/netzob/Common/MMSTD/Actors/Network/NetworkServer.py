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
import logging
import SocketServer
SocketServer.TCPServer.allow_reuse_address = True
import threading
import time
import uuid
import select

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.MMSTD.Actors.AbstractActor import AbstractActor
from netzob.Common.MMSTD.Actors.MMSTDVisitor import MMSTDVisitor
from netzob.Common.MMSTD.Dictionary.AbstractionLayer import AbstractionLayer
from netzob.Common.MMSTD.MMSTD import MMSTD
from netzob.Common.MMSTD.Actors.Network.InstanciatedNetworkServer import InstanciatedNetworkServer
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

    def getVocabulary(self):
        return self.vocabulary

    def getInitialState(self):
        return self.initialState

    def isMaster(self):
        return self.master

    def setVocabulary(self, vocabulary):
        self.vocabulary = vocabulary

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

    def getVocabulary(self):
        return self.vocabulary

    def getInitialState(self):
        return self.initialState

    def isMaster(self):
        return self.master

    def setVocabulary(self, vocabulary):
        self.vocabulary = vocabulary

    def setInitialState(self, initialState):
        self.initialState = initialState

    def setMaster(self, master):
        self.master = master

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
        self.log = logging.getLogger('netzob.Common.MMSTD.Actors.Network.NetworkServer_ConnectionHandler.py')

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

        # We create an instantiated network server
        instanciatedNetworkServer = InstanciatedNetworkServer(self.request)

        # Create the input and output abstraction layer
        abstractionLayer = AbstractionLayer(instanciatedNetworkServer, vocabulary, Memory(vocabulary.getVariables()), self.server.getCBInputSymbol(), self.server.getCBOutputSymbol())

        # And we create an MMSTD visitor for this
        self.subVisitor = MMSTDVisitor("Instance-" + str(uuid.uuid4()), automata, isMaster, abstractionLayer)

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

    def handle(self):

        self.server.notifyAClientIsConnected()

        self.log = logging.getLogger('netzob.Common.MMSTD.Actors.Network.NetworkServer_ConnectionHandler.py')
        self.log.info("A client has just initiated a connection on the server.")

        # Create the input and output abstraction layer
        abstractionLayer = AbstractionLayer(self.rfile, self.wfile, self.server.getModel().getVocabulary(), Memory(self.server.getModel().getVocabulary().getVariables()), self.server.getCBInputSymbol(), self.server.getCBOutputSymbol())

        # Initialize a dedicated automata and creates a visitor
        modelVisitor = MMSTDVisitor(self.server.getModel(), self.server.isMaster(), abstractionLayer)
        self.log.info("An MMSTDVistor has been instantiated and assigned to the current network client.")
        modelVisitor.start()

        # save it
        self.server.addGeneratedInstance(modelVisitor)

        while (modelVisitor.isAlive()):
            ready = select.select([self.request], [], [], 1)
            time.sleep(0.1)

        self.server.notifyAClientIsDisconnected()


#+---------------------------------------------------------------------------+
#| NetworkServer:
#|     Definition of a server which follows the definition of the provided
#|     automata.
#+---------------------------------------------------------------------------+
class NetworkServer(AbstractActor):

    def __init__(self, host, protocol, port, sourcePort):
        AbstractActor.__init__(self, True, False)
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Common.MMSTD.Actors.Network.NetworkServer.py')

        self.port = port
        self.sourcePort = sourcePort
        self.host = host
        self.protocol = protocol
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
                if self.protocol == "UDP":
                    self.log.info("Configure an UDP Network Server to listen on " + self.host + ":" + str(self.port) + ".")
                    self.server = ThreadedUDPServer((self.host, self.port), UDPConnectionHandler)
                else:
                    self.log.info("Configure a TCP Network Server to listen on " + self.host + ":" + str(self.port) + ".")
                    self.server = ThreadedTCPServer((self.host, self.port), TCPConnectionHandler)
            except:
                self.log.warn("Impossible to open a server, attempts = " + str(nbAttempts) + "/" + str(maxNumberOfAttempts))
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

    def getMemory(self):
        return []

    def setAllowMultipleClients(self, allowMultipleClients):
        self.allowMultipleClients = allowMultipleClients

    def getGeneratedInstances(self):
        if self.server == None:
            return []
        return self.server.getGeneratedInstances()

    def stop(self):
        self.log.debug("Stopping the thread of the network server")

        self.close()
        AbstractActor.stop(self)

    #+-----------------------------------------------------------------------+
    #| GETTERS AND SETTERS
    #+-----------------------------------------------------------------------+
    def getPort(self):
        return self.port

    def setPort(self, port):
        self.port = port
