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
import _libNeedleman
from netzob.Common.Symbol import Symbol
import uuid
import random
from netzob.Inference.Vocabulary.Alignment.NeedlemanAndWunsch import NeedlemanAndWunsch


#+---------------------------------------------------------------------------+
#| UPGMA:
#|     Supports the use of UPGMA clustering
#+---------------------------------------------------------------------------+
class UPGMA(object):

    def __init__(self, project, symbols, explodeSymbols, nbIteration, minEquivalence, doInternalSlick, defaultFormat, unitSize, cb_status=None, scores={}):
        self.project = project
        self.nbIteration = nbIteration
        self.minEquivalence = minEquivalence
        self.doInternalSlick = doInternalSlick
        self.cb_status = cb_status
        self.defaultFormat = defaultFormat
        self.unitSize = unitSize
        self.log = logging.getLogger('netzob.Inference.Vocabulary.UPGMA.py')
        self.scores = scores
        self.path = []
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
        if self.cb_status == None:
            print "[UPGMA status] " + str(donePercent) + "% " + currentMessage
        else:
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

        # Find equel messages. Useful for redundant protocols before doing heavy computations with Needleman (complexity=O(N²) where N is #Symbols)
        ll = len(self.symbols) - 1
        i_equ = 0
        while(ll > 0):
            currentMess = self.symbols[i_equ].getMessages()[0].getReducedStringData()
            for j in range(ll):
                if(currentMess == self.symbols[i_equ + j + 1].getMessages()[0].getReducedStringData()):
                    self.mergeEffectiveRowCol(i_equ, i_equ + j + 1)
                    self.log.debug("Merge the equal column/line {0} with the column/line {1}".format(str(i_equ), str(j + 1)))
                    i_equ -= 1
                    break
            ll -= 1
            i_equ += 1

        # Process the UPGMA on symbols
        self.processUPGMA()

        # Retrieve the alignment of each symbol and the build the associated regular expression
        self.cb_executionStatus(50.0, "Executing last alignment...")
        alignment = NeedlemanAndWunsch(self.unitSize, self.cb_status)
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
    def processUPGMA(self):
        self.log.debug("Computing the associated matrix")

        # Serialize the symbols
        (serialSymbols, formatSymbols) = TypeConvertor.serializeSymbols(self.symbols, self.unitSize, self.scores)
        self.log.debug("Clustering input format " + formatSymbols)

        # Execute the Clustering part in C
        debug = False
        logging.debug("Execute the clustering part in C ...")
        (i_max, j_max, maxScore, scores) = _libNeedleman.getHighestEquivalentGroup(self.doInternalSlick, len(self.symbols), formatSymbols, serialSymbols, self.cb_executionStatus, debug)
        listScores = TypeConvertor.deserializeScores(self.symbols, scores)

        # Retrieve the scores for each association of symbols
        self.scores = {}
        for (iuid, juid, score) in listScores:
            if iuid not in self.scores.keys():
                self.scores[iuid] = {}
            if juid not in self.scores.keys():
                self.scores[juid] = {}
            self.scores[iuid][juid] = score
            if iuid not in self.scores[juid].keys():
                self.scores[juid][iuid] = score

        # Reduce the UPGMA matrix (merge symbols by similarity)
        self.computePhylogenicTree()
        return (i_max, j_max, maxScore)

    #+----------------------------------------------
    #| computePhylogenicTree:
    #|     Compute directly the phylogenic tree
    #| max_i : uid of i_maximum
    #| max_j : uid of j_maximum
    #| maxScore : the highest global score
    #+----------------------------------------------
    def computePhylogenicTree(self):
        maxScore = 0
        if len(self.scores) > 1:
            max_i = max(self.scores, key=lambda x: self.scores[x][max(self.scores[x], key=lambda y: self.scores[x][y])])
            max_j = max(self.scores[max_i], key=lambda y: self.scores[max_i][y])
            maxScore = self.scores[max_i][max_j]
        while len(self.scores) > 1 and maxScore >= self.minEquivalence:
#            self.computePathTree()
#            juid_maximum = self.path.pop()
#            iuid_maximum = self.path.pop()
#            (i_maximum, j_maximum) = (symbols_uid.index(iuid_maximum),symbols_uid.index(juid_maximum))
#            self.log.debug("Dic {0}: {1}".format(str(iuid_maximum),str(self.scores[iuid_maximum])))
#            self.log.debug("Dic {0}: {1}".format(str(juid_maximum),str(self.scores[juid_maximum])))
#            self.log.debug("Mess {0}".format(self.symbols[i_maximum].getMessages()[0].getData()))
#            self.log.debug("Mess {0}".format(self.symbols[j_maximum].getMessages()[0].getData()))
##            self.log.debug("Score avant: {0}".format(str(self.scores)))
            symbols_uid = [s.getID() for s in self.symbols]  # List of the UID in of symbols
            (i_maximum, j_maximum) = (symbols_uid.index(max_i), symbols_uid.index(max_j))
            size_i = len(self.symbols[i_maximum].getMessages())
            size_j = len(self.symbols[j_maximum].getMessages())
            self.log.debug("Merge the column/line {0} with the column/line {1} ; score = {2}".format(str(i_maximum), str(j_maximum), str(maxScore)))
            newuid = self.mergeEffectiveRowCol(i_maximum, j_maximum)
            self.updateScore(max_i, max_j, newuid, size_i, size_j)
