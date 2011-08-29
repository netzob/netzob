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


#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+
from xml.etree import ElementTree

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Import.GOTPoisoning import PrototypesRepositoryParser
from netzob.Common import ConfigurationParser


class PrototypesRepositoryTest(unittest.TestCase):
    
    def setUp(self):
        pass
    
    
    def test_loadFromXML(self):        
        repositoryFile = ConfigurationParser.ConfigurationParser().get("import", "repository_prototypes")
        print "Load Prototype repository from file : "+repositoryFile
        libs = PrototypesRepositoryParser.PrototypesRepositoryParser.loadFromXML(repositoryFile)
        for lib in libs :
            print "Lib "+lib.getName()+" has been parsed !"
            for func in lib.getFunctions() :
                print "\t-"+func.getPrototype()
                print func.getSource()
        
    

