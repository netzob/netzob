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
from netzob.Common.ResourcesConfiguration import ResourcesConfiguration
from netzob.Common.Symbol import Symbol
from netzob.Common.Field import Field
from netzob.Common.Plugins.NetzobPlugin import NetzobPlugin
from netzob.Common.SignalsManager import SignalsManager
from netzob.UI.Common.Controllers.MoveMessageController import MoveMessageController
from netzob.UI.Vocabulary.Controllers.Partitioning.SequenceAlignmentController import SequenceAlignmentController
from netzob.UI.Vocabulary.Controllers.Partitioning.ForcePartitioningController import ForcePartitioningController
from netzob.UI.Vocabulary.Controllers.Partitioning.SimplePartitioningController import SimplePartitioningController
from netzob.UI.Vocabulary.Controllers.Partitioning.SmoothPartitioningController import SmoothPartitioningController
from netzob.UI.Vocabulary.Controllers.Partitioning.ResetPartitioningController import ResetPartitioningController
from netzob.UI.Vocabulary.Controllers.MessagesDistributionController import MessagesDistributionController
from netzob.UI.Vocabulary.Controllers.SplitFieldController import SplitFieldController
from netzob.UI.Vocabulary.Controllers.Menus.ContextualMenuOnLayerController import ContextualMenuOnLayerController
from netzob.UI.Vocabulary.Controllers.VariableController import VariableTreeController
from netzob.UI.Vocabulary.Controllers.VariableDisplayerController import VariableDisplayerController
from netzob.UI.NetzobWidgets import NetzobQuestionMessage, NetzobErrorMessage, NetzobInfoMessage


