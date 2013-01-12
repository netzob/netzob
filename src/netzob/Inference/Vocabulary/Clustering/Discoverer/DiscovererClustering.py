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
from locale import gettext as _
import logging
import re
import string
import uuid
from netzob.Inference.Vocabulary.Clustering.AbstractClusteringAlgorithm import AbstractClusteringAlgorithm
from netzob.UI.Vocabulary.Controllers.Clustering.Discoverer.DiscovererClusteringConfigurationController import DiscovererClusteringConfigurationController
from netzob.Common.Type.TypeConvertor import TypeConvertor
from netzob.Common.Type.TypeIdentifier import TypeIdentifier
from netzob.Common.Symbol import Symbol

#+---------------------------------------------------------------------------+
#| Local Imports
#+---------------------------------------------------------------------------+


#+---------------------------------------------------------------------------+
#| UPGMAClustering:
#+---------------------------------------------------------------------------+
class DiscovererClustering(AbstractClusteringAlgorithm):
    """This represents the Discoverer algorithm as described in the paper 'Discoverer: Automatic Protocol Reverse Engineering from Network Traces'"""

    MIN_LENGTH_TEXT_SEG = "min_length_text_size"
    MAX_DISTINCT_FD = "max_distinct_fd"
    MIN_CLUSTER_SIZE = "min_cluster_size"
    MAX_MESSAGE_PREFIX = "max_message_prefix"
    ALIGNMENT_MATCH_SCORE = "alignment_match_score"
    ALIGNMENT_MISMATCH_SCORE = "alignment_mismatch_score"
    ALIGNMENT_GAP_SCORE = "alignment_gap_score"

    __algorithm_name__ = "Discoverer"
    __algorithm_description = "Cluster messages following their ASCII/Bin tokens as described in the paper 'Discoverer: Automatic Protocol Reverse Engineering from Network Traces'"

    @staticmethod
    def getDefaultMaximumDistinctValuesFD():
        return 10

    @staticmethod
    def getDefaultMaximumMessagePrefix():
        return 2048

    @staticmethod
    def getDefaultMinimumLengthTextSegments():
        return 3

    @staticmethod
    def getDefaultMinimumClusterSize():
        return 2

    @staticmethod
    def getDefaultAlignmentMatchScore():
        return 1

    @staticmethod
    def getDefaultAlignmentMismatchScore():
        return 0

    @staticmethod
    def getDefaultAlignmentGapScore():
        return -2

    class Token(object):
        ASCII = "ascii"
        BIN = "bin"

        def __init__(self, type, value, message):
            self.log = logging.getLogger(__name__)
            self.type = type
            self.value = value
            self.message = message

        def getType(self):
            return self.type

        def getValue(self):
            return self.value

        def getMessage(self):
            return self.message

    class Cluster(object):
        def __init__(self, signature):
            self.log = logging.getLogger(__name__)
            self.messages = []
            self.signature = signature
            self.tokens = dict()
            self.properties = dict()

        def addMessage(self, message, tokens):
            self.log.debug("Add message")
            self.messages.append(message)
            self.tokens[message] = tokens

        def getTokens(self):
            return self.tokens

        def getTokenValues(self, iToken):
            # Retrieve the different values of the current token
            tokenValues = []
            self.log.debug("Normal Values :")
            for message in self.getMessages():
                tokenValues.append(self.tokens[message][iToken].getValue())
                self.log.debug("- {0}".format(repr(self.tokens[message][iToken].getValue())))
            return tokenValues

        def getSubClustersByUniquValueInToken(self, iToken):
            subClusters = dict()
            for message in self.getMessages():
                valueToken = self.tokens[message][iToken]
                if valueToken in subClusters.keys():
                    subCluster = subClusters[valueToken]
                else:
                    subCluster = DiscovererClustering.Cluster(self.getSignature())
                    subClusters[valueToken] = subCluster
                subCluster.addMessage(message, self.tokens[message])
            result = []
            for value in subClusters.keys():
                result.append(subClusters[value])
            return result

        def getSignature(self):
            return self.signature

        def getMessages(self):
            return self.messages

        def merge(self, cluster):
            self.log.debug("Merge cluster {0} with cluster {1}".format(cluster.getSignature(), self.getSignature()))
            tokens = cluster.getTokens()
            for message in cluster.getMessages():
                self.addMessage(message, tokens[message])

        def compareFormat(self, cluster):
            """Execute a format comparison between current cluster and the provided one"""
            error = False
            nbToken = len(self.getSignature().split(';'))

            for iToken in range(0, nbToken):
                self.log.debug("Is token {0} matches ?".format(iToken))

                # Compare the semantic (if available)
                # Property Inference (constant and variable matching)
                # their domain should overlap
                values = self.getTokenValues(iToken)
                otherValues = cluster.getTokenValues(iToken)

                diff = set(values).intersection(set(otherValues))
                if len(diff) == 0:
                    self.log.debug("We didn't find an intersection value between the token values")
                    error = True
                    break
            if error:
                self.log.debug("The format comparison failed (on property inference step) on token {0}.".format(iToken))
                return False

            return True

        def getFormat(self):
            return self.properties

    def __init__(self):
        super(DiscovererClustering, self).__init__("discoverer")
        self.log = logging.getLogger(__name__)
        self.minimumLengthTextSegments = DiscovererClustering.getDefaultMinimumLengthTextSegments()
        self.ASCIIDelimitors = string.punctuation + ''.join(['\n', '\r', '\t', ' '])
        self.ASCIIDelimitorsPattern = re.compile("[" + self.ASCIIDelimitors + "]")
        self.maximumDistinctValuesFD = DiscovererClustering.getDefaultMaximumDistinctValuesFD()
        self.minimumClusterSize = DiscovererClustering.getDefaultMinimumClusterSize()
        self.alignmentMatchScore = DiscovererClustering.getDefaultAlignmentMatchScore()
        self.alignmentMismatchScore = DiscovererClustering.getDefaultAlignmentMismatchScore()
        self.alignmentGapScore = DiscovererClustering.getDefaultAlignmentGapScore()
        self.maximumMessagePrefix = DiscovererClustering.getDefaultMaximumMessagePrefix()

    def getConfigurationParameters(self):
        parameters = dict()
        parameters[DiscovererClustering.MIN_LENGTH_TEXT_SEG] = self.minimumLengthTextSegments
        parameters[DiscovererClustering.MAX_DISTINCT_FD] = self.maximumDistinctValuesFD
        parameters[DiscovererClustering.MIN_CLUSTER_SIZE] = self.minimumClusterSize
        parameters[DiscovererClustering.MAX_MESSAGE_PREFIX] = self.maximumMessagePrefix
        parameters[DiscovererClustering.ALIGNMENT_MATCH_SCORE] = self.alignmentMatchScore
        parameters[DiscovererClustering.ALIGNMENT_MISMATCH_SCORE] = self.alignmentMismatchScore
        parameters[DiscovererClustering.ALIGNMENT_GAP_SCORE] = self.alignmentGapScore
        return parameters

    def setConfigurationParameters(self, parameters):
        self.minimumLengthTextSegments = int(parameters[DiscovererClustering.MIN_LENGTH_TEXT_SEG])
        self.maximumDistinctValuesFD = int(parameters[DiscovererClustering.MAX_DISTINCT_FD])
        self.minimumClusterSize = int(parameters[DiscovererClustering.MIN_CLUSTER_SIZE])
        self.alignmentMatchScore = int(parameters[DiscovererClustering.ALIGNMENT_MATCH_SCORE])
        self.alignmentMismatchScore = int(parameters[DiscovererClustering.ALIGNMENT_MISMATCH_SCORE])
        self.alignmentGapScore = int(parameters[DiscovererClustering.ALIGNMENT_GAP_SCORE])
        self.maximumMessagePrefix = int(parameters[DiscovererClustering.MAX_MESSAGE_PREFIX])

    def execute(self, symbols):
        """Execute the clustering"""
        self.log.info("Execute DISCOVERER Clustering...")
        if len(symbols) < 1:
            self.log.debug("No layers provided")
            return None

        # Retrieve the current project
        currentProject = symbols[0].getProject()

        # Retrieve all the messages
        messages = []
        for symbol in symbols:
            messages.extend(symbol.getMessages())

        self.log.info("Start the Tokenization process")
        self.log.info("Number of messages : {0}".format(len(messages)))

        # First we retrieve all the tokens of messages
        tokens = dict()  # tokens[Message] = [token1, token2, token3, ...]
        for message in messages:
            tokens[message] = self.getTokensForMessage(message)

        # Cluster messages following their tokens
        clusters = []  # clusters = [cluster1, cluster2, ...]

        for message in messages:
            # Compute the signature for each message
            # signature = [Direction, Type token1, Type token2, ...]
            signature = []
            for token in tokens[message]:
                signature.append(str(token.getType()))
            signature = ';'.join(signature)

            found = False
            for cluster in clusters:
                if cluster.getSignature() == signature:
                    cluster.addMessage(message, tokens[message])
                    found = True
                    break
            if not found:
                newCluster = DiscovererClustering.Cluster(signature)
                newCluster.addMessage(message, tokens[message])
                clusters.append(newCluster)

        self.log.debug("{0} Clusters have been computed.".format(len(clusters)))

        # Execute the Recursive Clustering by Format Distinguishers
        # Select a cluster to work on
        # Search for an FD in the current cluster
        # Computes subclusters based on FD
        # Subcribe subclusters in the list of cluster to work on
        self.log.debug("Execute the Recursive Clustering by Format Distinguishers.")

        clustersToWorkOn = dict()
        for cluster in clusters:
            clustersToWorkOn[cluster] = 0

        # Final results of the discover algorithm
        finalClusters = []

        while len(clustersToWorkOn.keys()) > 0:
            currentCluster = clustersToWorkOn.keys()[0]
            startIToken = clustersToWorkOn[currentCluster]
            del clustersToWorkOn[currentCluster]

            self.log.debug("Searching for an FD after token {0} on cluster {1}".format(startIToken, currentCluster.getSignature()))

            clusterSignature = currentCluster.getSignature().split(";")
            nbToken = len(clusterSignature)

            subClustersFound = False
            for iToken in range(startIToken, nbToken):
                self.log.debug("==> Working on token : {0}".format(iToken))

                # Retrieve the different values of the current token
                tokenValues = currentCluster.getTokenValues(iToken)

                # is iToken is an FD

                # Verification 1 : there should be less than the maximumDistinctValuesFD different value for this token
                self.log.debug("Unique Values :")
                uniqTokenValues = dict()  # <value, nbInstance>
                for value in tokenValues:
                    if not value in uniqTokenValues.keys():
                        uniqTokenValues[value] = 1
                    else:
                        uniqTokenValues[value] = uniqTokenValues[value] + 1

                for uniqueValue in uniqTokenValues.keys():
                    self.log.debug("- {0} ({1})".format(repr(uniqueValue), uniqTokenValues[uniqueValue]))

                self.log.debug("Verification 1 : ")
                if len(uniqTokenValues.keys()) >= self.maximumDistinctValuesFD:
                    self.log.debug("Token {0} is not an FD (#1)".format(iToken))
                    continue
                else:
                    self.log.debug("Token {0} is conform to rule 1 (nbUniqueTokenValue = {1}<{2})".format(iToken, len(uniqTokenValues.keys()), self.maximumDistinctValuesFD))

                self.log.debug("Verification 2 : ")
                # Verification 2 : there should be at least a sub cluster with a number of message above the minimumClusterSize
                enoughLargeSubClusterFound = False
                for tokenValue in uniqTokenValues.keys():
                    nbMessage = uniqTokenValues[tokenValue]
                    if nbMessage > self.minimumClusterSize:
                        self.log.debug("We've found a sub-cluster with the requested number of different message")
                        enoughLargeSubClusterFound = True
                        break

                if not enoughLargeSubClusterFound:
                    self.log.debug("Token {0} is not conform to rule 2".format(iToken))
                    continue

                # Verification 3 : Format comparison
                # compare the format of each subclusters and merge commons subclusters
                # We have the definition of subclusters through the definition of unique tokens
                subClusters = currentCluster.getSubClustersByUniquValueInToken(iToken)

                self.log.debug("Found the following subclusters :")
                iSubCluster = 0
                for subCluster in subClusters:
                    self.log.debug("- SubCluster {0} : ".format(iSubCluster))
                    for message in subCluster.getMessages():
                        self.log.debug(" + {0}".format(message.getID()))
                    iSubCluster += 1

                self.log.debug("Try to merge common subclusters using their format")
                clustersToRemove = []
                for subCluster in subClusters:
                    if subCluster not in clustersToRemove:
                        for sc in subClusters:
                            if sc != subCluster and sc not in clustersToRemove and subCluster.compareFormat(sc):
                                self.log.debug("Equivalent Cluster found we can merge them")
                                subCluster.merge(sc)
                                clustersToRemove.append(sc)

                tmpSubClusters = subClusters
                subClusters = []
                for subCluster in tmpSubClusters:
                    if subCluster not in clustersToRemove:
                        subClusters.append(subCluster)
                if len(subClusters) > 1:
                    self.log.debug("Consider {0} subclusters computed with token {1} as an FD".format(len(subClusters), iToken))
                    for subCluster in subClusters:
                        clustersToWorkOn[subCluster] = iToken + 1
                    subClustersFound = True
                else:
                    self.log.debug("The retrieved FD didn't allow to create subclusters.")
                    finalClusters.extend(subClusters)
                    break

            if not subClustersFound:
                self.log.debug("The current cluster didn't provide more subclusters")
                finalClusters.append(currentCluster)

        self.log.debug("Recursive Clustering by Format Distinguishers")
        for cluster in finalClusters:
            self.log.debug("Cluster {0}".format(cluster.getSignature()))
        # Lets play with the third step :
        # Merging with Type-Based Sequence Alignment
        resultSymbols = []
        # Clustering finished we create symbols for each cluster
        self.log.debug("Creates a symbol for each cluster")
        for cluster in finalClusters:
            newSymbol = Symbol(uuid.uuid4(), cluster.getSignature(), currentProject)
            newSymbol.addMessages(cluster.getMessages())
            resultSymbols.append(newSymbol)
        return resultSymbols

    def getTokensForMessage(self, message):
        message_tokens = []

        lastAsciiBytes = []
        lastBinBytes = []
        for byte in TypeConvertor.netzobRawToPythonRaw(message.getStringData()):
            isAscii = False
            try:
                byte.decode('ascii')
                isAscii = True
            except:
                isAscii = False

            if isAscii:
                if len(lastBinBytes) > 0:
                    for b in lastBinBytes:
                        message_tokens.append(DiscovererClustering.Token(DiscovererClustering.Token.BIN, b, message))
