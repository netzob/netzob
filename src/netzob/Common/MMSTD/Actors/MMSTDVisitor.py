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
from gettext import gettext as _
import logging
import threading
from lxml.etree import ElementTree
from lxml import etree
from netzob.Common.MMSTD.Dictionary.AbstractionLayer import AbstractionLayer
from netzob.Common.Property import Property
from netzob.Common.Type.TypeIdentifier import TypeIdentifier
from netzob.Common.Type.Format import Format
from netzob.Common.Type.TypeConvertor import TypeConvertor

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+


#+---------------------------------------------------------------------------+
#| MMSTDVisitor:
#|     Definition of a visitor of an MMSTD automata
#+---------------------------------------------------------------------------+
class MMSTDVisitor(threading.Thread):

    TYPE = "MMSTD Visitor"

    def __init__(self, id, name, mmstd, initiator, abstractionLayer):
        threading.Thread.__init__(self)
        # create logger with the given configuration
        self.log = logging.getLogger(__name__)
        self.id = id
        self.name = name
        self.model = mmstd
        self.initiator = initiator
        self.abstractionLayer = abstractionLayer
        self.active = False

        self.modificationStatus_cb = None

    def clone(self):
        """The MMSTDVisitor is a thread. Hence we cannot restart it so it
        requires to clone it."""
        return MMSTDVisitor(self.id, self.name, self.model, self.initiator, self.abstractionLayer)

    def run(self):
        if self.initiator:
            self.log.debug("Starting the MMSTDVisitor as a Master")
        else:
            self.log.debug("Starting the MMSTDVisitor as a Client")
        self.setActive(True)
        if self.initiator:
            self.runAsMaster()
        else:
            self.runAsClient()
        self.log.debug("End of execution for the MMSTDVisitor")

    def stop(self):
        self.log.debug("Stops the MMSTDVisitor")
        self.abstractionLayer.disconnect()
        self.setActive(False)

    def runAsMaster(self):
        self.log.debug("The MMSTD Visitor is running as a master")
        currentState = self.model.getInitialState()
        while self.active:
            currentState = currentState.executeAsMaster(self.abstractionLayer)
            if currentState is None:
                self.setActive(False)
        self.log.debug("The MASTER stops !")

    def runAsClient(self):
        self.log.debug("The MMSTD Visitor is running as a client")

        currentState = self.model.getInitialState()
        while self.active:
            self.log.debug("Run as a client the state " + str(currentState.getName()))
            currentState = currentState.executeAsClient(self.abstractionLayer)
            if currentState is None:
                self.log.warn("The execution of the transition didn't provide the next state")
                self.setActive(False)
        self.log.debug("The CLIENT stops !")

    def getInputMessages(self):
        return self.abstractionLayer.getInputMessages()

    def getOutputMessages(self):
        return self.abstractionLayer.getOutputMessages()

    def getMemory(self):
        return self.abstractionLayer.getMemory()

    def getAbstractionLayer(self):
        return self.abstractionLayer

    def getProperties(self):
        """Compute and return the list of properties of the actor"""
        properties = []
        properties.append(Property("ID", Format.STRING, self.getID()))
        properties.append(Property("Name", Format.STRING, self.getName()))
        initiator = "No"
        if self.isInitiator():
            initiator = "Yes"
        properties.append(Property("Initiator", Format.STRING, initiator))

        properties.extend(self.getAbstractionLayer().getProperties())

        return properties

    #+-----------------------------------------------------------------------+
    #| GETTERS AND SETTERS
    #+-----------------------------------------------------------------------+
    def getID(self):
        return self.id

    def getName(self):
        return self.name

    def getModel(self):
        return self.model

    def getType(self):
        return self.TYPE

    def isInitiator(self):
        return self.initiator

    def isActive(self):
        return self.active

    def setModel(self, model):
        self.model = model

    def setName(self, name):
        self.name = name

    def setActive(self, active):
        """Update the status of the visitor.
        Triggers the execution of the notification callbacks (if it exists)"""
        self.active = active
        if self.modificationStatus_cb is not None:
            self.modificationStatus_cb()

    def setStatusModification_cb(self, cb):
        self.modificationStatus_cb = cb

    def save(self, root, namespace):
        """Save in the XML tree the actor definition"""
        xmlActor = etree.SubElement(root, "{" + namespace + "}actor")
        xmlActor.set('id', str(self.getID()))
        xmlActor.set('name', str(self.getName()))
        xmlActor.set('initiator', TypeConvertor.bool2str(self.isInitiator()))
        self.abstractionLayer.save(xmlActor, namespace)

    @staticmethod
    def loadFromXML(xmlRoot, namespace, version, automata, vocabulary):
        if version == "0.1":

            id = xmlRoot.get('id')
            name = xmlRoot.get('name')
            initiator = TypeConvertor.str2bool(xmlRoot.get('initiator'))

            abstractionLayer = None
            if xmlRoot.find("{" + namespace + "}abstractionLayer") is not None:
                abstractionLayer = AbstractionLayer.loadFromXML(xmlRoot.find("{" + namespace + "}abstractionLayer"), namespace, version, vocabulary)

            return MMSTDVisitor(id, name, automata, initiator, abstractionLayer)

        return None