#+----------------------------------------------
#| SymbolController:
#|     Controller for symbol rendering
#+----------------------------------------------
class SymbolController(object):

    def __init__(self, vocabularyController):
        self.vocabularyController = vocabularyController
        self.netzob = vocabularyController.netzob
        self._view = vocabularyController._view
        self.log = logging.getLogger(__name__)

        self.view.symbolListTreeViewSelection.set_select_function(self.symbol_list_selection_function, None)
        self.symbol_list_set_selection = True

    @property
    def view(self):
        return self._view

    def updateLeftPanel(self):
        self.updateSymbolList()
        self.updateSymbolListToolbar()
        self.updateSymbolProperties()

    ## Symbol List
    def updateSymbolList(self):
        """Updates the symbol list of the left panel, preserving the current
        selection"""
        # Retrieve symbols of the current project vocabulary (if one selected)
        layerList = []
        if self.getCurrentProject() is not None and self.getCurrentProject().getVocabulary() is not None:
            for symbol in self.getCurrentProject().getVocabulary().getSymbols():
                layerList.append(symbol.getField())

        checkedSymbolsIDList = []
        for row in self.view.symbolListStore:
            if (row[self.view.SYMBOLLISTSTORE_SELECTED_COLUMN]):
                checkedSymbolsIDList.append(row[self.view.SYMBOLLISTSTORE_ID_COLUMN])
        # Block selection changed handler
        self.view.symbolListTreeViewSelection.handler_block_by_func(self.symbolListTreeViewSelection_changed_cb)
        self.view.symbolListStore.clear()
        for layer in layerList:
            pIter = self.addRowSymbolList(checkedSymbolsIDList, layer.getName(),
                                          len(layer.getMessages()),
                                          len(layer.getExtendedFields()),
                                          str(layer.getID()))
            for fieldLayer in layer.getFieldLayers():
                self.addLayerRowSymbolList(pIter, checkedSymbolsIDList, layer, fieldLayer)
        self.setSelectedSymbolFromSelectedSymbolTable()
        self.view.symbolListTreeViewSelection.handler_unblock_by_func(self.symbolListTreeViewSelection_changed_cb)

    def setSelectedSymbolFromSelectedSymbolTable(self):
        if self.vocabularyController.selectedMessageTable is None:
            self.setSelectedSymbol(None)
        else:
            symbolTableSymbol = self.vocabularyController.selectedMessageTable.displayedObject
            self.setSelectedSymbol(symbolTableSymbol)

    def addRowSymbolList(self, checkedSymbolsIDList, name, message, field, symID):
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
        i = self.view.symbolListStore.append(None)
        self.view.symbolListStore.set(i, self.view.SYMBOLLISTSTORE_SELECTED_COLUMN, (symID in checkedSymbolsIDList))
        self.view.symbolListStore.set(i, self.view.SYMBOLLISTSTORE_TOPLEVEL_COLUMN, True)
        self.view.symbolListStore.set(i, self.view.SYMBOLLISTSTORE_NAME_COLUMN, name)
        self.view.symbolListStore.set(i, self.view.SYMBOLLISTSTORE_MESSAGE_COLUMN, message)
        self.view.symbolListStore.set(i, self.view.SYMBOLLISTSTORE_FIELD_COLUMN, field)
        self.view.symbolListStore.set(i, self.view.SYMBOLLISTSTORE_ID_COLUMN, symID)
        return i

    def addLayerRowSymbolList(self, parentIter, checkedSymbolsIDList, symbol, fieldLayer):
        """Adds a layer row in the symbol list of left panel
        @type  parentIter: string
        @param parentIter: parent iter
        @type  selection: boolean
        @param selection: if selected symbol
        @type  name: fieldLayer
        @param name: the targeted fieldLayer
        """
        i = self.view.symbolListStore.append(parentIter)
        self.view.symbolListStore.set(i, self.view.SYMBOLLISTSTORE_SELECTED_COLUMN, (str(fieldLayer.getID()) in checkedSymbolsIDList))
        self.view.symbolListStore.set(i, self.view.SYMBOLLISTSTORE_TOPLEVEL_COLUMN, False)
        self.view.symbolListStore.set(i, self.view.SYMBOLLISTSTORE_NAME_COLUMN, fieldLayer.getName())
        self.view.symbolListStore.set(i, self.view.SYMBOLLISTSTORE_MESSAGE_COLUMN, len(symbol.getMessages()))
        self.view.symbolListStore.set(i, self.view.SYMBOLLISTSTORE_FIELD_COLUMN, len(fieldLayer.getExtendedFields()))
        self.view.symbolListStore.set(i, self.view.SYMBOLLISTSTORE_ID_COLUMN, str(fieldLayer.getID()))
        # Add inner layers
        for innerFieldLayer in fieldLayer.getFieldLayers():
            self.addLayerRowSymbolList(i, checkedSymbolsIDList, symbol, innerFieldLayer)

    def updateSymbolListToolbar(self):
        """Enables or disable buttons of the symbol list toolbar"""
        selectedSymbolsCount = self.countSelectedSymbols()
        self.view.concatSymbolButton.set_sensitive((selectedSymbolsCount >= 2))
        self.view.deleteSymbolButton.set_sensitive((selectedSymbolsCount >= 1))

        # We emit signals depending of the number of selected symbols
        if selectedSymbolsCount == 0:
            self.netzob.getSignalsManager().emitSignal(SignalsManager.SIG_SYMBOLS_NONE_CHECKED)
        elif selectedSymbolsCount == 1:
            self.netzob.getSignalsManager().emitSignal(SignalsManager.SIG_SYMBOLS_SINGLE_CHECKED)
        else:
            self.netzob.getSignalsManager().emitSignal(SignalsManager.SIG_SYMBOLS_MULTIPLE_CHECKED)

    def countSelectedSymbols(self):
        count = 0
        for row in self.view.symbolListStore:
            if row[self.view.SYMBOLLISTSTORE_SELECTED_COLUMN]:
                count += 1
        return count

    def getCheckedLayerList(self):
        if self.getCurrentProject() is None:
            return []
        currentVocabulary = self.getCurrentProject().getVocabulary()
        selectedLayerList = []
        for row in self.view.symbolListStore:
            if row[self.view.SYMBOLLISTSTORE_SELECTED_COLUMN]:
                layer_id = row[self.view.SYMBOLLISTSTORE_ID_COLUMN]
                layer = currentVocabulary.getFieldByID(layer_id)
                selectedLayerList.append(layer)
        return selectedLayerList

    def getCheckedSymbolList(self):
        if self.getCurrentProject() is None:
            return []
        currentVocabulary = self.getCurrentProject().getVocabulary()
        selectedSymbolList = []
        for row in self.view.symbolListStore:
            if row[self.view.SYMBOLLISTSTORE_SELECTED_COLUMN]:
                layer_id = row[self.view.SYMBOLLISTSTORE_ID_COLUMN]
                layer = currentVocabulary.getFieldByID(layer_id)
                if not layer.getSymbol() in selectedSymbolList:
                    selectedSymbolList.append(layer.getSymbol())
        return selectedSymbolList

    def setSelectedSymbol(self, symbol):
        selection = self.view.symbolListTreeView.get_selection()
        if symbol is None:
            selection.unselect_all()
        else:
            path = self.getSymbolPathInSymbolList(symbol)
            if path is not None:
                selection.select_path(path)

    def getSelectedSymbol(self):
        """Returns the selected symbol in the list of symbols"""
        currentVocabulary = self.getCurrentProject().getVocabulary()
        model, iter = self.view.symbolListTreeView.get_selection().get_selected()
        if iter is not None:
            symID = model[iter][self.view.SYMBOLLISTSTORE_ID_COLUMN]
            return currentVocabulary.getSymbolByID(symID)
        return None

    def getSymbolPathInSymbolList(self, symbol):
        symID = symbol.getID()
        for path, row in enumerate(self.view.symbolListStore):
            if row[self.view.SYMBOLLISTSTORE_ID_COLUMN] == symID:
                return path

    def getDisplayedObject(self):
        if self.vocabularyController.selectedMessageTable is None:
            return None
        return self.vocabularyController.selectedMessageTable.getDisplayedObject()

    def getCurrentProject(self):
        return self.netzob.getCurrentProject()


    # Properties
    def getSymbolProperties(self):
        """Create the list of properties associated
        with the current displayed symbol"""
        properties = []
        symbol = self.vocabularyController.getDisplayedObjectInSelectedMessageTable()
        if symbol is not None:
            properties = symbol.getProperties()
        return properties

    def updateSymbolProperties(self):
        # clean store
        self.view.symbolPropertiesListstore.clear()
        # get symbol properties
        properties = self.getSymbolProperties()
