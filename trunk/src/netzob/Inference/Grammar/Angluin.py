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

#+---------------------------------------------- 
#| Related third party imports
#+----------------------------------------------

#+---------------------------------------------- 
#| Local application imports
#+----------------------------------------------


#+---------------------------------------------- 
#| Angluin :
#|    Definition of the Angluin L*A algorithm
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.3
#+---------------------------------------------- 
class Angluin(object):
     
    def __init__(self, dictionary, oracle):
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Inference.Grammar.Angluin.py')
        self.dictionary = dictionary
        self.oracle = oracle
        self.results = None
    
    def learn(self):
        self.log.info("Learn...")
        entries = self.dictionary.getEntries()        
        query = MembershipQuery([DictionarySymbol(entries[0]), DictionarySymbol(entries[4]), DictionarySymbol(entries[6])])
        self.results = self.submitQuery(query)
        
        
    def submitQuery(self, query):
        self.log.info("Submit the following query : " + str(query))
        
        # transform the query into a MMSTD
        mmstd = query.toMMSTD(self.dictionary)
        
        # start the oracle with the MMSTD
        self.oracle.start(mmstd)
        
#        # wait it has finished
#        while not self.oracle.hasFinish() :
        time.sleep(10)
        
        # stop the oracle and retrieve the query
        self.oracle.stop()
        
        resultQuery = self.oracle.getResults()
        
        self.log.info("The following query has been computed : " + str(resultQuery))
        
        return resultQuery
        
        
        
    def getResult(self):
        return self.results
        
