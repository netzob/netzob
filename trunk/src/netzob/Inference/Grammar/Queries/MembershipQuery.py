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

    def addSymbol(self, symbol):
        self.symbols.append(symbol)
        
    def getSymbols(self):
        return self.symbols

    def getSymbolsWhichAreNotEmpty(self):
        result = []
        for s in self.symbols :
            if s.getType() != "EmptySymbol" :
                result.append(s)
        return result
     
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
   
    def multiply(self, mqs):
        result = []
        for mq in mqs :
            result.append(self.getMQSuffixedWithMQ(mq))
        return result
        
        
        
   
    def getMQSuffixedWithMQ(self, mq):
        result = MembershipQuery([])
        for s in self.getSymbols() :
            result.addSymbol(s)
        
        for symbol in mq.getSymbols() :
            result.addSymbol(symbol)
        return result
    
    def isStrictlyEqual(self, other):
        if (len(self.getSymbolsWhichAreNotEmpty()) == len(other.getSymbolsWhichAreNotEmpty())) :
            symbols = self.getSymbolsWhichAreNotEmpty()
            symbols2 = other.getSymbolsWhichAreNotEmpty()
            
            nbSymbol = len(symbols)
            
            for i in range(0, nbSymbol) :
                if symbols[i].getID() != symbols2[i].getID() :
                    return False
            return True
        else :
            return False
            
                           
            
            
            
                
    def __cmp__(self, other):
        # Do not consider the EmptySymbols when comparing
        
        if (len(self.getSymbolsWhichAreNotEmpty()) == len(other.getSymbolsWhichAreNotEmpty())) :
            
            for symbol in self.getSymbolsWhichAreNotEmpty() :
                idself = symbol.getID()
                found = False
                for otherSymbol in other.getSymbolsWhichAreNotEmpty() :
                    if otherSymbol.getID() == idself :
                        found = True
                if not found :
                    return 1
            return 0
                
            
        elif (len(self.getSymbolsWhichAreNotEmpty()) > len(other.getSymbolsWhichAreNotEmpty())) :
            return 1
        else :
            return -1
        
        
    def __str__(self, *args, **kwargs):
        
        result = "MQ ("
        for symbol in self.symbols :
            result = result + str(symbol) + ", "
        
        return result + ")"
        
        
