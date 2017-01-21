# -*- coding: utf-8 -*-

# +---------------------------------------------------------------------------+
# |          01001110 01100101 01110100 01111010 01101111 01100010            |
# |                                                                           |
# |               Netzob : Inferring communication protocols                  |
# +---------------------------------------------------------------------------+
# | Copyright (C) 2011-2016 Georges Bossert and Frédéric Guihéry              |
# | This program is free software: you can redistribute it and/or modify      |
# | it under the terms of the GNU General Public License as published by      |
# | the Free Software Foundation, either version 3 of the License, or         |
# | (at your option) any later version.                                       |
# |                                                                           |
# | This program is distributed in the hope that it will be useful,           |
# | but WITHOUT ANY WARRANTY; without even the implied warranty of            |
# | MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the              |
# | GNU General Public License for more details.                              |
# |                                                                           |
# | You should have received a copy of the GNU General Public License         |
# | along with this program. If not, see <http://www.gnu.org/licenses/>.      |
# +---------------------------------------------------------------------------+
# | @url      : http://www.netzob.org                                         |
# | @contact  : contact@netzob.org                                            |
# | @sponsors : Amossys, http://www.amossys.fr                                |
# |             Supélec, http://www.rennes.supelec.fr/ren/rd/cidre/           |
# +---------------------------------------------------------------------------+

# +---------------------------------------------------------------------------+
# | File contributors :                                                       |
# |       - Georges Bossert <georges.bossert (a) supelec.fr>                  |
# |       - Frédéric Guihéry <frederic.guihery (a) amossys.fr>                |
# +---------------------------------------------------------------------------+

# +---------------------------------------------------------------------------+
# | Standard library imports                                                  |
# +---------------------------------------------------------------------------+
from collections import OrderedDict

# +---------------------------------------------------------------------------+
# | Related third party imports                                               |
# +---------------------------------------------------------------------------+

# +---------------------------------------------------------------------------+
# | Local application imports                                                 |
# +---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger
from netzob.Model.Vocabulary.Symbol import Symbol
from netzob.Model.Vocabulary.Messages.AbstractMessage import AbstractMessage
from netzob.Common.C_Extensions.WrapperArgsFactory import WrapperArgsFactory

# +---------------------------------------------------------------------------+
# | C Imports
# +---------------------------------------------------------------------------+
from netzob import _libScoreComputation


