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

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.ResourcesConfiguration import ResourcesConfiguration
from netzob.UI.Common.Views.ProjectPropertiesView import ProjectPropertiesView


class ProjectPropertiesController(object):
    """Manage project's properties"""

    def __init__(self, mainController, parent=None, project=None):
        self.mainController = mainController
        self.log = logging.getLogger(__name__)
        self.workspace = mainController.getCurrentWorkspace()

        if project:
            self.currentProject = project
        else:
            self.currentProject = mainController.getCurrentProject()

        if parent:
            parentWindow = parent
        else:
            parentWindow = mainController.view.mainWindow

        self.projectNameChanged = False
        self.projectDescriptionChanged = False

        self._view = ProjectPropertiesView(self, parent=parentWindow)

        vocabParameters = self.currentProject.getConfiguration().getVocabularyInferenceParameter
        self.projectFormat = vocabParameters(ProjectConfiguration.VOCABULARY_GLOBAL_FORMAT)
        self.projectSize = vocabParameters(ProjectConfiguration.VOCABULARY_GLOBAL_UNITSIZE)
        self.projectSign = vocabParameters(ProjectConfiguration.VOCABULARY_GLOBAL_SIGN)
        self.projectEndianess = vocabParameters(ProjectConfiguration.VOCABULARY_GLOBAL_ENDIANESS)

        self._refreshProjectProperties()

    @property
    def view(self):
        if hasattr(self, "_view"):
            return self._view
        return False

    def run(self):
        self.view.run()

    def connectDestroySignal(self, function):
        self.view.projectPropertiesDialog.connect("destroy", function)

    def _refreshProjectProperties(self):
        props = self.currentProject.getProperties()

        self.view.refreshProjectProperties(name=props['name'].getCurrentValue(),
                                           description=props['description'].getCurrentValue(),
                                           date=props['date'].getCurrentValue(),
                                           symbols=props['symbols'].getCurrentValue(),
                                           messages=props['messages'].getCurrentValue(),
                                           fields=props['fields'].getCurrentValue(),
                                           workspace=props['workspace'].getCurrentValue())

    def closebutton_clicked_cb(self, widget):
        self.view.destroy()

    def projectNameEntry_changed_cb(self, entry):
        self.projectNameChanged = True

        if len(entry.get_text()) >= 1:
            self.view.closebutton.set_sensitive(True)
        else:
            self.view.closebutton.set_sensitive(False)

    def projectNameEntry_focus_out_event_cb(self, entry, data):
        if self.projectNameChanged:
            projectName = entry.get_text()

            self.log.debug("Updating project name, from {0}, to {1}".format(self.currentProject.getName(),
                                                                            projectName))

            self.currentProject.setName(projectName)
            self.currentProject.saveConfigFile(self.workspace)
            self.mainController.updateListOfAvailableProjects()
            self._refreshProjectProperties()

    def projectDescriptionEntry_changed_cb(self, entry):
        self.projectDescriptionChanged = True

    def projectDescriptionEntry_focus_out_event_cb(self, entry, data):
        if self.projectDescriptionChanged:
            projectDescription = entry.get_text()

            self.log.debug("Updating project description, from {0}, to {1}".format(self.currentProject.getDescription(),
                                                                                   projectDescription))

            self.currentProject.setDescription(projectDescription)
            self.currentProject.saveConfigFile(self.workspace)
            self._refreshProjectProperties()
