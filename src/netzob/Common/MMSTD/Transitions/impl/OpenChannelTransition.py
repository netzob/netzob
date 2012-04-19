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
import time
from datetime import datetime
import uuid
#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+
from lxml.etree import ElementTree

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.MMSTD.Transitions.AbstractTransition import AbstractTransition
from lxml import etree
from netzob.Common.MMSTD.Transitions.impl.CloseChannelTransition import CloseChannelTransition
from netzob.Common.MMSTD.States.impl.NormalState import NormalState


#+---------------------------------------------------------------------------+
#| OpenChannelTransition:
#|    Special transition in charge of opening the transition
#+---------------------------------------------------------------------------+
class OpenChannelTransition(AbstractTransition):

    TYPE = "OpenChannel"

    def __init__(self, id, name, inputState, outputState, connectionTime, maxNumberOfAttempt):
        AbstractTransition.__init__(self, OpenChannelTransition.TYPE, id, name, inputState, outputState)
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Common.MMSTD.Transitions.impl.OpenChannelTransition.py')
        self.connectionTime = connectionTime
        self.maxNumberOfAttempt = maxNumberOfAttempt

    #+-----------------------------------------------------------------------+
    #| isValid
    #|     Computes if the received symbol is valid
    #| @return a boolean which indicates if received symbol is equivalent
    #+-----------------------------------------------------------------------+
    def isValid(self, receivedSymbol):
        return True

    #+-----------------------------------------------------------------------+
    #| executeAsClient
    #|     Open the connection
    #| @param abstractionLayer the abstract layer to contact in order to reach outside world
    #| @return the new state
    #+-----------------------------------------------------------------------+
    def executeAsClient(self, abstractionLayer):

        self.log.debug("Client is it a server ? " + str(abstractionLayer.getCommunicationChannel().isServer()))

        if abstractionLayer.getCommunicationChannel().isServer():
            self.log.debug("Cleaning the memory")
            abstractionLayer.getMemory().cleanMemory()

            self.activate()
            self.log.info("We instanciate a new server and close the current MMSTD")
            abstractionLayer.openServer(abstractionLayer.getVocabulary(), self.outputState, False)
            self.deactivate()

            startTime = datetime.now()

            # Here we wait for someone to connect to our server !
            finish = abstractionLayer.isConnected()
            error = False
            while (not finish):
                self.log.info("No one is connected !")
                currentTime = datetime.now()
                if ((currentTime - startTime).microseconds > self.connectionTime):
                    finish = True
                    error = True
                else:
                    finish = abstractionLayer.isConnected()
                time.sleep(1)

            if error:
                self.log.warn("No client has connect to our oracle.")
                return None
            else:
                error = False
                startTime = datetime.now()
                finish = not abstractionLayer.isConnected()
                while (not finish):
                    currentTime = datetime.now()
                    if ((currentTime - startTime).microseconds > 60000):
                        finish = True
                        error = True
                    else:
                        finish = not abstractionLayer.isConnected()
                    time.sleep(1)
                if error:
                    self.log.warn("Stop the server even if the client are still up")

                self.log.debug("The openChannelTransition finishes (the generated instance has been closed)!")
                # We create a Close Channel Transition to close the server
                inputState = NormalState(uuid.uuid4(), "Input State of the close server transition")
                outputState = NormalState(uuid.uuid4(), "Output State of the close server transition")
                closeChannelTransition = CloseChannelTransition(uuid.uuid4(), "Close Server transition", inputState, outputState, 300)
                inputState.registerTransition(closeChannelTransition)
                return inputState
        else:
            self.activate()
            result = self.openConnection(abstractionLayer)
            self.deactivate()
            if result:
                return self.outputState
            else:
                return None

    #+-----------------------------------------------------------------------+
    #| executeAsMaster
    #|     Open the connection
    #| @param abstractionLayer the abstract layer to contact in order to reach outside world
    #| @return the new state
    #+-----------------------------------------------------------------------+
    def executeAsMaster(self, abstractionLayer):
        if abstractionLayer.getCommunicationChannel().isServer():
            # start a specific listening network thread
            self.activate()
            self.log.info("We instanciate a new server and close the current MMSTD")
            abstractionLayer.openServer(abstractionLayer.getVocabulary(), self.outputState, True)
            self.deactivate()

            startTime = datetime.now()

            # Here we wait for someone to connect to our server !
            finish = abstractionLayer.isConnected()
            error = False
            while (not finish):
                self.log.info("No one is connected !")
                currentTime = datetime.now()
                if ((currentTime - startTime).microseconds > self.connectionTime):
                    finish = True
                    error = True
                else:
                    finish = abstractionLayer.isConnected()
                time.sleep(1)

            if error:
                self.log.warn("No client has connect to our oracle.")
                return None
            else:
                return self.outputState
        else:
            self.activate()
            result = self.openConnection(abstractionLayer)
            self.deactivate()
            if result:
                return self.outputState
            else:
                return None

    #+-----------------------------------------------------------------------+
    #| openConnection
    #|     Open the connection
    #| @param abstractionLayer the abstract layer to contact in order to reach outside world
    #| @return the new state
    #+-----------------------------------------------------------------------+
    def openConnection(self, abstractionLayer):
        self.log.info("OpenChannelTransition executed with the abstractionLayer : " + str(abstractionLayer))

        i = self.maxNumberOfAttempt
        j = 1
        while (not abstractionLayer.isConnected()  and i > 0):
            time.sleep(int(self.connectionTime) / 1000)
            abstractionLayer.connect()
            if abstractionLayer.isConnected():
                self.log.debug("Connected !")
            else:
                self.log.warn("Error, the connection attempt number " + str(j) + "failed")
