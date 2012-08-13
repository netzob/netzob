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

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+
from gi.repository import Gtk, Gdk
import gi
from netzob.UI.Vocabulary.Controllers.MessageTableController import MessageTableController
from netzob.Common.Type.TypeConvertor import TypeConvertor
from netzob.UI.Vocabulary.Controllers.MessagesDistributionController import MessagesDistributionController
from netzob.UI.Common.Controllers.MoveMessageController import MoveMessageController
gi.require_version('Gtk', '3.0')
from gi.repository import GObject
from collections import OrderedDict

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.ResourcesConfiguration import ResourcesConfiguration
from netzob.UI.Vocabulary.Controllers.NewResearchController import NewResearchController


class NewVocabularyView(object):
    SYMBOLLISTSTORE_SELECTED_COLUMN = 0
    SYMBOLLISTSTORE_NAME_COLUMN = 1
    SYMBOLLISTSTORE_MESSAGE_COLUMN = 2
    SYMBOLLISTSTORE_FIELD_COLUMN = 3
    SYMBOLLISTSTORE_ID_COLUMN = 4

    PROJECTPROPERTIESLISTSTORE_NAME_COLUMN = 0
    PROJECTPROPERTIESLISTSTORE_VALUE_COLUMN = 1

    SYMBOLPROPERTIESLISTSTORE_NAME_COLUMN = 0
    SYMBOLPROPERTIESLISTSTORE_VALUE_COLUMN = 1

    MESSAGEPROPERTIESLISTSTORE_NAME_COLUMN = 0
    MESSAGEPROPERTIESLISTSTORE_VALUE_COLUMN = 1

    FIELDPROPERTIESLISTSTORE_NAME_COLUMN = 0
    FIELDPROPERTIESLISTSTORE_VALUE_COLUMN = 1

    def __init__(self, controller):
        self.controller = controller
        self.netzob = self.controller.netzob
        self.builder = Gtk.Builder()
        self.builder.add_from_file(os.path.join(
            ResourcesConfiguration.getStaticResources(),
            "ui",
            "VocabularyView.glade"))
        self._getObjects(self.builder, ["vocabularyPanel", "symbolListStore",
                                        "renameSymbolButton", "concatSymbolButton", "deleteSymbolButton", "newMessageList",
                                        "projectTreeview", "symbolTreeview", "messageTreeview", "fieldTreeview",
                                        "projectPropertiesListstore", "symbolPropertiesListstore", "messagePropertiesListstore",
                                        "fieldPropertiesListstore", "messageTableBox", "symbolListTreeView",
                                        "symbolListTreeViewSelection", "messagesDistributionSymbolViewport"
                                        ])
        self._loadActionGroupUIDefinition()
        self.builder.connect_signals(self.controller)
        # Configure the drag and drop
        self.symbolListTreeView.drag_dest_set(Gtk.DestDefaults.ALL, [], Gdk.DragAction.MOVE)
        self.symbolListTreeView.connect('drag-data-received', self.drag_data_received_event)
        self.symbolListTreeView.enable_model_drag_dest([], Gdk.DragAction.MOVE)
        self.symbolListTreeView.drag_dest_add_text_targets()
        # List of currently displayed message tables
        self.messageTableList = []
        self.selectedMessageTable = None
        # add the netzobBegin label attribute
        self.netzobBegin = None
        # add the researchBar
        self.researchController = NewResearchController(self.controller)
        self.messageTableBox.pack_end(self.researchController._view.researchBar, False, False, 0)
        self.researchController._view.research_format.set_active(4)
        self.researchController.hide()

    def _loadActionGroupUIDefinition(self):
        """Loads the action group and the UI definition of menu items
        . This method should only be called in the constructor"""
        # Load actions
        actionsBuilder = Gtk.Builder()
        actionsBuilder.add_from_file(os.path.join(
            ResourcesConfiguration.getStaticResources(),
            "ui",
            "vocabularyActions.glade"))
        self._actionGroup = actionsBuilder.get_object("vocabularyActionGroup")
        actionsBuilder.connect_signals(self.controller)
        uiDefinitionFilePath = os.path.join(
            ResourcesConfiguration.getStaticResources(),
            "ui",
            "vocabularyMenuToolbar.ui")
        with open(uiDefinitionFilePath, "r") as uiDefinitionFile:
            self._uiDefinition = uiDefinitionFile.read()

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

    def drag_data_received_event(self, widget, drag_context, x, y, data, info, time):
        """Callback executed when the user drops
        some data in the treeview of symbols."""
        receivedData = data.get_text()

        # retrieve the drop row
        path, position = widget.get_dest_row_at_pos(x, y)
        targetSymbol = None
        if path is not None:
            symbolID = widget.get_model()[path][NewVocabularyView.SYMBOLLISTSTORE_ID_COLUMN]
            if symbolID is not None:
                targetSymbol = self.controller.getCurrentProject().getVocabulary().getSymbolByID(symbolID)

        if targetSymbol is None:
            return

        if receivedData is not None and len(receivedData) > 2:
            if targetSymbol is not None and receivedData[:2] == "m:":
                for msgID in receivedData[2:].split(","):
                    message = self.controller.getCurrentProject().getVocabulary().getMessageByID(msgID)
                    # verify if the target symbol's regex is valid according to the message
                    if message is not None:
                        if targetSymbol.isRegexValidForMessage(message):
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
            targetSymbol.addMessage(message)
            moveMessageController = MoveMessageController(self.controller, message, targetSymbol)
            moveMessageController.run()

    ## View manipulation methods
    def updateLeftPanel(self):
        self.updateSymbolList()
        self.updateSymbolListToolbar()
        self.updateProjectProperties()
        self.updateSymbolProperties()
        self.updateMessageProperties()
        self.updateFieldProperties()

    ## Message Tables management
    def addMessageTable(self):
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
                             if mTable.getDisplayedSymbol() in symbolList]
        for mTable in toBeRemovedTables:
            mTable.setDisplayedSymbol(None)

    def updateSelectedMessageTable(self):
        if self.selectedMessageTable is not None:
            self.selectedMessageTable.update()

    def updateMessageTableDisplayingSymbols(self, symbolList):
        toBeUpdatedTables = [mTable for mTable in self.messageTableList
                             if mTable.getDisplayedSymbol() in symbolList]
        for mTable in toBeUpdatedTables:
            mTable.update()

    def setSelectedMessageTable(self, selectedMessageTable):
        # Update appearance of old and new selected message table
        if self.selectedMessageTable is not None:
            self.selectedMessageTable.setSelected(False)
        selectedMessageTable.setSelected(True)
        # Update current selected message table and
        self.selectedMessageTable = selectedMessageTable
        self.setSelectedSymbolFromSelectedMessageTable()

    def setDisplayedSymbolInSelectedMessageTable(self, symbol):
        if len(self.messageTableList) == 0:
            self.addMessageTable()
            self.setSelectedMessageTable(self.messageTableList[0])

        if self.selectedMessageTable is None:
            return
        if symbol != self.selectedMessageTable.displayedSymbol:
            self.selectedMessageTable.setDisplayedSymbol(symbol)

    def getDisplayedSymbolInSelectedMessageTable(self):
        if self.selectedMessageTable is None:
            return None
        else:
            return self.selectedMessageTable.displayedSymbol

    ## Symbol List
    def updateSymbolList(self):
        """Updates the symbol list of the left panel, preserving the current
        selection"""
        # Retrieve symbols of the current project vocabulary (if one selected)
        symbolList = []
        if self.getCurrentProject() is not None and self.getCurrentProject().getVocabulary() is not None:
            symbolList.extend(self.getCurrentProject().getVocabulary().getSymbols())

        checkedMessagesIDList = []
        for row in self.symbolListStore:
            if (row[self.SYMBOLLISTSTORE_SELECTED_COLUMN]):
                checkedMessagesIDList.append(row[self.SYMBOLLISTSTORE_ID_COLUMN])
        # Block selection changed handler
        self.symbolListTreeViewSelection.handler_block_by_func(self.controller.symbolListTreeViewSelection_changed_cb)
        self.symbolListStore.clear()
        for sym in symbolList:
            self.addRowSymbolList(checkedMessagesIDList, sym.getName(),
                                  len(sym.getMessages()),
                                  len(sym.getFields()),
                                  str(sym.getID()))
        self.setSelectedSymbolFromSelectedMessageTable()
        self.symbolListTreeViewSelection.handler_unblock_by_func(self.controller.symbolListTreeViewSelection_changed_cb)

    def setSelectedSymbolFromSelectedMessageTable(self):
        if self.selectedMessageTable is None:
            self.setSelectedSymbol(None)
        else:
            messageTableSymbol = self.selectedMessageTable.displayedSymbol
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
        i = self.symbolListStore.append()
        self.symbolListStore.set(i, self.SYMBOLLISTSTORE_SELECTED_COLUMN, (symID in checkedMessagesIDList))
        self.symbolListStore.set(i, self.SYMBOLLISTSTORE_NAME_COLUMN, name)
        self.symbolListStore.set(i, self.SYMBOLLISTSTORE_MESSAGE_COLUMN, message)
        self.symbolListStore.set(i, self.SYMBOLLISTSTORE_FIELD_COLUMN, field)
        self.symbolListStore.set(i, self.SYMBOLLISTSTORE_ID_COLUMN, symID)

    def updateSymbolListToolbar(self):
        """Enables or disable buttons of the symbol list toolbar"""
        selectedSymbolsCount = self.countSelectedSymbols()
        self.renameSymbolButton.set_sensitive((selectedSymbolsCount == 1))
        self.concatSymbolButton.set_sensitive((selectedSymbolsCount >= 2))
        self.deleteSymbolButton.set_sensitive((selectedSymbolsCount >= 1))

    def countSelectedSymbols(self):
        count = 0
        for row in self.symbolListStore:
            if row[self.SYMBOLLISTSTORE_SELECTED_COLUMN]:
                count += 1
        return count

    def getCheckedSymbolList(self):
        currentVocabulary = self.getCurrentProject().getVocabulary()
        selectedSymbolList = []
        for row in self.symbolListStore:
            if row[self.SYMBOLLISTSTORE_SELECTED_COLUMN]:
                symID = row[self.SYMBOLLISTSTORE_ID_COLUMN]
                sym = currentVocabulary.getSymbolByID(symID)
                selectedSymbolList.append(sym)
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
        currentVocabulary = self.getCurrentProject().getVocabulary()
        model, iter = self.symbolListTreeView.get_selection().get_selected()
        if iter is not None:
            symID = model[iter][self.SYMBOLLISTSTORE_ID_COLUMN]
            return currentVocabulary.getSymbolByID(symID)

    def getSelectedMessageInSelectedMessageTable(self):
        if self.selectedMessageTable is not None:
            return self.selectedMessageTable.controller.getSelectedMessage()

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
        project = self.getCurrentProject()
        properties = OrderedDict()
        if project != None:
            configuration = project.getConfiguration()
            properties = OrderedDict()
            properties['workspace'] = self.controller.netzob.getCurrentWorkspace().getPath()
            properties['name'] = project.getName()
            properties['date'] = project.getCreationDate()
            properties['symbols'] = len(project.getVocabulary().getSymbols())
            properties['messages'] = len(project.getVocabulary().getMessages())
            field = 0
            for sym in project.getVocabulary().getSymbols():
                field = field + len(sym.getFields())
            properties['fields'] = field
            properties[configuration.VOCABULARY_GLOBAL_FORMAT] = configuration.getVocabularyInferenceParameter(configuration.VOCABULARY_GLOBAL_FORMAT)
            properties[configuration.VOCABULARY_GLOBAL_UNITSIZE] = configuration.getVocabularyInferenceParameter(configuration.VOCABULARY_GLOBAL_UNITSIZE)
            properties[configuration.VOCABULARY_GLOBAL_SIGN] = configuration.getVocabularyInferenceParameter(configuration.VOCABULARY_GLOBAL_SIGN)
            properties[configuration.VOCABULARY_GLOBAL_ENDIANESS] = configuration.getVocabularyInferenceParameter(configuration.VOCABULARY_GLOBAL_ENDIANESS)
        return properties

    # TODO
    def updateProjectProperties(self):
        # clean store
        self.projectPropertiesListstore.clear()
        # get project properties
        properties = self.getProjectProperties()
        # add project properties
        for key in properties:
            line = self.projectPropertiesListstore.append()
            self.projectPropertiesListstore.set(line, self.PROJECTPROPERTIESLISTSTORE_NAME_COLUMN, key)
            self.projectPropertiesListstore.set(line, self.PROJECTPROPERTIESLISTSTORE_VALUE_COLUMN, str(properties[key]))

    def getSymbolProperties(self):
        """Create the list of properties associated
        with the current displayed symbol"""
        symbol = self.getDisplayedSymbolInSelectedMessageTable()
        properties = OrderedDict()
        if symbol != None:
            properties['name'] = symbol.getName()
            properties['messages'] = len(symbol.getMessages())
            properties['fields'] = len(symbol.getFields())
            minMsgSize = None
            maxMsgSize = 0
            avgMsgSize = 0
            if len(symbol.getMessages()) > 0:
                for m in symbol.getMessages():
                    s = len(m.getData()) * 2
                    if minMsgSize is None or s < minMsgSize:
                        minMsgSize = s
                    if maxMsgSize is None or s > maxMsgSize:
                        maxMsgSize = s
                    avgMsgSize += s
                avgMsgSize = avgMsgSize / len(symbol.getMessages())
            properties['avg msg size (bytes)'] = avgMsgSize
            properties['min msg size (bytes)'] = minMsgSize
            properties['max msg size (bytes)'] = maxMsgSize
        return properties

    def updateSymbolProperties(self):
        # clean store
        self.symbolPropertiesListstore.clear()
        # get symbol properties
        properties = self.getSymbolProperties()
        # add symbol properties
        for key in properties:
            line = self.symbolPropertiesListstore.append()
            self.symbolPropertiesListstore.set(line, self.SYMBOLPROPERTIESLISTSTORE_NAME_COLUMN, key)
            self.symbolPropertiesListstore.set(line, self.SYMBOLPROPERTIESLISTSTORE_VALUE_COLUMN, str(properties[key]))

        # update the message distribution graphic
        #Todo when ploting in GTK3 will be available
