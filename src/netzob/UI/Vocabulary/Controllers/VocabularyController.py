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
from netzob.UI.Vocabulary.Controllers.EnvironmentDependenciesSearcherController import EnvironmentDependenciesSearcherController
from netzob.UI.Vocabulary.Views.VocabularyView import VocabularyView
from netzob.Common.ResourcesConfiguration import ResourcesConfiguration
from netzob.Common.Symbol import Symbol
from netzob.UI.Common.Controllers.MoveMessageController import MoveMessageController
from netzob.UI.Vocabulary.Controllers.Partitioning.SequenceAlignmentController import SequenceAlignmentController
from netzob.UI.Vocabulary.Controllers.Partitioning.ForcePartitioningController import ForcePartitioningController
from netzob.UI.Vocabulary.Controllers.Partitioning.SimplePartitioningController import SimplePartitioningController
from netzob.UI.Vocabulary.Controllers.Partitioning.SmoothPartitioningController import SmoothPartitioningController
from netzob.UI.Vocabulary.Controllers.MessagesDistributionController import MessagesDistributionController
from netzob.UI.Vocabulary.Controllers.Partitioning.ResetPartitioningController import ResetPartitioningController
from netzob.UI.Vocabulary.Controllers.SplitFieldController import SplitFieldController
from netzob.UI.Import.ImportFileChooserDialog import ImportFileChooserDialog
from netzob.Common.Plugins.NetzobPlugin import NetzobPlugin
from netzob.Common.Plugins.FileImporterPlugin import FileImporterPlugin
from netzob.UI.NetzobWidgets import NetzobQuestionMessage, NetzobErrorMessage, NetzobInfoMessage
from netzob.UI.Vocabulary.Controllers.RelationsController import RelationsController
from netzob.UI.Vocabulary.Controllers.Menus.ContextualMenuOnLayerController import ContextualMenuOnLayerController
from netzob.Common.Type.TypeConvertor import TypeConvertor
from netzob.UI.Vocabulary.Controllers.VariableController import VariableTreeController
from netzob.Common.Plugins.Extensions.CapturerMenuExtension import CapturerMenuExtension
from netzob.Common.SignalsManager import SignalsManager


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
        self.view.updateLeftPanel()
        self.selectedMessagesToMove = None

        self.view.symbolListTreeViewSelection.set_select_function(self.symbol_list_selection_function, None)
        self.symbol_list_set_selection = True

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
        self.view.removeAllMessageTables()
        self.view.updateLeftPanel()

    def getSignalsManager(self):
        return self.netzob.getSignalsManager()

    def updateListOfCapturerPlugins(self):
        """Fetch the list of available capturer plugins, and provide
        them to its associated view"""
        pluginExtensions = NetzobPlugin.getLoadedPluginsExtension(CapturerMenuExtension)
        self.view.updateListCapturerPlugins(pluginExtensions)

    ## Symbol List toolbar callbacks
    def selectAllSymbolsButton_clicked_cb(self, toolButton):
        """
        select all the symbol in the symbol list
        @type  widget: boolean
        @param widget: if selected symbol
        """
        for row in self.view.symbolListStore:
            row[self.view.SYMBOLLISTSTORE_SELECTED_COLUMN] = True
        self.view.updateSymbolListToolbar()

    def unselectAllSymbolsButton_clicked_cb(self, toolButton):
        """
        unselect all the symbol in the symbol list
        @type  widget: boolean
        @param widget: if selected symbol
        """
        for row in self.view.symbolListStore:
            row[self.view.SYMBOLLISTSTORE_SELECTED_COLUMN] = False
        self.view.updateSymbolListToolbar()

    def createSymbolButton_clicked_cb(self, toolButton):
        if self.getCurrentProject() is None:
            NetzobErrorMessage(_("No project selected."))
            return

        builder2 = Gtk.Builder()
        builder2.add_from_file(os.path.join(ResourcesConfiguration.getStaticResources(), "ui", "dialogbox.glade"))
        dialog = builder2.get_object("createsymbol")
        dialog.set_transient_for(self.netzob.view.mainWindow)

        # Disable apply button if no text
        applybutton = builder2.get_object("button1")
        entry = builder2.get_object("entry1")
        entry.connect("changed", self.entry_disableButtonIfEmpty_cb, applybutton)

        result = dialog.run()

        if (result == 0):
            newSymbolName = entry.get_text()
            newSymbolId = str(uuid.uuid4())
            self.log.debug("A new symbol will be created with the given name: {0}".format(newSymbolName))
            currentProject = self.netzob.getCurrentProject()
            newSymbol = Symbol(newSymbolId, newSymbolName, currentProject)
            currentProject.getVocabulary().addSymbol(newSymbol)
            self.view.updateLeftPanel()
            dialog.destroy()
        if (result == 1):
            dialog.destroy()

    def entry_disableButtonIfEmpty_cb(self, widget, button):
        if(len(widget.get_text()) > 0):
            button.set_sensitive(True)
        else:
            button.set_sensitive(False)

    def concatSymbolButton_clicked_cb(self, toolButton):
        if self.getCurrentProject() is None:
            NetzobErrorMessage(_("No project selected."))
            return
        # retrieve the checked symbols
        symbols = self.view.getCheckedSymbolList()

        # Create a new symbol
        newSymbol = Symbol(str(uuid.uuid4()), "Merged", self.getCurrentProject())

        # fetch all their messages
        for sym in symbols:
            newSymbol.addMessages(sym.getMessages())

        #delete all selected symbols
        self.view.emptyMessageTableDisplayingSymbols(symbols)
        for sym in symbols:
            self.getCurrentProject().getVocabulary().removeSymbol(sym)

        #add the concatenate symbol
        self.getCurrentProject().getVocabulary().addSymbol(newSymbol)

        #refresh view
        self.view.updateLeftPanel()

    def deleteSymbolButton_clicked_cb(self, toolButton):
        if self.getCurrentProject() is None:
            NetzobErrorMessage(_("No project selected."))
            return
        # Delete symbol
        for sym in self.view.getCheckedSymbolList():
            currentProject = self.netzob.getCurrentProject()
            currentVocabulary = currentProject.getVocabulary()
            for mess in sym.getMessages():
                currentVocabulary.removeMessage(mess)
            currentVocabulary.removeSymbol(sym)
            self.view.emptyMessageTableDisplayingSymbols([sym])
        # Update view
        self.view.updateLeftPanel()
        self.view.updateSelectedMessageTable()

    def newMessageTableButton_clicked_cb(self, toolButton):
        if self.getCurrentProject() is None:
            NetzobErrorMessage(_("No project selected."))
            return
        self.view.addMessageTable()

    def toggleCellRenderer_toggled_cb(self, widget, buttonid):
        # Update this flag so the line won't be selected.
        self.symbol_list_set_selection = False
        model = self.view.symbolListStore
        model[buttonid][0] = not model[buttonid][0]
        self.view.updateSymbolListToolbar()

    def symbol_list_selection_function(self, selection, model, path, selected, data):
        """This method is in charge of deciding if the current line of
        symbol tree view (symbolListTreeViewSelection) should be
        selected.

        If the users clicked on the checkbox, then, the current line
        should _not_ be selected. In other cases, the current line is
        selected.

        """

        if not self.symbol_list_set_selection:
            self.symbol_list_set_selection = True
            return False

        return True

    def symbolListTreeViewSelection_changed_cb(self, selection):
        """Callback executed when the user
        clicks on a symbol in the list"""
        if 1 != selection.count_selected_rows():
            return
        logging.debug("The current symbol has changed")
        (model, paths) = selection.get_selected_rows()
        aIter = model.get_iter(paths[0])  # We work on only one symbol/layer
        currentVocabulary = self.netzob.getCurrentProject().getVocabulary()
        if aIter is not None:
            logging.debug("Iter is not none")
            # We first check if the user selected a symbol
            ID = model[aIter][self.view.SYMBOLLISTSTORE_ID_COLUMN]
            field = currentVocabulary.getFieldByID(ID)
            self.executeMoveTargetOperation(field.getSymbol())
            self.view.setDisplayedFieldInSelectedMessageTable(field)
            self._view.updateSymbolProperties()
            self.getSignalsManager().emitSignal(SignalsManager.SIG_SYMBOLS_SINGLE_SELECTION)
        else:
            self.getSignalsManager().emitSignal(SignalsManager.SIG_SYMBOLS_NO_SELECTION)

    def symbolListTreeView_button_press_event_cb(self, treeview, eventButton):
        if 1 > treeview.get_selection().count_selected_rows():
            return
        # Popup a contextual menu if right click
        if eventButton.type == Gdk.EventType.BUTTON_PRESS and eventButton.button == 3:
            (model, paths) = treeview.get_selection().get_selected_rows()

            layers = []
            for path in paths:
                # Retrieve the selected layerFields
                layer_id = model[path][VocabularyView.SYMBOLLISTSTORE_ID_COLUMN]
                if layer_id is not None:
                    layer = self.getCurrentProject().getVocabulary().getFieldByID(layer_id)
                    layers.append(layer)
                else:
                    return

            # Popup a contextual menu
            menuController = ContextualMenuOnLayerController(self, layers)
            menuController.run(eventButton)
            return True  # To discard remaining signals (such as 'changed_cb')

