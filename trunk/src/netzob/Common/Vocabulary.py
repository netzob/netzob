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
import logging
from xml.etree import ElementTree

#+---------------------------------------------------------------------------+
#| Local Imports
#+---------------------------------------------------------------------------+
from netzob.Common.Symbol import Symbol
import time
from netzob.Inference.Vocabulary.Clusterer import Clusterer
from netzob.Common.ProjectConfiguration import ProjectConfiguration

#+---------------------------------------------------------------------------+
#| Vocabulary :
#|     Class definition of the vocabulary
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.2
#+---------------------------------------------------------------------------+
class Vocabulary(object):
    
    #+-----------------------------------------------------------------------+
    #| Constructor
    #+-----------------------------------------------------------------------+
    def __init__(self):
        self.symbols = []
        
 
    
    def getAllMessages(self):
        messages = []
        for symbol in self.symbols :
            for msg in symbol.getMessages() :
                messages.append(msg)
        return messages
    
    def getSymbols(self):
        return self.symbols    
    
    def getSymbol(self, symbolID):
        for symbol in self.symbols :
            if symbol.getID() == symbolID :
                return symbol
        return None
        
    def addSymbol(self, symbol):
        if not symbol in self.symbols :
            self.symbols.append(symbol)
        else :
            logging.warn("The symbol cannot be added in the vocabulary since it's already declared in.")
            
    def removeSymbol(self, symbol):
        self.symbols.remove(symbol)
        
        
        
    #+---------------------------------------------- 
    #| alignWithNeedlemanWunsh:
    #|  Align each messages of each group with the
    #|  Needleman Wunsh algorithm
    #+----------------------------------------------
    def alignWithNeedlemanWunsh(self, configuration, callback):
        tmpSymbols = []
        t1 = time.time()

        # We try to clusterize each symbol
        for symbol in self.symbols :
            clusterer = Clusterer(configuration, [symbol], explodeSymbols=True)
            clusterer.mergeGroups()
            tmpSymbols.extend(clusterer.getSymbols())
                
        # Now that all the groups are reorganized separately
        # we should consider merging them
        logging.info("Merging the symbols extracted from the different files")
        clusterer = Clusterer(configuration, tmpSymbols, explodeSymbols=False)
        clusterer.mergeGroups()
        
        # Now we execute the second part of NETZOB Magical Algorithms :)
        # clean the single groups  
        mergeOrphanReduction = configuration.getVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_ORPHAN_REDUCTION)          
        if mergeOrphanReduction :
            logging.info("Merging the orphan groups") 
            clusterer.mergeOrphanGroups()

        logging.info("Time of parsing : " + str(time.time() - t1))
        
        self.symbols = clusterer.getSymbols()
        callback()
        
    def save(self, root, namespace):
        xmlVocabulary = ElementTree.SubElement(root, "{" + namespace + "}vocabulary")
        xmlSymbols = ElementTree.SubElement(xmlVocabulary, "{" + namespace + "}symbols")
        for symbol in self.symbols :
            symbol.save(xmlSymbols, namespace)
    
    @staticmethod
    def loadVocabulary(xmlRoot, namespace, version):
        vocabulary = Vocabulary()
        
        if version == "0.1" :
            # parse all the symbols which are declared in the vocabulary
            for xmlSymbol in xmlRoot.findall("{" + namespace + "}symbols/{" + namespace + "}symbol") :
                symbol = Symbol.loadSymbol(xmlSymbol, namespace, version)
                if symbol != None :
                    vocabulary.addSymbol(symbol)
        
        return vocabulary
        
        
        
        
        
