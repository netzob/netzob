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
from collections import OrderedDict

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.ResourcesConfiguration import ResourcesConfiguration
from netzob.Common.SignalsManager import SignalsManager
from netzob.UI.Common.Controllers.MoveMessageController import MoveMessageController
from netzob.UI.Vocabulary.Controllers.ResearchController import ResearchController
from netzob.UI.Vocabulary.Controllers.FilterMessagesController import FilterMessagesController


class VocabularyView(object):
    PROJECTPROPERTIESLISTSTORE_NAME_COLUMN = 0
    PROJECTPROPERTIESLISTSTORE_VALUE_COLUMN = 1
    PROJECTPROPERTIESLISTSTORE_EDITABLE_COLUMN = 2
    PROJECTPROPERTIESLISTSTORE_MODEL_COLUMN = 3

    # Symbols
    SYMBOLLISTSTORE_SELECTED_COLUMN = 0
    SYMBOLLISTSTORE_TOPLEVEL_COLUMN = 1
    SYMBOLLISTSTORE_NAME_COLUMN = 2
    SYMBOLLISTSTORE_MESSAGE_COLUMN = 3
    SYMBOLLISTSTORE_FIELD_COLUMN = 4
    SYMBOLLISTSTORE_ID_COLUMN = 5

    SYMBOLPROPERTIESLISTSTORE_NAME_COLUMN = 0
    SYMBOLPROPERTIESLISTSTORE_VALUE_COLUMN = 1
    SYMBOLPROPERTIESLISTSTORE_EDITABLE_COLUMN = 2
    SYMBOLPROPERTIESLISTSTORE_MODEL_COLUMN = 3

    # Sessions
    SESSIONLISTSTORE_SELECTED_COLUMN = 0
    SESSIONLISTSTORE_TOPLEVEL_COLUMN = 1
    SESSIONLISTSTORE_NAME_COLUMN = 2
    SESSIONLISTSTORE_MESSAGE_COLUMN = 3
    SESSIONLISTSTORE_ID_COLUMN = 4

    SESSIONPROPERTIESLISTSTORE_NAME_COLUMN = 0
    SESSIONPROPERTIESLISTSTORE_VALUE_COLUMN = 1
    SESSIONPROPERTIESLISTSTORE_EDITABLE_COLUMN = 2
    SESSIONPROPERTIESLISTSTORE_MODEL_COLUMN = 3

    # Sequences
    SEQUENCELISTSTORE_SELECTED_COLUMN = 0
    SEQUENCELISTSTORE_TOPLEVEL_COLUMN = 1
    SEQUENCELISTSTORE_NAME_COLUMN = 2
    SEQUENCELISTSTORE_MESSAGE_COLUMN = 3
    SEQUENCELISTSTORE_ID_COLUMN = 4

    SEQUENCEPROPERTIESLISTSTORE_NAME_COLUMN = 0
    SEQUENCEPROPERTIESLISTSTORE_VALUE_COLUMN = 1
    SEQUENCEPROPERTIESLISTSTORE_EDITABLE_COLUMN = 2
    SEQUENCEPROPERTIESLISTSTORE_MODEL_COLUMN = 3

    # Messages
    MESSAGEPROPERTIESLISTSTORE_NAME_COLUMN = 0
    MESSAGEPROPERTIESLISTSTORE_VALUE_COLUMN = 1
    MESSAGEPROPERTIESLISTSTORE_EDITABLE_COLUMN = 2
    MESSAGEPROPERTIESLISTSTORE_MODEL_COLUMN = 3

    # Fields
    FIELDPROPERTIESLISTSTORE_NAME_COLUMN = 0
    FIELDPROPERTIESLISTSTORE_VALUE_COLUMN = 1

    def __init__(self, controller):
        self.controller = controller
        self.netzob = self.controller.netzob
        self.actionsBuilder = Gtk.Builder()
        self.builder = Gtk.Builder()
        self.builder.add_from_file(os.path.join(
            ResourcesConfiguration.getStaticResources(),
            "ui", "vocabulary",
            "vocabularyView.glade"))
        self._getObjects(self.builder, ["vocabularyPanel", "projectTreeview", "projectPropertiesListstore",
                                        "messageTableBox", "messageTableBoxAndResearchBox",
                                        "messagePropertiesListstore",
                                        # Symbols
                                        "symbolListStore", "concatSymbolButton", "deleteSymbolButton",
                                        "sequenceAlignmentButton", "partitioningForceButton", "partitioningSimpleButton",
                                        "partitioningSmoothButton", "partitioningResetButton", "messagesDistributionButton",
                                        "symbolTreeview", "symbolPropertiesListstore", "symbolListTreeView",
                                        "symbolListTreeViewSelection", "messagesDistributionSymbolViewport",
                                        "messageTableBoxAndResearchBox", "messagePropertiesListstore",
                                        "selectAllSymbolsButton", "unselectAllSymbolsButton", "createSymbolButton",
                                        "newSymbolTableButton", "symbolToggleCellRenderer",
                                        # Sessions
                                        "sessionListStore", "sessionTreeview", "sessionPropertiesListstore", "sessionListTreeView",
                                        "sessionListTreeViewSelection",
                                        "selectAllSessionsButton", "unselectAllSessionsButton", "createSessionButton",
                                        "concatSessionButton", "deleteSessionButton", "newSessionTableButton", "sessionToggleCellRenderer",
                                        # Sequences
                                        "sequenceListStore", "sequenceTreeview", "sequencePropertiesListstore", "sequenceListTreeView",
                                        "sequenceListTreeViewSelection",
                                        "selectAllSequencesButton", "unselectAllSequencesButton", "createSequenceButton",
                                        "concatSequenceButton", "deleteSequenceButton", "newSequenceTableButton", "sequenceToggleCellRenderer"
                                        ])
        self._loadActionGroupUIDefinition()
        self.builder.connect_signals(self.controller)

        # Add the researchBar
        self.researchController = ResearchController(self.controller)
        self.messageTableBoxAndResearchBox.pack_end(self.researchController._view.researchBar, False, False, 0)
        self.researchController._view.research_format.set_active(4)
        self.researchController.hide()

        # Add the filterBar
        self.filterMessagesController = FilterMessagesController(self.controller)
        self.messageTableBoxAndResearchBox.pack_end(self.filterMessagesController._view.filterBar, False, False, 0)
        self.filterMessagesController.hide()
        self.registerSignalListeners()

        self.registerSignalListeners()

    def _loadActionGroupUIDefinition(self):
        """Loads the action group and the UI definition of menu items
        . This method should only be called in the constructor"""
        # Load vocabulary actions
        self.actionsBuilder.add_from_file(os.path.join(
            ResourcesConfiguration.getStaticResources(),
            "ui", "vocabulary",
            "vocabularyActions.glade"))
        self.actionsBuilder.connect_signals(self.controller)
        self._actionGroup = self.actionsBuilder.get_object("vocabularyActionGroup")

        # Load UI definition
        uiDefinitionFilePath = os.path.join(
            ResourcesConfiguration.getStaticResources(),
            "ui", "vocabulary",
            "vocabularyMenuToolbar.ui")
        with open(uiDefinitionFilePath, "r") as uiDefinitionFile:
            self._uiDefinition = uiDefinitionFile.read()

    def loadSymbolActionGroupUIDefinition(self):
        """Loads the action group and the UI definition of menu items
        . This method should only be called in the constructor"""
        # Load symbol actions
        self.actionsBuilder.add_from_file(os.path.join(
            ResourcesConfiguration.getStaticResources(),
            "ui", "vocabulary",
            "symbolActions.glade"))
        self.actionsBuilder.connect_signals(self.controller.symbolController)

        # Trick to remove actions from symbolActionGroup and to add them to the main vocabularyActionGroup
        aSymbolActionGroup = self.actionsBuilder.get_object("symbolActionGroup")
        for action in aSymbolActionGroup.list_actions():
            aSymbolActionGroup.remove_action(action)
            self._actionGroup.add_action(action)
        self._actionGroup = self.actionsBuilder.get_object("vocabularyActionGroup")

        # Attach actions from the vocabularyActionGroup to the small panel on top of symbols
        sequenceAlignmentAction = self._actionGroup.get_action('sequenceAlignment')
        partitioningForceAction = self._actionGroup.get_action('partitioningForce')
        partitioningSimpleAction = self._actionGroup.get_action('partitioningSimple')
        partitioningSmoothAction = self._actionGroup.get_action('partitioningSmooth')
        partitioningResetAction = self._actionGroup.get_action('partitioningReset')
        messagesDistributionAction = self._actionGroup.get_action('messagesDistribution')
        selectAllSymbolsAction = self._actionGroup.get_action('selectAllSymbols')
        unselectAllSymbolsAction = self._actionGroup.get_action('unselectAllSymbols')
        createSymbolAction = self._actionGroup.get_action('createSymbol')
        concatSymbolAction = self._actionGroup.get_action('concatSymbol')
        deleteSymbolAction = self._actionGroup.get_action('deleteSymbol')
        newSymbolTableAction = self._actionGroup.get_action('newSymbolTable')

        self.sequenceAlignmentButton.set_related_action(sequenceAlignmentAction)
        self.partitioningForceButton.set_related_action(partitioningForceAction)
        self.partitioningSimpleButton.set_related_action(partitioningSimpleAction)
        self.partitioningSmoothButton.set_related_action(partitioningSmoothAction)
        self.partitioningResetButton.set_related_action(partitioningResetAction)
        self.messagesDistributionButton.set_related_action(messagesDistributionAction)
        self.selectAllSymbolsButton.set_related_action(selectAllSymbolsAction)
        self.unselectAllSymbolsButton.set_related_action(unselectAllSymbolsAction)
        self.createSymbolButton.set_related_action(createSymbolAction)
        self.concatSymbolButton.set_related_action(concatSymbolAction)
        self.deleteSymbolButton.set_related_action(deleteSymbolAction)
        self.newSymbolTableButton.set_related_action(newSymbolTableAction)

        self.symbolToggleCellRenderer.connect("toggled", self.controller.symbolController.toggleSymbolCellRenderer_toggled_cb)
        self.symbolListTreeViewSelection.connect("changed", self.controller.symbolController.symbolListTreeViewSelection_changed_cb)

    def loadSessionActionGroupUIDefinition(self):
        """Loads the action group and the UI definition of menu items
        . This method should only be called in the constructor"""
        # Load session actions
        self.actionsBuilder.add_from_file(os.path.join(
            ResourcesConfiguration.getStaticResources(),
            "ui", "vocabulary",
            "sessionActions.glade"))
        self.actionsBuilder.connect_signals(self.controller.sessionController)

        # Trick to remove actions from sessionActionGroup and to add them to the main vocabularyActionGroup
        aSessionActionGroup = self.actionsBuilder.get_object("sessionActionGroup")
        for action in aSessionActionGroup.list_actions():
            aSessionActionGroup.remove_action(action)
            self._actionGroup.add_action(action)
        self._actionGroup = self.actionsBuilder.get_object("vocabularyActionGroup")

        # Attach actions from the vocabularyActionGroup to the small panel on top of sessions
        selectAllSessionsAction = self._actionGroup.get_action('selectAllSessions')
        unselectAllSessionsAction = self._actionGroup.get_action('unselectAllSessions')
        createSessionAction = self._actionGroup.get_action('createSession')
        concatSessionAction = self._actionGroup.get_action('concatSession')
        deleteSessionAction = self._actionGroup.get_action('deleteSession')
        newSessionTableAction = self._actionGroup.get_action('newSessionTable')

        self.selectAllSessionsButton.set_related_action(selectAllSessionsAction)
        self.unselectAllSessionsButton.set_related_action(unselectAllSessionsAction)
        self.createSessionButton.set_related_action(createSessionAction)
        self.concatSessionButton.set_related_action(concatSessionAction)
        self.deleteSessionButton.set_related_action(deleteSessionAction)
        self.newSessionTableButton.set_related_action(newSessionTableAction)

        self.sessionToggleCellRenderer.connect("toggled", self.controller.sessionController.toggleSessionCellRenderer_toggled_cb)
        self.sessionListTreeViewSelection.connect("changed", self.controller.sessionController.sessionListTreeViewSelection_changed_cb)

    def loadSequenceActionGroupUIDefinition(self):
        """Loads the action group and the UI definition of menu items
        . This method should only be called in the constructor"""
        # Load sequence actions
        self.actionsBuilder.add_from_file(os.path.join(
            ResourcesConfiguration.getStaticResources(),
            "ui", "vocabulary",
            "sequenceActions.glade"))
        self.actionsBuilder.connect_signals(self.controller.sequenceController)

        # Trick to remove actions from sequenceActionGroup and to add them to the main vocabularyActionGroup
        aSequenceActionGroup = self.actionsBuilder.get_object("sequenceActionGroup")
        for action in aSequenceActionGroup.list_actions():
            aSequenceActionGroup.remove_action(action)
            self._actionGroup.add_action(action)
        self._actionGroup = self.actionsBuilder.get_object("vocabularyActionGroup")

        # Attach actions from the vocabularyActionGroup to the small panel on top of sequences
        selectAllSequencesAction = self._actionGroup.get_action('selectAllSequences')
        unselectAllSequencesAction = self._actionGroup.get_action('unselectAllSequences')
        createSequenceAction = self._actionGroup.get_action('createSequence')
        concatSequenceAction = self._actionGroup.get_action('concatSequence')
        deleteSequenceAction = self._actionGroup.get_action('deleteSequence')
        newSequenceTableAction = self._actionGroup.get_action('newSequenceTable')

        self.selectAllSequencesButton.set_related_action(selectAllSequencesAction)
        self.unselectAllSequencesButton.set_related_action(unselectAllSequencesAction)
        self.createSequenceButton.set_related_action(createSequenceAction)
        self.concatSequenceButton.set_related_action(concatSequenceAction)
        self.deleteSequenceButton.set_related_action(deleteSequenceAction)
        self.newSequenceTableButton.set_related_action(newSequenceTableAction)

        self.sequenceToggleCellRenderer.connect("toggled", self.controller.sequenceController.toggleSequenceCellRenderer_toggled_cb)
        self.sequenceListTreeViewSelection.connect("changed", self.controller.sequenceController.sequenceListTreeViewSelection_changed_cb)

    def _getObjects(self, builder, objectsList):
        for object in objectsList:
            setattr(self, object, builder.get_object(object))

    def registerSignalListeners(self):
        # Register signal processing on toolbar elements
        signalManager = self.netzob.getSignalsManager()
        if signalManager is None:
            self.log.warning("No signal manager has been found.")
            return

        signalManager.attach(self.projectStatusHasChanged_cb, [SignalsManager.SIG_PROJECT_OPEN, SignalsManager.SIG_PROJECT_CLOSE])
        signalManager.attach(self.symbolCheckedHasChanged_cb, [SignalsManager.SIG_SYMBOLS_NONE_CHECKED, SignalsManager.SIG_SYMBOLS_SINGLE_CHECKED, SignalsManager.SIG_SYMBOLS_MULTIPLE_CHECKED])
        signalManager.attach(self.symbolSelectionHasChanged_cb, [SignalsManager.SIG_SYMBOLS_NO_SELECTION, SignalsManager.SIG_SYMBOLS_SINGLE_SELECTION, SignalsManager.SIG_SYMBOLS_MULTIPLE_SELECTION])
        signalManager.attach(self.fieldSelectionHasChanged_cb, [SignalsManager.SIG_FIELDS_NO_SELECTION, SignalsManager.SIG_FIELDS_SINGLE_SELECTION, SignalsManager.SIG_FIELDS_MULTIPLE_SELECTION])
        signalManager.attach(self.messageSelectionHasChanged_cb, [SignalsManager.SIG_MESSAGES_NO_SELECTION, SignalsManager.SIG_MESSAGES_SINGLE_SELECTION, SignalsManager.SIG_MESSAGES_MULTIPLE_SELECTION])


    # Synchronize sensitivity of buttons based on authorized actions
    def projectStatusHasChanged_cb(self, signal):
        """projectStatusHasChanged_cb:
        Callback executed when a signal is emitted."""

        actions = ["importMessagesFromFile",
                   "captureMessages",
                   "relationsViewer",
                   "searchMenu",
                   "searchText",
                   "variableTable",
                   "automaticToolMenu",
                   "manualToolMenu",
                   ]

        if signal == SignalsManager.SIG_PROJECT_OPEN:
            for action in actions:
                self._actionGroup.get_action(action).set_sensitive(True)

        elif signal == SignalsManager.SIG_PROJECT_CLOSE:
            for action in actions:
                self._actionGroup.get_action(action).set_sensitive(False)

    def messageSelectionHasChanged_cb(self, signal):
        """messageSelectionHasChanged_cb:
            Callback executed when none, single or multiple messages are selected"""
        if signal == SignalsManager.SIG_MESSAGES_NO_SELECTION:
            self._actionGroup.get_action('moveMessagesToOtherSymbol').set_sensitive(False)
            self._actionGroup.get_action('deleteMessages').set_sensitive(False)

        elif signal == SignalsManager.SIG_MESSAGES_SINGLE_SELECTION:
            self._actionGroup.get_action('moveMessagesToOtherSymbol').set_sensitive(True)
            self._actionGroup.get_action('deleteMessages').set_sensitive(True)

        elif signal == SignalsManager.SIG_MESSAGES_MULTIPLE_SELECTION:
            self._actionGroup.get_action('moveMessagesToOtherSymbol').set_sensitive(True)
            self._actionGroup.get_action('deleteMessages').set_sensitive(True)

    def fieldSelectionHasChanged_cb(self, signal):
        """fieldSelectionHasChanhed_cb:
            Callback executed when none, single or multiple fields are selected."""
        if signal == SignalsManager.SIG_FIELDS_NO_SELECTION:
            self._actionGroup.get_action('concatField').set_sensitive(False)
            self._actionGroup.get_action('split').set_sensitive(False)
            self._actionGroup.get_action('editVariable').set_sensitive(False)
        elif signal == SignalsManager.SIG_FIELDS_SINGLE_SELECTION:
            self._actionGroup.get_action('concatField').set_sensitive(False)
            self._actionGroup.get_action('split').set_sensitive(True)
            self._actionGroup.get_action('editVariable').set_sensitive(True)
        elif signal == SignalsManager.SIG_FIELDS_MULTIPLE_SELECTION:
            self._actionGroup.get_action('concatField').set_sensitive(True)
            self._actionGroup.get_action('split').set_sensitive(False)
            self._actionGroup.get_action('editVariable').set_sensitive(False)

    def symbolCheckedHasChanged_cb(self, signal):
        """symbolCheckedHasChanged_cb:
        callback executed when none, one or multiple symbols are checked."""
        if signal == SignalsManager.SIG_SYMBOLS_NONE_CHECKED:
            self._actionGroup.get_action('partitioningSimple').set_sensitive(False)
            self._actionGroup.get_action('partitioningSmooth').set_sensitive(False)
            self._actionGroup.get_action('partitioningReset').set_sensitive(False)
            self._actionGroup.get_action('editVariable').set_sensitive(False)
            self._actionGroup.get_action('environmentDep').set_sensitive(False)
            self._actionGroup.get_action('messagesDistribution').set_sensitive(False)
            self._actionGroup.get_action('partitioningForce').set_sensitive(False)
            self._actionGroup.get_action('sequenceAlignment').set_sensitive(False)
        elif signal == SignalsManager.SIG_SYMBOLS_SINGLE_CHECKED or signal == SignalsManager.SIG_SYMBOLS_MULTIPLE_CHECKED:
            self._actionGroup.get_action('partitioningSimple').set_sensitive(True)
            self._actionGroup.get_action('partitioningSmooth').set_sensitive(True)
            self._actionGroup.get_action('partitioningReset').set_sensitive(True)
            self._actionGroup.get_action('environmentDep').set_sensitive(True)
            self._actionGroup.get_action('messagesDistribution').set_sensitive(True)
            self._actionGroup.get_action('partitioningForce').set_sensitive(True)
            self._actionGroup.get_action('sequenceAlignment').set_sensitive(True)
            if signal == SignalsManager.SIG_SYMBOLS_SINGLE_CHECKED:
                self._actionGroup.get_action('editVariable').set_sensitive(False)

    def symbolSelectionHasChanged_cb(self, signal):
        """symbolSelectionHasChanged_cb:
        callback executed when none, one or multiple symbols are selected."""
        if signal == SignalsManager.SIG_SYMBOLS_NO_SELECTION or signal == SignalsManager.SIG_SYMBOLS_MULTIPLE_SELECTION:
            self._actionGroup.get_action('filterMessages').set_sensitive(False)
        elif signal == SignalsManager.SIG_SYMBOLS_SINGLE_SELECTION:
            self._actionGroup.get_action('filterMessages').set_sensitive(True)


    ## Mandatory view methods
    def getPanel(self):
        return self.vocabularyPanel

    # Return the actions
    def getActionGroup(self):
        return self._actionGroup

    # Return toolbar and menu
    def getMenuToolbarUIDefinition(self):
        return self._uiDefinition

    # Plugins update
    def updateListCapturerPlugins(self, pluginsExtensions):
        """Update the menu"""
        pluginMenu = self.netzob.view.uiManager.get_widget("/mainMenuBar/fileMenu/fileMenuAdditions/captureMessages").get_submenu()

        # Update the list of exporters
        for i in pluginMenu.get_children():
            pluginMenu.remove(i)

        for pluginExtension in pluginsExtensions:
            pluginEntry = Gtk.MenuItem(pluginExtension.menuText)
            pluginEntry.connect("activate", pluginExtension.executeAction, self)
            pluginMenu.append(pluginEntry)
        pluginMenu.show_all()
