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
#| Global Imports
#+---------------------------------------------------------------------------+
import logging

#+---------------------------------------------------------------------------+
#| Local Imports
#+---------------------------------------------------------------------------+
from netzob.Common.Type.TypeConvertor import TypeConvertor

#+---------------------------------------------------------------------------+
#| C Imports
#+---------------------------------------------------------------------------+
import libNeedleman
from netzob.Common.Symbol import Symbol
import uuid
from netzob.Inference.Vocabulary.Alignment.NeedlemanAndWunsch import NeedlemanAndWunsch

#+---------------------------------------------------------------------------+
#| UPGMA:
#|     Supports the use of UPGMA clustering
#+---------------------------------------------------------------------------+
class UPGMA(object):
    
    def __init__(self, project, symbols, explodeSymbols, nbIteration, minEquivalence, doInternalSlick, defaultFormat, cb_status=None):
        self.project = project;
        self.nbIteration = nbIteration
        self.minEquivalence = minEquivalence
        self.doInternalSlick = doInternalSlick
        self.cb_status = cb_status
        self.defaultFormat = defaultFormat
        
        self.log = logging.getLogger('netzob.Inference.Vocabulary.UPGMA.py')
        
        if explodeSymbols == False:
            self.symbols = symbols
            
        else:
            # Create a symbol for each message
            self.symbols = []
            i_symbol = 1
            for symbol in symbols:
                for m in symbol.getMessages():
                    tmpSymbol = Symbol(str(uuid.uuid4()), "Symbol " + str(i_symbol), project)
                    tmpSymbol.addMessage(m)
                    self.symbols.append(tmpSymbol)
                    i_symbol += 1
                    
        self.log.debug("A number of {0} already aligned symbols will be clustered.".format(str(len(symbols))))
        
        
    #+-----------------------------------------------------------------------+
    #| cb_executionStatus
    #|     Callback function called by the C extension to provide info on status
    #| @param donePercent a float between 0 and 100 included
    #| @param currentMessage a str which represents the current alignment status
    #+-----------------------------------------------------------------------+
    def cb_executionStatus(self, donePercent, currentMessage):
        if self.cb_status == None :
            print "[UPGMA status] " + str(donePercent) + "% " + currentMessage
        else :
            self.cb_status(donePercent, currentMessage)
    
    #+-----------------------------------------------------------------------+
    #| executeClustering
    #|     execute the clustering operation
    #| @param symbols the list of symbol to consider in the clustering
    #| @nbIteration the number of iteration maximum
    #| @minEquivalence the minimum requirement to consider two symbol as equivalent
    #| @return the new list of symbols
    #+-----------------------------------------------------------------------+
    def executeClustering(self):    
        self.log.debug("Re-Organize the symbols (nbIteration={0}, min_equivalence={1})".format(self.nbIteration, self.minEquivalence))
        for iteration in range(0, self.nbIteration):
            self.cb_executionStatus(50.0, "Iteration {0}/{1} started...".format(str(iteration), str(self.nbIteration)))
            # Create the score matrix for each symbol
            (i_maximum, j_maximum, maximum) = self.retrieveEffectiveMaxIJ()

            self.log.debug("Searching for the maximum of equivalence.")
            if (maximum >= self.minEquivalence):
                self.log.debug("Merge the column/line {0} with the column/line {1} ; score = {2}".format(str(i_maximum), str(j_maximum), str(maximum)))
                self.mergeEffectiveRowCol(i_maximum, j_maximum)
            else:
                self.log.debug("Stopping the clustering operation since the maximum found is {0} (<{1})".format(str(maximum), str(self.minEquivalence)))
                break

        self.cb_executionStatus(50.0, "Executing last alignment...")
        alignment = NeedlemanAndWunsch(self.cb_status)
        # Compute the regex/alignment of each symbol
        for symbol in self.symbols:
            alignment.alignSymbol(symbol, self.doInternalSlick, self.defaultFormat)
            
            
        return self.symbols
            
    #+----------------------------------------------
    #| retrieveMaxIJ:
    #|   given a list of symbols, it computes the
    #|   the possible two symbols which can be merged
    #| @return (i,j,max) (i,j) path in the matrix of
    #|                   the symbols to merge
    #|                    max score of the two symbols
    #+----------------------------------------------
    def retrieveEffectiveMaxIJ(self):
        self.log.debug("Computing the associated matrix")
        
        # Serialize the symbols
        (serialSymbols, formatSymbols) = TypeConvertor.serializeSymbols(self.symbols)
        
        # Execute the Clustering part in C :) (thx fgy)
        debug = False
        (i_max, j_max, maxScore) = libNeedleman.getHighestEquivalentGroup(self.doInternalSlick, len(self.symbols), formatSymbols, serialSymbols, self.cb_executionStatus, debug)
        return (i_max, j_max, maxScore)
    
    
    #+----------------------------------------------
    #| mergeRowCol:
    #|   Merge the symbols i and j in the "symbols" structure
    #+----------------------------------------------
    def mergeEffectiveRowCol(self, i_maximum, j_maximum):
        # Extract symbols i and j
        if i_maximum > j_maximum:
            symbol1 = self.symbols.pop(i_maximum)
            symbol2 = self.symbols.pop(j_maximum)
        else:
            symbol1 = self.symbols.pop(j_maximum)
            symbol2 = self.symbols.pop(i_maximum)

        # Merge the symbols i and j
        messages = []
        messages.extend(symbol1.getMessages())
        messages.extend(symbol2.getMessages())

        newSymbol = Symbol(str(uuid.uuid4()), "Symbol", self.project)
        for message in messages:
            newSymbol.addMessage(message)

        # Append th new symbol to the "symbols" structure
        self.symbols.append(newSymbol)  
        
        
    #+-----------------------------------------------------------------------+
    #| deserializeGroups
    #|     Useless (functionally) function created for testing purposes
    #| @param symbols a list of symbols
    #| @returns number Of Deserialized symbols
    #+-----------------------------------------------------------------------+
    def deserializeGroups(self, symbols): 
        # First we serialize the messages
        (serialSymbols, format) = TypeConvertor.serializeSymbols(symbols)
        
        debug = True
        return libNeedleman.deserializeGroups(len(symbols), format, serialSymbols, debug)
      
