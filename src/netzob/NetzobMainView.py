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
import os
import logging

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+
from gi.repository import Gtk, Gdk
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GObject

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.UI.NetzobWidgets import addNetzobIconsToDefaultFactory
from netzob.Common.ResourcesConfiguration import ResourcesConfiguration
from netzob.Common.SignalsManager import SignalsManager
from netzob.UI.Vocabulary.Controllers.VocabularyController import VocabularyController
from netzob.UI.Grammar.Controllers.GrammarController import GrammarController
from netzob.UI.Simulator.Controllers.SimulatorController import SimulatorController


class NetzobMainView(object):
    """Netzob main window view"""

    GRAMMAR_INFERENCE_VIEW = "grammar-inference-view"
    TRAFFIC_SIMULATOR_VIEW = "traffic-simulator-view"

    def __init__(self, controller):
        addNetzobIconsToDefaultFactory()
        self.log = logging.getLogger(__name__)
        # Load main window definition
        self.builder = Gtk.Builder()
        self.builder.add_from_file(os.path.join(ResourcesConfiguration.getStaticResources(), "ui", "mainWindow.glade"))
        self._getObjects(self.builder, ["mainWindow", "toolbarBox", "mainBox", "perspectiveListStore", "perspectiveComboBox"])
        self.controller = controller
        self.builder.connect_signals(self.controller)
        self.perspectiveDict = {}
        self.currentPerspectiveMergeID = None
        self.currentPerspectiveActionGroup = None
        self.currentPerspectivePanel = None
        self.loadBaseMenuBarAndToolbar()
        self.registerSignalListeners()

    def registerSignalListeners(self):
        # Register signal processing on toolbar elements
        signalManager = self.controller.getSignalsManager()
        if signalManager is None:
            self.log.warning("No signal manager has been found.")
            return

        signalManager.attach(self.projectStatusHasChanged_cb, [SignalsManager.SIG_PROJECT_OPEN, SignalsManager.SIG_PROJECT_CLOSE])

    def projectStatusHasChanged_cb(self, signal):
        """projectStatusHasChanged_cb:
        Callback executed when a signal is emitted."""

        if signal == SignalsManager.SIG_PROJECT_OPEN:
            self.mainActionGroup.get_action('saveProject').set_sensitive(True)
            self.mainActionGroup.get_action('exportProject').set_sensitive(True)
        elif signal == SignalsManager.SIG_PROJECT_CLOSE:
            self.mainActionGroup.get_action('saveProject').set_sensitive(False)
            self.mainActionGroup.get_action('exportProject').set_sensitive(False)

    def _getObjects(self, builder, objectsList):
        for object in objectsList:
            setattr(self, object, builder.get_object(object))

    def run(self):
        self.mainWindow.show()

    def registerPerspectives(self):
        self.registerPerspective(VocabularyController.PERSPECTIVE_ID,
                                 _("Vocabulary Inference"),
                                 VocabularyController)
        self.registerPerspective(self.GRAMMAR_INFERENCE_VIEW,
                                 _("Grammar Inference"),
                                 GrammarController)
        self.registerPerspective(self.TRAFFIC_SIMULATOR_VIEW,
                                 _("Simulator"),
                                 SimulatorController)
        # Useless
