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
import unittest
import random
import os
import time
import logging

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+
from xml.etree import ElementTree

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Inference.Grammar.Oracles.NetworkOracle import NetworkOracle
from netzob.Inference.Grammar.GrammarInferer import GrammarInferer
from netzob.Common.MMSTD.Actors.Network.NetworkClient import NetworkClient
from netzob.Common.MMSTD.Actors.Network.NetworkServer import NetworkServer
from netzob.Common.MMSTD.Actors.MMSTDVisitor import MMSTDVisitor
from netzob.Common.MMSTD.Dictionary.AbstractionLayer import AbstractionLayer
from netzob.Common.ConfigurationParser import ConfigurationParser
from netzob.Common.MMSTD.Tools.Parsers.MMSTDParser.MMSTDXmlParser import MMSTDXmlParser

class GrammarInferenceTest(unittest.TestCase):
    
    def setUp(self):
        pass
    
    def test_grammarInference(self):
        
        # First we create the server and starts it
        actorGrammar = "example_learning.xml"
        actorIP = "localhost"
        actorPort = random.randint(9000, 9999)
        actorNetworkProtocol = "TCP"
        
        serverName = "Server"
        
        
        # Create a network server
        grammar_directory = ConfigurationParser().get("automata", "path") 
        xmlFile = os.path.join(grammar_directory, actorGrammar)
        tree = ElementTree.ElementTree()
        tree.parse(xmlFile)
        # Load the automata based on its XML definition
        serverAutomata = MMSTDXmlParser.loadFromXML(tree.getroot())
        dictionary = serverAutomata.getDictionary()
            
        # Create the network layer
        serverCommunicationChannel = NetworkServer(actorIP, actorNetworkProtocol, actorPort)
        
        # Create the abstraction layer for this connection
        serverAbstractionLayer = AbstractionLayer(serverCommunicationChannel, serverAutomata.getDictionary())
        
        # And we create an MMSTD visitor for this
        server = MMSTDVisitor(serverName, serverAutomata, False, serverAbstractionLayer) 
        server.run()     
        
        logging.info("Starting the server")
        time.sleep(1)
        
        
        
        
        # Lets create a simple network oracle
        oracleCommunicationChannel = NetworkClient(actorIP, actorNetworkProtocol, actorPort)
        
        equivalenceOracle = None
        
        inferer = GrammarInferer(dictionary, oracleCommunicationChannel, equivalenceOracle)
        inferer.infer()

        server.stop()

