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
from netzob.UI.Vocabulary.Controllers.ResearchController import ResearchController
from netzob.UI.Vocabulary.Controllers.FilterMessagesController import FilterMessagesController
from netzob.UI.Vocabulary.Controllers.MessageTableController import MessageTableController
from netzob.Common.SignalsManager import SignalsManager
from netzob.Common.Type.TypeConvertor import TypeConvertor
from netzob.UI.Vocabulary.Controllers.MessagesDistributionController import MessagesDistributionController
from netzob.UI.Common.Controllers.MoveMessageController import MoveMessageController
from netzob.UI.Vocabulary.Controllers.VariableDisplayerController import VariableDisplayerController


class VocabularyView(object):
    SYMBOLLISTSTORE_SELECTED_COLUMN = 0
    SYMBOLLISTSTORE_TOPLEVEL_COLUMN = 1
    SYMBOLLISTSTORE_NAME_COLUMN = 2
    SYMBOLLISTSTORE_MESSAGE_COLUMN = 3
    SYMBOLLISTSTORE_FIELD_COLUMN = 4
    SYMBOLLISTSTORE_ID_COLUMN = 5

    PROJECTPROPERTIESLISTSTORE_NAME_COLUMN = 0
    PROJECTPROPERTIESLISTSTORE_VALUE_COLUMN = 1
    PROJECTPROPERTIESLISTSTORE_EDITABLE_COLUMN = 2
    PROJECTPROPERTIESLISTSTORE_MODEL_COLUMN = 3

    SYMBOLPROPERTIESLISTSTORE_NAME_COLUMN = 0
    SYMBOLPROPERTIESLISTSTORE_VALUE_COLUMN = 1
    SYMBOLPROPERTIESLISTSTORE_EDITABLE_COLUMN = 2
    SYMBOLPROPERTIESLISTSTORE_MODEL_COLUMN = 3

    MESSAGEPROPERTIESLISTSTORE_NAME_COLUMN = 0
    MESSAGEPROPERTIESLISTSTORE_VALUE_COLUMN = 1
    MESSAGEPROPERTIESLISTSTORE_EDITABLE_COLUMN = 2
    MESSAGEPROPERTIESLISTSTORE_MODEL_COLUMN = 3

    FIELDPROPERTIESLISTSTORE_NAME_COLUMN = 0
    FIELDPROPERTIESLISTSTORE_VALUE_COLUMN = 1

    def __init__(self, controller):
        self.controller = controller
        self.netzob = self.controller.netzob
        self.builder = Gtk.Builder()
        self.builder.add_from_file(os.path.join(
            ResourcesConfiguration.getStaticResources(),
            "ui", "vocabulary",
            "vocabularyView.glade"))
        self._getObjects(self.builder, ["vocabularyPanel", "symbolListStore",
                                        "concatSymbolButton", "deleteSymbolButton", "newMessageList",
                                        "sequenceAlignmentButton",
                                        "partitioningForceButton",
                                        "partitioningSimpleButton",
                                        "partitioningSmoothButton",
                                        "partitioningResetButton",
                                        "messagesDistributionButton",
                                        "projectTreeview", "symbolTreeview", "messageTreeview", "fieldTreeview",
                                        "projectPropertiesListstore", "symbolPropertiesListstore", "messagePropertiesListstore",
                                        "messageTableBox", "symbolListTreeView",
                                        "symbolListTreeViewSelection", "messagesDistributionSymbolViewport", "messageTableBoxAndResearchBox"
                                        ])
        self._loadActionGroupUIDefinition()
        self.builder.connect_signals(self.controller)
        # Configure the drag and drop
        self.symbolListTreeView.drag_dest_set(Gtk.DestDefaults.ALL, [], Gdk.DragAction.MOVE)
        self.symbolListTreeView.connect("drag-data-received", self.drag_data_received_event)
        self.symbolListTreeView.connect("button-press-event", self.controller.symbolListTreeView_button_press_event_cb)
        self.symbolListTreeView.enable_model_drag_dest([], Gdk.DragAction.MOVE)
        self.symbolListTreeView.drag_dest_add_text_targets()

        # List of currently displayed message tables
        self.messageTableList = []
        self.selectedMessageTable = None
        # add the netzobBegin label attribute
        self.netzobBegin = None
        # add the researchBar
        self.researchController = ResearchController(self.controller)
        self.messageTableBoxAndResearchBox.pack_end(self.researchController._view.researchBar, False, False, 0)
        self.researchController._view.research_format.set_active(4)
        self.researchController.hide()

        # add the filterBar
        self.filterMessagesController = FilterMessagesController(self.controller)
        self.messageTableBoxAndResearchBox.pack_end(self.filterMessagesController._view.filterBar, False, False, 0)
        self.filterMessagesController.hide()
        self.registerSignalListeners()

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

    def _loadActionGroupUIDefinition(self):
        """Loads the action group and the UI definition of menu items
        . This method should only be called in the constructor"""
        # Load actions
        actionsBuilder = Gtk.Builder()
        actionsBuilder.add_from_file(os.path.join(
            ResourcesConfiguration.getStaticResources(),
            "ui", "vocabulary",
            "vocabularyActions.glade"))
        self._actionGroup = actionsBuilder.get_object("vocabularyActionGroup")
        actionsBuilder.connect_signals(self.controller)
        uiDefinitionFilePath = os.path.join(
            ResourcesConfiguration.getStaticResources(),
            "ui", "vocabulary",
            "vocabularyMenuToolbar.ui")
        with open(uiDefinitionFilePath, "r") as uiDefinitionFile:
            self._uiDefinition = uiDefinitionFile.read()

        # Attach actions from the vocabularyActionGroup to the small panel on top of symbols
        sequenceAlignmentAction = self._actionGroup.get_action('sequenceAlignment')
        self.sequenceAlignmentButton.set_related_action(sequenceAlignmentAction)

        partitioningForceAction = self._actionGroup.get_action('partitioningForce')
        self.partitioningForceButton.set_related_action(partitioningForceAction)

        partitioningSimpleAction = self._actionGroup.get_action('partitioningSimple')
        self.partitioningSimpleButton.set_related_action(partitioningSimpleAction)

        partitioningSmoothAction = self._actionGroup.get_action('partitioningSmooth')
        self.partitioningSmoothButton.set_related_action(partitioningSmoothAction)

        partitioningResetAction = self._actionGroup.get_action('partitioningReset')
        self.partitioningResetButton.set_related_action(partitioningResetAction)

        messagesDistributionAction = self._actionGroup.get_action('messagesDistribution')
        self.messagesDistributionButton.set_related_action(messagesDistributionAction)

    def _getObjects(self, builder, objectsList):
        for object in objectsList:
            setattr(self, object, builder.get_object(object))

    ## Mandatory view methods
    def getPanel(self):
        return self.vocabularyPanel

    # Return the actions
    def getActionGroup(self):
        return self._actionGroup

    # Return toolbar and menu
    def getMenuToolbarUIDefinition(self):
        return self._uiDefinition

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

    def drag_data_received_event(self, widget, drag_context, x, y, data, info, time):
        """Callback executed when the user drops
        some data in the treeview of symbols."""
        receivedData = data.get_text()

        if widget is None:
            logging.debug("No widget selected, cannot move the message")
            return

        # retrieve the drop row
        path, position = widget.get_dest_row_at_pos(x, y)
        targetSymbol = None
        if path is not None:
            layerID = widget.get_model()[path][VocabularyView.SYMBOLLISTSTORE_ID_COLUMN]
            if layerID is not None:
                targetField = self.controller.getCurrentProject().getVocabulary().getFieldByID(layerID)
                targetSymbol = targetField.getSymbol()
        if targetSymbol is None:
            return

        if receivedData is not None and len(receivedData) > 2:
            if targetSymbol is not None and receivedData[:2] == "m:":
                for msgID in receivedData[2:].split(","):
                    message = self.controller.getCurrentProject().getVocabulary().getMessageByID(msgID)
                    # verify if the target symbol's regex is valid according to the message
                    if message is not None:
                        if targetSymbol.getField().isRegexValidForMessage(message):
                            self.controller.moveMessage(message, targetSymbol)
                        else:
                            self.drag_receivedMessages(targetSymbol, message)
                        self.updateSelectedMessageTable()
                        self.updateLeftPanel()

    def drag_receivedMessages(self, targetSymbol, message):
        """Executed by the drop callback which has discovered
        some messages (identified by their ID) to be moved from their
        current symbol to the selected symbol"""
        if message is not None:
            moveMessageController = MoveMessageController(self.controller, [message], targetSymbol)
            moveMessageController.run()

    ## View manipulation methods
    def updateLeftPanel(self):
        self.updateSymbolList()
        self.updateSymbolListToolbar()
        self.updateProjectProperties()
        self.updateSymbolProperties()
        self.updateMessageProperties()

    ## Message Tables management
    def addMessageTable(self):
        """ Create a new message table and selects it"""
        messageTableController = MessageTableController(self)
        messageTable = messageTableController.view
        self.messageTableList.append(messageTable)
        self.setSelectedMessageTable(messageTable)
        self.messageTableBox.pack_start(messageTable.getPanel(), True, True, 0)

    def removeMessageTable(self, messageTable):
        self.messageTableBox.remove(messageTable.getPanel())
        messageTable.destroy()
        self.messageTableList = [mTable for mTable in self.messageTableList
                                 if mTable != messageTable]
        # Select a new table in messageTable was the selected message table
        if len(self.messageTableList) > 0:
            self.setSelectedMessageTable(self.messageTableList[0])

    def removeAllMessageTables(self):
        for child in self.messageTableBox.get_children():
            self.messageTableBox.remove(child)

        self.messageTableList = []

    def emptyMessageTableDisplayingSymbols(self, symbolList):
        toBeRemovedTables = [mTable for mTable in self.messageTableList
                             if mTable.getDisplayedField() in symbolList]
        for mTable in toBeRemovedTables:
            mTable.setDisplayedField(None)

    def updateSelectedMessageTable(self):
        if self.selectedMessageTable is not None:
            self.selectedMessageTable.update()

    def updateMessageTableDisplayingSymbols(self, symbolList):
        toBeUpdatedTables = [mTable for mTable in self.messageTableList
                             if mTable.getDisplayedField() in symbolList]
        for mTable in toBeUpdatedTables:
            mTable.update()

    def setSelectedMessageTable(self, selectedMessageTable):
        """Set provided message table as selected"""

        if selectedMessageTable == self.selectedMessageTable:
            return

        # Update appearance of old and new selected message table
        if self.selectedMessageTable is not None:
            self.selectedMessageTable.setSelected(False)

        # Update current selected message table and
        self.selectedMessageTable = selectedMessageTable
        self.selectedMessageTable.setSelected(True)

    def setDisplayedFieldInSelectedMessageTable(self, symbol):
        """Show the definition of provided symbol on the selected
        message table"""
        logging.debug("Update the displayed symbol in selected table message")

        # Open a message table if none is available
        if len(self.messageTableList) == 0:
            self.addMessageTable()

        # if a message table is selected we update its symbol
        self.selectedMessageTable.setDisplayedField(symbol)

    def getDisplayedFieldInSelectedMessageTable(self):
        if self.selectedMessageTable is None:
            return None
        else:
            return self.selectedMessageTable.displayedField

    ## Symbol List
    def updateSymbolList(self):
        """Updates the symbol list of the left panel, preserving the current
        selection"""
        # Retrieve symbols of the current project vocabulary (if one selected)
        layerList = []
        if self.getCurrentProject() is not None and self.getCurrentProject().getVocabulary() is not None:
            for symbol in self.getCurrentProject().getVocabulary().getSymbols():
                layerList.append(symbol.getField())

        checkedMessagesIDList = []
        for row in self.symbolListStore:
            if (row[self.SYMBOLLISTSTORE_SELECTED_COLUMN]):
                checkedMessagesIDList.append(row[self.SYMBOLLISTSTORE_ID_COLUMN])
        # Block selection changed handler
        self.symbolListTreeViewSelection.handler_block_by_func(self.controller.symbolListTreeViewSelection_changed_cb)
        self.symbolListStore.clear()
        for layer in layerList:
            pIter = self.addRowSymbolList(checkedMessagesIDList, layer.getName(),
                                          len(layer.getMessages()),
                                          len(layer.getExtendedFields()),
                                          str(layer.getID()))
            for fieldLayer in layer.getFieldLayers():
                self.addLayerRowSymbolList(pIter, checkedMessagesIDList, layer, fieldLayer)
        self.setSelectedSymbolFromSelectedMessageTable()
        self.symbolListTreeViewSelection.handler_unblock_by_func(self.controller.symbolListTreeViewSelection_changed_cb)

    def setSelectedSymbolFromSelectedMessageTable(self):
        if self.selectedMessageTable is None:
            self.setSelectedSymbol(None)
        else:
            messageTableSymbol = self.selectedMessageTable.displayedField
            self.setSelectedSymbol(messageTableSymbol)

    def addRowSymbolList(self, checkedMessagesIDList, name, message, field, symID):
        """Adds a row in the symbol list of left panel
        @type  selection: boolean
        @param selection: if selected symbol
        @type  name: string
        @param name: name of the symbol
        @type  message: string
        @param message: number of message in the symbol
        @type  field: string
        @param field: number of field in the symbol
        @type  image: string
        @param image: image of the lock button (freeze partitioning)"""
        i = self.symbolListStore.append(None)
        self.symbolListStore.set(i, self.SYMBOLLISTSTORE_SELECTED_COLUMN, (symID in checkedMessagesIDList))
        self.symbolListStore.set(i, self.SYMBOLLISTSTORE_TOPLEVEL_COLUMN, True)
        self.symbolListStore.set(i, self.SYMBOLLISTSTORE_NAME_COLUMN, name)
        self.symbolListStore.set(i, self.SYMBOLLISTSTORE_MESSAGE_COLUMN, message)
        self.symbolListStore.set(i, self.SYMBOLLISTSTORE_FIELD_COLUMN, field)
        self.symbolListStore.set(i, self.SYMBOLLISTSTORE_ID_COLUMN, symID)
        return i

    def addLayerRowSymbolList(self, parentIter, checkedMessagesIDList, symbol, fieldLayer):
        """Adds a layer row in the symbol list of left panel
        @type  parentIter: string
        @param parentIter: parent iter
        @type  selection: boolean
        @param selection: if selected symbol
        @type  name: fieldLayer
        @param name: the targeted fieldLayer
        """
        i = self.symbolListStore.append(parentIter)
        self.symbolListStore.set(i, self.SYMBOLLISTSTORE_SELECTED_COLUMN, (str(fieldLayer.getID()) in checkedMessagesIDList))
        self.symbolListStore.set(i, self.SYMBOLLISTSTORE_TOPLEVEL_COLUMN, False)
        self.symbolListStore.set(i, self.SYMBOLLISTSTORE_NAME_COLUMN, fieldLayer.getName())
        self.symbolListStore.set(i, self.SYMBOLLISTSTORE_MESSAGE_COLUMN, len(symbol.getMessages()))
        self.symbolListStore.set(i, self.SYMBOLLISTSTORE_FIELD_COLUMN, len(fieldLayer.getExtendedFields()))
        self.symbolListStore.set(i, self.SYMBOLLISTSTORE_ID_COLUMN, str(fieldLayer.getID()))
        # Add inner layers
        for innerFieldLayer in fieldLayer.getFieldLayers():
            self.addLayerRowSymbolList(i, checkedMessagesIDList, symbol, innerFieldLayer)

    def updateSymbolListToolbar(self):
        """Enables or disable buttons of the symbol list toolbar"""
        selectedSymbolsCount = self.countSelectedSymbols()
        self.concatSymbolButton.set_sensitive((selectedSymbolsCount >= 2))
        self.deleteSymbolButton.set_sensitive((selectedSymbolsCount >= 1))

        # We emit signals depending of the number of selected symbols
        if selectedSymbolsCount == 0:
            self.netzob.getSignalsManager().emitSignal(SignalsManager.SIG_SYMBOLS_NONE_CHECKED)
        elif selectedSymbolsCount == 1:
            self.netzob.getSignalsManager().emitSignal(SignalsManager.SIG_SYMBOLS_SINGLE_CHECKED)
        else:
            self.netzob.getSignalsManager().emitSignal(SignalsManager.SIG_SYMBOLS_MULTIPLE_CHECKED)

    def countSelectedSymbols(self):
        count = 0
        for row in self.symbolListStore:
            if row[self.SYMBOLLISTSTORE_SELECTED_COLUMN]:
                count += 1
        return count

    def getCheckedLayerList(self):
        if self.getCurrentProject() is None:
            return []
        currentVocabulary = self.getCurrentProject().getVocabulary()
        selectedLayerList = []
        for row in self.symbolListStore:
            if row[self.SYMBOLLISTSTORE_SELECTED_COLUMN]:
                layer_id = row[self.SYMBOLLISTSTORE_ID_COLUMN]
                layer = currentVocabulary.getFieldByID(layer_id)
                selectedLayerList.append(layer)
        return selectedLayerList

    def getCheckedSymbolList(self):
        if self.getCurrentProject() is None:
            return []
        currentVocabulary = self.getCurrentProject().getVocabulary()
        selectedSymbolList = []
        for row in self.symbolListStore:
            if row[self.SYMBOLLISTSTORE_SELECTED_COLUMN]:
                layer_id = row[self.SYMBOLLISTSTORE_ID_COLUMN]
                layer = currentVocabulary.getFieldByID(layer_id)
                if not layer.getSymbol() in selectedSymbolList:
                    selectedSymbolList.append(layer.getSymbol())
        return selectedSymbolList

    def setSelectedSymbol(self, symbol):
        selection = self.symbolListTreeView.get_selection()
        if symbol is None:
            selection.unselect_all()
        else:
            path = self.getSymbolPathInSymbolList(symbol)
            if path is not None:
                selection.select_path(path)

    def getSelectedSymbol(self):
        """Returns the selected symbol in the list of symbols"""
        currentVocabulary = self.getCurrentProject().getVocabulary()
        model, iter = self.symbolListTreeView.get_selection().get_selected()
        if iter is not None:
            symID = model[iter][self.SYMBOLLISTSTORE_ID_COLUMN]
            return currentVocabulary.getSymbolByID(symID)
        return None

    def getSelectedMessagesInSelectedMessageTable(self):
        if self.selectedMessageTable is not None:
            return self.selectedMessageTable.controller.getSelectedMessages()
        else:
            return None

    def getSymbolPathInSymbolList(self, symbol):
        symID = symbol.getID()
        for path, row in enumerate(self.symbolListStore):
            if row[self.SYMBOLLISTSTORE_ID_COLUMN] == symID:
                return path

    ## Properties panel
    def getProjectProperties(self):
        """Computes the set of properties
        on the current project, and displays them
        in the treeview"""
        properties = []
        project = self.getCurrentProject()
        if project is not None:
            properties = project.getProperties()
        return properties

    def updateProjectProperties(self):
        # clean store
        self.projectPropertiesListstore.clear()
        # get project properties
        properties = self.getProjectProperties()
        # add project properties
        for prop in properties:
            line = self.projectPropertiesListstore.append()
            self.projectPropertiesListstore.set(line, self.PROJECTPROPERTIESLISTSTORE_NAME_COLUMN, prop.getName())
            self.projectPropertiesListstore.set(line, self.PROJECTPROPERTIESLISTSTORE_VALUE_COLUMN, str(prop.getCurrentValue()))
            #self.projectPropertiesListstore.set(line, self.PROJECTPROPERTIESLISTSTORE_EDITABLE_COLUMN, prop.isEditable)
            self.projectPropertiesListstore.set(line, self.PROJECTPROPERTIESLISTSTORE_EDITABLE_COLUMN, False)
            if prop.getPossibleValues() != []:
                liststore_possibleValues = Gtk.ListStore(str)
                for val in prop.getPossibleValues():
                    liststore_possibleValues.append([val])
                self.projectPropertiesListstore.set(line, self.PROJECTPROPERTIESLISTSTORE_MODEL_COLUMN, liststore_possibleValues)

    def getSymbolProperties(self):
        """Create the list of properties associated
        with the current displayed symbol"""
        properties = []
        symbol = self.getDisplayedFieldInSelectedMessageTable()
        if symbol is not None:
            properties = symbol.getProperties()
        return properties

    def updateSymbolProperties(self):
        # clean store
        self.symbolPropertiesListstore.clear()
        # get symbol properties
        properties = self.getSymbolProperties()
