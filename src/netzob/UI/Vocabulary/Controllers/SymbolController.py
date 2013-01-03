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
from netzob.UI.Vocabulary.Controllers.EnvironmentDependenciesSearcherController import EnvironmentDependenciesSearcherController
from netzob.UI.Vocabulary.Views.SymbolView import SymbolView
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
#| SymbolController:
#|     Controller for symbol rendering
#+----------------------------------------------
class SymbolController(object):

    def __init__(self, netzob):
        self.netzob = netzob
        self._view = SymbolView(self)
        self.log = logging.getLogger(__name__)

        self.view.symbolListTreeViewSelection.set_select_function(self.symbol_list_selection_function, None)
        self.symbol_list_set_selection = True

    @property
    def view(self):
        return self._view

    def updateLeftPanel(self):
        self.view.updateSymbolList()
        self.view.updateSymbolListToolbar()

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
        self.view.symbolPropertiesListstore.clear()
        # get symbol properties
        properties = self.getSymbolProperties()
#        # add symbol properties
        for prop in properties:
            line = self.symbolPropertiesListstore.append()
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
        self.view.emptyMessageTableDisplayingSymbols(symbols)
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
            self.view.emptyMessageTableDisplayingSymbols([sym])
        # Update view
        self.updateLeftPanel()
        self.view.updateSelectedMessageTable()

    def newSymbolTableButton_clicked_cb(self, toolButton):
        if self.getCurrentProject() is None:
            NetzobErrorMessage(_("No project selected."))
            return
        self.view.addMessageTable()

    def toggleSymbolCellRenderer_toggled_cb(self, widget, buttonid):
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
