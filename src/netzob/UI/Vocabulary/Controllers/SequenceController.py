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
from netzob.Common.Sequence import Sequence
from netzob.Common.Plugins.NetzobPlugin import NetzobPlugin
from netzob.Common.SignalsManager import SignalsManager
from netzob.UI.Common.Controllers.MoveMessageController import MoveMessageController
from netzob.UI.Vocabulary.Controllers.Partitioning.SequenceAlignmentController import SequenceAlignmentController
from netzob.UI.Vocabulary.Controllers.Partitioning.ForcePartitioningController import ForcePartitioningController
from netzob.UI.Vocabulary.Controllers.Partitioning.SimplePartitioningController import SimplePartitioningController
from netzob.UI.Vocabulary.Controllers.Partitioning.SmoothPartitioningController import SmoothPartitioningController
from netzob.UI.Vocabulary.Controllers.Partitioning.ResetPartitioningController import ResetPartitioningController
from netzob.UI.Vocabulary.Controllers.SplitFieldController import SplitFieldController
from netzob.UI.Vocabulary.Controllers.Menus.ContextualMenuOnLayerController import ContextualMenuOnLayerController
from netzob.UI.Vocabulary.Controllers.VariableController import VariableTreeController
from netzob.UI.Vocabulary.Controllers.VariableDisplayerController import VariableDisplayerController
from netzob.UI.NetzobWidgets import NetzobQuestionMessage, NetzobErrorMessage, NetzobInfoMessage


