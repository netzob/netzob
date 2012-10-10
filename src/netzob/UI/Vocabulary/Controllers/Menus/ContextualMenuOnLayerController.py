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
import logging
import time
import os

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+
from gi.repository import Gtk, Gdk, GObject
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GObject
from gi.repository import Pango

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.UI.Common.Controllers.CustomMathFilterController import CustomMathFilterController
from netzob.Common.ResourcesConfiguration import ResourcesConfiguration
from netzob.UI.Vocabulary.Views.Menus.ContextualMenuOnLayerView import ContextualMenuOnLayerView
from netzob.UI.NetzobWidgets import NetzobLabel
from netzob.Common.Type.TypeConvertor import TypeConvertor
from netzob.UI.Vocabulary.Controllers.PopupEditFieldController import PopupEditFieldController
from netzob.UI.Vocabulary.Controllers.Partitioning.SequenceAlignmentController import SequenceAlignmentController
from netzob.UI.Vocabulary.Controllers.Partitioning.ForcePartitioningController import ForcePartitioningController
from netzob.UI.Vocabulary.Controllers.Partitioning.SimplePartitioningController import SimplePartitioningController
from netzob.UI.Vocabulary.Controllers.Partitioning.SmoothPartitioningController import SmoothPartitioningController
from netzob.UI.Vocabulary.Controllers.Partitioning.ResetPartitioningController import ResetPartitioningController


class ContextualMenuOnLayerController(object):
    """Contextual menu on layer (visualization, etc.)"""

    def __init__(self, vocabularyController, layer):
        self.vocabularyController = vocabularyController
        self.layer = layer
        self._view = ContextualMenuOnLayerView(self)
        self.log = logging.getLogger(__name__)

    @property
    def view(self):
        return self._view

    def run(self, event):
        self._view.run(event)

    #+----------------------------------------------
    #| rightClickToChangeFormat:
    #|   Callback to change the field/symbol format
    #|   by doing a right click on it.
    #+----------------------------------------------
    def changeFormat_cb(self, event, aFormat):
        self.layer.setFormat(aFormat)
        self.vocabularyController.view.updateSelectedMessageTable()

    #+----------------------------------------------
    #| rightClickToChangeUnitSize:
    #|   Callback to change the field/symbol unitsize
    #|   by doing a right click on it.
    #+----------------------------------------------
    def changeUnitSize_cb(self, event, unitSize):
        self.layer.setUnitSize(unitSize)
        self.vocabularyController.view.updateSelectedMessageTable()

    #+----------------------------------------------
    #| rightClickToChangeSign:
    #|   Callback to change the field/symbol sign
    #|   by doing a right click on it.
    #+----------------------------------------------
    def changeSign_cb(self, event, sign):
        self.layer.setSign(sign)
        self.vocabularyController.view.updateSelectedMessageTable()

    #+----------------------------------------------
    #| rightClickToChangeEndianess:
    #|   Callback to change the field/symbol endianess
    #|   by doing a right click on it.
    #+----------------------------------------------
    def changeEndianess_cb(self, event, endianess):
        self.layer.setEndianess(endianess)
        self.vocabularyController.view.updateSelectedMessageTable()

    def applyMathematicFilter_cb(self, event, mathFilter):
        """Add the selected mathematics filter"""

        found = False
        for appliedFilter in self.layer.getMathematicFilters():
            if appliedFilter.getName() == mathFilter.getName():
                found = True
                break
        if found:
            self.layer.removeMathematicFilter(appliedFilter)
        else:
            self.layer.addMathematicFilter(mathFilter)

        self.layer.resetPartitioning()
        self.vocabularyController.view.updateSelectedMessageTable()

    def createCustomFilter_cb(self, event):
        """Callback executed when the user
        clicks on menu entry to create a custom filter"""
        customFilterController = CustomMathFilterController(self.vocabularyController, self.layer)
        customFilterController.run()

    def renameLayer_cb(self, widget):
        builder2 = Gtk.Builder()
        builder2.add_from_file(os.path.join(
            ResourcesConfiguration.getStaticResources(),
            "ui",
            "dialogbox.glade"))
        dialog = builder2.get_object("renamelayer")
        dialog.set_title("Rename the layer " + self.layer.getName())

        #button apply
        applybutton = builder2.get_object("button10")
        applybutton.set_sensitive(False)
        dialog.add_action_widget(applybutton, 0)
        #button cancel
        cancelbutton = builder2.get_object("button2")
        dialog.add_action_widget(cancelbutton, 1)
        #disable apply button if no text
        entry = builder2.get_object("entry3")
        entry.connect("changed", self.entry_disableButtonIfEmpty_cb, applybutton)
        #run the dialog window and wait for the result
        result = dialog.run()

        if (result == 0):
            #apply
            newLayerName = entry.get_text()
            self.log.debug(_("Renamed layer {0} to {1}").format(self.layer.getName(), newLayerName))
            currentProject = self.vocabularyController.netzob.getCurrentProject()
            currentProject.getVocabulary().getFieldByID(self.layer.getID()).setName(newLayerName)
            self.vocabularyController.view.updateLeftPanel()
            self.vocabularyController.view.updateSelectedMessageTable()
            dialog.destroy()
        if (result == 1):
            #cancel
            dialog.destroy()

    def entry_disableButtonIfEmpty_cb(self, widget, button):
        if(len(widget.get_text()) > 0):
            button.set_sensitive(True)
        else:
            button.set_sensitive(False)

    def deleteLayer_cb(self, widget):
        # Verify if selected layer is the top layer (i.e. the symbol)
        if self.layer == self.layer.getSymbol().getField():
            # If so, delete the symbol and its messages
            currentProject = self.vocabularyController.netzob.getCurrentProject()
            currentVocabulary = currentProject.getVocabulary()
            for mess in self.layer.getSymbol().getMessages():
                currentVocabulary.removeMessage(mess)
            currentVocabulary.removeSymbol(self.layer.getSymbol())
            self.vocabularyController.view.emptyMessageTableDisplayingSymbols([self.layer.getSymbol()])
        else:
            self.layer.flattenLocalFields()
        self.vocabularyController.view.updateLeftPanel()
        self.vocabularyController.view.updateSelectedMessageTable()

    def sequenceAlignment_cb(self, action):
        sequence_controller = SequenceAlignmentController(self.vocabularyController, [self.layer])
        sequence_controller.run()

    def forcePartitionment_cb(self, action):
        force_controller = ForcePartitioningController(self.vocabularyController, [self.layer])
        force_controller.run()

    def simplePartitionment_cb(self, action):
        simple_controller = SimplePartitioningController(self.vocabularyController, [self.layer])
        simple_controller.run()

    def smoothPartitionment_cb(self, action):
        smooth_controller = SmoothPartitioningController(self.vocabularyController, [self.layer])
        smooth_controller.run()

    def resetPartitionment_cb(self, action):
        reset_controller = ResetPartitioningController(self.vocabularyController, [self.layer])
        reset_controller.run()
