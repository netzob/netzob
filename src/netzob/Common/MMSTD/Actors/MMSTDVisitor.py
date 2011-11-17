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
import threading

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from ... import ConfigurationParser

#+---------------------------------------------------------------------------+
#| MMSTDVisitor :
#|     Definition of a visitor of an MMSTD automata
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.3
#+---------------------------------------------------------------------------+
class MMSTDVisitor(threading.Thread):
    
    def __init__(self, name, mmstd, isMaster, abstractionLayer):
        threading.Thread.__init__(self)
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Common.MMSTD.Actors.MMSTDVisitor.py')
        self.name = name
        self.model = mmstd
        self.isMaster = isMaster
        self.abstractionLayer = abstractionLayer
        self.active = False
    
    def run(self):
        self.active = True
        if self.isMaster :
            self.runAsMaster()
        else :
            self.runAsClient()
   
    def stop(self):
        self.abstractionLayer.disconnect()
        self.active = False
        
    
    
    def runAsMaster(self):
        self.log.info("The MMSTD Visitor is running as a master")    
        currentState = self.model.getInitialState()
        while self.active :
            currentState = currentState.executeAsMaster(self.abstractionLayer)
            if currentState == None :
                self.active = False
        self.log.info("The MASTER stops !")
        
        
    def runAsClient(self):
        self.log.info("The MMSTD Visitor is running as a client")
       
        currentState = self.model.getInitialState()
        while self.active :
            currentState = currentState.executeAsClient(self.abstractionLayer)
            if currentState == None :
                self.active = False
        self.log.info("The CLIENT stops !")
        
    def getInputMessages(self):
        return self.abstractionLayer.getInputMessages()
    def getOutputMessages(self):
        return self.abstractionLayer.getOutputMessages()  
    def getMemory(self):
        return self.abstractionLayer.getMemory()
    def getAbstractionLayer(self):
        return self.abstractionLayer
                
    #+-----------------------------------------------------------------------+
    #| GETTERS AND SETTERS
    #+-----------------------------------------------------------------------+
    def getName(self):
        return self.name
    def getModel(self):
        return self.model
    def isMaster(self):
        return self.isMaster
    def isActive(self):
        return self.active
   
    def setModel(self, model):
        self.model = model
    def setName(self, name):
        self.name = name
    
    
