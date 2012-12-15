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
from netzob.Inference.Vocabulary.Clustering.AbstractClusteringAlgorithm import AbstractClusteringAlgorithm
from netzob.UI.Vocabulary.Controllers.Clustering.Discoverer.DiscovererClusteringConfigurationController import DiscovererClusteringConfigurationController
from netzob.Common.Type.TypeConvertor import TypeConvertor
from netzob.Common.Type.TypeIdentifier import TypeIdentifier

#+---------------------------------------------------------------------------+
#| Local Imports
#+---------------------------------------------------------------------------+


#+---------------------------------------------------------------------------+
#| UPGMAClustering:
#+---------------------------------------------------------------------------+
class DiscovererClustering(AbstractClusteringAlgorithm):
    """This represents the Discoverer algorithm as described in the paper 'Discoverer: Automatic Protocol Reverse Engineering from Network Traces'"""

    __algorithm_name__ = "Discoverer"
    __algorithm_description = "Cluster messages following their ASCII/Bin tokens as described in the paper 'Discoverer: Automatic Protocol Reverse Engineering from Network Traces'"

    @staticmethod
    def getDefaultMinASCII():
        return 3

    @staticmethod
    def getDefaultMinimumClusterSize():
        return 2

    @staticmethod
    def getDefaultMaximumDistinctValues():
        return 10


    class Token:
        ASCII = "ascii"
        BIN = "bin"

        def __init__(self, type, value, message):
            self.type = type
            self.value = value
            self.message = message

        def getType(self):
            return self.type

        def getValue(self):
            return self.value

        def getMessage(self):
            return self.message

    class Cluster:
        def __init__(self, signature, messages=[]):
            self.messages = messages
            self.signature = signature

        def addMessage(self, message):
            self.messages.append(message)

        def getSignature(self):
            return self.signature

        def getMessages(self):
            return self.messages



    def __init__(self):
        super(DiscovererClustering, self).__init__("discoverer")
        self.log = logging.getLogger(__name__)
        self.minASCIIthreshold = DiscovererClustering.getDefaultMinASCII()
        self.ASCIIDelimitors = string.punctuation + ''.join(['\n', '\r', '\t', ' '])
        self.ASCIIDelimitorsPattern = re.compile("[" + self.ASCIIDelimitors + "]")
        self.maximumDistinctValuesThreshold = DiscovererClustering.getDefaultMaximumDistinctValues()
        self.minimumClusterSizeThreshold = DiscovererClustering.getDefaultMinimumClusterSize()

    def execute(self, layers):
        """Execute the clustering"""
        self.log.info("Execute DISCOVERER Clustering...")
        # Retrieve all the messages
        messages = []
        for layer in layers:
            messages.extend(layer.getMessages())

        self.log.info("Start the Tokenization process")
        self.log.info("Number of messages : {0}".format(len(messages)))

        # First we retrieve all the tokens of messages
        tokens = dict() # tokens[Message] = [token1, token2, token3, ...]
        for message in messages:
            tokens[message] = self.getTokensForMessage(message)

        # Cluster messages following their tokens
        clusters = [] # clusters = [cluster1, cluster2, ...]

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
                    cluster.addMessage(message)
                    found = True
                    break
            if not found:
                clusters.append(DiscovererClustering.Cluster(signature, [message]))

        self.log.debug("{0} Clusters have been computed.".format(len(clusters)))

        # Execute the Recursive Clustering by Format Distinguishers
        self.log.debug("Execute the Recursive Clustering by Format Distinguishers.")

        for cluster in clusters:
            clusterSignature = cluster.getSignature().split(";")
            nbToken = len(clusterSignature)

            self.log.debug("Working on cluster : {0}".format(cluster.getSignature()))
            for message in cluster.getMessages():
                self.log.debug(" + {0}".format(message.getID()))
            self.log.debug("----------------------------------------------")
            self.log.debug("Searching for FDs in it.")
