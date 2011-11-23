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
from netzob.Inference.Grammar.Oracles.NetworkOracle import NetworkOracle

#+---------------------------------------------- 
#| Related third party imports
#+----------------------------------------------

#+---------------------------------------------- 
#| Local application imports
#+----------------------------------------------


#+---------------------------------------------- 
#| LearningAlgorithm :
#|    Abstract class which provides to his children 
#| the necessary functions to learn 
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.3
#+---------------------------------------------- 
class LearningAlgorithm(object):
     
    def __init__(self, dictionary, communicationChannel):
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Inference.Grammar.LearningAlgorithm.py')
        self.dictionary = dictionary
        self.communicationChannel = communicationChannel
        self.inferedAutomata = None
    
    def learn(self):
        self.log.error("The LearningAlgorithm class doesn't support 'learn'.")
        raise NotImplementedError("The LearningAlgorithm class doesn't support 'learn'.")
        
        
    def submitQuery(self, query):
        self.log.info("Submit the following query : " + str(query))
        
        # transform the query into a MMSTD
        mmstd = query.toMMSTD(self.dictionary)
        
        # create an oracle for this MMSTD
        oracle = NetworkOracle(self.communicationChannel)
        
        # start the oracle with the MMSTD
        oracle.setMMSTD(mmstd)
        oracle.start()
        
#        # wait it has finished
        self.log.info("Waiting for the oracle to have finish")
        while oracle.isAlive() :
            time.sleep(0.01)
        self.log.info("The oracle has finished !")
        
        # stop the oracle and retrieve the query
        oracle.stop()
        
#        exit()
        resultQuery = oracle.getResults()
        
        self.log.info("The following query has been computed : " + str(resultQuery))
        # return only the last result
        return resultQuery[len(resultQuery) - 1]
    
    def getInferedAutomata(self):
        return self.inferedAutomata
