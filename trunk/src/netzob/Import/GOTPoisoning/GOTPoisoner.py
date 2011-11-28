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
import logging
import os

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| GOTPoisoner :
#|     Inject a parasite into specified process
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.2
#+---------------------------------------------------------------------------+
class GOTPoisoner():
    
    def __init__(self, parasite, injector):
        # create logger with the given configuration
        self.logger = logging.getLogger('netzob.Capturing.GOTPoisoning.GOTPoisoner.py')
        self.parasite = parasite
        self.injector = injector
        
    def injectProcess(self, pid):
        self.logger.info("Inject into process " + str(pid))
        
        
        
        functionNames = []
        for func in self.parasite.getFunctions() :
            functionNames.append(func.getName())
        
        f = os.popen(self.injector.getFolder() + "/netzob_injector " + str(pid) + " " + " ".join(functionNames))
        for i in f.readlines():
            print "EXEC:", i,
        
        
    
    
   
