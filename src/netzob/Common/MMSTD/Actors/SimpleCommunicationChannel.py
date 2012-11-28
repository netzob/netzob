# -* - coding: utf-8 -*-

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
from collections import deque
from gettext import gettext as _
import bitarray
import logging

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.MMSTD.Dictionary.VariableProcessingToken.VariableWritingToken import \
    VariableWritingToken
from netzob.Common.MMSTD.Actors.AbstractChannel import AbstractChannel


#+---------------------------------------------------------------------------+
#| SimpleCommunicationLayer:
#|     Definition of a simple communicationLayer
#+---------------------------------------------------------------------------+
class SimpleCommunicationLayer(AbstractChannel):

    def __init__(self, id, inputs, outputs, vocabulary, memory):
        AbstractChannel.__init__(self, id, False, False, memory, None, None, None, None, None)

        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Common.MMSTD.Actors.SimpleCommunicationLayer.py')
        self.predefinedInputs = deque(inputs)
        self.predefinedOutputs = deque(outputs)
        self.inputMessages = []
        self.outputMessages = []
        self.vocabulary = vocabulary
        self.memory = memory

    def open(self):
        self.log.debug("We open it !")
        return True

    def close(self):
        self.log.debug("We close it !")
        return True

    def read(self, timeout):
        self.log.debug("We read it !")
        if (len(self.predefinedInputs) > 0):
            symbol = self.predefinedInputs.popleft()
            self.log.debug("We simulate the reception of symbol " + str(symbol))

            # TODO: replace default values by clever values.
            writingToken = VariableWritingToken(False, self.vocabulary, self.memory, bitarray(''), ["random"])
            self.symbol.write(writingToken)
            value = writingToken.getValue()
            self.inputMessages.append(value)
            return value
        else:
            self.log.debug("No more inputs to simulate, nothing was read ")
            return None

    def write(self, message):
        self.log.debug("Write down !")
        self.outputMessages.append(message)

    def getInputMessages(self):
        return self.inputMessages

    def getOutputMessages(self):
        return self.outputMessages

    def getGeneratedInstances(self):
        return []

    def stop(self):
        self.log.debug("Stopping the thread of the client")
        AbstractActor.stop(self)
