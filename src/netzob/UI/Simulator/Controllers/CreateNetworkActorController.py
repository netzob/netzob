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
import time
import uuid

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+
from gi.repository import Gtk, Gdk
import gi
from netzob.UI.Simulator.Views.CreateNetworkActorView import CreateNetworkView
from netzob.Common.MMSTD.Dictionary.AbstractionLayer import AbstractionLayer
from netzob.Common.MMSTD.Dictionary.Memory import Memory
from netzob.Common.MMSTD.Actors.MMSTDVisitor import MMSTDVisitor
from netzob.Common.MMSTD.Dictionary.Variables.DataVariable import DataVariable
from netzob.Common.MMSTD.Dictionary.DataTypes.WordType import WordType
from netzob.Common.MMSTD.Dictionary.DataTypes.IPv4WordType import IPv4WordType
from netzob.Common.MMSTD.Dictionary.DataTypes.IntegerType import IntegerType
from netzob.Common.MMSTD.Actors.NetworkChannels.NetworkClient import NetworkClient
from netzob.Common.MMSTD.Actors.NetworkChannels.NetworkServer import NetworkServer

gi.require_version('Gtk', '3.0')
from gi.repository import GObject

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+


class CreateNetworkActorController(object):
    """Manages the creation of a network (client or server) actor"""

    def __init__(self, simulatorController):
        self.simulatorController = simulatorController
        self.idActor = str(uuid.uuid4())
        self._view = CreateNetworkView(self, self.idActor)
        self.log = logging.getLogger(__name__)

    @property
    def view(self):
        return self._view

    def displayErrorMessage(self, errorMessage):
        if errorMessage is None:
            self._view.errorImage.hide()
            self._view.errorLabel.set_label("")
            self._view.errorLabel.hide()
        else:
            self._view.errorLabel.set_label(errorMessage)
            self._view.errorLabel.show()
            self._view.errorImage.show()

    def cancelButton_clicked_cb(self, event):
        """Callback executed when the user clicks on the cancel button"""
        self._view.destroy()

    def createButton_clicked_cb(self, event):
        """callback executed when the user clicks on the create button"""

        actorName = self._view.nameEntry.get_text()
        if actorName is None or len(actorName) == 0:
            errorMessage = _("Give a name to the actor")
            self.displayErrorMessage(errorMessage)
            return

        # verify the name is unique
        found = False
        for actor in self.simulatorController.getCurrentProject().getSimulator().getActors():
            if actor.getName() == actorName:
                found = True
                break

        if found:
            errorMessage = _("An actor already has this name.")
            self.displayErrorMessage(errorMessage)
            return

        # initiator
        initiator = self._view.initiatorCheckButton.get_active()

        # Create the Channel

        # retrieve the type (SERVER or CLIENT)
        typeActorStr = self._view.typeComboBoxText.get_active_text()
        if typeActorStr is None:
            errorMessage = _("Specify the type of the actor.")
            self.displayErrorMessage(errorMessage)
            return

        actorIsClient = False
        if typeActorStr == _("CLIENT"):
            actorIsClient = True

        # retrieve the L4 protocol
        l4Protocol = self._view.l4ProtocolComboBoxText.get_active_text()
        if l4Protocol is None or (l4Protocol != "TCP" and l4Protocol != "UDP"):
            errorMessage = _("Only UDP and TCP layer 4 protocols are supported.")
            self.displayErrorMessage(errorMessage)
            return

        # retrieve IP and Ports
        bindIP = self._view.bindIPEntry.get_text()
        bindPort = self._view.bindPortEntry.get_text()
        if bindPort is not None and len(bindPort) > 0:
            try:
                bindPort = int(bindPort)
            except:
                bindPort = -1

            if bindPort <= 0:
                errorMessage = _("Specify a valid bind port (int>0)")
                self.displayErrorMessage(errorMessage)
                return
        else:
            bindPort = None

        targetIP = self._view.targetIPEntry.get_text()
        targetPort = self._view.targetPortEntry.get_text()
        if targetPort is not None and len(targetPort) > 0:
            try:
                targetPort = int(targetPort)
            except:
                targetPort = -1

            if targetPort <= 0:
                errorMessage = _("Specify a valid target port (int>0)")
                self.displayErrorMessage(errorMessage)
                return
        else:
            targetPort = None

        communicationChannel = None
        idChannel = str(uuid.uuid4())

        # Initialize a memory with communication channels variables
        memory = Memory()

        if actorIsClient:
            # Create a Client Network Actor
            # target IP and target Port must be specified !
            if targetIP is None or len(targetIP) == 0:
                errorMessage = _("A network client requires a target IP.")
                self.displayErrorMessage(errorMessage)
                return

            if targetPort is None:
                errorMessage = _("A network client requires a target port.")
                self.displayErrorMessage(errorMessage)
                return

            communicationChannel = NetworkClient(idChannel, memory, l4Protocol, bindIP, bindPort, targetIP, targetPort)
        else:
            # Create a Server Network Actor
            # bind IP and bind Port must be specified !
            if bindIP is None or len(bindIP) == 0:
                errorMessage = _("A network server requires a bind IP.")
                self.displayErrorMessage(errorMessage)
                return

            if bindPort is None:
                errorMessage = _("A network server requires a bind port.")
                self.displayErrorMessage(errorMessage)
                return

            communicationChannel = NetworkServer(idChannel, memory, l4Protocol, bindIP, bindPort, targetIP, targetPort)

        if communicationChannel is not None and memory is not None:
            vocabulary = self.simulatorController.getCurrentProject().getVocabulary()
            grammar = self.simulatorController.getCurrentProject().getGrammar()

            # Create the abstraction layer
            abstractionLayer = AbstractionLayer(communicationChannel, vocabulary, memory)

            # Create the MMSTD Visitor
            actor = MMSTDVisitor(self.idActor, actorName, grammar.getAutomata(), initiator, abstractionLayer)

            # Register the new actor
            self.simulatorController.getCurrentProject().getSimulator().addActor(actor)

        self._view.destroy()
        self.simulatorController.restart()

    def run(self):
        self._view.run()
