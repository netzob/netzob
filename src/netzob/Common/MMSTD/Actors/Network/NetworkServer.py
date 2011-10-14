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

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from .... import ConfigurationParser
from ..AbstractActor import AbstractActor
from ..MMSTDVisitor import MMSTDVisitor

#+---------------------------------------------------------------------------+
#| Configuration of the logger
#+---------------------------------------------------------------------------+
loggingFilePath = ConfigurationParser.ConfigurationParser().get("logging", "path")
logging.config.fileConfig(loggingFilePath)

#+---------------------------------------------------------------------------+
#| Container 
#+---------------------------------------------------------------------------+
class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    
    def setIsMaster(self, isMaster):
        self.isMaster = isMaster
    def isMaster(self):
        return self.isMaster
    
    
    def setAutomata(self, automata):
        self.automata = automata
    def getAutomata(self):
        return self.automata

class ConnectionHandler(SocketServer.StreamRequestHandler):
      
    def handle(self):
        self.log = logging.getLogger('netzob.Common.MMSTD.Actors.Network.NetworkServer_ConnectionHandler.py')
        self.log.info("A client has just initiated a connection on the server.")
        
        # Initialize a dedicated automata and creates a visitor
        modelVisitor = MMSTDVisitor(self.server.getAutomata(), self.server.isMaster(), self.rfile, self.wfile)
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
    
    def __init__(self, name, model, isMaster, host, port):
        AbstractActor.__init__(self, name, model, isMaster)
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Common.MMSTD.Actors.Network.NetworkServer.py')
        self.port = port
        self.host = host
        
    def run (self):
        # Instantiates the server
        self.server = ThreadedTCPServer((self.host, self.port), ConnectionHandler)        
        self.server.setAutomata(self.getModel())
#        self.server.setIsMaster(self.isMaster())
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.log.info("Starts a TCP Network Server listening on " + self.host + ":" + str(self.port) + ".")
        self.server_thread.start()
        
    
    
    #+-----------------------------------------------------------------------+
    #| GETTERS AND SETTERS
    #+-----------------------------------------------------------------------+
    def getPort(self):
        return self.port
    
    def setPort(self, port):
        self.port = port
    
