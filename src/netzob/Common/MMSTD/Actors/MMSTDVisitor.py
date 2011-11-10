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
#| MMSTDVisitor :
#|     Definition of a visitor of an MMSTD automata
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.3
#+---------------------------------------------------------------------------+
class MMSTDVisitor():
    
    def __init__(self, mmstd, isMaster, abstractionLayer):
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Common.MMSTD.Actors.MMSTDVisitor.py')
        self.mmstd = mmstd
        self.isMaster = isMaster
        self.abstractionLayer = abstractionLayer
        
    def run(self):
        if self.isMaster :
            self.runAsMaster()
        else :
            self.runAsClient()
    
    
    def runAsMaster(self):
        self.log.info("The MMSTD Visitor is running as a master")
        active = True        
        currentState = self.mmstd.getInitialState()
        while active :
            currentState = currentState.executeAsMaster(self.abstractionLayer)
            if currentState == None :
                active = False
        
        
        
    def runAsClient(self):
        self.log.info("The MMSTD Visitor is running as a client")
        
        active = True
        
        currentState = self.mmstd.getInitialState()
        while active :
            currentState = currentState.executeAsClient(self.abstractionLayer)
            if currentState == None :
                active = False
        
        
        
                
    #+-----------------------------------------------------------------------+
    #| GETTERS AND SETTERS
    #+-----------------------------------------------------------------------+
    def getName(self):
        return self.name
    def getModel(self):
        return self.model
    def isMaster(self):
        return self.isMaster
    
    def setModel(self, model):
        self.model = model
    def setName(self, name):
        self.name = name
    
    
