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

#+---------------------------------------------- 
#| Standard library imports
#+----------------------------------------------
import logging

#+---------------------------------------------- 
#| Related third party imports
#+----------------------------------------------

#+---------------------------------------------- 
#| Local application imports
#+----------------------------------------------
from .. import ConfigurationParser

#+---------------------------------------------- 
#| Configuration of the logger
#+----------------------------------------------
loggingFilePath = ConfigurationParser.ConfigurationParser().get("logging", "path")
logging.config.fileConfig(loggingFilePath)

#+---------------------------------------------- 
#| MMSTD :
#|    Definition of an "Machine de Mealy Stochastiques
#|    à Transitions Déterministes"
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.3
#+---------------------------------------------- 
class MMSTD(object):
  
        
    
    #+---------------------------------------------- 
    #| Constructor :
    #+---------------------------------------------- 
    def __init__(self, initialState):
        
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Common.MMSTD.MMSTD.py')
       
        # Initial state
        self.initialState = initialState
       
       
  
    def getAllStates(self):
        states = []
        toAnalyze = []
        toAnalyze.append(self.initialState)        
        while (len(toAnalyze) > 0) :        
                
            currentState = toAnalyze.pop()
            if currentState != None :
                found = False
                for tmpState in states :
                        if tmpState.getID() == currentState.getID() :
                            found = True 
                if not found :
                    for transition in currentState.getTransitions() :
                        outputState = transition.getOutputState()
                        found = False
                        for tmpState in states :
                            if tmpState.getID() == outputState.getID() :
                                found = True
                        for tmpState in toAnalyze :
                            if tmpState.getID() == outputState.getID() :
                                found = True
                        if not found :
                            toAnalyze.append(outputState)
                    states.append(currentState)
      
        return states

    
