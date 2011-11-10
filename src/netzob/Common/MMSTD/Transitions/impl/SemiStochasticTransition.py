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
import random
import time


#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+
from xml.etree import ElementTree

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from .... import ConfigurationParser
from ..AbstractTransition import AbstractTransition
from ...Symbols.impl.EmptySymbol import EmptySymbol


#+---------------------------------------------------------------------------+
#| Configuration of the logger
#+---------------------------------------------------------------------------+
#loggingFilePath = ConfigurationParser.ConfigurationParser().get("logging", "path")
#logging.config.fileConfig(loggingFilePath)

#+---------------------------------------------------------------------------+
#| SemiStochasticTransition :
#|     Definition of a semi stochastic transition
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.3
#+---------------------------------------------------------------------------+
class SemiStochasticTransition(AbstractTransition):
    
    def __init__(self, id, name, inputState, outputState, inputSymbol):
        AbstractTransition.__init__(self, id, name, inputState, outputState)
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Common.MMSTD.Transitions.impl.SemiStochasticTransition.py')
        self.inputSymbol = inputSymbol
        # Output Symbols : [[Symbol, Probability, Time], [Symbol, Probability, Time]]
        self.outputSymbols = []
    
    #+-----------------------------------------------------------------------+
    #| getOutputSymbols
    #|     Return the associated output symbols
    #| @return the outputSymbols ([[Symbol, Probability, Time], [Symbol, Probability, Time]])
    #+-----------------------------------------------------------------------+
    def getOutputSymbols(self):
        return self.outputSymbols
    
    #+-----------------------------------------------------------------------+
    #| getInputSymbol
    #|     Return the associated oinput symbol
    #| @return the input symbol
    #+-----------------------------------------------------------------------+
    def getInputSymbol(self):
        return self.inputSymbol
    
    #+-----------------------------------------------------------------------+
    #| addOutputSymbol
    #|     Add an output symbol to the current transition
    #| @param outputsymbol the symbol to add
    #| @param probability the associated probability (<100)
    #| @param time the necessary time for this symbol
    #| @return the outputSymbols
    #+-----------------------------------------------------------------------+
    def addOutputSymbol(self, outputSymbol, probability, time):
        self.outputSymbols.append([outputSymbol, probability, time])
    
    
    #+-----------------------------------------------------------------------+
    #| isValid
    #|     Computes if the received symbol is valid
    #| @return a boolean which indicates if received symbol is equivalent
    #+-----------------------------------------------------------------------+
    def isValid(self, receivedSymbol):
        return self.inputSymbol.isEquivalent(receivedSymbol)
    
    #+-----------------------------------------------------------------------+
    #| pickOutputSymbol
    #|     Randomly select an output symbol
    #| @return the randomly picked output symbol [symbol, proba, time]
    #+-----------------------------------------------------------------------+
    def pickOutputSymbol(self):
        r = random.randrange(0, len(self.outputSymbols))
        return self.outputSymbols[r]
    
    #+-----------------------------------------------------------------------+
    #| executeAsClient
    #|     Randomly pick an outputSymbol and send it
    #| @param abstractionLayer the abstract layer to contact in order to reach outside world
    #| @return the new state
    #+-----------------------------------------------------------------------+
    def executeAsClient(self, abstractionLayer):
        self.activate()
        self.log.debug("Executing transition " + self.name + " with input : " + str(self.inputSymbol))
        if (len(self.outputSymbols) > 0) :
            [outputSymbol, probability, reactionTime] = self.pickOutputSymbol()
            
            # before sending it we simulate the reaction time
            time.sleep(int(reactionTime) / 1000)
            
            abstractionLayer.writeSymbol(outputSymbol)
        self.deactivate()
        return self.outputState
    
    #+-----------------------------------------------------------------------+
    #| executeAsMaster
    #|     Send input symbol and waits to received one of the output symbol
    #| @param input method access to the input flow
    #| @param abstractionLayer the abstract layer to contact in order to reach outside world
    #| @return the new state
    #+-----------------------------------------------------------------------+
    def executeAsMaster(self, abstractionLayer):
        self.activate()
        self.log.debug("Executing transition " + self.name)
        # write the input symbol on the output channel
        abstractionLayer.writeSymbol(self.inputSymbol)
        finish = False
        while (not finish) :
            # Wait for a message
            (receivedSymbol, message) = abstractionLayer.receiveSymbol()
            
            if (not (isinstance(receivedSymbol, EmptySymbol))):
                self.log.debug("The server consider the reception of symbol " + str(receivedSymbol))
                if (len(self.outputSymbols) == 0) :
                    self.log.debug("Nothing is considered since the server didn't expect anything.")
                    finish = True
                
                for arSymbol in self.outputSymbols :
                    [symbol, proba, time] = arSymbol
                    if symbol.isEquivalent(receivedSymbol) :
                        self.log.debug("Received symbol is understood !!")
                        finish = True
            
        self.deactivate()
        return self.outputState
     
    
    def getDescription(self):
        inputSymbolId = self.getInputSymbol().getID()
        
        desc = []
        for outSymbolDesc in self.getOutputSymbols() :
            desc.append("(" + str(outSymbolDesc[0].getID()) + ", " + str(outSymbolDesc[1]) + "%, " + str(outSymbolDesc[2]) + "ms)")
        
         
        return "(" + str(inputSymbolId) + ";{" + ",".join(desc) + "})"
    
    #+-----------------------------------------------------------------------+
    #| toXMLString
    #|     Abstract method to retrieve the XML definition of current transition
    #| @return String representation of the XML
    #+-----------------------------------------------------------------------+
    def toXMLString(self, idStartState):
        root = ElementTree.Element("transition")
        root.set("id", int(self.getID()))
        root.set("name", self.name)
        root.set("class", "SemiStochasticTransition")
        root.set("idStart", int(idStartState))
        root.set("idEnd", int(self.outputState.getID()))
                         
        # input symbol
        input = ElementTree.SubElement(root, "input")
        input.set("class", "DictionnarySymbol")
        input.text = str(self.inputSymbol.getID())
        
        # output symbols
        for arSymbol in self.outputSymbols :
            [symbol, proba, time] = arSymbol
            output = ElementTree.SubElement(root, "output")
            output.set("class", "DictionnarySymbol")
            output.set("probability", str(proba))
            output.set("time", str(time))
            output.text = str(symbol.getID())
                      
                      
                 
                 
        return ElementTree.tostring(root)
    
    
