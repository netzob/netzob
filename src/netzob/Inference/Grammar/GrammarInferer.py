# -*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|          01001110 01100101 01110100 01111010 01101111 01100010            |
#|                                                                           |
#|               Netzob : Inferring communication protocols                  |
#+---------------------------------------------------------------------------+
#| Copyright (C) 2011 Georges Bossert and Frédéric Guihéry                   |
#| This program is free software: you can redistribute it and/or modify      |
#| it under the terms of the GNU General Public License as published by      |
#| the Free Software Foundation, either version 3 of the License, or         |
#| (at your option) any later version.                                       |
#|                                                                           |
#| This program is distributed in the hope that it will be useful,           |
#| but WITHOUT ANY WARRANTY; without even the implied warranty of            |
#| MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the              |
#| GNU General Public License for more details.                              |
#|                                                                           |
#| You should have received a copy of the GNU General Public License         |
#| along with this program. If not, see <http://www.gnu.org/licenses/>.      |
#+---------------------------------------------------------------------------+
#| @url      : http://www.netzob.org                                         |
#| @contact  : contact@netzob.org                                            |
#| @sponsors : Amossys, http://www.amossys.fr                                |
#|             Supélec, http://www.rennes.supelec.fr/ren/rd/cidre/           |
#+---------------------------------------------------------------------------+

#+---------------------------------------------- 
#| Standard library imports
#+----------------------------------------------
import logging
import os

#+---------------------------------------------- 
#| Related third party imports
#+----------------------------------------------

#+---------------------------------------------- 
#| Local application imports
#+----------------------------------------------
from Angluin import Angluin
from netzob.Inference.Grammar.Queries.MembershipQuery import MembershipQuery
from netzob.Common.MMSTD.Symbols.impl.DictionarySymbol import DictionarySymbol

#+---------------------------------------------- 
#| GrammarInferer :
#|    Given Angluin's L*a algorithm, it learns
#|    the grammar of a protocol
#+---------------------------------------------- 
class GrammarInferer(object):
     
    def __init__(self, vocabulary, oracle, equivalenceOracle):
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Inference.Grammar.GrammarInferer.py')
        self.vocabulary = vocabulary
        self.oracle = oracle
        self.equivalenceOracle = equivalenceOracle
        
    
    def infer(self):
        
        # we first initialize the angluin's algo
        learner = Angluin(self.vocabulary, self.oracle)
        
        equivalent = False
        
        while not equivalent :
            self.log.info("=============================================================================")
            self.log.info("Execute one new round of the infering process")
            self.log.info("=============================================================================")
            
            learner.learn()
            hypotheticalAutomaton = learner.getInferedAutomata()            
            self.log.info("An hypothetical automaton has been computed") 
            
            counterExample = self.equivalenceOracle.findCounterExample(hypotheticalAutomaton)
            
            if counterExample == None :
                self.log.info("No counter-example were found !")
                equivalent = True
            else :
                self.log.info("A counter-example has been found")
                for s in counterExample.getSymbols() :
                    self.log.info("symbol : " + str(s) + " => " + str(s.getID()))                
                learner.addCounterExamples([counterExample])
            
        automaton = learner.getInferedAutomata()    
        
        self.log.info("The infering process is finished !")
        self.log.info("The following automaton has been computed : " + str(automaton))
        return automaton    
            
        
            
            
        
    
