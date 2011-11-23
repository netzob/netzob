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

#+---------------------------------------------- 
#| Standard library imports
#+----------------------------------------------
import logging
import time

#+---------------------------------------------- 
#| Related third party imports
#+----------------------------------------------

#+---------------------------------------------- 
#| Local application imports
#+----------------------------------------------
from AbstractOracle import AbstractOracle
from ....Common.MMSTD.Dictionary.AbstractionLayer import AbstractionLayer
from ....Common.MMSTD.Actors.MMSTDVisitor import MMSTDVisitor
from ....Common.MMSTD.Symbols.impl.DictionarySymbol import DictionarySymbol
import threading

#+---------------------------------------------- 
#| NetworkOracle :
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.3
#+---------------------------------------------- 
class NetworkOracle(threading.Thread):
     
    def __init__(self, communicationChannel):
        threading.Thread.__init__(self)
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Inference.Grammar.Oracle.NetworkOracle.py')       
        self.communicationChannel = communicationChannel
    
        
    def setMMSTD(self, mmstd):
        self.mmstd = mmstd
        
    def run(self): 
        self.log.info("Start the network oracle based on given MMSTD")
        
        # Create the abstraction layer for this connection
        abstractionLayer = AbstractionLayer(self.communicationChannel, self.mmstd.getDictionary())
        
        # And we create an MMSTD visitor for this
        self.oracle = MMSTDVisitor("MMSTD-NetworkOracle", self.mmstd, True, abstractionLayer) 
        self.oracle.start()  
        
        while (self.oracle.isAlive()) :
            time.sleep(0.01)
            
        self.log.warn("The network ORACLE has finished")
        
        
        
    def stop(self):
        self.log.info("Stop the network oracle")
        self.oracle.stop()
    
    def hasFinish(self):
        return not self.oracle.isActive()
        
        
    def getResults(self):
        symbols = []
        # Retrieve all the IO from the abstraction layer
        abstractionLayer = self.oracle.getAbstractionLayer()        
        for io in abstractionLayer.getGeneratedInputAndOutputsSymbols() :
            symbols.append(DictionarySymbol(io))
        return symbols
