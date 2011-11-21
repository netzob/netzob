# -*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|         01001110 01100101 01110100 01111010 01101111 01100010             | 
#+---------------------------------------------------------------------------+
#| NETwork protocol modeliZatiOn By reverse engineering                      |
#| ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~+
#| @license      : GNU GPL v3                                                |
#| @copyright    : Georges Bossert and Frederic Guihery                      |
#| @url          : http://code.google.com/p/netzob/                          |
#| ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~+
#| @author       : {gbt,fgy}@amossys.fr                                      |
#| @organization : Amossys, http://www.amossys.fr                            |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+ 
#| Standard library imports
#+---------------------------------------------------------------------------+
import logging.config
import SocketServer
import threading
import time
import uuid

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from .... import ConfigurationParser
from ..AbstractActor import AbstractActor
from ..MMSTDVisitor import MMSTDVisitor
from ...Dictionary.AbstractionLayer import AbstractionLayer
from ...MMSTD import MMSTD
from .InstanciatedNetworkServer import InstanciatedNetworkServer

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
        
        # save it
        self.server.addGeneratedInstance(self.subVisitor)
        
        self.log.info("An MMSTDVistor has been instantiated and assigned to the current network client.")
        self.subVisitor.run()
        
    def finish(self):
        self.log.info("Closing the NetworkServer since the client is disconnected")
        SocketServer.BaseRequestHandler.finish(self)
        self.subVisitor.stop()
        
            
    
        
        
        
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
            self.server = ThreadedTCPServer((self.host, self.port), TCPConnectionHandler)
            self.log.info("Configure a TCP Network Server to listen on " + self.host + ":" + str(self.port) + ".")
            
            
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
        self.log.info("Stopping the thread of the network server")
        AbstractActor.stop(self)
    
    #+-----------------------------------------------------------------------+
    #| GETTERS AND SETTERS
    #+-----------------------------------------------------------------------+
    def getPort(self):
        return self.port
    
    def setPort(self, port):
        self.port = port
    
