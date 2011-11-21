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
from Angluin import Angluin

#+---------------------------------------------- 
#| GrammarInferer :
#|    Given Angluin's L*a algorithm, it learns
#|    the grammar of a protocol
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.3
#+---------------------------------------------- 
class GrammarInferer(object):
     
    def __init__(self, dictionary, oracle, equivalenceOracle):
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Inference.Grammar.GrammarInferer.py')
        self.dictionary = dictionary
        self.oracle = oracle
        self.equivalenceOracle = equivalenceOracle
        
    
    def infer(self):
        
        # we first initialize the angluin's algo
        learner = Angluin(self.dictionary, self.oracle)
        
        equivalent = False
        
        while not equivalent :
            self.log.info("Execute one new round of the infering process")
            
            learner.learn()
                        
            hypotheticalAutomaton = learner.getResult()
            self.log.info("An hypothetical automaton has been computed")
            
            counterExample = None #self.equivalenceOracle.findCounterExample(hypotheticalAutomaton)
            if counterExample == None :
                self.log.info("No counter-example were found !")
                equivalent = True
            else :
                self.log.info("A counter-example has been found")
                learner.addCounterExample(counterExample)
            
        automaton = learner.getResult()    
        
        self.log.info("The infering process is finished !")
        self.log.info("The following automaton has been computed : " + str(automaton))
            
            
        
            
            
        
    
