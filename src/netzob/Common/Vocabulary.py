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

#+---------------------------------------------------------------------------+ 
#| Standard library imports
#+---------------------------------------------------------------------------+
import logging
import time
from lxml.etree import ElementTree
from lxml import etree

#+---------------------------------------------------------------------------+
#| Local Imports
#+---------------------------------------------------------------------------+
from netzob.Common.Symbol import Symbol
from netzob.Inference.Vocabulary.Clusterer import Clusterer
from netzob.Common.ProjectConfiguration import ProjectConfiguration
from netzob.Common.Field import Field


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

    def getSymbolWhichContainsMessage(self, message):
        for symbol in self.symbols :
            for msg in symbol.getMessages() :
                if msg.getID() == message.getID() :
                    return symbol
        return None

    
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
        
    def getVariables(self):
        variables = []
        for symbol in self.symbols :
            for variable in symbol.getVariables() :
                if not variable in variables :
                    variables.append(variable)
        return variables
        
    #+---------------------------------------------- 
    #| alignWithNeedlemanWunsh:
    #|  Align each messages of each symbol with the
    #|  Needleman Wunsh algorithm
    #+----------------------------------------------
    def alignWithNeedlemanWunsh(self, configuration, callback):
        tmpSymbols = []
        t1 = time.time()

        # We try to clusterize each symbol
        for symbol in self.symbols :
            clusterer = Clusterer(configuration, [symbol], explodeSymbols=True)
            clusterer.mergeSymbols()
            tmpSymbols.extend(clusterer.getSymbols())
                
        # Now that all the symbols are reorganized separately
        # we should consider merging them
        logging.info("Merging the symbols extracted from the different files")
        clusterer = Clusterer(configuration, tmpSymbols, explodeSymbols=False)
        clusterer.mergeSymbols()
        
        # Now we execute the second part of NETZOB Magical Algorithms :)
        # clean the single symbols  
        mergeOrphanReduction = configuration.getVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_ORPHAN_REDUCTION)          
        if mergeOrphanReduction :
            logging.info("Merging the orphan symbols") 
            clusterer.mergeOrphanSymbols()

        logging.info("Time of parsing : " + str(time.time() - t1))
        
        self.symbols = clusterer.getSymbols()
        callback()

    #+---------------------------------------------- 
    #| alignWithDelimiter:
    #|  Align each message of each symbol with a specific delimiter
    #+----------------------------------------------
    def alignWithDelimiter(self, configuration, encodingType, delimiter):
        for symbol in self.symbols :
            symbol.alignWithDelimiter(configuration, encodingType, delimiter)
       
    def save(self, root, namespace):
        xmlVocabulary = etree.SubElement(root, "{" + namespace + "}vocabulary")
        xmlSymbols = etree.SubElement(xmlVocabulary, "{" + namespace + "}symbols")
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

    #+---------------------------------------------- 
    #| findSizeField:
    #|  try to find the size field of each symbols
    #+----------------------------------------------    
    def findSizeFields(self, store):
        for symbol in self.getSymbols():
            symbol.findSizeFields(store)
        
        
        
