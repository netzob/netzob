#!/usr/bin/python
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

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from .... import ConfigurationParser
from ..AbstractActor import AbstractActor
from ..MMSTDVisitor import MMSTDVisitor
from ...Dictionary.AbstractionLayer import AbstractionLayer

#+---------------------------------------------------------------------------+
#| Configuration of the logger
#+---------------------------------------------------------------------------+
loggingFilePath = ConfigurationParser.ConfigurationParser().get("logging", "path")
logging.config.fileConfig(loggingFilePath)

#+---------------------------------------------------------------------------+
#| Container 
#+---------------------------------------------------------------------------+
class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    
    def setIsMaster(self, master):
        self.master = master
    def isMaster(self):
        return self.master
    
    
    def setModel(self, model):
        self.model = model
    def getModel(self):
        return self.model

class ThreadedUDPServer(SocketServer.ThreadingMixIn, SocketServer.UDPServer):
    
    def setIsMaster(self, master):
        self.master = master
    def isMaster(self):
        return self.master
    
    
    def setModel(self, model):
        self.model = model
    def getModel(self):
        return self.model
    
    

class TCPConnectionHandler(SocketServer.StreamRequestHandler):
      
    def handle(self):
        self.log = logging.getLogger('netzob.Common.MMSTD.Actors.Network.NetworkServer_ConnectionHandler.py')
        self.log.info("A client has just initiated a connection on the server.")
        
        time.sleep(2)
        
        # Create the input and output abstraction layer
        abstractionLayer = AbstractionLayer(self.rfile, self.wfile, self.server.getModel().getDictionary())
        
        # Initialize a dedicated automata and creates a visitor
        modelVisitor = MMSTDVisitor(self.server.getModel(), self.server.isMaster(), abstractionLayer)
        self.log.info("An MMSTDVistor has been instantiated and assigned to the current network client.")
        modelVisitor.run()
        
class UDPConnectionHandler(SocketServer.DatagramRequestHandler):
      
    def handle(self):
        self.log = logging.getLogger('netzob.Common.MMSTD.Actors.Network.NetworkServer_ConnectionHandler.py')
        self.log.info("A client has just initiated a connection on the server.")
        
        time.sleep(2)
        
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
    
    def __init__(self, name, model, isMaster, host, protocol, port):
        AbstractActor.__init__(self, name, model, isMaster)
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Common.MMSTD.Actors.Network.NetworkServer.py')
        self.port = port
        self.host = host
        self.protocol = protocol
        
    def run (self):
        # Instantiates the server
        if self.protocol == "UDP" :
            self.server = ThreadedUDPServer((self.host, self.port), UDPConnectionHandler)
            self.log.info("Configure an UDP Network Server to listen on " + self.host + ":" + str(self.port) + ".")
        else :
            self.server = ThreadedTCPServer((self.host, self.port), TCPConnectionHandler)
            self.log.info("Configure a TCP Network Server to listen on " + self.host + ":" + str(self.port) + ".")
        
                
        self.server.setModel(self.getModel())
        self.server.setIsMaster(self.isMaster())
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.log.info("Start the server")
        self.server_thread.start()
        
    def getInputMessages(self):
        return []
    def getOutputMessages(self):
        return []
    def getMemory(self):
        return []
    
    
    #+-----------------------------------------------------------------------+
    #| GETTERS AND SETTERS
    #+-----------------------------------------------------------------------+
    def getPort(self):
        return self.port
    
    def setPort(self, port):
        self.port = port
    
