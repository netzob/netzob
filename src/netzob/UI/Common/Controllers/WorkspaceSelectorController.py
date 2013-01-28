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

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+
import gi
gi.require_version('Gtk', '3.0')

from gi.repository import Gtk

from netzob.Common.ResourcesConfiguration import ResourcesConfiguration
from netzob.UI.Common.Views.WorkspaceSelectorView import WorkspaceSelectorView
from netzob.Common.Workspace import Workspace


#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
class WorkspaceSelectorController(object):
    """Manage the definition of the current workspace"""

    def __init__(self, mainController=None):
        self.mainController = mainController
        self.log = logging.getLogger(__name__)
        self._view = WorkspaceSelectorView(self)
        self._selectedWorkspace = None
        self.loadedWorkspace = None

    def getWorkspace(self, workspaceDir):
        """Request and load the specified workspace
        by user either through the dedicated interface
        either through the user config file.

        This method returns None if no workspace
        has been retrieved or the loaded workspace."""
        logging.debug("+ Load workspace...")

        self._selectedWorkspace = workspaceDir

        # Loading the workspace
        if workspaceDir is not None:
            (self.loadedWorkspace, error) = (Workspace.loadWorkspace(workspaceDir))
            if error is not None:
                self.setError(error)

        if self.loadedWorkspace is None:
            self.run()

        return self.loadedWorkspace

    def setError(self, errorMessage):
        self._view.setError(errorMessage)

    def getSelectedWorkspace(self):
        return self.selectedWorkspace

    def pathEntry_changed_cb(self, widget, data=None):
        """Callback executed when the path entry is edited"""
        textEntry = widget.get_text()
        if textEntry != "":
            self._selectedWorkspace = textEntry
        else:
            self._selectedWorkspace = None

    def pathEntry_focus_in_event_cb(self, widget, data=None):
        """Callback executed when the user clicks
        on the path entry"""
        self.view.openBrowseDialog(self._selectedWorkspace)

    def browseButton_clicked_cb(self, widget):
        """Callback executed when the user clicks
        on the browse button"""
        self.view.openBrowseDialog(self._selectedWorkspace)

    def applyButton_clicked_cb(self, widget):
        """Callback executed when the user clicks on the apply button"""
        workspacePath = self.getSelectedWorkspace()
        # We verify the workspace can be loaded.
        # if it can, we stop the current GTK
        if workspacePath is None or len(workspacePath) == 0:
            self.setError(_("No workspace provided."))
        else:
            logging.debug("Create the requested workspace")
            try:
                ResourcesConfiguration.createWorkspace(workspacePath)
            except OSError as e:
                self.log.warning("Impossible to create a workspace : {0}".format(e))
                self.setError("Impossible to create a workspace here.")

                return

            (workspace, error) = (Workspace.loadWorkspace(self._selectedWorkspace))
            if workspace is not None:
                # If we managed to load the given workspace, we save it and stop the GTK
                ResourcesConfiguration.generateUserFile(self._selectedWorkspace)
                self.loadedWorkspace = workspace
                self.stop()
            else:
                self.setError(error)

    def cancelButton_clicked_cb(self, widget):
        """Cabblack executed when the user clicks on the
        cancel button"""
        self._selectedWorkspace = None
        self.stop()

    def stop(self):
        self.view.destroy()
        Gtk.main_quit()

    def workspaceSelectorDialog_destroy_cb(self, widget):
        """Callback executed when the signal 'destroy' is emitted
        by the dialog"""
        self.stop()

    @property
    def view(self):
        return self._view

    @property
    def selectedWorkspace(self):
        return self._selectedWorkspace

    def run(self):
        self._view.run()
        Gtk.main()

    def closeButton_clicked_cb(self, widget):
        self._view.destroy()
