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
from gettext import ngettext
import os
import uuid
import logging

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+
from gi.repository import Gtk, Gdk
import gi
gi.require_version('Gtk', '3.0')


#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.Plugins.NetzobPlugin import NetzobPlugin
from netzob.Common.Plugins.FileImporterPlugin import FileImporterPlugin
from netzob.Common.Type.TypeConvertor import TypeConvertor
from netzob.Common.Plugins.Extensions.CapturerMenuExtension import CapturerMenuExtension
from netzob.Common.SignalsManager import SignalsManager
from netzob.Common.ResourcesConfiguration import ResourcesConfiguration
from netzob.Common.Field import Field
from netzob.Common.Session import Session
from netzob.Common.Sequence import Sequence
from netzob.UI.Vocabulary.Controllers.SymbolTableController import SymbolTableController
from netzob.UI.Vocabulary.Controllers.SessionTableController import SessionTableController
from netzob.UI.Vocabulary.Controllers.SequenceTableController import SequenceTableController
from netzob.UI.Vocabulary.Controllers.RelationsController import RelationsController
from netzob.UI.Vocabulary.Controllers.EnvironmentDependenciesSearcherController import EnvironmentDependenciesSearcherController
from netzob.UI.Vocabulary.Views.VocabularyView import VocabularyView
from netzob.UI.Vocabulary.Views.SymbolTableView import SymbolTableView
from netzob.UI.Vocabulary.Views.SessionTableView import SessionTableView
from netzob.UI.Vocabulary.Views.SequenceTableView import SequenceTableView
from netzob.UI.Vocabulary.Controllers.SymbolController import SymbolController
from netzob.UI.Vocabulary.Controllers.SessionController import SessionController
from netzob.UI.Vocabulary.Controllers.SequenceController import SequenceController
from netzob.UI.Common.Controllers.MoveMessageController import MoveMessageController
from netzob.UI.Import.ImportFileChooserDialog import ImportFileChooserDialog
from netzob.UI.NetzobWidgets import NetzobQuestionMessage, NetzobErrorMessage, NetzobInfoMessage


