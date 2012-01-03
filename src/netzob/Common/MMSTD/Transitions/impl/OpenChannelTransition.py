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


#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+
from lxml.etree import ElementTree

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.MMSTD.Transitions.AbstractTransition import AbstractTransition
from lxml import etree


#+---------------------------------------------------------------------------+
#| OpenChannelTransition :
#|    Special transition in charge of opening the transition
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.3
#+---------------------------------------------------------------------------+
class OpenChannelTransition(AbstractTransition):
    
    def __init__(self, id, name, inputState, outputState, connectionTime, maxNumberOfAttempt):
        AbstractTransition.__init__(self, "OpenChannel", id, name, inputState, outputState)
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
         
        if abstractionLayer.getCommunicationChannel().isServer() :
            # start a specific listening network thread
            self.activate()
            self.log.debug("We instanciate a new server and close the current MMSTD")     
            abstractionLayer.openServer(abstractionLayer.getDictionary(), self.outputState, False)
            self.deactivate()
            return None
        else :  
            self.activate()     
            result = self.openConnection(abstractionLayer)
            self.deactivate()
            if result :
                return self.outputState
            else :
                return None
            
    #+-----------------------------------------------------------------------+
    #| executeAsMaster
    #|     Open the connection
    #| @param abstractionLayer the abstract layer to contact in order to reach outside world
    #| @return the new state
    #+-----------------------------------------------------------------------+
    def executeAsMaster(self, abstractionLayer):    
        if abstractionLayer.getCommunicationChannel().isServer() :
            # start a specific listening network thread
            self.activate()     
            abstractionLayer.openServer(abstractionLayer.getDictionary(), self.outputState, True)
            self.deactivate()
            return None
        else :  
            self.activate()     
            result = self.openConnection(abstractionLayer)
            self.deactivate()
            if result :
                return self.outputState
            else :
                return None
        
    #+-----------------------------------------------------------------------+
    #| openConnection
    #|     Open the connection
    #| @param abstractionLayer the abstract layer to contact in order to reach outside world
    #| @return the new state
    #+-----------------------------------------------------------------------+
    def openConnection(self, abstractionLayer):
        self.log.debug("OpenChannelTransition executed.")
        
        i = self.maxNumberOfAttempt
        while (not abstractionLayer.isConnected()  and i > 0) :
            time.sleep(int(self.connectionTime) / 1000)
            abstractionLayer.connect()
            if abstractionLayer.isConnected() :
                self.log.debug("Connected !")
            else :
                self.log.warn("Error, the connection attempt failed")
            i = i - 1
        
        if (abstractionLayer.isConnected()) :
            return True
        else :
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
            
        idStartTransition = xmlTransition.find("{" + namespace + "}startState").text
        idEndTransition = xmlTransition.find("{" + namespace + "}endState").text
        
        inputStateTransition = None
        outputStateTransition = None
        for state in states :
            if state.getID() == idStartTransition :
                inputStateTransition = state
            if state.getID() == idEndTransition :
                outputStateTransition = state
        
        connectionTime = int(xmlTransition.find("{" + namespace + "}connectionTime").text)
        maxNumberOfAttempt = int(xmlTransition.find("{" + namespace + "}maxNumberOfAttempt").text)
       
        transition = OpenChannelTransition(idTransition, nameTransition, inputStateTransition, outputStateTransition, connectionTime, maxNumberOfAttempt)
        inputStateTransition.registerTransition(transition)
        return transition
