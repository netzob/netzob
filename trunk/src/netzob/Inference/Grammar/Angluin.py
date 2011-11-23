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


from netzob.Inference.Grammar.Queries.MembershipQuery import MembershipQuery
from netzob.Common.MMSTD.Symbols.impl.DictionarySymbol import DictionarySymbol
from netzob.Inference.Grammar.LearningAlgorithm import LearningAlgorithm
from netzob.Common.MMSTD.Symbols.impl.EmptySymbol import EmptySymbol
from netzob.Common.MMSTD.Symbols.AbstractSymbol import AbstractSymbol
from numpy.core.numeric import zeros
from netzob.Common.MMSTD.States.impl.NormalState import NormalState
from netzob.Common.MMSTD.Transitions.impl.SimpleTransition import SimpleTransition
from netzob.Common.MMSTD.Transitions.impl.SemiStochasticTransition import SemiStochasticTransition
from netzob.Common.MMSTD.MMSTD import MMSTD
#+---------------------------------------------- 
#| Related third party imports
#+----------------------------------------------

#+---------------------------------------------- 
#| Local application imports
#+----------------------------------------------


#+---------------------------------------------- 
#| Angluin :
#|    Definition of the Angluin L*A algorithm to infer MEALY automatas
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.3
#+---------------------------------------------- 
class Angluin(LearningAlgorithm):
     
    def __init__(self, dictionary, communicationChannel):
        LearningAlgorithm.__init__(self, dictionary, communicationChannel)
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Inference.Grammar.Angluin.py')
        
        self.observationTable = dict()
        self.initializeObservationTable()
        
        

    def initializeObservationTable(self):
        self.log.info("Initialization of the observation table")
        self.suffixes = []
        self.D = []
        self.initialD = []
        # fullfill D with the dictionary
        for entry in self.dictionary.getEntries()[:2] :
            letter = DictionarySymbol(entry)
            mq = MembershipQuery([letter])
            self.addWordInD(mq)
            self.initialD.append(mq)
#            self.D.append(letter)
#            self.suffixes.append(letter)
        
        
        # Create the S and SA
        self.S = []
        self.SA = []
        
    
       
    
    
    def addWordInD(self, words):
        if words in self.D :
            self.log.info("The words " + str(words) + " already exists in D")
            return
        self.log.info("Adding word " + str(words) + " in D")
        self.D.append(words)
        self.observationTable[words] = None
        
    def addWordInS(self, word):
        # first we verify the word is not already in S
        if word in self.S :
            self.log.info("The word " + str(word) + " already exists in S")
            return 
        
        self.log.info("Adding word " + str(word) + " to S")
        self.S.append(word)
        
        # We create a MQ which looks like : MQ(word,letter)
        for letter in self.D :
            mq = word.getMQSuffixedWithMQ(letter)
            # we add it in the observation table
            if self.observationTable[letter] != None :
                cel = self.observationTable[letter]
            else :
                cel = dict()
            
            cel[word] = self.submitQuery(mq)    
            self.observationTable[letter] = cel 
        
        # Now we add 
        for letter in self.D :
            self.addWordInSA(word.getMQSuffixedWithMQ(letter))
    
    def addWordInSA(self, word):
        # first we verify the word is not already in SA
        if word in self.SA :
            self.log.info("The word " + str(word) + " already exists in SA")
            return
        
        if word in self.S :
            self.log.info("The word " + str(word) + " already exists in S (addWordInSA)")
            return 
        
        
        self.log.info("Adding word " + str(word) + " to SA")
        self.SA.append(word)
        
        for letter in self.D :
            mq = word.getMQSuffixedWithMQ(letter)
            if self.observationTable[letter] != None :
                cel = self.observationTable[letter]
            else :
                cel = dict()
            cel[word] = self.submitQuery(mq)    
            self.observationTable[letter] = cel
          
    
    def learn(self):
        self.log.info("Learn...")
                
        # Initialize the observation table
        emptyMQ = MembershipQuery([EmptySymbol()])
        self.addWordInS(emptyMQ)
        self.displayObservationTable()

#
        while (not self.isClosed() or not self.isConsistent()) :
            self.log.info("Another turn")
            self.displayObservationTable()
        
        # We compute an automata
        self.computeAutomata()
        
        self.log.info("We search for a counterexample...")
        # now we simulate a counter example :
        

