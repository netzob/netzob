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
#| Standard library imports                                                  |
#+---------------------------------------------------------------------------+
from gettext import gettext as _
from bitarray import bitarray
import datetime
import logging

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+
from lxml.etree import ElementTree
from lxml import etree

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.MMSTD.Dictionary.VariableProcessingToken.VariableReadingToken import \
    VariableReadingToken
from netzob.Common.MMSTD.Dictionary.VariableProcessingToken.VariableWritingToken import \
    VariableWritingToken
from netzob.Common.MMSTD.Symbols.impl.EmptySymbol import EmptySymbol
from netzob.Common.MMSTD.Symbols.impl.UnknownSymbol import UnknownSymbol
from netzob.Common.Type.TypeConvertor import TypeConvertor
from netzob.Common.MMSTD.Actors.AbstractChannel import AbstractChannel
from netzob.Common.MMSTD.Dictionary.Memory import Memory


class TimeoutException(Exception):
    pass


#+---------------------------------------------------------------------------+
#| AbstractionLayer:
#|     Definition of an abstractionLayer
#+---------------------------------------------------------------------------+
class AbstractionLayer():

    def __init__(self, communicationChannel, vocabulary, memory, cb_inputSymbol=None, cb_outputSymbol=None):
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Common.MMSTD.vocabulary.AbstractionLayer.py')
        self.communicationChannel = communicationChannel
        self.vocabulary = vocabulary
        self.memory = memory
        self.inputMessages = []
        self.outputMessages = []
        self.manipulatedSymbols = []
        self.outputSymbols = []
        self.inputSymbols = []
        self.connected = False
        self.cb_inputSymbol = cb_inputSymbol
        self.cb_outputSymbol = cb_outputSymbol

    def isConnected(self):
        return self.connected

    def setConnected(self):
        self.log.debug("Connected changes to TRUE")
        self.connected = True

    def setDisconnected(self):
        self.log.debug("Connected changes to FALSE")
        self.connected = False

    def openServer(self, vocabulary, outputState, isMaster):
        self.log.info("OpenServer " + str(self.communicationChannel))
        self.connected = False

        # if it's an instanciated network server we kill it
        # and create a new one !
        if self.communicationChannel.isAnInstanciated():
#            self.communicationChannel = self.communicationChannel.createNewServer()
            pass
        else:
            self.communicationChannel.openServer(vocabulary, outputState, isMaster, self.setConnected, self.setDisconnected, self.registerInputSymbol, self.registerOutputSymbol)

    def connect(self):
        self.log.debug("Connect ...")
        if self.connected:
            self.log.warn("Impossible to connect : already connected")
        else:
            # if its a server:
            if self.communicationChannel.isServer():
                self.log.info("Opening the server to outside connections")

            else:
            # if its a client:
                self.log.info("Connecting the client...")
                self.connected = self.communicationChannel.open()

    def disconnect(self):
        self.log.debug("Disconnecting the abstraction layer")
        self.communicationChannel.close()
        self.connected = False

    #+-----------------------------------------------------------------------+
    #| receiveSymbol
    #|     Manage the reception of a message and its transformation in a symbol
    #| @return a tupple containing the symbol and the associated received message
    #+-----------------------------------------------------------------------+
    def receiveSymbol(self):
        self.log.debug("Waiting for the reception of a message")
        return self.receiveSymbolWithTimeout(-1)

    def registerInputSymbol(self, receptionTime, message, symbol):
        self.manipulatedSymbols.append(symbol)
        self.inputSymbols.append(symbol)
        if (self.cb_inputSymbol is not None):
            self.cb_inputSymbol(receptionTime, message, symbol)

    def registerOutputSymbol(self, sendingTime, message, symbol):
        self.manipulatedSymbols.append(symbol)
        self.outputSymbols.append(symbol)
        if self.cb_outputSymbol is not None:
            self.cb_outputSymbol(sendingTime, message, symbol)

    def receiveSymbolWithTimeout(self, timeout):
        # First we read from the input the message
        receivedData = self.communicationChannel.read(timeout)

        nbMaxAttempts = 5

        if receivedData is None:
            self.log.warn("The communication channel seems to be closed !")
