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
from gettext import gettext as _
import logging
import uuid
import random

#+---------------------------------------------------------------------------+
#| Local Imports
#+---------------------------------------------------------------------------+
from netzob.Common.Type.TypeConvertor import TypeConvertor
from netzob.Common.C_Extensions.WrapperArgsFactory import WrapperArgsFactory
from netzob.Common.Symbol import Symbol
from netzob.Inference.Vocabulary.Alignment.NeedlemanAndWunsch import NeedlemanAndWunsch
from netzob.Common.ProjectConfiguration import ProjectConfiguration

#+---------------------------------------------------------------------------+
#| C Imports
#+---------------------------------------------------------------------------+
from netzob import _libScoreComputation
from netzob import _libInterface


#+---------------------------------------------------------------------------+
#| UPGMA:
#|     Supports the use of UPGMA clustering
#+---------------------------------------------------------------------------+
class UPGMA(object):
    """This class provides the required methods to compute clustering
    between multiple symbols/messages using UPGMA algorithms (see U{http://en.wikipedia.org/wiki/UPGMA}).
    When processing, the matrix of scores is computed by the C extensions (L{_libScoreComputation} and L{_libInterface})
    and used to regroup messages and symbols into equivalent cluster."""

    def __init__(self, project, symbols, unitSize, cb_status=None, scores={}):
        self.project = project
        self.unitSize = unitSize
        self.cb_status = cb_status
        self.scores = scores

        # Then we retrieve all the parameters of the CLUSTERING / ALIGNMENT
        self.defaultFormat = self.project.getConfiguration().getVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_GLOBAL_FORMAT)
        self.nbIteration = self.project.getConfiguration().getVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_NB_ITERATION)
        self.minEquivalence = self.project.getConfiguration().getVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_EQUIVALENCE_THRESHOLD)
        self.doInternalSlick = self.project.getConfiguration().getVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_DO_INTERNAL_SLICK)

        self.log = logging.getLogger('netzob.Inference.Vocabulary.UPGMA.py')
        self.path = []
        self.flagStop = False
        self.currentAlignment = None

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

    def cb_executionStatus(self, stage, donePercent, currentMessage):
        """Callback function called by the C extension to provide info on status
        @param donePercent: a float between 0 and 100 included
        @param currentMessage: a str which represents the current alignment status"""
        if self.cb_status is None:
            self.log.info("[UPGMA status]" + str(donePercent) + "% " + currentMessage)
        else:
            self.cb_status(stage, donePercent, currentMessage)

    def executeClustering(self):
        """Execute the clustering operation
        @return the new list of symbols"""
        self.log.debug("Re-Organize the symbols (nbIteration={0}, min_equivalence={1})".format(self.nbIteration, self.minEquivalence))
        # Process the UPGMA on symbols

        if self.isFinish():
            return None

        self.cb_executionStatus(0, 0, "Clustering into symbols...")
        self.processUPGMA()
        self.cb_executionStatus(1, 100, None)
        # Retrieve the alignment of each symbol and the build the associated regular expression
        self.cb_executionStatus(2, 0, "Compute the definition for each cluster...")

        if self.isFinish():
            return None

        self.currentAlignment = NeedlemanAndWunsch(self.unitSize, self.project, False, self.cb_status)
        self.currentAlignment.absoluteStage = 2
        self.currentAlignment.statusRatio = len(self.symbols)
        self.currentAlignment.statusRatioOffset = 0

        for symbol in self.symbols:

            if self.isFinish():
                return None

            self.currentAlignment.alignField(symbol.getField())
            self.currentAlignment.statusRatioOffset = self.currentAlignment.statusRatioOffset + 1

        return self.symbols

    def processUPGMA(self):
        """Computes the matrix of equivalences (in C) and reduce it
        iteratively."""
        self.log.debug("Computing the associated matrix")

        # Execute the Clustering part in C
        debug = False
        wrapper = WrapperArgsFactory("_libScoreComputation.getHighestEquivalentGroup")
        wrapper.typeList[wrapper.function](self.symbols)
        (i_max, j_max, maxScore, listScores) = _libScoreComputation.getHighestEquivalentGroup(self.doInternalSlick, self.cb_executionStatus, self.isFinish, debug, wrapper)

        # Retrieve the scores for each association of symbols
        self.scores = {}
        for (iuid, juid, score) in listScores:

            if self.isFinish():
                return (None, None, None)

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

    def computePhylogenicTree(self):
        """Compute the phylogenic tree
        @var max_i: uid of i_maximum
        @var max_j: uid of j_maximum
        @var maxScore: the highest global score"""
        maxScore = 0
        status = 0
        step = (float(100) - float(self.minEquivalence)) / float(100)

        if len(self.scores) > 1:
            max_i = max(self.scores, key=lambda x: self.scores[x][max(self.scores[x], key=lambda y: self.scores[x][y])])
            max_j = max(self.scores[max_i], key=lambda y: self.scores[max_i][y])
            maxScore = self.scores[max_i][max_j]
        while len(self.scores) > 1 and maxScore >= self.minEquivalence:

            if self.isFinish():
                return

            symbols_uid = [s.getID() for s in self.symbols]  # List of the UID in of symbols
            (i_maximum, j_maximum) = (symbols_uid.index(max_i), symbols_uid.index(max_j))
            size_i = len(self.symbols[i_maximum].getMessages())
            size_j = len(self.symbols[j_maximum].getMessages())

            infoMessage = "Clustering {0} with {1} (score = {2})".format(str(i_maximum), str(j_maximum), str(maxScore))
            status = (float(100) - float(maxScore)) / float(step)
            self.cb_executionStatus(1, status, infoMessage)

            newuid = self.mergeEffectiveRowCol(i_maximum, j_maximum)
            self.updateScore(max_i, max_j, newuid, size_i, size_j)