#+----------------------------------------------
#| SequenceController:
#|     Controller for sequence rendering
#+----------------------------------------------
class SequenceController(object):

    def __init__(self, vocabularyController):
        self.vocabularyController = vocabularyController
        self.netzob = vocabularyController.netzob
        self._view = vocabularyController._view
        self.log = logging.getLogger(__name__)

        self.view.sequenceListTreeViewSelection.set_select_function(self.sequence_list_selection_function, None)
        self.sequence_list_set_selection = True

    @property
    def view(self):
        return self._view

    def updateLeftPanel(self):
        self.updateSequenceList()
        self.updateSequenceListToolbar()
        self.updateSequenceProperties()

    ## Sequence List
    def updateSequenceList(self):
        """Updates the sequence list of the left panel, preserving the current
        selection"""
        # Retrieve sequences of the current project vocabulary (if one selected)
        sequenceList = []
        if self.getCurrentProject() is not None and self.getCurrentProject().getGrammar() is not None:
            sequenceList.extend(self.getCurrentProject().getGrammar().getSequences())

        checkedSequencesIDList = []
        for row in self.view.sequenceListStore:
            if (row[self.view.SEQUENCELISTSTORE_SELECTED_COLUMN]):
                checkedSequencesIDList.append(row[self.view.SEQUENCELISTSTORE_ID_COLUMN])
        # Block selection changed handler
        self.view.sequenceListTreeViewSelection.handler_block_by_func(self.sequenceListTreeViewSelection_changed_cb)
        self.view.sequenceListStore.clear()
        for sequence in sequenceList:
            pIter = self.addRowSequenceList(checkedSequencesIDList, sequence.getName(),
                                          len(sequence.getMessages()),
                                          str(sequence.getID()))
        self.setSelectedSequenceFromSelectedSequenceTable()
        self.view.sequenceListTreeViewSelection.handler_unblock_by_func(self.sequenceListTreeViewSelection_changed_cb)

    def setSelectedSequenceFromSelectedSequenceTable(self):
        if self.vocabularyController.selectedMessageTable is None:
            self.setSelectedSequence(None)
        else:
            sequenceTableSequence = self.vocabularyController.selectedMessageTable.displayedObject
            self.setSelectedSequence(sequenceTableSequence)

    def addRowSequenceList(self, checkedSequencesIDList, name, message, symID):
        """Adds a row in the sequence list of left panel
        @type  selection: boolean
        @param selection: if selected sequence
        @type  name: string
        @param name: name of the sequence
        @type  message: string
        @param message: number of message in the sequence
        @type  image: string
        @param image: image of the lock button (freeze partitioning)"""
        i = self.view.sequenceListStore.append(None)
        self.view.sequenceListStore.set(i, self.view.SEQUENCELISTSTORE_SELECTED_COLUMN, (symID in checkedSequencesIDList))
        self.view.sequenceListStore.set(i, self.view.SEQUENCELISTSTORE_TOPLEVEL_COLUMN, True)
        self.view.sequenceListStore.set(i, self.view.SEQUENCELISTSTORE_NAME_COLUMN, name)
        self.view.sequenceListStore.set(i, self.view.SEQUENCELISTSTORE_MESSAGE_COLUMN, message)
        self.view.sequenceListStore.set(i, self.view.SEQUENCELISTSTORE_ID_COLUMN, symID)
        return i

    def updateSequenceListToolbar(self):
        """Enables or disable buttons of the sequence list toolbar"""
        selectedSequencesCount = self.countSelectedSequences()
        self.view.concatSequenceButton.set_sensitive((selectedSequencesCount >= 2))
        self.view.deleteSequenceButton.set_sensitive((selectedSequencesCount >= 1))

        # We emit signals depending of the number of selected sequences
        if selectedSequencesCount == 0:
            self.netzob.getSignalsManager().emitSignal(SignalsManager.SIG_SEQUENCES_NONE_CHECKED)
        elif selectedSequencesCount == 1:
            self.netzob.getSignalsManager().emitSignal(SignalsManager.SIG_SEQUENCES_SINGLE_CHECKED)
        else:
            self.netzob.getSignalsManager().emitSignal(SignalsManager.SIG_SEQUENCES_MULTIPLE_CHECKED)

    def countSelectedSequences(self):
        count = 0
        for row in self.view.sequenceListStore:
            if row[self.view.SEQUENCELISTSTORE_SELECTED_COLUMN]:
                count += 1
        return count

    def getCheckedLayerList(self):
        if self.getCurrentProject() is None:
            return []
        currentVocabulary = self.getCurrentProject().getVocabulary()
        selectedLayerList = []
        for row in self.view.sequenceListStore:
            if row[self.view.SEQUENCELISTSTORE_SELECTED_COLUMN]:
                layer_id = row[self.view.SEQUENCELISTSTORE_ID_COLUMN]
                layer = currentVocabulary.getFieldByID(layer_id)
                selectedLayerList.append(layer)
        return selectedLayerList

    def getCheckedSequenceList(self):
        if self.getCurrentProject() is None:
            return []
        currentVocabulary = self.getCurrentProject().getVocabulary()
        selectedSequenceList = []
        for row in self.view.sequenceListStore:
            if row[self.view.SEQUENCELISTSTORE_SELECTED_COLUMN]:
                layer_id = row[self.view.SEQUENCELISTSTORE_ID_COLUMN]
                layer = currentVocabulary.getFieldByID(layer_id)
                if not layer.getSequence() in selectedSequenceList:
                    selectedSequenceList.append(layer.getSequence())
        return selectedSequenceList

    def setSelectedSequence(self, sequence):
        selection = self.view.sequenceListTreeView.get_selection()
        if sequence is None:
            selection.unselect_all()
        else:
            path = self.getSequencePathInSequenceList(sequence)
            if path is not None:
                selection.select_path(path)

    def getSelectedSequence(self):
        """Returns the selected sequence in the list of sequences"""
        currentVocabulary = self.getCurrentProject().getVocabulary()
        model, iter = self.view.sequenceListTreeView.get_selection().get_selected()
        if iter is not None:
            symID = model[iter][self.view.SEQUENCELISTSTORE_ID_COLUMN]
            return currentVocabulary.getSequenceByID(symID)
        return None

    def getSequencePathInSequenceList(self, sequence):
        symID = sequence.getID()
        for path, row in enumerate(self.view.sequenceListStore):
            if row[self.view.SEQUENCELISTSTORE_ID_COLUMN] == symID:
                return path

    def getDisplayedObject(self):
        if self.vocabularyController.selectedMessageTable is None:
            return None
        return self.vocabularyController.selectedMessageTable.getDisplayedObject()

    def getCurrentProject(self):
        return self.netzob.getCurrentProject()


    # Properties
    def getSequenceProperties(self):
        """Create the list of properties associated
        with the current displayed sequence"""
        properties = []
        sequence = self.vocabularyController.getDisplayedObjectInSelectedMessageTable()
        if sequence is not None:
            properties = sequence.getProperties()
        return properties

    def updateSequenceProperties(self):
        # clean store
        self.view.sequencePropertiesListstore.clear()
        # get sequence properties
        properties = self.getSequenceProperties()
