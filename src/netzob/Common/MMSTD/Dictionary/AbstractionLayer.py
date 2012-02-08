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
import datetime

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+


#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.MMSTD.Symbols.impl.EmptySymbol import EmptySymbol
from netzob.Common.Type.TypeConvertor import TypeConvertor


class TimeoutException(Exception):
    pass

#+---------------------------------------------------------------------------+
#| AbstractionLayer:
#|     Definition of an abstractionLayer
#+---------------------------------------------------------------------------+
class AbstractionLayer():

    def __init__(self, communicationChannel, vocabulary, memory):
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Common.MMSTD.vocabulary.AbstractionLayer.py')
        self.communicationChannel = communicationChannel
        self.vocabulary = vocabulary
        self.memory = memory
        self.inputMessages = []
        self.outputMessages = []
        self.manipulatedSymbols = []
        self.outputSymbols = []
        self.connected = False

    def isConnected(self):
        return self.connected

    def openServer(self, vocabulary, outputState, isMaster):
        self.log.info("OpenServer " + str(self.communicationChannel))
        self.connected = True

        # if it's an instanciated network server we kill it
        # and create a new one !
        if self.communicationChannel.isAnInstanciated():
#            self.communicationChannel = self.communicationChannel.createNewServer()
            pass
        else:
            self.communicationChannel.openServer(vocabulary, outputState, isMaster)

    def closeServer(self):
        self.log.debug("CloseServer ...")
        self.connected = False
        self.communicationChannel.close()

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
        self.log.warn("Disconnect ...")
        if self.connected:
            self.log.debug("Disconnecting ...")
            self.connected = not self.communicationChannel.close()
            self.log.debug("Connected = " + str(self.connected))
            # if its a server:
            if self.communicationChannel.isServer():
                self.log.debug("Close the server")
                self.closeServer()

            else:
            # if its a client:
                self.log.debug("Close the client...")
                try:
                    self.connected = self.communicationChannel.close()
                except:
                    self.log.warn("Error while trying to disconnect")

        else:
            self.log.debug("Impossible to disconnect : not connected")


    #+-----------------------------------------------------------------------+
    #| receiveSymbol
    #|     Manage the reception of a message and its transformation in a symbol
    #| @return a tupple containing the symbol and the associated received message
    #+-----------------------------------------------------------------------+
    def receiveSymbol(self):
        self.log.debug("Waiting for the reception of a message")
        return self.receiveSymbolWithTimeout(-1)


    def receiveSymbolWithTimeout(self, timeout):
        # First we read from the input the message
        receivedData = self.communicationChannel.read(timeout)

        if receivedData == None:
            self.log.warn("The communication channel seems to be closed !")
#            return (EmptySymbol(), None)
            return (None, None)

        if len(receivedData) > 0:
            now = datetime.datetime.now()
            receptionTime = now.strftime("%H:%M:%S")
            self.log.info("Received following message : " + str(receivedData))

            # Now we abstract the message
            symbol = self.abstract(receivedData)

            # We store the received messages its time and its abstract representation
            self.inputMessages.append([receptionTime, receivedData, symbol])
            self.manipulatedSymbols.append(symbol)
            self.outputSymbols.append(symbol)
            return (symbol, receivedData)
        else:
            if len(self.manipulatedSymbols) > 5:
                if  self.manipulatedSymbols[len(self.manipulatedSymbols) - 1].getType() == "EmptySymbol":
                    self.log.warn("Consider client has disconnected since no valid symbol received for the second time")
                    return (None, None)




            symbol = EmptySymbol()
            self.manipulatedSymbols.append(symbol)
            return (symbol, None)



    def writeSymbol(self, symbol):
        self.log.info("Sending symbol '" + symbol.getName() + "' over the communication channel")
        # First we specialize the symbol in a message
        (binMessage, strMessage) = self.specialize(symbol)
        self.log.info("- str = '" + strMessage + "'")
        self.log.info("- bin = '" + str(binMessage) + "'")

        # now we send it
        now = datetime.datetime.now()
        sendingTime = now.strftime("%H:%M:%S")
        self.communicationChannel.write(binMessage)

        self.outputMessages.append([sendingTime, strMessage, symbol])
        self.manipulatedSymbols.append(symbol)

    #+-----------------------------------------------------------------------+
    #| abstract
    #|     Searches in the vocabulary the symbol which abstract the received message
    #| @return a possible symbol or None if none exist in the vocabulary
    #+-----------------------------------------------------------------------+
    def abstract(self, message):
        # we search in the vocabulary an entry which match the message
        for symbol in self.vocabulary.getSymbols():
            print message
            print TypeConvertor.strBitarray2Bitarray(message)
            if symbol.getRoot().compare(TypeConvertor.strBitarray2Bitarray(message), 0, False, self.memory) != -1:
                self.log.debug("Entry in the vocabulary found")
                self.log.info("The message " + str(message) + " match symbol " + symbol.getName())
                return symbol
            else:
                self.log.debug("Entry " + str(symbol.getID()) + " doesn't match")
                # we first restore possibly learnt value
                self.log.debug("Restore possibly learnt value")
#                entry.restore()


        return EmptySymbol()

    def specialize(self, symbol):
        self.log.info("Specializing the symbol " + symbol.getName())
        return symbol.getValueToSend(False, self.memory)  # (bin, str)

    def getMemory(self):
        return self.memory

    #+-----------------------------------------------------------------------+
    #| getGeneratedInputAndOutputsSymbols
    #|     Retrieves all the received and the sent symbols in their manipulation order
    #| @return an array contening all the symbols
    #+-----------------------------------------------------------------------+
    def getGeneratedInputAndOutputsSymbols(self):
        return self.manipulatedSymbols
    def getGeneratedOutputSymbols(self):
        return self.outputSymbols

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
