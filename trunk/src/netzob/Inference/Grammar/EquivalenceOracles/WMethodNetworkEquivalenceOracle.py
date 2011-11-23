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
from collections import deque
#+---------------------------------------------- 
#| Related third party imports
#+----------------------------------------------

#+---------------------------------------------- 
#| Local application imports
#+----------------------------------------------
from AbstractEquivalenceOracle import AbstractEquivalenceOracle
from netzob.Common.MMSTD.Symbols.impl.DictionarySymbol import DictionarySymbol
from netzob.Inference.Grammar.Queries.MembershipQuery import MembershipQuery
from netzob.Common.MMSTD.Symbols.impl.EmptySymbol import EmptySymbol



#+---------------------------------------------- 
#| WMethodNetworkEquivalenceOracle :
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.3
#+---------------------------------------------- 
class WMethodNetworkEquivalenceOracle(AbstractEquivalenceOracle):
     
    def __init__(self, communicationChannel, maxSize):
        AbstractEquivalenceOracle.__init__(self, "WMethodNetworkEquivalenceOracle")
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Inference.Grammar.EquivalenceOracles.WMethodNetworkEquivalenceOracle')       
        self.communicationChannel = communicationChannel
        self.m = maxSize
    
    def canWeDistinguishStates(self, mmstd, mq, state1, state2):            
        (traceState1, endStateTrace1) = mmstd.getOutputTrace(state1, mq.getSymbols())
        (traceState2, endStateTrace2) = mmstd.getOutputTrace(state2, mq.getSymbols())
        self.log.info("Trace 1 = " + str(traceState1))
        self.log.info("Trace 2 = " + str(traceState2)) 
        if traceState1 == traceState2 :
            self.log.info("Impossible to distinguish the strings")
            return False
        else :
            self.log.info("YES, its distinguished strings")
            return True
           
                
    
    def findCounterExample(self, mmstd): 
        self.log.info("Find a counterexample which invalids the given MMSTD")
        
        inputDictionary = []
        for entry in mmstd.dictionary.getEntries()[:2] :
            letter = DictionarySymbol(entry)
            inputDictionary.append(letter)
            self.log.info("INPUT : " + str(letter))
        
        # -----------------------------------------------------------------------
        # FIRST WE COMPUTE WHICH WILL WE MAKE !
        # -----------------------------------------------------------------------
        # This our plan to find same
        # STEP 1 : Estimate the maximum number of states (m) in the correct implementation 
        #          of the FSM (DONE PREVISOULY AND TRANSMITED THROUGH PARAM self.maxsize 
        # STEP 2 : Construct the characterization set W for [MMSTD]
        # STEP 3 : 
        #          (a) Construct the "testing tree" for MMSTD
        #          (b) Generate the transition cover set P from the testing tree
        # STEP 4 : Construct set Z from W and m
        # STEP 5 : We have the list of so desired test cases = P.Z
        
        # STEP 2 :
        # - Construct a sequence of k-equivalence partitions of the states of MMSTD :
       
        # Find all the couples of states 
        couples = []
        states = mmstd.getAllStates()
        W = []
        self.log.info("The MMSTD has " + str(len(states)) + " states")
        for state in states :
            for state2 in states :
                if state != state2 :
                    found = False
                    for (s1, s2) in couples :
                        if not ((s1 == state) and (s2 == state2) or ((s1 == state2) and (s2 == state))) :
                            found = True
                    if not found :
                        couples.append((state, state))
        self.log.info("A number of " + str(len(couples)) + " couples was found")
        
        for (state1, state2) in couples :
            self.log.info("Search a distinguish string between " + state1.getName() + " and " + state2.getName())
            z = MembershipQuery([EmptySymbol()])
            
            mqToTest = deque([])
            for letter in inputDictionary :
                mqToTest.append(z.getMQSuffixedWithMQ(MembershipQuery([letter])))
            
            lastIndiguishableZ = z
            distinguishableZ = z
            done = False
            i = 0 
            while not done :
                mq = mqToTest.popleft()   
                if i > self.m * self.m :
                    break
                
                
                self.log.info("Can we distinguish with MQ = " + str(mq))
                if not self.canWeDistinguishStates(mmstd, mq, state1, state2) :
                    done = False
                    lastIndiguishableZ = mq
                    for letter in inputDictionary :
                        z = mq.getMQSuffixedWithMQ(MembershipQuery([letter]))
                        mqToTest.append(z)
                else :
                    done = True
                    distinguishableZ = mq        
                
                i = i + 1
            self.log.info("FOUND : the following distinguish them : " + str(distinguishableZ) + " last which doesn't is " + str(lastIndiguishableZ))        
    
        self.log.info("W = " + str(W))
        
        # Execute STEP 3 : We compute P
        # init P = {E, ...}
        currentMQ = MembershipQuery([EmptySymbol()])
        P = [currentMQ]
        openMQ = deque([currentMQ])
        closeMQ = []
        statesSeen = [mmstd.getInitialState()]
        while len(openMQ) > 0 :
            mq = openMQ.popleft()
            tmpstatesSeen = []
            for letter in inputDictionary :
                z = mq.getMQSuffixedWithMQ(MembershipQuery([letter]))
                (trace, outputState) = mmstd.getOutputTrace(mmstd.getInitialState(), z.getSymbols())
                if outputState in statesSeen :
                    # we close this one
                    closeMQ.append(z)
                else :
                    tmpstatesSeen.append(outputState)
                    closeMQ.append(z)
                    # still open
                    
                    openMQ.append(z)
            statesSeen.extend(tmpstatesSeen)
        
        self.log.info("POSSIBLES : CLOSE : " + str(closeMQ))
        
        P.extend(closeMQ)    
        for m in P :
            self.log.info("=> " + str(m))
        
            
        
        
        
        
                
                    
            
            
            
            
            
        
        
        
        
        
        
        return None