#        # add sequence properties
        for prop in properties:
            line = self.view.sequencePropertiesListstore.append()
            self.view.sequencePropertiesListstore.set(line, self.view.SEQUENCEPROPERTIESLISTSTORE_NAME_COLUMN, prop.getName())
            self.view.sequencePropertiesListstore.set(line, self.view.SEQUENCEPROPERTIESLISTSTORE_VALUE_COLUMN, str(prop.getCurrentValue()))
            self.view.sequencePropertiesListstore.set(line, self.view.SEQUENCEPROPERTIESLISTSTORE_EDITABLE_COLUMN, prop.isEditable)
            if prop.getPossibleValues() != []:
                liststore_possibleValues = Gtk.ListStore(str)
                for val in prop.getPossibleValues():
                    liststore_possibleValues.append([val])
                self.view.sequencePropertiesListstore.set(line, self.view.SEQUENCEPROPERTIESLISTSTORE_MODEL_COLUMN, liststore_possibleValues)

        # update the variable definition
        self.updateSequenceVariableDefinition()

    def updateSequenceVariableDefinition(self):
        currentSequence = self.vocabularyController.getDisplayedObjectInSelectedMessageTable()
        if currentSequence is not None:
            variableDisplayerController = VariableDisplayerController(self.vocabularyController, currentSequence, True)
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

    ## Sequence List toolbar callbacks
    def selectAllSequencesButton_clicked_cb(self, toolButton):
        """
        select all the sequence in the sequence list
        @type  widget: boolean
        @param widget: if selected sequence
        """
        for row in self.view.sequenceListStore:
            row[self.view.SEQUENCELISTSTORE_SELECTED_COLUMN] = True
        self.updateSequenceListToolbar()

    def unselectAllSequencesButton_clicked_cb(self, toolButton):
        """
        unselect all the sequence in the sequence list
        @type  widget: boolean
        @param widget: if selected sequence
        """
        for row in self.view.sequenceListStore:
            row[self.view.SEQUENCELISTSTORE_SELECTED_COLUMN] = False
        self.updateSequenceListToolbar()

    def createSequenceButton_clicked_cb(self, toolButton):
        if self.getCurrentProject() is None:
            NetzobErrorMessage(_("No project selected."))
            return

        builder2 = Gtk.Builder()
        builder2.add_from_file(os.path.join(ResourcesConfiguration.getStaticResources(), "ui", "dialogbox.glade"))
        dialog = builder2.get_object("createsequence")
        dialog.set_transient_for(self.netzob.view.mainWindow)

        # Disable apply button if no text
        applybutton = builder2.get_object("button1")
        entry = builder2.get_object("entry1")
        entry.connect("changed", self.entry_disableButtonIfEmpty_cb, applybutton)

        result = dialog.run()

        if (result == 0):
            newSequenceName = entry.get_text()
            newSequenceId = str(uuid.uuid4())
            self.log.debug("A new sequence will be created with the given name: {0}".format(newSequenceName))
            currentProject = self.netzob.getCurrentProject()
            newSequence = Sequence(newSequenceId, newSequenceName, currentProject)
            currentProject.getVocabulary().addSequence(newSequence)
            self.updateLeftPanel()
            dialog.destroy()
        if (result == 1):
            dialog.destroy()

    def entry_disableButtonIfEmpty_cb(self, widget, button):
        if(len(widget.get_text()) > 0):
            button.set_sensitive(True)
        else:
            button.set_sensitive(False)

    def concatSequenceButton_clicked_cb(self, toolButton):
        if self.getCurrentProject() is None:
            NetzobErrorMessage(_("No project selected."))
            return
        # retrieve the checked sequences
        sequences = self.view.getCheckedSequenceList()

        # Create a new sequence
        newSequence = Sequence(str(uuid.uuid4()), "Merged", self.getCurrentProject())

        # fetch all their messages
        for sym in sequences:
            newSequence.addMessages(sym.getMessages())

        #delete all selected sequences
        self.vocabularyController.emptyMessageTableDisplayingObjects(sequences)
        for sym in sequences:
            self.getCurrentProject().getVocabulary().removeSequence(sym)

        #add the concatenate sequence
        self.getCurrentProject().getVocabulary().addSequence(newSequence)

        #refresh view
        self.updateLeftPanel()

    def deleteSequenceButton_clicked_cb(self, toolButton):
        if self.getCurrentProject() is None:
            NetzobErrorMessage(_("No project selected."))
            return
        # Delete sequence
        for sym in self.view.getCheckedSequenceList():
            currentProject = self.netzob.getCurrentProject()
            currentVocabulary = currentProject.getVocabulary()
            for mess in sym.getMessages():
                currentVocabulary.removeMessage(mess)
            currentVocabulary.removeSequence(sym)
            self.vocabularyController.emptyMessageTableDisplayingObjects([sym])
        # Update view
        self.vocabularyController.updateSelectedMessageTable()
        self.updateLeftPanel()

    def newSequenceTableButton_clicked_cb(self, toolButton):
        if self.getCurrentProject() is None:
            NetzobErrorMessage(_("No project selected."))
            return
        self.vocabularyController.addMessageTable(Sequence)

    def toggleSequenceCellRenderer_toggled_cb(self, widget, buttonid):
        # Update this flag so the line won't be selected.
        self.sequence_list_set_selection = False
        model = self.view.sequenceListStore
        model[buttonid][0] = not model[buttonid][0]
        self.updateSequenceListToolbar()

    def sequence_list_selection_function(self, selection, model, path, selected, data):
        """This method is in charge of deciding if the current line of
        sequence tree view (sequenceListTreeViewSelection) should be
        selected.

        If the users clicked on the checkbox, then, the current line
        should _not_ be selected. In other cases, the current line is
        selected.

        """

        if not self.sequence_list_set_selection:
            self.sequence_list_set_selection = True
            return False

        return True

    def sequenceListTreeViewSelection_changed_cb(self, selection):
        """Callback executed when the user
        clicks on a sequence in the list"""
        if 1 != selection.count_selected_rows():
            return
        logging.debug("The current sequence has changed")
        (model, paths) = selection.get_selected_rows()
        aIter = model.get_iter(paths[0])  # We work on only one sequence/layer
        currentVocabulary = self.netzob.getCurrentProject().getVocabulary()
        if aIter is not None:
            logging.debug("Iter is not none")
            # We first check if the user selected a sequence
            ID = model[aIter][self.view.SEQUENCELISTSTORE_ID_COLUMN]
            field = currentVocabulary.getFieldByID(ID)
            self.vocabularyController.executeMoveTargetOperation(field.getSequence())
            self.vocabularyController.setDisplayedObjectInSelectedMessageTable(field)
            self.updateSequenceProperties()
            self.netzob.getSignalsManager().emitSignal(SignalsManager.SIG_SEQUENCES_SINGLE_SELECTION)
        else:
            self.netzob.getSignalsManager().emitSignal(SignalsManager.SIG_SEQUENCES_NO_SELECTION)

    def sequenceListTreeView_button_press_event_cb(self, treeview, eventButton):
        if 1 > treeview.get_selection().count_selected_rows():
            return
        # Popup a contextual menu if right click
        if eventButton.type == Gdk.EventType.BUTTON_PRESS and eventButton.button == 3:
            (model, paths) = treeview.get_selection().get_selected_rows()

            layers = []
            for path in paths:
                # Retrieve the selected layerFields
                layer_id = model[path][VocabularyView.SEQUENCELISTSTORE_ID_COLUMN]
                if layer_id is not None:
                    layer = self.getCurrentProject().getVocabulary().getFieldByID(layer_id)
                    layers.append(layer)
                else:
                    return

            # Popup a contextual menu
            menuController = ContextualMenuOnLayerController(self.vocabularyController, layers)
            menuController.run(eventButton)
            return True  # To discard remaining signals (such as 'changed_cb')

################ TO BE FIXED
    def button_newview_cb(self, widget):
        self.focus = self.addSpreadSheet("empty", 0)
        self.focus.idsequence = None

    def button_closeview_cb(self, widget, spreadsheet):
        spreadsheet.destroy()

        #refresh focus
        if self.focus.get_object("spreadsheet") == spreadsheet:
            self.focus = None
