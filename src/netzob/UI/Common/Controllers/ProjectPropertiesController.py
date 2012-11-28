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
from netzob.Common.Type.Format import Format
from netzob.Common.Type.UnitSize import UnitSize
from netzob.Common.Type.Sign import Sign
from netzob.Common.Type.Endianess import Endianess
from netzob.Common.ProjectConfiguration import ProjectConfiguration
from netzob.UI.Vocabulary.Controllers.VocabularyController import VocabularyController


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
        self._initializeComboBoxes()

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

    def _initializeComboBoxes(self):
        """This function permits to update the several combobox in the
        dialog box."""

        vocabParameters = self.currentProject.getConfiguration().getVocabularyInferenceParameter

        formats = Format.getSupportedFormats()
        projectFormat = vocabParameters(ProjectConfiguration.VOCABULARY_GLOBAL_FORMAT)

        sizes = [UnitSize.NONE, UnitSize.BITS4, UnitSize.BITS8, UnitSize.BITS16, UnitSize.BITS32, UnitSize.BITS64]
        projectSize = vocabParameters(ProjectConfiguration.VOCABULARY_GLOBAL_UNITSIZE)

        signs = [Sign.SIGNED, Sign.UNSIGNED]
        projectSign = vocabParameters(ProjectConfiguration.VOCABULARY_GLOBAL_SIGN)

        endianesses = [Endianess.BIG, Endianess.LITTLE]
        projectEndianess = vocabParameters(ProjectConfiguration.VOCABULARY_GLOBAL_ENDIANESS)

        self.view.initializeComboBoxes(formats, projectFormat,
                                       sizes, projectSize,
                                       signs, projectSign,
                                       endianesses, projectEndianess)

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

    def propertiesFormatCombobox_changed_cb(self, combo):
        tree_iter = combo.get_active_iter()
        frmt = combo.get_model()[tree_iter][0]

        setParam = self.currentProject.getConfiguration().setVocabularyInferenceParameter
        setParam(ProjectConfiguration.VOCABULARY_GLOBAL_FORMAT, frmt)

        self.currentProject.saveConfigFile(self.workspace)

    def propertiesUnitsizeCombobox_changed_cb(self, combo):
        tree_iter = combo.get_active_iter()
        unitSize = combo.get_model()[tree_iter][0]

        setParam = self.currentProject.getConfiguration().setVocabularyInferenceParameter
        setParam(ProjectConfiguration.VOCABULARY_GLOBAL_UNITSIZE, unitSize)

        self.currentProject.saveConfigFile(self.workspace)

    def propertiesSignCombobox_changed_cb(self, combo):
        tree_iter = combo.get_active_iter()
        sign = combo.get_model()[tree_iter][0]

        setParam = self.currentProject.getConfiguration().setVocabularyInferenceParameter
        setParam(ProjectConfiguration.VOCABULARY_GLOBAL_SIGN, sign)

        self.currentProject.saveConfigFile(self.workspace)

    def propertiesEndianessCombobox_changed_cb(self, combo):
        tree_iter = combo.get_active_iter()
        endianess = combo.get_model()[tree_iter][0]

        setParam = self.currentProject.getConfiguration().setVocabularyInferenceParameter
        setParam(ProjectConfiguration.VOCABULARY_GLOBAL_ENDIANESS, endianess)

        self.currentProject.saveConfigFile(self.workspace)

    def _getComboValue(self, combobox):
        combo = getattr(self.view, combobox)
        tree_iter = combo.get_active_iter()
        return combo.get_model()[tree_iter][0]

    def vocabPropertiesApplyToAll_clicked_cb(self, button):
        symbols = self.currentProject.getVocabulary().getSymbols()

        self.log.debug("Setting 'Format' setting to all symbols")
        map(lambda x: x.field.setFormat(self._getComboValue("propertiesFormatCombobox")), symbols)

        self.log.debug("Setting 'UnitSize' setting to all symbols")
        map(lambda x: x.field.setUnitSize(self._getComboValue("propertiesUnitsizeCombobox")), symbols)

        self.log.debug("Setting 'Sign' setting to all symbols")
        map(lambda x: x.field.setSign(self._getComboValue("propertiesSignCombobox")), symbols)

        self.log.debug("Setting 'Endianess' setting to all symbols")
        map(lambda x: x.field.setEndianess(self._getComboValue("propertiesEndianessCombobox")), symbols)

        vocabView = self.mainController.view.perspectiveDict[VocabularyController.PERSPECTIVE_ID][1].view
        vocabView.updateSelectedMessageTable()