#        # add symbol properties
        for prop in properties:
            line = self.view.symbolPropertiesListstore.append()
            self.view.symbolPropertiesListstore.set(line, self.view.SYMBOLPROPERTIESLISTSTORE_NAME_COLUMN, prop.getName())
            self.view.symbolPropertiesListstore.set(line, self.view.SYMBOLPROPERTIESLISTSTORE_VALUE_COLUMN, str(prop.getCurrentValue()))
            self.view.symbolPropertiesListstore.set(line, self.view.SYMBOLPROPERTIESLISTSTORE_EDITABLE_COLUMN, prop.isEditable)
            if prop.getPossibleValues() != []:
                liststore_possibleValues = Gtk.ListStore(str)
                for val in prop.getPossibleValues():
                    liststore_possibleValues.append([val])
                self.view.symbolPropertiesListstore.set(line, self.view.SYMBOLPROPERTIESLISTSTORE_MODEL_COLUMN, liststore_possibleValues)

        # update the variable definition
        self.updateSymbolVariableDefinition()

    def updateSymbolVariableDefinition(self):
        currentSymbol = self.vocabularyController.getDisplayedObjectInSelectedMessageTable()
        if currentSymbol is not None:
            variableDisplayerController = VariableDisplayerController(self, currentSymbol, True)
            variableDisplayerController.run(self.view.messagesDistributionSymbolViewport)

    def getMessageProperties(self):
        """Retrieve the current first selected message (in the
        selected TableMessage) and return its properties"""
        properties = []
        messages = self.vocabularyController.getSelectedMessagesInSelectedMessageTable()
        if messages is not None and len(messages) > 0:
            message = messages[0]
            if message is not None:
                properties = message.getProperties()
        return properties

    def updateMessageProperties(self):
        # clean store
        self.view.messagePropertiesListstore.clear()
        # get message properties
        properties = self.getMessageProperties()
        # add message properties
        for prop in properties:
            line = self.view.messagePropertiesListstore.append()
            self.view.messagePropertiesListstore.set(line, self.view.MESSAGEPROPERTIESLISTSTORE_NAME_COLUMN, prop.getName())
            self.view.messagePropertiesListstore.set(line, self.view.MESSAGEPROPERTIESLISTSTORE_VALUE_COLUMN, str(prop.getCurrentValue()))
            self.view.messagePropertiesListstore.set(line, self.view.MESSAGEPROPERTIESLISTSTORE_EDITABLE_COLUMN, prop.isEditable)
            if prop.getPossibleValues() != []:
                liststore_possibleValues = Gtk.ListStore(str)
                for val in prop.getPossibleValues():
                    liststore_possibleValues.append([val])
                self.view.messagePropertiesListstore.set(line, self.view.MESSAGEPROPERTIESLISTSTORE_MODEL_COLUMN, liststore_possibleValues)

    ## Symbol List toolbar callbacks
    def selectAllSymbolsButton_clicked_cb(self, toolButton):
        """
        select all the symbol in the symbol list
        @type  widget: boolean
        @param widget: if selected symbol
        """
        for row in self.view.symbolListStore:
            row[self.view.SYMBOLLISTSTORE_SELECTED_COLUMN] = True
        self.updateSymbolListToolbar()

    def unselectAllSymbolsButton_clicked_cb(self, toolButton):
        """
        unselect all the symbol in the symbol list
        @type  widget: boolean
        @param widget: if selected symbol
        """
        for row in self.view.symbolListStore:
            row[self.view.SYMBOLLISTSTORE_SELECTED_COLUMN] = False
        self.updateSymbolListToolbar()

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
            self.updateLeftPanel()
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
        self.vocabularyController.emptyMessageTableDisplayingObjects(symbols)
        for sym in symbols:
            self.getCurrentProject().getVocabulary().removeSymbol(sym)

        #add the concatenate symbol
        self.getCurrentProject().getVocabulary().addSymbol(newSymbol)

        #refresh view
        self.updateLeftPanel()

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
            self.vocabularyController.emptyMessageTableDisplayingObjects([sym])
        # Update view
        self.vocabularyController.updateSelectedMessageTable()
        self.updateLeftPanel()

    def newSymbolTableButton_clicked_cb(self, toolButton):
        if self.getCurrentProject() is None:
            NetzobErrorMessage(_("No project selected."))
            return
        self.vocabularyController.addMessageTable(Field)

    def toggleSymbolCellRenderer_toggled_cb(self, widget, buttonid):
        # Update this flag so the line won't be selected.
        self.symbol_list_set_selection = False
        model = self.view.symbolListStore
        model[buttonid][0] = not model[buttonid][0]
        self.updateSymbolListToolbar()

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
            self.vocabularyController.executeMoveTargetOperation(field.getSymbol())
            self.vocabularyController.setDisplayedObjectInSelectedMessageTable(field)
            self.updateSymbolProperties()
            self.netzob.getSignalsManager().emitSignal(SignalsManager.SIG_SYMBOLS_SINGLE_SELECTION)
        else:
            self.netzob.getSignalsManager().emitSignal(SignalsManager.SIG_SYMBOLS_NO_SELECTION)

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


    ## Actions on fields
    def concatField_activate_cb(self, action):
        # Sanity check
        if self.getCurrentProject() is None:
            NetzobErrorMessage(_("No project selected."))
            return
        symbol = self.view.getDisplayedObject()
        if symbol is None:
            NetzobErrorMessage(_("No selected symbol."))
            return
        selectedFields = self.vocabularyController.selectedMessageTable.treeViewHeaderGroup.getSelectedFields()
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
            self.vocabularyController.updateSelectedMessageTable()
            self.updateLeftPanel()

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
            self.vocabularyController.updateSelectedMessageTable()
        NetzobInfoMessage(_("Fields limits computed."))

    def split_activate_cb(self, action):
        # Sanity check
        if self.getCurrentProject() is None:
            NetzobErrorMessage(_("No project selected."))
            return
#        displayedObject = self.view.getDisplayedObject()
#        if displayedObject is None:
#            NetzobErrorMessage(_("No selected symbol."))
#            return
        fields = self.vocabularyController.selectedMessageTable.treeViewHeaderGroup.getSelectedFields()
        # Split field
        if fields is not None and len(fields) > 0:
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
        symbol = self.view.getDisplayedObject()
        if symbol is None:
            NetzobErrorMessage(_("No selected symbol."))
            return
        fields = self.vocabularyController.selectedMessageTable.treeViewHeaderGroup.getSelectedFields()
        if fields is None or len(fields) < 1:
            NetzobErrorMessage(_("No selected field."))
            return
        # Open a popup to edit the variable
        field = fields[-1]  # We take the last selected field
        creationPanel = VariableTreeController(self.netzob, symbol, field)