#            self.log.debug("Score après: {0}".format(str(self.scores)))
            if len(self.scores) > 1:
                max_i = max(self.scores, key=lambda x: self.scores[x][max(self.scores[x], key=lambda y: self.scores[x][y])])
                max_j = max(self.scores[max_i], key=lambda y: self.scores[max_i][y])
                maxScore = self.scores[max_i][max_j]

    def updateScore(self, iuid, juid, newuid, size_i, size_j):
        """Update the score of two merged clusters.
        @param iuid: id of the first cluster merged
        @param juid: id of the second cluster merged
        @param newuid: new id of the merged cluster
        @param size_i: size of the first cluster
        @param size_j: size of the second cluster"""
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
        """TODO ?"""
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

    def mergeEffectiveRowCol(self, i_maximum, j_maximum):
        """Merge the symbols i and j in the "symbols" structure
        @param i_maximum: id of the first symbol to merge
        @param j_maximum: id of the second symbol to merge
        @return the newly created symbol result of the merged process"""
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

        newSymbol = Symbol(str(uuid.uuid4()), symbol1.getName(), self.project)
        newSymbol.setMinEqu(self.minEquivalence)
        for message in messages:
            newSymbol.addMessage(message)

        # Append th new symbol to the "symbols" structure
        self.symbols.append(newSymbol)

        return newSymbol.getID()

    def executeOrphanReduction(self):
        """Execute the orphan reduction process by merging symbols
        which are progressively reduced in size."""
        leftReductionFactor = 0
        rightReductionFactor = 0
        currentReductionIsLeft = False
        increment = 10

        while leftReductionFactor < 80 and rightReductionFactor < 80:

            # First we retrieve the current orphans
            orphans = []
            tmp_symbols = []
            # extract orphans
            for i, symbol in zip(range(len(self.symbols)), self.symbols):
                if len(symbol.getMessages()) == 1:
                    orphans.append(symbol)

            # create a tmp symbols array where symbols will be added once computed
            for symbol in self.symbols:
                if len(symbol.getMessages()) > 1:
                    tmp_symbols.append(symbol)

            if len(orphans) <= 1:
                self.log.info("Number of orphan symbols: {0}. The orphan merging op. is finished!".format(len(orphans)))
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

        self.cb_executionStatus(3, 50.0, "Executing last alignment...")
        alignment = NeedlemanAndWunsch(self.unitSize, self.project, False, self.cb_status)
        # Compute the regex/alignment of each symbol
        for symbol in self.symbols:
            alignment.alignField(symbol.getField())
        return self.symbols

    def deserializeGroups(self, symbols):
        """Useless (functionally) function created for testing purposes
        @param symbols a list of symbols
        @returns number Of deserialized symbols"""
        # First we serialize the messages
        (serialSymbols, format) = TypeConvertor.serializeSymbols(symbols, self.unitSize, self.scores)

        debug = False
        return _libInterface.deserializeGroups(len(symbols), format, serialSymbols, debug)

    def getScores(self):
        """@return: the dictionnary of scores"""
        return self.scores

    def stop(self):
        """Stop the current execution of any clustering operation"""
        self.flagStop = True
        if self.currentAlignment is not None:
            self.currentAlignment.stop()

    def isFinish(self):
        """Compute if we should finish the current clustering operation"""
        return self.flagStop
