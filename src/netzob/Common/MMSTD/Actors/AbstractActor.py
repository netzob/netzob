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
import logging.config
from threading import Thread

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from ... import ConfigurationParser

#+---------------------------------------------------------------------------+
#| Configuration of the logger
#+---------------------------------------------------------------------------+
#loggingFilePath = ConfigurationParser.ConfigurationParser().get("logging", "path")
#logging.config.fileConfig(loggingFilePath)

#+---------------------------------------------------------------------------+
#| AbstractActor :
#|     Definition of an actor
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.3
#+---------------------------------------------------------------------------+
class AbstractActor(Thread):
    
    def __init__(self, server):
        Thread.__init__(self)
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Common.MMSTD.Actors.AbstractActor.py')
        self.Terminated = False
        self.server = server
    
    def stop(self):
        self.Terminated = True
        
    def isServer(self):
        return self.server    
    
    #+-----------------------------------------------------------------------+
    #| GETTERS AND SETTERS
    #+-----------------------------------------------------------------------+
  
    
    