@NetzobLogger
class ClusterByAlignment(object):
    """This clustering process regroups messages in groups that maximes
    their alignement. It provides the required methods to compute clustering
    between multiple symbols/messages using UPGMA algorithms (see U{http://en.wikipedia.org/wiki/UPGMA}).
    When processing, the matrix of scores is computed by the C extensions (L{_libScoreComputation}
    and used to regroup messages and symbols into equivalent cluster.


    >>> from netzob.all import *
    >>> pseudos = ["zoby", "ditrich", "toto", "carlito"]
    >>> cities = ["Paris", "Munich", "Barcelone", "Vienne"]
    >>> ips = ["192.168.0.10", "10.120.121.212", "78.167.23.10"]
    >>> # Creation of the different types of message
    >>> msgsType1 = [ RawMessage("hello {0}, what's up in {1} ?".format(pseudo, city).encode('utf-8')) for pseudo in pseudos for city in cities]
    >>> msgsType2 = [ RawMessage("My ip address is {0}".format(ip).encode('utf-8')) for ip in ips]
    >>> msgsType3 = [ RawMessage("Your IP is {0}, name = {1} and city = {2}".format(ip, pseudo, city).encode('utf-8')) for ip in ips for pseudo in pseudos for city in cities]
    >>> messages = msgsType1 + msgsType2 + msgsType3
    >>> clustering = ClusterByAlignment()
    >>> symbols = clustering.cluster(messages)
    >>> len(symbols)
    3
    >>> print(symbols[0])
    Field               | Field | Field | Field | Field | Field | Field | Field | Field | Field
    ------------------- | ----- | ----- | ----- | ----- | ----- | ----- | ----- | ----- | -----
    'My ip address is ' | '78'  | '.1'  | '67'  | '.'   | '23'  | '.'   | ''    | '1'   | '0'  
    'My ip address is ' | '192' | '.1'  | '68'  | '.'   | '0'   | '.'   | ''    | '1'   | '0'  
    'My ip address is ' | '10'  | '.1'  | '20'  | '.'   | '121' | '.'   | '2'   | '1'   | '2'  
    ------------------- | ----- | ----- | ----- | ----- | ----- | ----- | ----- | ----- | -----

    >>> print(symbols[2])
    Field    | Field     | Field             | Field       | Field
    -------- | --------- | ----------------- | ----------- | -----
    'hello ' | 'carlito' | ", what's up in " | 'Munich'    | ' ?' 
    'hello ' | 'carlito' | ", what's up in " | 'Paris'     | ' ?' 
    'hello ' | 'ditrich' | ", what's up in " | 'Munich'    | ' ?' 
    'hello ' | 'ditrich' | ", what's up in " | 'Paris'     | ' ?' 
    'hello ' | 'carlito' | ", what's up in " | 'Vienne'    | ' ?' 
    'hello ' | 'ditrich' | ", what's up in " | 'Vienne'    | ' ?' 
    'hello ' | 'toto'    | ", what's up in " | 'Paris'     | ' ?' 
    'hello ' | 'zoby'    | ", what's up in " | 'Paris'     | ' ?' 
    'hello ' | 'toto'    | ", what's up in " | 'Munich'    | ' ?' 
    'hello ' | 'zoby'    | ", what's up in " | 'Munich'    | ' ?' 
    'hello ' | 'toto'    | ", what's up in " | 'Vienne'    | ' ?' 
    'hello ' | 'zoby'    | ", what's up in " | 'Vienne'    | ' ?' 
    'hello ' | 'carlito' | ", what's up in " | 'Barcelone' | ' ?' 
    'hello ' | 'ditrich' | ", what's up in " | 'Barcelone' | ' ?' 
    'hello ' | 'toto'    | ", what's up in " | 'Barcelone' | ' ?' 
    'hello ' | 'zoby'    | ", what's up in " | 'Barcelone' | ' ?' 
    -------- | --------- | ----------------- | ----------- | -----

    """

    def __init__(self, minEquivalence=50, internalSlick=True, recomputeMatrixThreshold=None):
        self.minEquivalence = minEquivalence
        self.internalSlick = internalSlick
        self.recomputeMatrixThreshold = recomputeMatrixThreshold

    @typeCheck(list)
    def cluster(self, messages):
        if messages is None:
            raise TypeError("Messages cannot be None")
        if len(messages) == 0:
            raise TypeError("There should be at least one message.")

        for m in messages:
            if not isinstance(m, AbstractMessage):
                raise TypeError("At least one message ({0}) is not an AbstractMessage.".format(str(m)))

        self._logger.debug("Identify similar messages following their alignment (min_equivalence={0})".format(self.minEquivalence))

        self._logger.debug("Initiating the clustering by alignment on {0} messages...".format(len(messages)))
        symbols = self._processUPGMA(messages, self.recomputeMatrixThreshold)
        self._logger.debug("Clustering completed, computing final alignment.")

        # Retrieve the alignment of each symbol and the build the associated regular expression
        for symbol in symbols:
            self._logger.debug("Align messages from symbol {0}".format(symbol.name))
            from netzob.Inference.Vocabulary.Format import Format
            Format.splitAligned(symbol, useSemantic=False)

        return symbols

    @typeCheck(list)
    def _processUPGMA(self, messages, recomputeMatrixThreshold=None):
        """Computes the matrix of equivalences (in C) and reduces it
        iteratively."""
        if messages is None:
            raise TypeError("Messages cannot be None")
        if len(messages) == 0:
            raise TypeError("There should be at least one message.")
        for m in messages:
            if not isinstance(m, AbstractMessage):
                raise TypeError("At least one message ({0}) is not an AbstractMessage.".format(str(m)))

        # We create one symbol for each message
        initialSymbols = [Symbol(messages=[message]) for message in messages]

        self._logger.debug("Computing the associated matrix")

        # Compute initial similarity matrix
        self.scores = self._computeSimilarityMatrix(initialSymbols)

        # Reduce the UPGMA matrix (merge symbols by similarity)
        return self._computePhylogenicTree(initialSymbols, recomputeMatrixThreshold)

    @typeCheck(list)
    def _computeSimilarityMatrix(self, symbols):
        if symbols is None:
            raise TypeError("Symbols cannot be None")
        for symbol in symbols:
            if not isinstance(symbol, Symbol):
                raise TypeError("At least one specified symbol is not a valid symbol")

        # Execute the Clustering part in C
        debug = False
        wrapper = WrapperArgsFactory("_libScoreComputation.computeSimilarityMatrix")
        wrapper.typeList[wrapper.function](symbols)
        self._logger.debug("wrapper = {0}".format(wrapper))

        (listScores) = _libScoreComputation.computeSimilarityMatrix(self.internalSlick, self._cb_executionStatus, self._isFinish, debug, wrapper)
        # Retrieve the scores for each association of symbols
        scores = OrderedDict()
        for (iuid, juid, score) in listScores:
            if iuid not in list(scores.keys()):
                scores[iuid] = OrderedDict()
            if juid not in list(scores.keys()):
                scores[juid] = OrderedDict()
            scores[iuid][juid] = score
            if iuid not in list(scores[juid].keys()):
                scores[juid][iuid] = score
        return scores

    def _computePhylogenicTree(self, symbols, recomputeMatrixThreshold):
        """Compute the phylogenic tree
        @var max_i: uid of i_maximum
        @var max_j: uid of j_maximum
        @var maxScore: the highest global score"""
        maxScore = 0
        status = 0
        step = (float(100) - float(self.minEquivalence)) / float(100)
        self.lastScore = None

        if len(self.scores) > 1:
            max_i = max(self.scores, key=lambda x: self.scores[x][max(self.scores[x], key=lambda y: self.scores[x][y])])
            max_j = max(self.scores[max_i], key=lambda y: self.scores[max_i][y])
            maxScore = self.scores[max_i][max_j]
        while len(self.scores) > 1 and maxScore >= self.minEquivalence:

            symbols_uid = [str(s.id) for s in symbols]  # List of the UID in of symbols
            (i_maximum, j_maximum) = (symbols_uid.index(max_i), symbols_uid.index(max_j))
            size_i = len(symbols[i_maximum].messages)
            size_j = len(symbols[j_maximum].messages)

            self._logger.debug("Clustering {0} with {1} (score = {2})".format(str(i_maximum), str(j_maximum), str(maxScore)))

            newuid = self._mergeEffectiveRowCol(symbols, i_maximum, j_maximum)
            self._updateScore(symbols, max_i, max_j, newuid, size_i, size_j, recomputeMatrixThreshold)
