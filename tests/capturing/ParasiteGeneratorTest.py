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
        putsFunc = HijackedFunction("puts", "int", ["char *"])
        putsFunc.setSource('''    int (*origfunc)(char *p) = 0x00000000;            
            int fd = _open("/tmp/content2.log");
            _write(fd, param0 , 3);
            _close(fd);
            origfunc("test");''')

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
        poisoner.injectProcess(24304)
        
        
   