#        self.switchPerspective(self.VOCABULARY_INFERENCE_VIEW)
        self.perspectiveComboBox.set_active(0)

    def loadBaseMenuBarAndToolbar(self):
        # Load actions
        mainActionsBuilder = Gtk.Builder()
        mainActionsBuilder.add_from_file(os.path.join(
            ResourcesConfiguration.getStaticResources(),
            "ui",
            "mainActions.glade"))
        mainActionsBuilder.connect_signals(self.controller)
        self.mainActionGroup = mainActionsBuilder.get_object("mainActionGroup")
        # Load menu bar and toolbar UI definitions
        self.uiManager = Gtk.UIManager()
        self.uiManager.insert_action_group(self.mainActionGroup)
        self.uiManager.add_ui_from_file(os.path.join(
            ResourcesConfiguration.getStaticResources(),
            "ui",
            "mainMenuToolbar.ui"))
        mainToolbar = self.uiManager.get_widget("/mainToolbar")
        mainToolbar.set_icon_size(Gtk.IconSize.LARGE_TOOLBAR)
        self.setPrimaryToolbarStyle(mainToolbar)
        self.setMenuBar(self.uiManager.get_widget("/mainMenuBar"))
        self.setToolbar(mainToolbar)

        # Add accel group to window
        self.mainWindow.add_accel_group(self.uiManager.get_accel_group())

    def resetMainWindow(self):
        self.log.debug("Resetting main window to its original state.")
        # Reset menu and toolbar
        if self.currentPerspectiveActionGroup is not None:
            self.uiManager.remove_action_group(self.currentPerspectiveActionGroup)
            self.currentPerspectiveActionGroup = None
        if self.currentPerspectiveMergeID is not None:
            self.uiManager.remove_ui(self.currentPerspectiveMergeID)
            self.currentPerspectiveMergeID = None
        # Reset central panel
        if self.currentPerspectivePanel is not None:
            self.mainBox.remove(self.currentPerspectivePanel)
            self.currentPerspectivePanel = None

    def registerPerspective(self, perspectiveCode, perspectiveDescription, perspectiveControllerClass):
        self.perspectiveDict[perspectiveCode] = (perspectiveDescription, perspectiveControllerClass(self.controller))
        self.perspectiveListStore.append([perspectiveCode, perspectiveDescription])

    def getRegisteredPerspectives(self):
        """registeredPerspectives:
                Returns a dictionary which contains the list of registered perspectives"""
        return self.perspectiveDict

    def setPrimaryToolbarStyle(self, toolbar):
        """Make toolbar a GTK primary toolbar. In most GTK themes,
        primary toolbars have a specific background.
        @type  toolbar: string
        @param toolbar: The toolbar name"""
        styleContext = toolbar.get_style_context()
        styleContext.add_class("primary-toolbar")

    def setToolbar(self, toolbar):
        self.positionElementInBox(self.toolbarBox, 0, toolbar, True, True)

    def setMenuBar(self, menuBar):
        self.positionElementInBox(self.mainBox, 0, menuBar)

    def setCentralPanel(self, panel):
        self.positionElementInBox(self.mainBox, 2, panel, True, True)

    def positionElementInBox(self, box, position, element, expand=False, fill=False, padding=0):
        box.pack_start(element, expand, fill, 0)
        box.reorder_child(element, position)

    def switchPerspective(self, newPerspectiveCode):
        """@type  newPerspective: string
        @param newPerspective: Switch for the view.
        Value available: "vocabulary", "grammar" and "traffic"."""
        # Reset base menu and toolbar
        self.resetMainWindow()
        self.log.debug("Setting perspective ID {0}".format(newPerspectiveCode))
        perspective = self.perspectiveDict[newPerspectiveCode][1]
        # Switch central panel
        self.currentPerspectivePanel = perspective.view.getPanel()
        self.setCentralPanel(self.currentPerspectivePanel)
        # Add action group to UI Manager
        self.currentPerpectiveActionGroup = perspective.view.getActionGroup()
        self.uiManager.insert_action_group(self.currentPerpectiveActionGroup)
        # Merge UI definition into UI Manager
        self.currentPerspectiveMergeID = self.uiManager.add_ui_from_string(
            perspective.view.getMenuToolbarUIDefinition())
        # Activate it
        perspective.activate()

    def currentProjectHasChanged(self):
        """Update the view when the current project has changed"""
        for key in self.perspectiveDict:
            (pDescription, pController) = self.perspectiveDict[key]
            if pController is not None:
                logging.debug("Restarting the perspective {0}".format(pDescription))
                pController.restart()
        # Update the switch project menu (to update the toggled element)
        self.controller.updateListOfAvailableProjects()

    def currentWorkspaceHasChanged(self):
        """currentWorkspaceHasChanged:
        Execute the operations which must be done when
        the current workspace has changed :
        - Update the view,
        - Save the new workspace."""
        if self.controller.getCurrentWorkspace() is not None:
            ResourcesConfiguration.generateUserFile(self.controller.getCurrentWorkspace().getPath(), ResourcesConfiguration.extractAPIKeyDefinitionFromLocalFile())

        self.currentProjectHasChanged()
        self.updateSwitchProjectMenu(self.controller.getCurrentWorkspace().getNameOfProjects())

    def updateSwitchProjectMenu(self, listOfProjectsNameAndPath):
        """Update the menu"""
        switchProjectMenu = self.uiManager.get_widget("/mainMenuBar/fileMenu/switchProject").get_submenu()

        if len(listOfProjectsNameAndPath) == 0:
            self.uiManager.get_widget("/mainMenuBar/fileMenu/switchProject").set_sensitive(False)
            return

        # Update the list of project
        for i in switchProjectMenu.get_children():
            switchProjectMenu.remove(i)

        # Retrieves the Name of the current project
        currentProjectName = None
        currentProject = self.controller.getCurrentProject()
        if currentProject is not None:
            currentProjectName = currentProject.getName()
            currentProjectPath = currentProject.getPath()

        for (projectName, projectPath) in listOfProjectsNameAndPath:
            projectLoaded = False
            # Set toggled the current project
            if currentProjectName is not None:
                if (currentProjectName == projectName and currentProjectPath == projectPath):
                    projectLoaded = True
                else:
                    projectLoaded = False

            projectEntry = Gtk.CheckMenuItem(projectName)
            projectEntry.set_active(projectLoaded)
            projectEntry.connect("activate", self.controller.switchProject_cb, projectPath)
            switchProjectMenu.append(projectEntry)

        switchProjectMenu.show_all()
        self.uiManager.get_widget("/mainMenuBar/fileMenu/switchProject").set_sensitive(True)

    def updateListExporterPlugins(self, pluginsExtensions):
        """Update the menu"""
        exportersMenu = self.uiManager.get_widget("/mainMenuBar/fileMenu/exportProject").get_submenu()

        # Update the list of exporters
        for i in exportersMenu.get_children():
            exportersMenu.remove(i)

        # Add XML export
        exporterEntry = Gtk.MenuItem(_("XML"))
        exporterEntry.connect("activate", self.controller.xmlExportProject_activate_cb)
        exportersMenu.append(exporterEntry)

        # Add human readable export
        exporterEntry = Gtk.MenuItem(_("Human readable"))
        exporterEntry.connect("activate", self.controller.rawExportProject_activate_cb)
        exportersMenu.append(exporterEntry)

        # Add plugin specific exports
        for pluginExtension in pluginsExtensions:
            pluginEntry = Gtk.MenuItem(pluginExtension.menuText)
            pluginEntry.connect("activate", pluginExtension.executeAction)
            exportersMenu.append(pluginEntry)
        exportersMenu.show_all()

    def offerToSaveCurrentProject(self):
        """Display a message dialog which
        offer to the user to save the current project"""

        projectName = self.controller.getCurrentProject().getName()

        questionMsg = _("Save the changes to the project \"{0}\" before closing?").format(projectName)

        md = Gtk.MessageDialog(self.mainWindow,
                               Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
                               Gtk.MessageType.WARNING,
                               Gtk.ButtonsType.NONE,
                               questionMsg)

        md.format_secondary_text(_("If you don't save, changes will be permanently lost."))

        md.add_button(_("Close _Without Saving"), Gtk.ResponseType.NO)
        md.add_button(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)
        md.add_button(Gtk.STOCK_SAVE, Gtk.ResponseType.YES)
        md.set_default_response(Gtk.ResponseType.YES)

        result = md.run()
        md.destroy()

        return result
