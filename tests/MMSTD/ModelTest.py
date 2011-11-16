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
import gtk
import time
import os

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+
from xml.etree import ElementTree

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.MMSTD.States.impl.NormalState import NormalState
from netzob.Common.MMSTD.Tools.Parsers.MMSTDParser import MMSTDXmlParser
from netzob.Common.MMSTD.Tools.Drawing import MMSTDViewer
from netzob.Common.MMSTD.Actors.Network import NetworkServer 
from netzob.Common.MMSTD.Actors.Network import NetworkClient
from netzob.Common.ConfigurationParser import ConfigurationParser
from netzob.Common.MMSTD.Dictionary.AbstractionLayer import AbstractionLayer
from netzob.Common.MMSTD.Actors.MMSTDVisitor import MMSTDVisitor

class ModelTest(unittest.TestCase):
    
    def setUp(self):
        pass
    
    def test_GraphCreation(self):
        
        actorGrammar = "simple.xml"
        actorIP = "localhost"
        actorPort = 9998
        actorNetworkProtocol = "TCP"
        actorName = "SERVER"
        isMaster = False
        
        
        # Create a network server
        grammar_directory = ConfigurationParser().get("automata", "path") 
        xmlFile = os.path.join(grammar_directory, actorGrammar)
        tree = ElementTree.ElementTree()
        tree.parse(xmlFile)
        # Load the automata based on its XML definition
        automata = MMSTDXmlParser.MMSTDXmlParser.loadFromXML(tree.getroot())
            
        # Create the network layer
        communicationChannel = NetworkServer.NetworkServer(actorIP, actorNetworkProtocol, actorPort)
        
        # Create the abstraction layer for this connection
        abstractionLayer = AbstractionLayer(communicationChannel, automata.getDictionary())
        
        # And we create an MMSTD visitor for this
        visitor = MMSTDVisitor(actorName, automata, isMaster, abstractionLayer) 
        
        visitor.start()
        
        
        
        
        
      
        
      