#+----------------------------------------------
#| VocabularyController:
#|     GUI for vocabulary inference
#+----------------------------------------------
class VocabularyController(object):

    PERSPECTIVE_ID = "vocabulary-inference-view"

    def __init__(self, netzob):
        self.netzob = netzob
        self._view = VocabularyView(self)
        self.log = logging.getLogger(__name__)

        # List of currently displayed message tables
        self.messageTableList = []
        self.selectedMessageTable = None

        # Create symbol controller and connect signals
        self.symbolController = SymbolController(self)
        self._view.loadSymbolActionGroupUIDefinition()

        # Create session controller and connect signals
        self.sessionController = SessionController(self)
        self._view.loadSessionActionGroupUIDefinition()

        # Create sequence controller and connect signals
        self.sequenceController = SequenceController(self)
        self._view.loadSequenceActionGroupUIDefinition()

        # Configure the drag and drop
        self.view.symbolListTreeView.drag_dest_set(Gtk.DestDefaults.ALL, [], Gdk.DragAction.MOVE)
        self.view.symbolListTreeView.connect("drag-data-received", self.drag_data_received_event)
        self.view.symbolListTreeView.connect("button-press-event", self.symbolController.symbolListTreeView_button_press_event_cb)
        self.view.symbolListTreeView.enable_model_drag_dest([], Gdk.DragAction.MOVE)
        self.view.symbolListTreeView.drag_dest_add_text_targets()
        self.selectedMessagesToMove = None

        self.updateLeftPanel()

    @property
    def view(self):
        return self._view

    def activate(self):
        """Activate the perspective"""
        # Refresh list of available exporter plugins
        self.updateListOfCapturerPlugins()
        pass

    def restart(self):
        """Restart the view"""
        logging.debug("Restarting the vocabulary view")
        self.removeAllMessageTables()
        self.updateLeftPanel()

    def getSignalsManager(self):
        return self.netzob.getSignalsManager()

    def updateLeftPanel(self):
        self.updateProjectProperties()
        self.symbolController.updateLeftPanel()
        self.sessionController.updateLeftPanel()
        self.sequenceController.updateLeftPanel()


    # Project properties
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
        self.view.projectPropertiesListstore.clear()
        # get project properties
        properties = self.getProjectProperties()
        # add project properties
        for prop in properties:
            line = self.view.projectPropertiesListstore.append()
            self.view.projectPropertiesListstore.set(line, self.view.PROJECTPROPERTIESLISTSTORE_NAME_COLUMN, prop.getName())
            self.view.projectPropertiesListstore.set(line, self.view.PROJECTPROPERTIESLISTSTORE_VALUE_COLUMN, str(prop.getCurrentValue()))
            #self.view.projectPropertiesListstore.set(line, self.view.PROJECTPROPERTIESLISTSTORE_EDITABLE_COLUMN, prop.isEditable)
            self.view.projectPropertiesListstore.set(line, self.view.PROJECTPROPERTIESLISTSTORE_EDITABLE_COLUMN, False)
            if prop.getPossibleValues() != []:
                liststore_possibleValues = Gtk.ListStore(str)
                for val in prop.getPossibleValues():
                    liststore_possibleValues.append([val])
                self.view.projectPropertiesListstore.set(line, self.view.PROJECTPROPERTIESLISTSTORE_MODEL_COLUMN, liststore_possibleValues)

    def cellrenderer_project_props_changed_cb(self, cellrenderer, path, new_value):
        if isinstance(new_value, Gtk.TreeIter):  # a combo box entry has been selected
            liststore_possibleValues = cellrenderer.get_property('model')
            value = liststore_possibleValues[new_value][0]
        else:  # the cellrenderer entry has changed
            value = new_value

        # Identify the property name/value and reconstruct the associated setter
        name = self.view.projectPropertiesListstore[path][0]

        for prop in self.getCurrentProject().getProperties():
            if prop.getName() == name:
                prop.setCurrentValue(TypeConvertor.encodeGivenTypeToNetzobRaw(value, prop.getFormat()))
                break
        self.view.updateProjectProperties()


    # Plugins update
    def updateListOfCapturerPlugins(self):
        """Fetch the list of available capturer plugins, and provide
        them to its associated view"""
        pluginExtensions = NetzobPlugin.getLoadedPluginsExtension(CapturerMenuExtension)
        self.view.updateListCapturerPlugins(pluginExtensions)


    # Drag and drop of messages
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
                targetField = self.getCurrentProject().getVocabulary().getFieldByID(layerID)
                targetSymbol = targetField.getSymbol()
        if targetSymbol is None:
            return

        if receivedData is not None and len(receivedData) > 2:
            if targetSymbol is not None and receivedData[:2] == "m:":
                for msgID in receivedData[2:].split(","):
                    message = self.getCurrentProject().getVocabulary().getMessageByID(msgID)
                    # verify if the target symbol's regex is valid according to the message
                    if message is not None:
                        if targetSymbol.getField().isRegexValidForMessage(message):
                            self.moveMessage(message, targetSymbol)
                        else:
                            self.drag_receivedMessages(targetSymbol, message)
                        self.updateSelectedMessageTable()
                        self.updateLeftPanel()

    def drag_receivedMessages(self, targetSymbol, message):
        """Executed by the drop callback which has discovered
        some messages (identified by their ID) to be moved from their
        current symbol to the selected symbol"""
        if message is not None:
            moveMessageController = MoveMessageController(self, [message], targetSymbol)
            moveMessageController.run()


    # Actions on messages
    def moveMessagesToOtherSymbol_activate_cb(self, action):
        """Callback executed when the user clicks on the move
        button. It retrieves the selected message, and change the cursor
        to show that moving is in progress. The user needs to click on a symbol to
        select the target symbol"""
        if self.getCurrentProject() is None:
            NetzobErrorMessage(_("No project selected."))
            return
        selectedMessages = self.getSelectedMessagesInSelectedMessageTable()
        if selectedMessages is None or len(selectedMessages) == 0:
            NetzobErrorMessage(_("No selected message."))
            return

        self.selectedMessagesToMove = selectedMessages

        cursor = Gdk.Cursor.new(Gdk.CursorType.FLEUR)
        self.view.vocabularyPanel.get_root_window().set_cursor(cursor)

    def executeMoveTargetOperation(self, targetSymbol):
        """Execute the pending move operation on the specified symbol"""
        if self.selectedMessagesToMove is not None and len(self.selectedMessagesToMove) > 0:
            # drop selected messages
            for message in self.selectedMessagesToMove:
                if message is not None:
                    if targetSymbol.getField().isRegexValidForMessage(message):
                        self.moveMessage(message, targetSymbol)
                    else:
                        moveMessageController = MoveMessageController(self, self.selectedMessagesToMove, targetSymbol)
                        moveMessageController.run()
            self.removePendingMessagesToMove()
            self.updateSelectedMessageTable()
            self.updateLeftPanel()

    def moveMessage(self, message, targetSymbol):
        """Move the provided message in the specified symbol.
        Warning, this method do not consider the possible regex problems
        which needs to be addressed by a set of dedicated solutions"""
        if message is not None and targetSymbol is not None:
            sourceSymbolID = message.getSymbol().getID()
            sourceSymbol = self.getCurrentProject().getVocabulary().getSymbolByID(sourceSymbolID)
            sourceSymbol.removeMessage(message)
            targetSymbol.addMessage(message)

    def removePendingMessagesToMove(self):
        """Clean the pending messages the user wanted to move (using the button)."""
        cursor = Gdk.Cursor.new(Gdk.CursorType.ARROW)
        self.view.vocabularyPanel.get_root_window().set_cursor(cursor)
        self.selectedMessagesToMove = None

    def deleteMessages_activate_cb(self, action):
        if self.getCurrentProject() is None:
            NetzobErrorMessage(_("No project selected."))
            return
        selectedMessages = self.getSelectedMessagesInSelectedMessageTable()
        if selectedMessages == [] or selectedMessages is None:
            NetzobErrorMessage(_("No selected message."))
            return
        questionMsg = ngettext("Click yes to confirm the deletion of the selected message",
                               "Click yes to confirm the deletion of the selected messages",
                               len(selectedMessages))
        result = NetzobQuestionMessage(questionMsg)
        if result != Gtk.ResponseType.YES:
            return
        for message in selectedMessages:
            # Remove message from model
            self.netzob.getCurrentProject().getVocabulary().removeMessage(message)
            message.getSymbol().removeMessage(message)
        # Update view
        self.updateSelectedMessageTable()
        self.updateLeftPanel()

    def searchText_toggled_cb(self, action):
        """Callback executed when the user clicks
        on the research toggle button"""
        if self.getCurrentProject() is None:
            if action.get_active():
                NetzobErrorMessage(_("No project selected."))
            action.set_active(False)
            return
        if action.get_active():
            self._view.researchController.show()
        else:
            self._view.researchController.hide()

    def executeArbritrarySearch(self, searchTasks):
        """Execute a search (shows the dedicated view) but
        the user can't edit the searched informations. Only a displayer."""
        self._view.researchController.executeArbitrarySearch(searchTasks)

    def filterMessages_toggled_cb(self, action):
        """Callback executed when the user clicks
        on the filter messages toggle button"""
        if self.getCurrentProject() is None:
            if action.get_active():
                NetzobErrorMessage(_("No project selected."))
            action.set_active(False)
            return
        if action.get_active():
            self._view.filterMessagesController.show()
        else:
            self._view.filterMessagesController.hide()

    def environmentDep_activate_cb(self, action):
        """Callback executed when the user requests
        the execution of environmental deps search through menu
        or toolbar"""
        if self.getCurrentProject() is None:
            NetzobErrorMessage(_("No project selected."))
            return
        symbols = self.view.getCheckedSymbolList()
        if symbols == []:
            NetzobErrorMessage(_("No symbol selected."))
            return
        envDepController = EnvironmentDependenciesSearcherController(self, symbols)
        envDepController.run()


    # Message Tables management
    def addMessageTable(self, objectType):
        """ Create a new message table and selects it"""
        if objectType is Field:
            messageTableController = SymbolTableController(self)
        elif objectType is Session:
            messageTableController = SessionTableController(self)
        elif objectType is Sequence:
            messageTableController = SequenceTableController(self)
        else:
            return
        messageTable = messageTableController.view
        self.messageTableList.append(messageTable)
        self.setSelectedMessageTable(messageTable)
        self.view.messageTableBox.pack_start(messageTable.getPanel(), True, True, 0)

    def removeMessageTable(self, messageTable):
        self.view.messageTableBox.remove(messageTable.getPanel())
        messageTable.destroy()
        self.messageTableList = [mTable for mTable in self.messageTableList
                                 if mTable != messageTable]
        # Select a new table in messageTable was the selected message table
        if len(self.messageTableList) > 0:
            self.setSelectedMessageTable(self.messageTableList[0])

    def removeAllMessageTables(self):
        for child in self.view.messageTableBox.get_children():
            self.view.messageTableBox.remove(child)

        self.messageTableList = []

    def emptyMessageTableDisplayingObjects(self, objectList):
        toBeRemovedTables = [mTable for mTable in self.messageTableList
                             if mTable.getDisplayedObject() in objectList]
        for mTable in toBeRemovedTables:
            mTable.setDisplayedObject(None)

    def updateSelectedMessageTable(self):
        if self.selectedMessageTable is not None:
            self.selectedMessageTable.update()

    def updateMessageTableDisplayingObjects(self, objectList):
        toBeUpdatedTables = [mTable for mTable in self.messageTableList
                             if mTable.getDisplayedObject() in objectList]
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

    def getSelectedMessageTable(self):
        """Return the selected message table"""
        return self.selectedMessageTable

    def setDisplayedObjectInSelectedMessageTable(self, anObject):
        """Show the definition of provided object on the selected
        message table"""
        logging.debug("Update the displayed object in selected message table")

        # Open a message table if none is available
        if len(self.messageTableList) == 0:
            self.addMessageTable(type(anObject))
        else:
            recreateMessageTable = True
            if isinstance(anObject, Field) and type(self.getSelectedMessageTable()) is SymbolTableView:
                recreateMessageTable = False
            elif isinstance(anObject, Session) and type(self.getSelectedMessageTable()) is SessionTableView:
                recreateMessageTable = False
            elif isinstance(anObject, Sequence) and type(self.getSelectedMessageTable()) is SequenceTableView:
                recreateMessageTable = False
            if recreateMessageTable:
                self.removeMessageTable(self.getSelectedMessageTable())
                self.addMessageTable(type(anObject))

        # if a message table is selected we update its object
        self.selectedMessageTable.setDisplayedObject(anObject)

    def getDisplayedObjectInSelectedMessageTable(self):
        if self.selectedMessageTable is None:
            return None
        else:
            return self.selectedMessageTable.displayedObject

    def getSelectedMessagesInSelectedMessageTable(self):
        if self.selectedMessageTable is not None:
            return self.selectedMessageTable.controller.getSelectedMessages()
        else:
            return None

    # Variable management
    def relationsViewer_activate_cb(self, action):
        if self.getCurrentProject() is None:
            NetzobErrorMessage(_("No project selected."))
            return
        relations = RelationsController(self)
        relations.show()

    def variableTable_activate_cb(self, action):
        if self.getCurrentProject() is None:
            NetzobErrorMessage(_("No project selected."))
            return
        builder2 = Gtk.Builder()
        builder2.add_from_file(os.path.join(
            ResourcesConfiguration.getStaticResources(),
            "ui", "vocabulary",
            "variableTable.glade"))

        dialog = builder2.get_object("variableDialog")
        variable_liststore = builder2.get_object("variableListstore")

        # FIXME!
        # Missing code here!

        # ++CODE HERE++
        # ADD DATA NEEDED ON THE LISTSTORE FOR EVERY VARIABLE CREATE BY USER
        # EXEMPLE TO ADD ONE LINE WITH VALUE : [variable1, symbolToto, re{g0.6]ex, ipv4, initialValue : 192.168.0.6 ]
        # EXEMPLE CODE :
        # """i = variable_liststore.append()
        # variable_liststore.set(i, 0, "variable1")
        # variable_liststore.set(i, 1, "symbolToto")
        # variable_liststore.set(i, 2, "re{g0.6]ex")
        # variable_liststore.set(i, 3, "ipv4")
        # variable_liststore.set(i, 4, "initial value : 192.168.0.6")
        # i = variable_liststore.append()
        # variable_liststore.set(i, 0, "variable2")
        # variable_liststore.set(i, 1, "symbolToto")
        # variable_liststore.set(i, 2, "re{g1006.8]ex")
        # variable_liststore.set(i, 3, "binary")
        # variable_liststore.set(i, 4, "initial value : 0110, min bits : 2, max bits : 8")"""
        # ##

        result = dialog.run()

        if (result == 0):
            dialog.destroy()


    # Import and capture of messages
    def importMessagesFromFile_activate_cb(self, action):
        """Execute all the plugins associated with
        file import."""
        if self.getCurrentProject() is None:
            NetzobErrorMessage(_("No project selected."))
            return

        importerPlugins = NetzobPlugin.getLoadedPlugins(FileImporterPlugin)
        if len(importerPlugins) < 1:
            NetzobErrorMessage(_("No importer plugin available."))
            return

        chooser = ImportFileChooserDialog(importerPlugins)
        res = chooser.run()
        plugin = None
        if res == chooser.RESPONSE_OK:
            (filePathList, plugin) = chooser.getFilenameListAndPlugin()
        chooser.destroy()
        if plugin is not None:
            plugin.setFinish_cb(self.view.updateSymbolList)
            plugin.importFile(filePathList)


    # Misc
    def getCurrentProject(self):
        """Return the current project (can be None)"""
        return self.netzob.getCurrentProject()

    def getCurrentWorkspace(self):
        """Return the current workspace"""
        return self.netzob.getCurrentWorkspace()