#        # add symbol properties
        for prop in properties:
            line = self.symbolPropertiesListstore.append()
            self.symbolPropertiesListstore.set(line, self.SYMBOLPROPERTIESLISTSTORE_NAME_COLUMN, prop.getName())
            self.symbolPropertiesListstore.set(line, self.SYMBOLPROPERTIESLISTSTORE_VALUE_COLUMN, str(prop.getCurrentValue()))
            self.symbolPropertiesListstore.set(line, self.SYMBOLPROPERTIESLISTSTORE_EDITABLE_COLUMN, prop.isEditable)
            if prop.getPossibleValues() != []:
                liststore_possibleValues = Gtk.ListStore(str)
                for val in prop.getPossibleValues():
                    liststore_possibleValues.append([val])
                self.symbolPropertiesListstore.set(line, self.SYMBOLPROPERTIESLISTSTORE_MODEL_COLUMN, liststore_possibleValues)

        # update the variable definition
        self.updateSymbolVariableDefinition()

    def updateSymbolVariableDefinition(self):
        currentSymbol = self.getDisplayedFieldInSelectedMessageTable()
        if currentSymbol is not None:
            variableDisplayerController = VariableDisplayerController(self, currentSymbol, True)
            variableDisplayerController.run(self.messagesDistributionSymbolViewport)

    def getMessageProperties(self):
        """Retrieve the current first selected message (in the
        selected TableMessage) and return its properties"""
        properties = []
        messages = self.getSelectedMessagesInSelectedMessageTable()
        if messages is not None and len(messages) > 0:
            message = messages[0]
            if message is not None:
                properties = message.getProperties()
        return properties

    def updateMessageProperties(self):
        # clean store
        self.messagePropertiesListstore.clear()
        # get message properties
        properties = self.getMessageProperties()
        # add message properties
        for prop in properties:
            line = self.messagePropertiesListstore.append()
            self.messagePropertiesListstore.set(line, self.MESSAGEPROPERTIESLISTSTORE_NAME_COLUMN, prop.getName())
            self.messagePropertiesListstore.set(line, self.MESSAGEPROPERTIESLISTSTORE_VALUE_COLUMN, str(prop.getCurrentValue()))
            self.messagePropertiesListstore.set(line, self.MESSAGEPROPERTIESLISTSTORE_EDITABLE_COLUMN, prop.isEditable)
            if prop.getPossibleValues() != []:
                liststore_possibleValues = Gtk.ListStore(str)
                for val in prop.getPossibleValues():
                    liststore_possibleValues.append([val])
                self.messagePropertiesListstore.set(line, self.MESSAGEPROPERTIESLISTSTORE_MODEL_COLUMN, liststore_possibleValues)

    def getCurrentProject(self):
        return self.controller.netzob.getCurrentProject()

    def getDisplayedField(self):
        if self.selectedMessageTable is None:
            return None
        return self.selectedMessageTable.getDisplayedField()