#                    message_tokens.append(DiscovererClustering.Token(DiscovererClustering.Token.BIN, ''.join(lastBinBytes), message))
                    lastBinBytes = []

                lastAsciiBytes.append(byte)
            else:
                if len(lastAsciiBytes) >= self.minimumLengthTextSegments:
                    ascii_tokens = self.splitASCIIUsingDelimitors(lastAsciiBytes, message)
                    message_tokens.extend(ascii_tokens)
                    lastAsciiBytes = []
                elif len(lastAsciiBytes) > 0:
                    lastBinBytes.extend(lastAsciiBytes)
                    lastAsciiBytes = []

                lastBinBytes.append(byte)
        if len(lastBinBytes) > 0:
            for b in lastBinBytes:
                message_tokens.append(DiscovererClustering.Token(DiscovererClustering.Token.BIN, b, message))
#            message_tokens.append(DiscovererClustering.Token(DiscovererClustering.Token.BIN, ''.join(lastBinBytes), message))
            lastBinBytes = []
        if len(lastAsciiBytes) >= self.minimumLengthTextSegments:
            ascii_tokens = self.splitASCIIUsingDelimitors(lastAsciiBytes, message)
            message_tokens.extend(ascii_tokens)
        return message_tokens

    def splitASCIIUsingDelimitors(self, aBytes, message):
        """Split a set of ASCII bytes in valid ASCII tokens using
        a set of common delimitors"""
        results = []
        for subToken in self.ASCIIDelimitorsPattern.split(''.join(aBytes)):
            if len(subToken) > 0:
                results.append(DiscovererClustering.Token(DiscovererClustering.Token.ASCII, "".join(subToken), message))
        return results

    def getConfigurationErrorMessage(self):
        return None

    def getConfigurationController(self):
        """Create the controller which allows the configuration of the algorithm"""
        controller = DiscovererClusteringConfigurationController(self)
        return controller

    def setMaximumMessagePrefix(self, value):
        self.maximumMessagePrefix = value

    def getMaximumMessagePrefix(self):
        return self.maximumMessagePrefix

    def setMinimumLengthTextSegments(self, value):
        self.minimumLengthTextSegments = value

    def getMinimumLengthTextSegments(self):
        return self.minimumLengthTextSegments

    def setMinimumClusterSize(self, value):
        self.minimumClusterSize = value

    def getMinimumClusterSize(self):
        return self.minimumClusterSize

    def setMaximumDistinctValuesFD(self, value):
        self.maximumDistinctValuesFD = value

    def getMaximumDistinctValuesFD(self):
        return self.maximumDistinctValuesFD

    def setAlignmentMatchScore(self, value):
        self.alignmentMatchScore = value

    def getAlignmentMatchScore(self):
        return self.alignmentMatchScore

    def setAlignmentMismatchScore(self, value):
        self.alignmentMismatchScore = value

    def getAlignmentMismatchScore(self):
        return self.alignmentMismatchScore

    def setAlignmentGapScore(self, value):
        self.alignmentGapScore = value

    def getAlignmentGapScore(self):
        return self.alignmentGapScore
