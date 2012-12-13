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

    def __init__(self):
        super(DiscovererClustering, self).__init__("discoverer")
        self.log = logging.getLogger(__name__)
        self.minASCIIthreshold = 2
        self.ASCIIDelimitors = string.punctuation + ''.join(['\n', '\r', '\t', ' '])
        self.ASCIIDelimitorsPattern = re.compile("[" + self.ASCIIDelimitors + "]")

    def execute(self, layers):
        """Execute the clustering"""
        self.log.info("Execute DISCOVERER Clustering...")
        # Retrieve all the messages
        messages = []
        for layer in layers:
            messages.extend(layer.getMessages())

        self.log.info("Start the Tokenization process")
        self.log.info("Number of messages : {0}".format(len(messages)))

        # split messages in binary and ascii tokens
        # tokens = dict<message, [token,...]>
        # token = (isAscii, [byte1, byte2, ....])
        tokens = dict()
        typeIdentifier = TypeIdentifier()
        for message in messages:
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
                        message_tokens.append((False, lastBinBytes))
                        lastBinBytes = []

                    lastAsciiBytes.append(byte)
                else:
                    if len(lastAsciiBytes) >= self.minASCIIthreshold:
                        ascii_tokens = self.splitASCIIUsingDelimitors(lastAsciiBytes)
                        message_tokens.extend(ascii_tokens)
                        lastAsciiBytes = []
                    elif len(lastAsciiBytes) > 0:
                        lastBinBytes.extend(lastAsciiBytes)
                        lastAsciiBytes = []

                    lastBinBytes.append(byte)
            if len(lastBinBytes) > 0:
                message_tokens.append((False, lastBinBytes))
                lastBinBytes = []
            if len(lastAsciiBytes) >= self.minASCIIthreshold:

                ascii_tokens = self.splitASCIIUsingDelimitors(lastAsciiBytes)
                message_tokens.extend(ascii_tokens)

            tokens[message] = message_tokens

            self.log.debug("Tokenization of message {0} in {1} tokens".format(message.getID(), len(tokens[message])))

        return layers

    def splitASCIIUsingDelimitors(self, aBytes):
        """Split a set of ASCII bytes in valid ASCII tokens using
        a set of common delimitors"""
        results = []
        for subToken in self.ASCIIDelimitorsPattern.split(''.join(aBytes)):
            if len(subToken) > 0:
                results.append((True, subToken))
        return results

    def getConfigurationErrorMessage(self):
        return None

    def getConfigurationController(self):
        """Create the controller which allows the configuration of the algorithm"""
        controller = DiscovererClusteringConfigurationController(self)
        return controller
