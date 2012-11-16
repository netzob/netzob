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
from locale import gettext as _
import logging

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.ResourcesConfiguration import ResourcesConfiguration
from netzob.UI.Common.Views.WorkspaceConfigurationView import WorkspaceConfigurationView
from netzob.Common.LoggingConfiguration import LoggingConfiguration


class WorkspaceConfigurationController(object):
    """Manage the list of available plugins"""

    def __init__(self, mainController):
        self.mainController = mainController
        self.log = logging.getLogger(__name__)
        self._loggingConfiguration = LoggingConfiguration()

        self.keyUpdated = False

        self._view = WorkspaceConfigurationView(self, parent=mainController.view.mainWindow)

    @property
    def view(self):
        if hasattr(self, "_view"):
            return self._view
        return False

    def run(self):
        self.view.run()

    def closebutton_clicked_cb(self, widget):
        self.view.destroy()

    def advancedLoggingCombobox_changed_cb(self, combo):
        tree_iter = combo.get_active_iter()
        logLevel = combo.get_model()[tree_iter][0]
        self._loggingConfiguration.setLoggingLevel(logLevel)

    def advancedBugreportingEntry_changed_cb(self, entry):
        """Called when the "API key" is changed, if so, we set the
        keyUpdated's value to True in order to get the new API key
        saved on the "focus-out" event."""

        self.keyUpdated = True

    def advancedBugreportingEntry_focus_out_event_cb(self, entry, data):
        """Called on "focus-out" of the API key entry. If its value
        was changed, we can save the new value."""

        if self.keyUpdated:
            apiKey = entry.get_text()
            logging.info("Saving the new API key: {0}".format(apiKey))
            ResourcesConfiguration.saveAPIKey(apiKey)
            self.keyUpdated = False