#            self.log.debug("Score après: {0}".format(str(self.scores)))
            if len(self.scores) > 1:
                max_i = max(self.scores, key=lambda x: self.scores[x][max(self.scores[x], key=lambda y: self.scores[x][y])])
                max_j = max(self.scores[max_i], key=lambda y: self.scores[max_i][y])
                maxScore = self.scores[max_i][max_j]
        return symbols

    def _mergeEffectiveRowCol(self, symbols, i_maximum, j_maximum):
        """Merge the symbols i and j in the "symbols" structure
        @param i_maximum: id of the first symbol to merge
        @param j_maximum: id of the second symbol to merge
        @return the newly created symbol result of the merged process"""
        # Extract symbols i and j
        if i_maximum > j_maximum:
            symbol1 = symbols.pop(i_maximum)
            symbol2 = symbols.pop(j_maximum)
        else:
            symbol1 = symbols.pop(j_maximum)
            symbol2 = symbols.pop(i_maximum)

        # Merge the symbols i and j
        messages = []
        messages.extend(symbol1.messages)
        messages.extend(symbol2.messages)

        newSymbol = Symbol(messages=messages)

        # Append th new symbol to the "symbols" structure
        symbols.append(newSymbol)

        return str(newSymbol.id)

    def _updateScore(self, symbols, iuid, juid, newuid, size_i, size_j, recomputeMatrixThreshold=None):
        """Update the score of two merged clusters.
        @param iuid: id of the first cluster merged
        @param juid: id of the second cluster merged
        @param newuid: new id of the merged cluster
        @param size_i: size of the first cluster
        @param size_j: size of the second cluster"""

        self._logger.debug("Update score (recompte matrix : {0})".format(recomputeMatrixThreshold))

        currentScore = self.scores[iuid][juid]

        # Delete row and col
        del self.scores[iuid]
        del self.scores[juid]
        # Create a new col
        self.scores[newuid] = OrderedDict()

        # Should we recompute
        if self.lastScore is None:
            self.lastScore = currentScore

        if recomputeMatrixThreshold is None or abs(currentScore - self.lastScore) <= recomputeMatrixThreshold:
            self._logger.debug("Ok no need in recomputing the matrix")

            total_size = size_i + size_j

            for k in list(self.scores.keys()):
                if k != newuid:
                    self.scores[k][newuid] = (size_i * self.scores[k][iuid] + size_j * self.scores[k][juid]) * 1.0 / total_size
                    del self.scores[k][iuid]
                    del self.scores[k][juid]
                    self.scores[newuid][k] = self.scores[k][newuid]
        else:
            self._logger.debug("Merge and recompute matrix similarity threshold")
            self.scores = self.computeSimilarityMatrix(symbols)

        self.lastScore = currentScore

    def _cb_executionStatus(self, stage, donePercent, currentMessage):
        """Callback function called by the C extension to provide info on status
        @param donePercent: a float between 0 and 100 included
        @param currentMessage: a str which represents the current alignment status"""
        self._logger.debug("[UPGMA status]" + str(donePercent) + "% " + str(currentMessage))

    def _isFinish(self):
        """Compute if we should finish the current clustering operation.
        :todo: always returns False, it should be exposed to the user.
        """
        return False

    @property
    def minEquivalence(self):
        """Minimum equivalence score under which two messages are note
        considered as similar.

        :rtype: :class:`float`

        """
        return self.__minEquivalence

    @minEquivalence.setter
    @typeCheck(int)
    def minEquivalence(self, minEquivalence):
        if minEquivalence is None:
            raise TypeError("Min Equivalence cannot be None")
        self.__minEquivalence = minEquivalence

    @property
    def internalSlick(self):
        """If active, the alignment is slicked during the merging process while
        if not active, only final alignment is slicked."""
        return self.__internalSlick

    @internalSlick.setter
    @typeCheck(bool)
    def internalSlick(self, internalSlick):
        if internalSlick is None:
            raise TypeError("internal slick cannot be none")
        self.__internalSlick = internalSlick

    @property
    def recomputeMatrixThreshold(self):
        return self.__recomputeMatrixThreshold

    @recomputeMatrixThreshold.setter
    def recomputeMatrixThreshold(self, recomputeMatrixThreshold):
        self.__recomputeMatrixThreshold = recomputeMatrixThreshold

