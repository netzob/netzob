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

class ModelTest(unittest.TestCase):
    
    def setUp(self):
        pass
    
    def test_GraphCreation(self):
        print "Graph created !"
        
        xmlFile = "resources/automaton/example1.xml"     
        tree = ElementTree.ElementTree()
        tree.parse(xmlFile)
           
        automata = MMSTDXmlParser.MMSTDXmlParser.loadFromXML(tree.getroot())
        viewer = MMSTDViewer.MMSTDViewer(automata)
        viewer.start()
        
        # now we create two network actors, one is a client and the other is a server
        actor1 = NetworkServer.NetworkServer("Server", automata, False, "localhost", 7010)
        actor1.start()
        
#        actor2 = NetworkServer.NetworkServer("Server2", automata, True, "localhost", 7001)
#        actor2.start()
        
        
        
        
      
        
      
