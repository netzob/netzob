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
import os

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+
from gi.repository import Gtk, Gdk

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.ResourcesConfiguration import ResourcesConfiguration


class WorkspaceConfigurationView(object):

    def __init__(self, controller, parent=None):
        self.builder = Gtk.Builder()
        self.builder.add_from_file(os.path.join(ResourcesConfiguration.getStaticResources(),
                                                "ui",
                                                "workspaceConfigurationDialog.glade"))
        self._getObjects(self.builder,
                         ["workspaceConfigurationDialog",
                          "advancedLoggingCombobox",
                          "advancedBugreportingEntry",
                          "advancedBugreportingCheckbox",
                          "advancedBugreportingTestkey",
                          "advancedBugreportingTestkeySpinner",
                          "projectsTreestore1",
                          "projectCurrentName",
                          "projectCurrentDate",
                          "projectCurrentSymbolsCount",
                          "projectCurrentMessagesCount",
                          "projectsDuplicateButton",
                          "projectsDeleteButton",
                          "projectsExportButton",
                          "projectsTreeviewSelection",
                          "projectsConfigureButton",
                          "workspaceConfigurationActionGroup",
                          ])

        self.controller = controller
        self.workspaceConfigurationDialog.set_transient_for(parent)

        # Set combobox to the configured log level
        model = self.advancedLoggingCombobox.get_model()
        treeIter = model.get_iter_first()
        while treeIter is not None:
            if model[treeIter][0] == self.controller._loggingConfiguration.getLoggingLevel():
                self.advancedLoggingCombobox.set_active_iter(treeIter)
                break
            treeIter = model.iter_next(treeIter)

        # Update API key
        key = ResourcesConfiguration.extractAPIKeyDefinitionFromLocalFile()
        self.advancedBugreportingEntry.set_text(key or "")

        # Set the 'enable bug reporting' toggle
        enableBugReporting = controller.workspace.enableBugReporting
        self.advancedBugreportingCheckbox.set_active(enableBugReporting)
        self.refreshEnableBugReporting(enableBugReporting)

        # Updating the "Defined projects" list
        self.refreshProjectList()

        # Getting the popup menu
        self.uiManager = Gtk.UIManager()
        self.uiManager.insert_action_group(self.workspaceConfigurationActionGroup)
        self.uiManager.add_ui_from_file(os.path.join(ResourcesConfiguration.getStaticResources(), "ui", "workspaceConfigurationPopupMenu.ui"))
        self.popup = self.uiManager.get_widget("/PopupMenu")

        # Finally, connect signals to the controller
        self.builder.connect_signals(self.controller)

    def refreshEnableBugReporting(self, enable):
        if enable:
            self.advancedBugreportingEntry.set_sensitive(True)
            self.advancedBugreportingTestkey.set_sensitive(True)
            self.advancedBugreportingEntry.set_sensitive(True)

            testkey = len(self.advancedBugreportingEntry.get_text()) > 0
            self.advancedBugreportingTestkey.set_sensitive(testkey)
        else:
            self.advancedBugreportingEntry.set_sensitive(False)
            self.advancedBugreportingTestkey.set_sensitive(False)

    def testKeySetValidity(self, validity):
        icon = Gtk.STOCK_APPLY

        if validity is False:
            icon = Gtk.STOCK_DIALOG_WARNING

        self.advancedBugreportingEntry.set_icon_from_stock(Gtk.EntryIconPosition.SECONDARY, icon)

    def testKeyUpdateSpinnerState(self, state):
        spinner = self.advancedBugreportingTestkeySpinner

        if state == 0:
            spinner.stop()
            spinner.hide()

        elif state == 1:
            spinner.show()
            spinner.start()

    def changeTestButtonSensitivity(self, sensitivity):
        self.advancedBugreportingTestkey.set_sensitive(sensitivity)

    def _getObjects(self, builder, objectsList):
        for obj in objectsList:
            setattr(self, obj, builder.get_object(obj))

    def run(self):
        self.workspaceConfigurationDialog.show_all()
        self.advancedBugreportingTestkeySpinner.hide()

    def destroy(self):
        self.workspaceConfigurationDialog.destroy()

    def updateProjectProperties(self, name, date, symbols, messages):
        currentDate = ""

        if date:
            currentDate = date.strftime("%c")

        self.projectCurrentName.set_text(name)
        self.projectCurrentDate.set_text(currentDate)
        self.projectCurrentSymbolsCount.set_text(str(symbols))
        self.projectCurrentMessagesCount.set_text(str(messages))

    def refreshProjectList(self):
        workspace = self.controller.mainController.getCurrentWorkspace()

        self.projectsTreestore1.clear()
        for project in workspace.getProjects():
            self.projectsTreestore1.append([project.getPath(),
                                            project.getName(),
                                            project.getDescription()])

    def showDuplicateProjectDialog(self, origProjectName):
        self._getObjects(self.builder,
                         ["workspaceConfigurationCloneProject",
                          "cloneProjectNameEntry",
                          "cloneProjectApplyButton",
                          ])

        dialog = self.workspaceConfigurationCloneProject
        dialog.show_all()
        dialog.set_transient_for(self.workspaceConfigurationDialog)

        self.cloneProjectNameEntry.set_text(origProjectName)

        return dialog.run()
