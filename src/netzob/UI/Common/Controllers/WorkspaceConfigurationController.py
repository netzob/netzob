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
from gi.repository import Gtk, Gdk, GObject

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.ResourcesConfiguration import ResourcesConfiguration
from netzob.UI.Common.Views.WorkspaceConfigurationView import WorkspaceConfigurationView
from netzob.Common.LoggingConfiguration import LoggingConfiguration
from netzob.Common.BugReporter import BugReporter
from netzob.Common.Threads.Tasks.ThreadedTask import ThreadedTask, TaskError
from netzob.Common.Threads.Job import Job
from netzob.Common.Project import Project
from netzob.UI.Common.Controllers.ProjectImportController import ProjectImportController
from netzob.UI.Common.Controllers.ProjectExportController import ProjectExportController
from netzob.UI.Common.Controllers.ProjectPropertiesController import ProjectPropertiesController


class WorkspaceConfigurationController(object):
    """Manage the list of available plugins"""

    def __init__(self, mainController):
        self.mainController = mainController
        self.log = logging.getLogger(__name__)
        self._loggingConfiguration = LoggingConfiguration()
        self.workspace = mainController.getCurrentWorkspace()

        self.selectedProject = None
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

    def advancedBugreportingCheckbox_toggled_cb(self, toggle):
        enable = toggle.get_active()

        self.workspace.setEnableBugReporting(enable)
        self.mainController.enableBugReporter(enable)

        if self.view:
            self.view.refreshEnableBugReporting(enable)

    def advancedBugreportingEntry_changed_cb(self, entry):
        """Called when the "API key" is changed, if so, we set the
        keyUpdated's value to True in order to get the new API key
        saved on the "focus-out" event."""

        self.keyUpdated = True

        if len(entry.get_text()) == 0:
            self.view.changeTestButtonSensitivity(False)
        else:
            self.view.changeTestButtonSensitivity(True)

    def advancedBugreportingEntry_focus_out_event_cb(self, entry, data):
        """Called on "focus-out" of the API key entry. If its value
        was changed, we can save the new value."""

        if self.keyUpdated:
            apiKey = entry.get_text()
            self.log.info("Saving the new API key: {0}".format(apiKey))
            ResourcesConfiguration.saveAPIKey(apiKey)
            self.keyUpdated = False

    def advancedBugreportingTestkey_clicked_cb(self, button):
        """Called when the use clicks on the "Test Key" button."""

        self.view.testKeyUpdateSpinnerState(state=1)
        Job(self._startKeyValidation())

    def _startKeyValidation(self):
        try:
            (yield ThreadedTask(self._keyValidationTask))

            if not self.validKey:
                dialog = Gtk.MessageDialog(self.view.workspaceConfigurationDialog,
                                           Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
                                           Gtk.MessageType.WARNING,
                                           Gtk.ButtonsType.OK,
                                           _("The specified key is invalid!"))
                dialog.run()
                dialog.destroy()

        except TaskError, e:
            self.log.error("Error while validating the API key: {0}".format(str(e)))

    def _keyValidationTask(self):
        reporter = BugReporter()

        self.validKey = reporter.isAPIKeyValid()

        if self.validKey:
            self.log.error("The specified key is valid.")
            GObject.idle_add(self.view.testKeySetValidity, True,
                             priority=GObject.PRIORITY_DEFAULT)

        else:
            self.log.error("The specified key is invalid!")
            GObject.idle_add(self.view.testKeySetValidity, False,
                             priority=GObject.PRIORITY_DEFAULT)

        GObject.idle_add(self.view.testKeyUpdateSpinnerState, 0,
                         priority=GObject.PRIORITY_DEFAULT)

    def projectsTreeviewSelection_changed_cb(self, selection):
        (model, treeiter) = selection.get_selected()

        if treeiter is not None:
            (projectPath, projectName) = self._getSelectedProject()

            self.log.debug("Selected project: '{0}' (path: {1})".format(projectName, projectPath))

            self.selectedProject = Project.loadProject(self.workspace, projectPath)

            self._refreshProjectProperties()

            self.view.projectsDuplicateButton.set_sensitive(True)
            self.view.projectsDeleteButton.set_sensitive(True)
            self.view.projectsExportButton.set_sensitive(True)
            self.view.projectsConfigureButton.set_sensitive(True)

        else:
            self.selectedProject = None
            self._refreshProjectProperties()

            self.view.projectsDuplicateButton.set_sensitive(False)
            self.view.projectsDeleteButton.set_sensitive(False)
            self.view.projectsExportButton.set_sensitive(False)
            self.view.projectsConfigureButton.set_sensitive(False)

    def _refreshProjectProperties(self):
        propsProjectName = ""
        propsDate = None
        propsSymbols = ""
        propsMessages = ""

        if self.selectedProject:
            props = self.selectedProject.getProperties()
            propsProjectName = props['name'].getCurrentValue()
            propsDate = props['date'].getCurrentValue()
            propsSymbols = props['symbols'].getCurrentValue()
            propsMessages = props['messages'].getCurrentValue()

        self.view.updateProjectProperties(name=propsProjectName,
                                          date=propsDate,
                                          symbols=propsSymbols,
                                          messages=propsMessages)

    def _getSelectedProject(self):
        (model, treeiter) = self.view.projectsTreeviewSelection.get_selected()
        projectPath = model[treeiter][0]
        projectName = model[treeiter][1]

        return (projectPath, projectName)

    def projectsImportButton_clicked_cb(self, button):
        self.log.debug("Import project")

        controller = ProjectImportController(self.mainController, parent=self.view.workspaceConfigurationDialog)
        controller.run()

        self.view.refreshProjectList()

    def projectsExportButton_clicked_cb(self, button):
        (projectPath, projectName) = self._getSelectedProject()

        self.log.debug("Export project")

        controller = ProjectExportController(self.mainController,
                                             parent=self.view.workspaceConfigurationDialog,
                                             project=self.selectedProject)
        controller.run()

    def projectsDuplicateButton_clicked_cb(self, button):
        self.log.debug("Duplicate project")

        (projectPath, projectName) = self._getSelectedProject()

        response = self.view.showDuplicateProjectDialog(projectName)

        if response == 1:
            project = self.selectedProject
            cloneName = self.view.cloneProjectNameEntry.get_text()

            self.log.info("User validated to clone the project, new name: '{0}'".format(cloneName))

            project.cloneProjectTo(self.workspace, cloneName)

            self.selectedProject = None
            self.view.refreshProjectList()
            self.mainController.updateListOfAvailableProjects()

        self.view.workspaceConfigurationCloneProject.hide()

    def cloneProjectNameEntry_changed_cb(self, entry):
        if len(entry.get_text()) == 0:
            self.view.cloneProjectApplyButton.set_sensitive(False)
        else:
            self.view.cloneProjectApplyButton.set_sensitive(True)

    def projectsDeleteButton_clicked_cb(self, button):
        (projectPath, projectName) = self._getSelectedProject()

        questionMsg = _("Are you sure to delete the project \"{0}\" from the current workspace?").format(projectName)

        dialog = Gtk.MessageDialog(self.view.workspaceConfigurationDialog,
                                   Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
                                   Gtk.MessageType.WARNING,
                                   Gtk.ButtonsType.NONE,
                                   questionMsg)

        dialog.format_secondary_text(_("If delete the project, your project files will be permanently lost."))

        dialog.add_button(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)
        dialog.add_button(Gtk.STOCK_DELETE, Gtk.ResponseType.YES)
        dialog.set_default_response(Gtk.ResponseType.CANCEL)

        response = dialog.run()

        if response == Gtk.ResponseType.YES:
            self.log.info("User confirmed to delete the current project.")

            self.selectedProject.deleteProject(self.workspace)
            self.selectedProject = None

            # Finally, refresh project list in Netzob's main window
            # and in the "Workspace Configuration" dialog
            self.view.projectsTreeviewSelection.unselect_all()
            self.view.refreshProjectList()
            self.mainController.updateListOfAvailableProjects()

        dialog.destroy()

    def projectsTreeview_button_press_event_cb(self, treeView, event):
        if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 3:

            selection = treeView.get_selection()

            # Select the row on which user clicked
            try:
                (selectedPath, selectedColumn, x, y) = treeView.get_path_at_pos(event.x, event.y)
                if selectedPath:
                    selection.unselect_all()
                    selection.select_path(selectedPath)

                    self.view.popup.popup(None, None, None, None, event.button, event.time)
                return True
            except:
                return False

    def projectsConfigureButton_clicked_cb(self, button):
        controller = ProjectPropertiesController(self.mainController,
                                                 parent=self.view.workspaceConfigurationDialog,
                                                 project=self.selectedProject)

        def _refreshProjectList(window):
            self.view.refreshProjectList()

        controller.connectDestroySignal(_refreshProjectList)
        controller.run()
