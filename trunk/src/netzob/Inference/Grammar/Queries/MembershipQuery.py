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
        
        initialState = NormalState(0, "State 0")
        previousState = initialState
        idState = 1
        for symbol in self.symbols :
            # we create the current state
            currentState = NormalState(idState, "State " + str(idState))
            # we create a normal transition between it and the previous state
            idTransition = idState - 1
            transition = SimpleTransition(idTransition, "Transition " + str(idTransition), previousState, currentState, 1000, symbol)
            previousState.registerTransition(transition)
        
        mmstd = MMSTD(initialState, dictionary)    
        return mmstd
        
        
        
        
        
        
