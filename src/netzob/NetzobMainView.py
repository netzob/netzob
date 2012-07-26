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
from netzob.UI.Vocabulary.Controllers.NewVocabularyController import NewVocabularyController
from netzob.UI.Simulator.UISimulator import UISimulator
from netzob.UI.Grammar.UIGrammarInference import UIGrammarInference


class NetzobMainView(object):
    """Netzob main window view"""

    VOCABULARY_INFERENCE_VIEW = "vocabulary-inference-view"
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
        self.perspectiveDict = {}
        self.currentPerspectiveMergeID = None
        self.currentPerspectiveActionGroup = None
        self.currentPerspectivePanel = None
        self.loadBaseMenuBarAndToolbar()
        self._registerPerspectives()

    def _getObjects(self, builder, objectsList):
        for object in objectsList:
            setattr(self, object, builder.get_object(object))

    def run(self):
        self.mainWindow.show()

    def _registerPerspectives(self):
        self.registerPerspective(self.VOCABULARY_INFERENCE_VIEW,
                                 "Vocabulary Inference",
                                 NewVocabularyController)
        self.registerPerspective(self.GRAMMAR_INFERENCE_VIEW,
                                 "Grammar Inference",
                                 UIGrammarInference)
        self.registerPerspective(self.TRAFFIC_SIMULATOR_VIEW,
                                 "Simulator",
                                 UISimulator)
        self.switchPerspective(self.VOCABULARY_INFERENCE_VIEW)
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

    def updateProject(self):
        """Update the view when the current project has changed"""
        for key in self.perspectiveDict:
            (pDescription, pController) = self.perspectiveDict[key]
            if pController is not None:
                pController.restart()

    def updateSwitchProjectMenu(self, listOfProjectsNameAndPath):
        """Update the menu"""
        switchProjectMenu = self.uiManager.get_widget("/mainMenuBar/fileMenu/switchProject").get_submenu()

        # Update the list of project
        for i in switchProjectMenu.get_children():
            switchProjectMenu.remove(i)

        for (projectName, projectPath) in listOfProjectsNameAndPath:
#            actionSwitchOtherProject = Gtk.Action("FileMenu", "File", None, None)
            projectEntry = Gtk.MenuItem(projectName)
            projectEntry.connect("activate", self.switchProject_cb, projectPath)
            switchProjectMenu.append(projectEntry)

        switchProjectMenu.show_all()
        self.uiManager.get_widget("/mainMenuBar/fileMenu/switchProject").set_sensitive(True)

    def switchProject_cb(self, widget, projectPath):
        """Callback executed when the user
        click on project to load it."""
        if projectPath != None:
            self.controller.switchProject(projectPath)