#        conjectureConfirmed = False
#        while not conjectureConfirmed :
#            while (not self.isClosed() or not self.isConsistent()) :
#                if not self.isConsistent() :
#                    self.add_column()
#                if not self.isClosed() :
#                    self.move_row()
#                    
#            conjectureConfirmed = self.isEquivalent()
    
    def add_column(self):
        pass
    def move_row(self):
        pass
    def isEquivalent(self):
        return True
     
    def isClosed(self):
        rowSA = []
        rowS = []
        
        for wordSA in self.SA :
            rowSA = self.getRowOfObservationTable(wordSA)
            found = False
            for wordS in self.S :
                rowS = self.getRowOfObservationTable(wordS)
                
                if self.rowsEquals(rowS, rowSA) :
                    found = True

            if not found :
                self.log.info("The low-row associated with " + str(wordSA) + " was not found in S")
                self.moveWordFromSAtoS(wordSA)
                return False
        return True
    
    def isConsistent(self):
        # search for all the rows of S which are equals
        rowS = []
        equalsRows = []
        for wordS in self.S :
            rowS.append((wordS, self.getRowOfObservationTable(wordS)))
        for (word, row) in rowS :
            for (word2, row2) in rowS :
                if row != row2 and self.rowsEquals(row, row2) :
                    equalsRows.append((word, word2))
        self.log.info("Equals words : ")
        for (w1, w2) in equalsRows:
            self.log.info(str(w1) + " == " + str(w2))
        return len(equalsRows) == 0    
            
            
            
    
    def rowsEquals(self, r1, r2):
        if (len(r1) != len(r2)) :
            return False
        
        for r in r1 :
            if not r in r2 :
                return False
            
        return True
        
    
    def moveWordFromSAtoS(self, wordSA):
        if not wordSA in self.SA :
            self.log.warn("Impossible to move the word from SA since it doesn't exist")
            return
        self.SA.remove(wordSA)
        self.addWordInS(wordSA)
        
            
    def getRowOfObservationTable(self, rowName):
        cols = []
        for letter in self.D :
            cols.append(self.observationTable[letter][rowName])
        return cols
    
    def getUniqueRowsInS(self):
        # Unique rows in S => new states (name = value of the row)
        uniqueRowsInS = []
        for wordS in self.S :
            rowS = self.getRowOfObservationTable(wordS)
            found = False
            for (w, r) in uniqueRowsInS :
                if self.rowsEquals(r, rowS) :
                    found = True
            if not found :
                uniqueRowsInS.append((wordS, rowS))
        return uniqueRowsInS
        
    def getSandSAWords(self):
        result = []
        for wordS in self.S :
            result.append(wordS)
        for wordSA in self.SA :
            result.append(wordSA)
        return result    
    
    def computeAutomata(self):
        wordAndStates = []
        startState = None
        idState = 0
        idTransition = 0
        
        self.log.info("Compute the automata...")
        
        # Create the states of the automata
        uniqueRowsInS = self.getUniqueRowsInS()
        for (w, r) in uniqueRowsInS :
            self.log.info("The row with word " + str(w) + " is unique !")
            # We create a State for each unique row
            nameState = self.appendValuesInRow(r)
            self.log.info("Create state : " + nameState)
            currentState = NormalState(idState, nameState)
            wordAndStates.append((w, currentState))
            # Is it the starting state (wordS = [EmptySymbol])
            if startState == None and w == MembershipQuery([EmptySymbol()]):
                startState = currentState
                self.log.info("Its the starting state")
            
            idState = idState + 1
        
        # Create the transitions of the automata            
        for (word, state) in wordAndStates :
            for symbol in self.initialD :
                # retrieve the value :
                dicValue = self.observationTable[symbol]
                value = dicValue[word]
                # search for the output state
                mq = word.getMQSuffixedWithMQ(symbol)
                
                
                
                for wordSandSA in self.getSandSAWords() :
                    self.log.info("IS " + str(wordSandSA) + " eq " + str(mq))
                    if wordSandSA == mq :
                        rowOutputState = self.getRowOfObservationTable(wordSandSA)
                        outputStateName = self.appendValuesInRow(rowOutputState)
                        # search for the state having this name :
                        outputState = None
                        for (w2, s2) in wordAndStates :
                            if s2.getName() == outputStateName :
                                outputState = s2
                        if outputState != None :
                            inputSymbol = symbol.getSymbols()[0]
                            transition = SemiStochasticTransition(idTransition, "Transition " + str(idTransition), state, outputState, inputSymbol)
                            transition.addOutputSymbol(value, 100, 1000)
                            state.registerTransition(transition)
                            idTransition = idTransition + 1
                            self.log.info("We create a transition from " + str(state.getName()) + " input : " + str(symbol) + " output : " + str(value) + " outputstate " + str(outputState))

        mmstd = MMSTD(startState, self.dictionary)   
        self.log.info(mmstd.getDotCode())       
                
            
            
        
        
    def appendValuesInRow(self, row):
        result = []
        for i in range(0, len(row)) :
            result.append(str(row[i]))
        return '-'.join(result)
    
    def displayObservationTable(self):
        self.log.info(self.observationTable)
        
        horizontal = "---------------------------------------------------------------------------------"
        horizontal2 = "================================================================================="
        self.log.info(horizontal)
        line = []
        for letter in self.D :
            line.append(str(letter))
        self.log.info("\t|\t|" + "\t|".join(line))
        self.log.info(horizontal2)
        
        for mqS in self.S :
            line = []
            line.append(str(mqS))
            for letter in self.D :
                tmp = self.observationTable[letter]
                line.append(str(tmp[mqS]))
            self.log.info("\t|".join(line))
            self.log.info(horizontal)
        self.log.info(horizontal2)    
        for mqSA in self.SA :
            line = []
            line.append(str(mqSA))
            for letter in self.D :
                tmp = self.observationTable[letter]
                line.append(str(tmp[mqSA]))
            self.log.info("\t|".join(line))
            self.log.info(horizontal)
            
            
        
        
#        self.addWordInS(MembershipQuery([]))
        
