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
import shutil
import os
import uuid

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.ResourcesConfiguration import ResourcesConfiguration
from netzob.UI.Common.Views.ProjectImportView import ProjectImportView
from netzob.Common.Project import Project, ProjectException


class ProjectImportController(object):
    """Manage import of new project."""

    def __init__(self, mainController, parent=None):
        self.mainController = mainController
        self.log = logging.getLogger(__name__)
        self.workspace = mainController.getCurrentWorkspace()

        if not parent:
            parent = mainController.view.mainWindow
        self._view = ProjectImportView(self, parent=parent)

    @property
    def view(self):
        if hasattr(self, "_view"):
            return self._view
        return False

    def run(self):
        self.view.run()

    def closebutton_clicked_cb(self, widget):
        self.view.destroy()

    def fileSetFileChooser_importProject_cb(self, widget):
        """Callback executed when the user selects a file in the file
        chooser of the import project dialog box"""

        selectedFile = widget.get_filename()
        if selectedFile is not None:
            self.view.importProjectApplyButton.set_sensitive(True)
        else:
            self.view.importProjectApplyButton.set_sensitive(False)

    def importProjectCancelButton_clicked_cb(self, button):
        self.view.destroy()

    def importProjectApplyButton_clicked_cb(self, button):
        selectedFile = self.view.importProjectFileChooserButton.get_filename()

        if selectedFile is None:
            self.view.showErrorMessage(_("No file selected"))
        else:
            # Verify the file is a valid definition of a project
            if Project.loadProjectFromFile(selectedFile) is None:
                self.view.showErrorMessage(_("The file doesn't define a valid project."))
            else:
                try:
                    Project.importNewXMLProject(self.workspace, selectedFile)
                    self.mainController.updateListOfAvailableProjects()
                    self.view.destroy()
                except ProjectException, e:
                    self.view.showErrorMessage(str(e))
