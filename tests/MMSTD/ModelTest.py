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

class ModelTest(unittest.TestCase):
    
    def setUp(self):
        pass
    
    def test_GraphCreation(self):
        print "Graph created !"
        
        xmlFile = "resources/workspace/automaton/reputation.xml"     
        tree = ElementTree.ElementTree()
        tree.parse(xmlFile)
        
          
        automataServer = MMSTDXmlParser.MMSTDXmlParser.loadFromXML(tree.getroot())
        automataClient = MMSTDXmlParser.MMSTDXmlParser.loadFromXML(tree.getroot())
        
        actor = NetworkServer.NetworkServer("Server", automataServer, False, "10.94.0.100", "UDP", 8007)
#        actor = NetworkClient.NetworkClient("Client1", automataClient, True, "79.125.11.244", "UDP", 8007)
        actor.start()

        time.sleep(2)

        
#        actor.start()
        
        
        
      
        
      