################ TO BE FIXED
    def button_newview_cb(self, widget):
        self.focus = self.addSpreadSheet("empty", 0)
        self.focus.idsymbol = None

    def button_closeview_cb(self, widget, spreadsheet):
        spreadsheet.destroy()

        #refresh focus
        if self.focus.get_object("spreadsheet") == spreadsheet:
            self.focus = None

###############

######### MENU / TOOLBAR ENTRIES CONTROLLERS
    def sequenceAlignment_activate_cb(self, action):
        if self.getCurrentProject() is None:
            NetzobErrorMessage(_("No project selected."))
            return
        layers = self.view.getCheckedLayerList()
        if layers == []:
            NetzobErrorMessage(_("No layer selected."))
            return
        sequence_controller = SequenceAlignmentController(self, layers, doUpgma=True)
        sequence_controller.run()

    def partitioningForce_activate_cb(self, action):
        if self.getCurrentProject() is None:
            NetzobErrorMessage(_("No project selected."))
            return
        layers = self.view.getCheckedLayerList()
        if layers == []:
            NetzobErrorMessage(_("No symbol selected."))
            return
        force_controller = ForcePartitioningController(self, layers)
        force_controller.run()

    def partitioningSimple_activate_cb(self, action):
        if self.getCurrentProject() is None:
            NetzobErrorMessage(_("No project selected."))
            return
        layers = self.view.getCheckedLayerList()
        if layers == []:
            NetzobErrorMessage(_("No symbol selected."))
            return
        simple_controller = SimplePartitioningController(self, layers)
        simple_controller.run()

    def partitioningSmooth_activate_cb(self, action):
        if self.getCurrentProject() is None:
            NetzobErrorMessage(_("No project selected."))
            return
        layers = self.view.getCheckedLayerList()
        if layers == []:
            NetzobErrorMessage(_("No symbol selected."))
            return
        smooth_controller = SmoothPartitioningController(self, layers)
        smooth_controller.run()

    def partitioningReset_activate_cb(self, action):
        """Callback executed when the user clicks
        on the reset button. It starts the dedicated controller."""
        if self.getCurrentProject() is None:
            NetzobErrorMessage(_("No project selected."))
            return
        layers = self.view.getCheckedLayerList()
        if layers == []:
            NetzobErrorMessage(_("No symbol selected."))
            return
        reset_controller = ResetPartitioningController(self, layers)
        reset_controller.run()

    def concatField_activate_cb(self, action):
        # Sanity check
        if self.getCurrentProject() is None:
            NetzobErrorMessage(_("No project selected."))
            return
        symbol = self.view.getDisplayedField()
        if symbol is None:
            NetzobErrorMessage(_("No selected symbol."))
            return
        selectedFields = self.view.selectedMessageTable.treeViewHeaderGroup.getSelectedFields()
        if selectedFields is None or len(selectedFields) < 2:
            NetzobErrorMessage(_("You need to select at least two fields."))
            return
        # We retrieve the first and last fields selected
        firstField = selectedFields[0]
        lastField = selectedFields[0]

        for selectedField in selectedFields:
            if selectedField.getIndex() < firstField.getIndex():
                firstField = selectedField
            if selectedField.getIndex() > lastField.getIndex():
                lastField = selectedField

        # We concat all the fields in the first one
        (errorCode, errorMsg) = firstField.concatFields(lastField)
        if errorCode is False:
            NetzobErrorMessage(errorMsg)
        else:
            self.view.updateSelectedMessageTable()
            self.view.updateLeftPanel()

    def split_activate_cb(self, action):
        # Sanity check
        if self.getCurrentProject() is None:
            NetzobErrorMessage(_("No project selected."))
            return