#        self.updateSymbolPropertiesMessagesDistribution()

    def updateSymbolPropertiesMessagesDistribution(self):
        currentSymbol = self.getDisplayedSymbolInSelectedMessageTable()
        if currentSymbol is not None:
            messagesDistributionController = MessagesDistributionController([])
            messagesDistributionController.run(self.messagesDistributionSymbolViewport)

    def getMessageProperties(self):
        """Retrieve the current selected message (in the selected TableMessage)
        and return its properties"""
        message = self.getSelectedMessageInSelectedMessageTable()
        if message is not None:
            properties = OrderedDict()
            if message != None:
                for p in message.getProperties():
                    properties[p[0]] = str(p[2])
            return properties
        else:
            return []

    def updateMessageProperties(self):
        # clean store
        self.messagePropertiesListstore.clear()
        # get message properties
        properties = self.getMessageProperties()
        # add message properties
        for key in properties:
            line = self.messagePropertiesListstore.append()
            self.messagePropertiesListstore.set(line, self.MESSAGEPROPERTIESLISTSTORE_NAME_COLUMN, key)
            self.messagePropertiesListstore.set(line, self.MESSAGEPROPERTIESLISTSTORE_VALUE_COLUMN, str(properties[key]))

    def getFieldProperties(self):
        return []
#        field = self.focusMessageTable.getFocusField()#TODO METHOD
#        properties = OrderedDict()
#        if field != None:
#            properties['name'] = field.getName()
#            # ++CODE HERE++
#            # ADD PROPERTIES FROM message
#            # ADD LIST [ regex, 4 format variable, idea? ]
#        return properties

    def updateFieldProperties(self):
        # clean store
        self.fieldPropertiesListstore.clear()
        # get field properties
        properties = self.getFieldProperties()
        # add field properties
        for key in properties:
            line = self.fieldPropertiesListstore.append()
            self.fieldPropertiesListstore.set(line, 0, key)
            self.fieldPropertiesListstore.set(line, 1, str(properties[key]))

    def getCurrentProject(self):
        return self.controller.netzob.getCurrentProject()

    def getDisplayedSymbol(self):
        return self.selectedMessageTable.getDisplayedSymbol()
