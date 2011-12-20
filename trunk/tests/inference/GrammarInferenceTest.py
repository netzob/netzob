#!/usr/bin/python
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
from netzob.Inference.Grammar.EquivalenceOracles.WMethodNetworkEquivalenceOracle import WMethodNetworkEquivalenceOracle
from netzob.Common.MMSTD.Actors.Network.NetworkClient import NetworkClient
from netzob.Common.MMSTD.Actors.Network.NetworkServer import NetworkServer
from netzob.Common.MMSTD.Actors.MMSTDVisitor import MMSTDVisitor
from netzob.Common.MMSTD.Dictionary.AbstractionLayer import AbstractionLayer
from netzob.Common.ConfigurationParser import ConfigurationParser
from netzob.Common.MMSTD.Tools.Parsers.MMSTDParser.MMSTDXmlParser import MMSTDXmlParser
from netzob.Common.MMSTD.States.impl.NormalState import NormalState
from netzob.Common.MMSTD.Transitions.impl.SemiStochasticTransition import SemiStochasticTransition
from netzob.Common.MMSTD.Symbols.impl.DictionarySymbol import DictionarySymbol
from netzob.Common.MMSTD.MMSTD import MMSTD

class GrammarInferenceTest(unittest.TestCase):
    
    def setUp(self):
        pass
    
    def test_WMethod(self):
        
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
        
        # Lets create a X-METHOD equivalence network oracle
        oracleCommunicationChannel = NetworkClient(actorIP, actorNetworkProtocol, actorPort)
        equivalenceOracle = WMethodNetworkEquivalenceOracle(oracleCommunicationChannel, 3)
        
        # We create a temporary MMSTD (to simulate the research of a counter-exemple)
        state1 = NormalState(0, "q1")
        state2 = NormalState(1, "q2")
        
        symbola = DictionarySymbol(dictionary.getEntry(1))
        symbolb = DictionarySymbol(dictionary.getEntry(2))
        symbol0 = DictionarySymbol(dictionary.getEntry(3))
        symbol1 = DictionarySymbol(dictionary.getEntry(4))
        
        transition0 = SemiStochasticTransition(0, "transition-0", state1, state2, symbola)
        transition0.addOutputSymbol(symbol0, 100, 500)
        state1.registerTransition(transition0)
        
        transition1 = SemiStochasticTransition(1, "transition-1", state1, state2, symbolb)
        transition1.addOutputSymbol(symbol0, 100, 500)
        state1.registerTransition(transition1)
        
        transition2 = SemiStochasticTransition(0, "transition-2", state2, state2, symbola)
        transition2.addOutputSymbol(symbol1, 100, 500)
        state2.registerTransition(transition2)
        
        transition3 = SemiStochasticTransition(1, "transition-3", state2, state2, symbolb)
        transition3.addOutputSymbol(symbol1, 100, 500)
        state2.registerTransition(transition3)
    
        mmstd = MMSTD(state1, dictionary)
        
        logging.info(mmstd.getDotCode())
        equivalenceOracle.findCounterExample(mmstd)
        
        
        
        server.stop()
    
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
        # Lets create an equivalence oracle
        equivalenceOracle = WMethodNetworkEquivalenceOracle(oracleCommunicationChannel, 5)
        
        inferer = GrammarInferer(dictionary, oracleCommunicationChannel, equivalenceOracle)
        resultedAutomaton = inferer.infer()
        
        logging.info(resultedAutomaton.getDotCode())
        
        

        server.stop()

