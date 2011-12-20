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

#+---------------------------------------------------------------------------+
#| Container 
#+---------------------------------------------------------------------------+
class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    
    def __init__(self, connectionInfos, UDPConnectionHandler):
        SocketServer.TCPServer.__init__(self, connectionInfos, UDPConnectionHandler)  
        self.instances = []
        
    
    def getDictionary(self):
        return self.dictionary
    def getInitialState(self):
        return self.initialState
    def isMaster(self):
        return self.master
    
    def setDictionary(self, dictionary):
        self.dictionary = dictionary
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
    
    def shutdown(self):
        logging.info("shutingdown")
        SocketServer.TCPServer.shutdown(self)

class ThreadedUDPServer(SocketServer.ThreadingMixIn, SocketServer.UDPServer):
    
    def getDictionary(self):
        return self.dictionary
    def getInitialState(self):
        return self.initialState
    def isMaster(self):
        return self.master
    
    def setDictionary(self, dictionary):
        self.dictionary = dictionary
    def setInitialState(self, initialState):
        self.initialState = initialState
    def setMaster(self, master):
        self.master = master
    

class TCPConnectionHandler(SocketServer.BaseRequestHandler):
    
    def __init__(self, request, client_address, server):
        SocketServer.BaseRequestHandler.__init__(self, request, client_address, server)
        self.subVisitor = None
    
    def handle(self):
        self.log = logging.getLogger('netzob.Common.MMSTD.Actors.Network.NetworkServer_ConnectionHandler.py')
        self.log.info("A client has just initiated a connection on the server.")
        
        initialState = self.server.getInitialState()
        dictionary = self.server.getDictionary()
        isMaster = self.server.isMaster()
        
        # we create a sub automata
        automata = MMSTD(initialState, dictionary)

        # We create an instanciated network server
        instanciatedNetworkServer = InstanciatedNetworkServer(self.request)        
        
        # Create the input and output abstraction layer
        abstractionLayer = AbstractionLayer(instanciatedNetworkServer, dictionary)        
        
        # And we create an MMSTD visitor for this
        self.subVisitor = MMSTDVisitor("Instance-" + str(uuid.uuid4()), automata, isMaster, abstractionLayer) 
        
        self.log.info("An MMSTDVistor has been instantiated and assigned to the current network client.")
        self.subVisitor.start()
        
        # save it
        self.server.addGeneratedInstance(self.subVisitor)
        
        while (self.subVisitor.isAlive()) :
            ready = select.select([self.request], [], [], 1)
            time.sleep(0.1)
        
        self.log.warn("End of the execution of the TCP Connection handler")
#    def finish(self):
#        self.log.info("Closing the NetworkServer since the client is disconnected")
#        SocketServer.BaseRequestHandler.finish(self)
#        self.subVisitor.stop()
        
            
    
        
        
        
class UDPConnectionHandler(SocketServer.DatagramRequestHandler):
      
    def handle(self):
        self.log = logging.getLogger('netzob.Common.MMSTD.Actors.Network.NetworkServer_ConnectionHandler.py')
        self.log.info("A client has just initiated a connection on the server.")
        
        # Create the input and output abstraction layer
        abstractionLayer = AbstractionLayer(self.rfile, self.wfile, self.server.getModel().getDictionary())
        
        # Initialize a dedicated automata and creates a visitor
        modelVisitor = MMSTDVisitor(self.server.getModel(), self.server.isMaster(), abstractionLayer)
        self.log.info("An MMSTDVistor has been instantiated and assigned to the current network client.")
        modelVisitor.run()


#+---------------------------------------------------------------------------+
#| NetworkServer :
#|     Definition of a server which follows the definition of the provided 
#|     automata.
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.3
#+---------------------------------------------------------------------------+
class NetworkServer(AbstractActor):
    
    def __init__(self, host, protocol, port):
        AbstractActor.__init__(self, True)
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Common.MMSTD.Actors.Network.NetworkServer.py')
        self.port = port
        self.host = host
        self.protocol = protocol
        self.server = None
        self.instantiatedServers = []
        
    def openServer(self, dictionary, initialState, master):
        # Instantiates the server
        if self.protocol == "UDP" :
            self.server = ThreadedUDPServer((self.host, self.port), UDPConnectionHandler)
            self.log.info("Configure an UDP Network Server to listen on " + self.host + ":" + str(self.port) + ".")
        else :
            self.log.info("Configure a TCP Network Server to listen on " + self.host + ":" + str(self.port) + ".")
            self.server = ThreadedTCPServer((self.host, self.port), TCPConnectionHandler)
            
            
            
        self.server.setDictionary(dictionary)
        self.server.setInitialState(initialState)
        self.server.setMaster(master)
        
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.log.info("Start the server")
        self.server_thread.start()
        
    def close(self):
        self.log.info("Shuting down the server")
        self.server.shutdown()
        
    def getInputMessages(self):
        return []
    def getOutputMessages(self):
        return []
    def getMemory(self):
        return []
    def getGeneratedInstances(self):
        if self.server == None :
            return []
        return self.server.getGeneratedInstances()
    
    def stop(self):
        self.log.debug("Stopping the thread of the network server")
        AbstractActor.stop(self)
    
    #+-----------------------------------------------------------------------+
    #| GETTERS AND SETTERS
    #+-----------------------------------------------------------------------+
    def getPort(self):
        return self.port
    
    def setPort(self, port):
        self.port = port
    
