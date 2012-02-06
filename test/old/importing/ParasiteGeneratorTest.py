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

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Import.GOTPoisoning.ParasiteGenerator import ParasiteGenerator
from netzob.Import.GOTPoisoning.HijackedFunction import HijackedFunction
from netzob.Import.GOTPoisoning.InjectorGenerator import InjectorGenerator
from netzob.Import.GOTPoisoning.GOTPoisoner import GOTPoisoner

class ParasiteGeneratorTest(unittest.TestCase):
    
    def setUp(self):
        pass
    
    def test_sourceCodeGenerator(self):
        testFolder = "/home/gbt/Developpements/DLL_Injection/got_netzob"
        
        # create the parasite generator
        parasiteGenerator = ParasiteGenerator(testFolder)
        
        # register the two following functions to hijack
        # int     SSL_read(void *ssl,char *buf,int num);
        # int     SSL_write(void *ssl,char *buf,int num);        
#        sslReadFunc = HijackedFunction("SSL_read", "int", ["void *", "char *", "int"])
#        sslWriteFunc = HijackedFunction("SSL_write", "int", ["void *", "char *", "int"])
        putsFunc = HijackedFunction("puts", "int", [ ["char *", "param0"]])
        putsFunc.setSource('''''')

#        parasiteGenerator.addAnHijackedFunctions(sslReadFunc)
#        parasiteGenerator.addAnHijackedFunctions(sslWriteFunc)
        parasiteGenerator.addAnHijackedFunctions(putsFunc)
        
        parasiteGenerator.writeParasiteToFile()
        parasiteGenerator.compileParasite()
        parasiteGenerator.linkParasite()
        
        injectorGenerator = InjectorGenerator("/home/gbt/Developpements/DLL_Injection/got_netzob", parasiteGenerator)
        injectorGenerator.writeInjectorToFile()    
        injectorGenerator.compileInjector()
        
        poisoner = GOTPoisoner(parasiteGenerator, injectorGenerator) 
        poisoner.injectProcess(20121)
        
        
   