#
            for iToken in range(0, nbToken):
                self.log.debug("Working on token : {0}".format(iToken))
                self.log.debug("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
                # Retrieve the different values of the current token
                tokenValues = []
                self.log.debug("Normal Values :")
                abstractToken = None
                for message in cluster.getMessages():
                    if abstractToken is None:
                        abstractToken = DiscovererClustering.Token(tokens[message][iToken].getType(), None, None)
                    tokenValues.append(tokens[message][iToken].getValue())
                    self.log.debug("- {0}".format(repr(tokens[message][iToken].getValue())))

                # is iToken is an FD

                # Verification 1 : there should be less than the maximumDistinctValuesThreshold different value for this token
                self.log.debug("Unique Values :")
                uniqTokenValues = dict() # <value, nbInstance>
                for value in tokenValues:
                    if not value in uniqTokenValues.keys():
                        uniqTokenValues[value] = 1
                    else:
                        uniqTokenValues[value] = uniqTokenValues[value] + 1

                for uniqueValue in uniqTokenValues.keys():
                    self.log.debug("- {0} ({1})".format(repr(uniqueValue), uniqTokenValues[uniqueValue]))

                self.log.debug("Verification 1 : ")
                if len(uniqTokenValues.keys()) >= self.maximumDistinctValuesThreshold:
                    self.log.debug("Token {0} is not an FD (#1)".format(iToken))
                    continue
                else:
                    self.log.debug("Token {0} is conform to rule 1 (nbUniqueTokenValue = {1}<{2})".format(iToken, len(uniqTokenValues.keys()), self.maximumDistinctValuesThreshold))

                self.log.debug("Verification 2 : ")
                # Verification 2 : there should be at least a sub cluster with a number of message above the minimumClusterSizeThreshold
                enoughLargeSubClusterFound = False
                for tokenValue in uniqTokenValues.keys():
                    nbMessage = uniqTokenValues[tokenValue]
                    if nbMessage > self.minimumClusterSizeThreshold:
                        self.log.debug("We've found a sub-cluster with the requested number of different message")
                        enoughLargeSubClusterFound = True
                        break

                if not enoughLargeSubClusterFound:
                    self.log.debug("Token {0} is not conform to rule 2".format(iToken))
                    continue

#                # Verification 3 : Format comparison
#                # compare the format of each subclusters and merge commons subclusters
#                # We have the definition of subclusters through the definition of unique tokens
                subClusters = []
                for uniqueValue in uniqTokenValues.keys():
                    messagesInSubCluster = []

                    # retrieve all the message in this cluster with the uniqvalue
                    for message in cluster.getMessages():
                        if tokens[message][iToken].getValue() == uniqueValue:
                            messagesInSubCluster.append(message)
                    subClusters.append(DiscovererClustering.Cluster(uniqueValue, messagesInSubCluster))

                self.log.debug("Found the following subclusters :")
                for subCluster in subClusters:
                    self.log.debug("- SubCluster : ")
                    for message in subCluster.getMessages():
                        self.log.debug(" + {0}".format(message.getID()))

                self.log.debug("Try to merge common subclusters using their format")
                for subCluster in subClusters:
                    format = subCluster.getFormat()

                    for sc in subClusters:
                        if format.isEquivalent(sc.getFormat()):
                            self.log.debug("Equivalent Cluster found")



                    self.log.debug("Subcluster tokens : {0}".format(tokens[messages[0]]))




#
#                self.log.debug("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++=")
#                self.log.debug("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++=")
#                self.log.debug("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++=")
#                self.log.debug("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++=")
#                self.log.debug("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++=")
#
#
#
#
#
#
#
#
#



        return layers

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
#                    for b in lastBinBytes:
#                        message_tokens.append(DiscovererClustering.Token(DiscovererClustering.Token.BIN, b, message))
                    message_tokens.append(DiscovererClustering.Token(DiscovererClustering.Token.BIN, ''.join(lastBinBytes), message))
                    lastBinBytes = []

                lastAsciiBytes.append(byte)
            else:
                if len(lastAsciiBytes) >= self.minASCIIthreshold:
                    ascii_tokens = self.splitASCIIUsingDelimitors(lastAsciiBytes, message)
                    message_tokens.extend(ascii_tokens)
                    lastAsciiBytes = []
                elif len(lastAsciiBytes) > 0:
                    lastBinBytes.extend(lastAsciiBytes)
                    lastAsciiBytes = []

                lastBinBytes.append(byte)
        if len(lastBinBytes) > 0:
#            for b in lastBinBytes:
#                message_tokens.append(DiscovererClustering.Token(DiscovererClustering.Token.BIN, b, message))
            message_tokens.append(DiscovererClustering.Token(DiscovererClustering.Token.BIN, ''.join(lastBinBytes), message))
            lastBinBytes = []
        if len(lastAsciiBytes) >= self.minASCIIthreshold:
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
