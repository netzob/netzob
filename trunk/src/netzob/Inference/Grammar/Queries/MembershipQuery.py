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
from netzob.Common.MMSTD.States.impl.NormalState import NormalState

#+---------------------------------------------- 
#| Related third party imports
#+----------------------------------------------

#+---------------------------------------------- 
#| Local application imports
#+----------------------------------------------
from ....Common.MMSTD.Transitions.impl.SimpleTransition import SimpleTransition
from netzob.Common.MMSTD.Transitions.impl.OpenChannelTransition import OpenChannelTransition
from netzob.Common.MMSTD.Transitions.impl.CloseChannelTransition import CloseChannelTransition
from ....Common.MMSTD.MMSTD import MMSTD

#+---------------------------------------------- 
#| MembershipQuery :
#| Represents a set of query which will be submited to 
#| an oracle
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.3
#+---------------------------------------------- 
class MembershipQuery(object):
     
    def __init__(self, symbols):
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Inference.Grammar.Queries.MembershipQuery.py')
        self.symbols = symbols  


    def toMMSTD(self, dictionary):
        # We create an MMSTD which will submit the following symbols
        
        # Create the transition which opens the connection
        rootState = NormalState(0, "State 0")
        initialState = NormalState(1, "State 1")
        openingTransition = OpenChannelTransition(0, "Connection", rootState, initialState, 1000, 3)
        rootState.registerTransition(openingTransition)
        
        previousState = initialState
        idState = 2
        for symbol in self.symbols :
            self.log.info("=>" + str(symbol))
            # we create the current state
            currentState = NormalState(idState, "State " + str(idState))
            # we create a normal transition between it and the previous state
            idTransition = idState - 1
            transition = SimpleTransition(idTransition, "Transition " + str(idTransition), previousState, currentState, 3000, symbol)
            previousState.registerTransition(transition)
            idState = idState + 1
            previousState = currentState
            
        # Create the transition which close the connection
        endState = NormalState(idState, "State " + str(idState))
        closingTransition = CloseChannelTransition(idState - 1, "Disconnection", currentState, endState, 1000)
        currentState.registerTransition(closingTransition)
        
        mmstd = MMSTD(rootState, dictionary)   
        self.log.info(mmstd.getDotCode()) 
        return mmstd
        
        
    def __str__(self, *args, **kwargs):
        
        result = "MQ ("
        for symbol in self.symbols :
            result = result + str(symbol) + ", "
        
        return result + ")"
        
        