#        displayedField = self.view.getDisplayedField()
#        if displayedField is None:
#            NetzobErrorMessage(_("No selected symbol."))
#            return
        fields = self.view.selectedMessageTable.treeViewHeaderGroup.getSelectedFields()
        # Split field
        if fields != None and len(fields) > 0:
            field = fields[-1]  # We take the last selected field
            controller = SplitFieldController(self, field)
            controller.run()
        else:
            NetzobErrorMessage(_("No selected field."))

    def editVariable_activate_cb(self, action):
        # Sanity check
        if self.getCurrentProject() is None:
            NetzobErrorMessage(_("No project selected."))
            return
        symbol = self.view.getDisplayedField()
        if symbol is None:
            NetzobErrorMessage(_("No selected symbol."))
            return
        fields = self.view.selectedMessageTable.treeViewHeaderGroup.getSelectedFields()
        if fields is None or len(fields) < 1:
            NetzobErrorMessage(_("No selected field."))
            return
        # Open a popup to edit the variable
        field = fields[-1]  # We take the last selected field
        creationPanel = VariableTreeController(self.netzob, symbol, field)

    def moveMessagesToOtherSymbol_activate_cb(self, action):
        """Callback executed when the user clicks on the move
        button. It retrieves the selected message, and change the cursor
        to show that moving is in progress. The user needs to click on a symbol to
        select the target symbol"""
        if self.getCurrentProject() is None:
            NetzobErrorMessage(_("No project selected."))
            return
        selectedMessages = self.view.getSelectedMessagesInSelectedMessageTable()
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
            self.view.updateSelectedMessageTable()
            self.view.updateLeftPanel()

    def removePendingMessagesToMove(self):
        """Clean the pending messages the user wanted to move (using the button)."""
        cursor = Gdk.Cursor.new(Gdk.CursorType.ARROW)
        self.view.vocabularyPanel.get_root_window().set_cursor(cursor)
        self.selectedMessagesToMove = None

    def deleteMessages_activate_cb(self, action):
        if self.getCurrentProject() is None:
            NetzobErrorMessage(_("No project selected."))
            return
        selectedMessages = self.view.getSelectedMessagesInSelectedMessageTable()
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
        self.view.updateSelectedMessageTable()
        self.view.updateLeftPanel()

    def searchText_toggled_cb(self, action):
        """Callback executed when the user clicks
        on the research toggle button"""
        if self.getCurrentProject() is None:
            if action.get_active() == True:
                NetzobErrorMessage(_("No project selected."))
            action.set_active(False)
            return
        if action.get_active():
            self._view.researchController.show()
        else:
            self._view.researchController.hide()

    def filterMessages_toggled_cb(self, action):
        """Callback executed when the user clicks
        on the filter messages toggle button"""
        if self.getCurrentProject() is None:
            if action.get_active() == True:
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

    def messagesDistribution_activate_cb(self, action):
        # Sanity check
        if self.getCurrentProject() is None:
            NetzobErrorMessage(_("No project selected."))
            return
        symbols = self.view.getCheckedSymbolList()
        if symbols == []:
            NetzobErrorMessage(_("No symbol selected."))
            return
        distribution = MessagesDistributionController(self, self._view.getCheckedSymbolList())
        distribution.run()

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

    def fieldLimits_activate_cb(self, action):
        # Sanity checks
        if self.netzob.getCurrentProject() is None:
            NetzobErrorMessage(_("No project selected."))
            return

        layers = self.view.getCheckedLayerList()
        if layers == []:
            NetzobErrorMessage(_("No symbol selected."))
            return

        for layer in layers:
            layer.computeFieldsLimits()
            self.view.updateSelectedMessageTable()
        NetzobInfoMessage(_("Fields limits computed."))

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

    def getCurrentProject(self):
        """Return the current project (can be None)"""
        return self.netzob.getCurrentProject()

    def getCurrentWorkspace(self):
        """Return the current workspace"""
        return self.netzob.getCurrentWorkspace()

    def moveMessage(self, message, targetSymbol):
        """Move the provided message in the specified symbol.
        Warning, this method do not consider the possible regex problems
        which needs to be addressed by a set of dedicated solutions"""
        if message is not None and targetSymbol is not None:
            sourceSymbolID = message.getSymbol().getID()
            sourceSymbol = self.getCurrentProject().getVocabulary().getSymbolByID(sourceSymbolID)
            sourceSymbol.removeMessage(message)
            targetSymbol.addMessage(message)

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

    def executeAbritrarySearch(self, searchTasks):
        """Execute a search (shows the dedicated view) but
        the user can't edit the searched informations. Only a displayer."""
        self._view.researchController.executeArbitrarySearch(searchTasks)