#            i = i - 1
            j = j + 1

        if (abstractionLayer.isConnected()):
            return True
        else:
            self.log.warn("Max connection attempt reached !")
            return False

    def getDescription(self):
        return "OpenChannelTransition"

    def getConnectionTime(self):
        return self.connectionTime

    def getMaxNumberOfAttempt(self):
        return self.maxNumberOfAttempt

    def save(self, root, namespace):
        xmlTransition = etree.SubElement(root, "{" + namespace + "}transition")
        xmlTransition.set("id", str(self.getID()))
        xmlTransition.set("name", str(self.getName()))
        xmlTransition.set("{http://www.w3.org/2001/XMLSchema-instance}type", "netzob:OpenChannelTransition")

        xmlStartState = etree.SubElement(xmlTransition, "{" + namespace + "}startState")
        xmlStartState.text = str(self.getInputState().getID())

        xmlEndState = etree.SubElement(xmlTransition, "{" + namespace + "}endState")
        xmlEndState.text = str(self.getOutputState().getID())

        xmlConnectionTime = etree.SubElement(xmlTransition, "{" + namespace + "}connectionTime")
        xmlConnectionTime.text = str(self.getConnectionTime())

        xmlMaxNumberOfAttempt = etree.SubElement(xmlTransition, "{" + namespace + "}maxNumberOfAttempt")
        xmlMaxNumberOfAttempt.text = str(self.getMaxNumberOfAttempt())

    #+-----------------------------------------------------------------------+
    #| loadFromXML
    #|     Extract from an XML declaration the definition of the transition
    #| @return the instanciated object declared in the XML
    #+-----------------------------------------------------------------------+
    @staticmethod
    def loadFromXML(states, xmlTransition, namespace, version):
        idTransition = xmlTransition.get("id")
        nameTransition = xmlTransition.get("name")

        idStartTransition = xmlTransition.find("{" + namespace + "}startState").text.strip()
        idEndTransition = xmlTransition.find("{" + namespace + "}endState").text.strip()

        inputStateTransition = None
        outputStateTransition = None
        for state in states:

            if state.getID() == idStartTransition:
                inputStateTransition = state
            if state.getID() == idEndTransition:
                outputStateTransition = state

        connectionTime = int(xmlTransition.find("{" + namespace + "}connectionTime").text)
        maxNumberOfAttempt = int(xmlTransition.find("{" + namespace + "}maxNumberOfAttempt").text)

        transition = OpenChannelTransition(idTransition, nameTransition, inputStateTransition, outputStateTransition, connectionTime, maxNumberOfAttempt)
        inputStateTransition.registerTransition(transition)
        return transition