#            return (EmptySymbol(), None)
            return (None, None)

        if len(receivedData) > 0:
            now = datetime.datetime.now()
            receptionTime = now.strftime("%H:%M:%S")
            self.log.info("Received following message : " + TypeConvertor.bin2strhex(receivedData))

            # Now we abstract the message
            symbol = self.abstract(receivedData)

            # We store the received messages its time and its abstract representation
            self.inputMessages.append([receptionTime, TypeConvertor.bin2strhex(receivedData), symbol.getName()])
            self.registerInputSymbol(receptionTime, TypeConvertor.bin2strhex(receivedData), symbol)

            return (symbol, receivedData)
        else:
            if len(self.manipulatedSymbols) > nbMaxAttempts:
                if self.manipulatedSymbols[len(self.manipulatedSymbols) - 1].getType() == EmptySymbol.TYPE or self.manipulatedSymbols[len(self.manipulatedSymbols) - 1].getType() == UnknownSymbol.TYPE:
                    self.log.warn("Consider client has disconnected since no valid symbol received after " + str(nbMaxAttempts) + " attempts")
                    return (None, None)
            now = datetime.datetime.now()
            receptionTime = now.strftime("%H:%M:%S")
            symbol = EmptySymbol()
            self.registerInputSymbol(receptionTime, "", symbol)
            return (symbol, None)

    def writeSymbol(self, symbol):

        self.log.info("Sending symbol '" + str(symbol) + "' over the communication channel")
        # First we specialize the symbol in a message
        binMessage = self.specialize(symbol)
        if type(binMessage) == tuple:  # Means EmptySymbol or UnknownSymbol
            (binMessage, dummy) = binMessage
        strMessage = TypeConvertor.bin2strhex(binMessage)
        self.log.info("Write str message = '" + strMessage + "'")

        # now we send it
        now = datetime.datetime.now()
        sendingTime = now.strftime("%H:%M:%S")
        self.outputMessages.append([sendingTime, strMessage, symbol.getName()])
        self.registerOutputSymbol(sendingTime, strMessage, symbol)

        self.communicationChannel.write(binMessage)

    def abstract(self, message):
        """abstract:
                Searches in the vocabulary the symbol which abstract the received message.

                @type message: netzob.Common.Models.AbstractMessage
                @param message: the message that is being read/compare/learn.
                @rtype: netzob.Common.Symbol
                @return: the symbol which content matches the message.
        """
        self.log.debug("We abstract the received message : " + TypeConvertor.bin2strhex(message))
        # we search in the vocabulary an entry which match the message
        for symbol in self.vocabulary.getSymbols():
            self.log.debug("Try to abstract message through : {0}.".format(symbol.getName()))
            readingToken = VariableReadingToken(False, self.vocabulary, self.memory, TypeConvertor.strBitarray2Bitarray(message), 0)
            symbol.getRoot().read(readingToken)

            logging.debug("ReadingToken: isOk: {0}, index: {1}, len(value): {2}".format(str(readingToken.isOk()), str(readingToken.getIndex()), str(len(readingToken.getValue()))))
            # The message matches if the read is ok and the whole entry was read.
            if readingToken.isOk() and readingToken.getIndex() == len(readingToken.getValue()):
                self.log.debug("The message matches symbol {0}.".format(symbol.getName()))
                # It matches so we learn from it if it's possible
                return symbol
            else:
                self.log.debug("The message doesn't match symbol {0}.".format(symbol.getName()))
            # This is now managed in the variables modules.
            #===================================================================
            #    self.memory.createMemory()
            #    self.log.debug("We memorize the symbol " + str(symbol.getRoot()))
            #    readingToken = VariableReadingToken(False, self.vocabulary, self.memory, TypeConvertor.strBitarray2Bitarray(message), 0)
            #    symbol.getRoot().learn(readingToken)
            #    self.memory.persistMemory()
            #    return symbol
            # else:
            #    self.log.debug("Entry " + str(symbol.getID()) + " doesn't match")
            #    # we first restore a possibly learned value
            #    self.log.debug("Restore possibly learned value")
            #    processingToken = AbstractVariableProcessingToken(False, self.vocabulary, self.memory)
            #    symbol.getRoot().restore(processingToken)
            #===================================================================
        return UnknownSymbol()

    def specialize(self, symbol):
        self.log.info("Specializing the symbol {0}".format(symbol.getName()))

        #TODO: Replace all default values with clever values.
        writingToken = VariableWritingToken(False, self.vocabulary, self.memory, bitarray(''), ["random"])
        result = symbol.write(writingToken)
        return result

    def getMemory(self):
        return self.memory

    #+-----------------------------------------------------------------------+
    #| getGeneratedInputAndOutputsSymbols
    #|     Retrieves all the received and the sent symbols in their manipulation order
    #| @return an array contening all the symbols
    #+-----------------------------------------------------------------------+
    def getGeneratedInputAndOutputsSymbols(self):
        print "communication channel = " + str(self.communicationChannel)
        return self.manipulatedSymbols

    def getGeneratedInputSymbols(self):
        return self.inputSymbols

    def getGeneratedOutputSymbols(self):
        return self.outputSymbols

    def getProperties(self):
        """Compute and return the list of properties of the
        abstraction layer"""
        properties = []
        properties.extend(self.getCommunicationChannel().getProperties())

        return properties

    #+-----------------------------------------------------------------------+
    #| GETTERS AND SETTERS
    #+-----------------------------------------------------------------------+
    def getInputMessages(self):
        return self.inputMessages

    def getOutputMessages(self):
        return self.outputMessages

    def getVocabulary(self):
        return self.vocabulary

    def getCommunicationChannel(self):
        return self.communicationChannel

    def setInputSymbolReception_cb(self, cb):
        self.cb_inputSymbol = cb

    def setOutputSymbolSending_cb(self, cb):
        self.cb_outputSymbol = cb

    def save(self, root, namespace):
        """Save in the XML tree the abstraction Layer definition"""
        xmlLayer = etree.SubElement(root, "{" + namespace + "}abstractionLayer")

        # save the communication channel
        self.communicationChannel.save(xmlLayer, namespace)

    @staticmethod
    def loadFromXML(xmlRoot, namespace, version, vocabulary):
        if version == "0.1":
            communicationChannel = None
            memory = Memory()

            if xmlRoot.find("{" + namespace + "}communicationChannel") is not None:
                communicationChannel = AbstractChannel.loadFromXML(xmlRoot.find("{" + namespace + "}communicationChannel"), namespace, version, memory)

            if memory is None or communicationChannel is None:
                logging.warn("An error occurred and prevented loading the abstraction layer from its XML definiton")
                return None

            return AbstractionLayer(communicationChannel, vocabulary, memory)

        return None