#            self.log.debug("Score après: {0}".format(str(self.scores)))
            if len(self.scores) > 1:
                max_i = max(self.scores, key=lambda x: self.scores[x][max(self.scores[x], key=lambda y: self.scores[x][y])])
                max_j = max(self.scores[max_i], key=lambda y: self.scores[max_i][y])
                maxScore = self.scores[max_i][max_j]

    def updateScore(self, iuid, juid, newuid, size_i, size_j):
        total_size = size_i + size_j
        del self.scores[iuid]
        del self.scores[juid]
        self.scores[newuid] = {}
        for k in self.scores.keys():
            if k != newuid:
                self.scores[k][newuid] = (size_i * self.scores[k][iuid] + size_j * self.scores[k][juid]) * 1.0 / total_size
                del self.scores[k][iuid]
                del self.scores[k][juid]
                self.scores[newuid][k] = self.scores[k][newuid]

    def computePathTree(self):
        if self.path == []:
            clusterIndex = int(random.random() * len(self.scores.keys()))
            self.path.append(self.scores.keys()[0])
        if len(self.path) > 1:  # Check if Cl-1,Cl-2 minimum pair
            lastId = self.path[len(self.path) - 1]
            if max(self.scores[lastId], key=lambda x: self.scores[lastId][x]) == self.path[len(self.path) - 2]:
                return
        while True:
            lastId = self.path[len(self.path) - 1]
            juid = max(self.scores[lastId], key=lambda x: self.scores[lastId][x])
            self.path.append(juid)
            if max(self.scores[juid], key=lambda x: self.scores[juid][x]) == lastId:
                break

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

        newSymbol = Symbol(str(uuid.uuid4()), symbol1.getName(), self.project, minEqu=self.minEquivalence)
        for message in messages:
            newSymbol.addMessage(message)

        # Append th new symbol to the "symbols" structure
        self.symbols.append(newSymbol)

        return newSymbol.getID()

    #+----------------------------------------------
    #| mergeOrphanSymbols:
    #|   try to merge orphan symbols by progressively
    #|   reducing the taken into account size of msgs
    #+----------------------------------------------
    def executeOrphanReduction(self):
        leftReductionFactor = 0
        rightReductionFactor = 0
        currentReductionIsLeft = False
        increment = 10

        while leftReductionFactor < 80 and rightReductionFactor < 80:

            # First we retrieve the current orphans
            orphans = []
            tmp_symbols = []
            # extract orphans
            for symbol in self.symbols:
                if len(symbol.getMessages()) == 1:
                    orphans.append(symbol)
            # create a tmp symbols array where symbols will be added once computed
            for symbol in self.symbols:
                if len(symbol.getMessages()) > 1:
                    tmp_symbols.append(symbol)

            if len(orphans) <= 1:
                self.log.info("Number of orphan symbols : {0}. The orphan merging op. is finished !".format(len(orphans)))
                break

            self.symbols = orphans
            if currentReductionIsLeft:
                leftReductionFactor = leftReductionFactor + increment
                # Reduce the size of the messages by 50% from the left
                for orphan in self.symbols:
                    orphan.getMessages()[0].setLeftReductionFactor(leftReductionFactor)
                    orphan.getMessages()[0].setRightReductionFactor(0)

                self.log.info("Start to merge orphans reduced by {0}% from the left".format(str(leftReductionFactor)))
                self.executeClustering()
                currentReductionIsLeft = False

            if not currentReductionIsLeft:
                rightReductionFactor = rightReductionFactor + increment
                # Reduce the size of the messages from the right
                for orphan in self.symbols:
                    orphan.getMessages()[0].setRightReductionFactor(rightReductionFactor)
                    orphan.getMessages()[0].setLeftReductionFactor(0)

                self.log.info("Start to merge orphans reduced by {0}% from the right".format(str(rightReductionFactor)))
                self.executeClustering()
                currentReductionIsLeft = True

            for orphan in self.symbols:
                for message in orphan.getMessages():
                    message.setLeftReductionFactor(0)
                    message.setRightReductionFactor(0)
                tmp_symbols.append(orphan)
            self.symbols = tmp_symbols

        self.cb_executionStatus(50.0, "Executing last alignment...")
        alignment = NeedlemanAndWunsch(self.unitSize, self.cb_status)
        # Compute the regex/alignment of each symbol
        for symbol in self.symbols:
            alignment.alignSymbol(symbol, self.doInternalSlick, self.defaultFormat)
        return self.symbols

    #+-----------------------------------------------------------------------+
    #| deserializeGroups
    #|     Useless (functionally) function created for testing purposes
    #| @param symbols a list of symbols
    #| @returns number Of Deserialized symbols
    #+-----------------------------------------------------------------------+
    def deserializeGroups(self, symbols):
        # First we serialize the messages
        (serialSymbols, format) = TypeConvertor.serializeSymbols(symbols, self.unitSize, self.scores)

        debug = False
        return _libNeedleman.deserializeGroups(len(symbols), format, serialSymbols, debug)

    #+-----------------------------------------------------------------------+
    #| getScores
    #|     get the dictionary of scores
    #+-----------------------------------------------------------------------+
    def getScores(self):
        return self.scores
