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
from netzob.Common.MMSTD.Actors.Network.NetworkServer import NetworkServer
from netzob.Common.MMSTD.Actors.Network.NetworkClient import NetworkClient

gi.require_version('Gtk', '3.0')
from gi.repository import GObject

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+


class CreateNetworkActorController(object):
    """Manages the creation of a network (client or server) actor"""

    def __init__(self, simulatorController):
        self.simulatorController = simulatorController
        self.idActor = uuid.uuid4()
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

        # retrieve the type (SERVER or CLIENT)
        typeActor = self._view.typeComboBoxText.get_active_text()
        if typeActor is None:
            errorMessage = _("Specify the type of the actor.")
            self.displayErrorMessage(errorMessage)
            return

        if typeActor != "CLIENT" and typeActor != "SERVER":
            errorMessage = _("Choose between a CLIENT or a SERVER type.")
            self.displayErrorMessage(errorMessage)
            return

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

        actor = None

        if typeActor == "CLIENT":
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

            actor = NetworkClient(self.idActor, actorName, l4Protocol, bindIP, bindPort, targetIP, targetPort)

        if typeActor == "SERVER":
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

            actor = NetworkServer(self.idActor, actorName, l4Protocol, bindIP, bindPort, targetIP, targetPort)

        if actor is not None:
            # Register the new actor
            self.simulatorController.getCurrentProject().getSimulator().addActor(actor)

        self._view.destroy()
        self.simulatorController.restart()

    def run(self):
        self._view.run()
