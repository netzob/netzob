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
from netzob.UI.Simulator.Views.SimulatorView import SimulatorView
from netzob.UI.Simulator.Controllers.CreateNetworkActorController import CreateNetworkActorController

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+


#+---------------------------------------------------------------------------+
#| SimulatorController:
#+---------------------------------------------------------------------------+
class SimulatorController:

    def __init__(self, netzob):
        self.netzob = netzob
        self._view = SimulatorView(self)
        self.log = logging.getLogger(__name__)

    @property
    def view(self):
        return self._view

    def restart(self):
        """Restart the view"""
        logging.debug("Restarting the simulator perspective")
        self._view.restart()

    def activate(self):
        """Activate the perspective"""
        self.restart()

    def getCurrentProject(self):
        """Return the current project (can be None)"""
        return self.netzob.getCurrentProject()

    def getCurrentWorkspace(self):
        """Return the current workspace"""
        return self.netzob.getCurrentWorkspace()

    def createNetworkActor_activate_cb(self, event):
        """Callback executed when the user wants to create a network actor"""
        if self.getCurrentProject() is None:
            logging.info("No project loaded.")
            return

        controller = CreateNetworkActorController(self)
        controller.run()

    def editActorButton_clicked_cb(self, event):
        """Callback executed when the user wants to edit a selected actor"""
        if self.getCurrentProject() is None:
            logging.info("No project loaded.")
            return

    def deleteActorButton_clicked_cb(self, event):
        """Callback executed when the user wants to delete a selected actor"""
        if self.getCurrentProject() is None:
            logging.info("No project loaded.")
            return

    def stopActorButton_clicked_cb(self, event):
        """Callback executed when the user wants to stop a selected actor"""
        if self.getCurrentProject() is None:
            logging.info("No project loaded.")
            return

    def startActorButton_clicked_cb(self, event):
        """Callback executed when the user wants to start a selected actor"""
        if self.getCurrentProject() is None:
            logging.info("No project loaded.")
            return

    def stopCurrentActorButton_clicked_cb(self, event):
        """Callback executed when the user wants to start the current actor"""
        if self.getCurrentProject() is None:
            logging.info("No project loaded.")
            return

    def startCurrentActorButton_clicked_cb(self, event):
        """Callback executed when the user wants to stop the current Actor"""
        if self.getCurrentProject() is None:
            logging.info("No project loaded.")
            return
