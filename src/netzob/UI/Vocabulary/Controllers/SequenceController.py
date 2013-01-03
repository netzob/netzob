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
from netzob.UI.Vocabulary.Views.SequenceView import SequenceView
from netzob.Common.ResourcesConfiguration import ResourcesConfiguration
from netzob.Common.Sequence import Sequence
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
#| SequenceController:
#|     Controller for sequence rendering
#+----------------------------------------------
class SequenceController(object):

    def __init__(self, netzob):
        self.netzob = netzob
        self._view = SequenceView(self)
        self.log = logging.getLogger(__name__)

        self.view.sequenceListTreeViewSelection.set_select_function(self.sequence_list_selection_function, None)
        self.sequence_list_set_selection = True

    @property
    def view(self):
        return self._view

    ## Sequence List toolbar callbacks
    def selectAllSequencesButton_clicked_cb(self, toolButton):
        """
        select all the sequence in the sequence list
        @type  widget: boolean
        @param widget: if selected sequence
        """
        for row in self.view.sequenceListStore:
            row[self.view.SEQUENCELISTSTORE_SELECTED_COLUMN] = True
        self.view.updateSequenceListToolbar()

    def unselectAllSequencesButton_clicked_cb(self, toolButton):
        """
        unselect all the sequence in the sequence list
        @type  widget: boolean
        @param widget: if selected sequence
        """
        for row in self.view.sequenceListStore:
            row[self.view.SEQUENCELISTSTORE_SELECTED_COLUMN] = False
        self.view.updateSequenceListToolbar()

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
            self.view.updateLeftPanel()
            dialog.destroy()
        if (result == 1):
            dialog.destroy()

    def entry_disableButtonIfEmpty_cb(self, widget, button):
        if(len(widget.get_text()) > 0):
            button.set_sensitive(True)
        else:
            button.set_sensitive(False)

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
            self.view.emptyMessageTableDisplayingSequences([sym])
        # Update view
        self.view.updateLeftPanel()
        self.view.updateSelectedMessageTable()

    def newSequenceTableButton_clicked_cb(self, toolButton):
        if self.getCurrentProject() is None:
            NetzobErrorMessage(_("No project selected."))
            return
        self.view.addMessageTable()

    def toggleSequenceCellRenderer_toggled_cb(self, widget, buttonid):
        # Update this flag so the line won't be selected.
        self.sequence_list_set_selection = False
        model = self.view.sequenceListStore
        model[buttonid][0] = not model[buttonid][0]
        self.view.updateSequenceListToolbar()

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
            self.executeMoveTargetOperation(field.getSequence())
            self.view.setDisplayedFieldInSelectedMessageTable(field)
            self._view.updateSequenceProperties()
            self.getSignalsManager().emitSignal(SignalsManager.SIG_SEQUENCES_SINGLE_SELECTION)
        else:
            self.getSignalsManager().emitSignal(SignalsManager.SIG_SEQUENCES_NO_SELECTION)

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
            menuController = ContextualMenuOnLayerController(self, layers)
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
