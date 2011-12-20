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


#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+
from xml.etree import ElementTree

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Import.GOTPoisoning import PrototypesRepositoryParser
from netzob.Common import ConfigurationParser
from netzob.Common import SharedLib
from netzob.Import.GOTPoisoning import HijackedFunction


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

        
    def test_saveInXML(self):
        libName = "testLib"
        funcName = "testFunc"
        returnType = "int"
        parameters = [["char *", "buffer"], ["int", "taille_buffer"]]
        newlib = SharedLib.SharedLib(libName)
        func = HijackedFunction.HijackedFunction(funcName, returnType, parameters)
        newlib.setFunctions([func])
        
        
        
        
        
        
