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
import uuid

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
from netzob.UI.Vocabulary.Views.Menus.ContextualMenuOnFieldView import ContextualMenuOnFieldView
from netzob.UI.NetzobWidgets import NetzobLabel
from netzob.Common.Symbol import Symbol
from netzob.Common.Field import Field
from netzob.Common.Models.RawMessage import RawMessage
from netzob.UI.Vocabulary.Controllers.PopupEditFieldController import PopupEditFieldController
from netzob.UI.Vocabulary.Controllers.FieldAnalysisController import FieldAnalysisController
from netzob.UI.Vocabulary.Controllers.VariableController import VariableTreeController
from netzob.UI.Import.Controllers.ConfirmImportMessagesController import ConfirmImportMessagesController
from netzob.UI.NetzobWidgets import NetzobErrorMessage


class ContextualMenuOnFieldController(object):
    """Contextual menu on field (copy to clipboard, message
    visualization, etc.)"""

    def __init__(self, vocabularyController, layer, messages, field):
        self.vocabularyController = vocabularyController
        self.layer = layer
        self.messages = messages
        self.field = field
        self._view = ContextualMenuOnFieldView(self)
        self.log = logging.getLogger(__name__)

    @property
    def view(self):
        return self._view

    def run(self, event):
        self._view.run(event)

    def getSymbol(self):
        return self.field.getSymbol()

    #+----------------------------------------------
    #| rightClickToCopyToClipboard:
    #|   Copy the message to the clipboard
    #+----------------------------------------------
    def copyToClipboard_cb(self, event, aligned, encoded, fieldLevel):
        if aligned is False:  # Copy the entire raw message
            text = ""
            for message in self.messages:
                text += message.getStringData() + "\n"
            self.vocabularyController.netzob.clipboard.set_text(text, -1)
        elif fieldLevel is False:  # Copy the entire aligned message
            text = ""
            for message in self.messages:
                tmp = message.applyAlignment(styled=False, encoded=encoded)
                text += str(tmp) + "\n"
            self.vocabularyController.netzob.clipboard.set_text(text, -1)
        else:  # Just copy the selected field
            text = ""
            for message in self.messages:
                text += str(message.applyAlignment(styled=False, encoded=encoded)[self.field.getIndex()]) + "\n"
            self.vocabularyController.netzob.clipboard.set_text(text, -1)

    #+----------------------------------------------
    #| rightClickToChangeFormat:
    #|   Callback to change the field/symbol format
    #|   by doing a right click on it.
    #+----------------------------------------------
    def changeFormat_cb(self, event, aFormat):
        self.field.setFormat(aFormat)
        self.vocabularyController.view.updateSelectedMessageTable()

    #+----------------------------------------------
    #| rightClickToChangeUnitSize:
    #|   Callback to change the field/symbol unitsize
    #|   by doing a right click on it.
    #+----------------------------------------------
    def changeUnitSize_cb(self, event, unitSize):
        self.field.setUnitSize(unitSize)
        self.vocabularyController.view.updateSelectedMessageTable()

    #+----------------------------------------------
    #| rightClickToChangeSign:
    #|   Callback to change the field/symbol sign
    #|   by doing a right click on it.
    #+----------------------------------------------
    def changeSign_cb(self, event, sign):
        self.field.setSign(sign)
        self.vocabularyController.view.updateSelectedMessageTable()

    #+----------------------------------------------
    #| rightClickToChangeEndianess:
    #|   Callback to change the field/symbol endianess
    #|   by doing a right click on it.
    #+----------------------------------------------
    def changeEndianess_cb(self, event, endianess):
        self.field.setEndianess(endianess)
        self.vocabularyController.view.updateSelectedMessageTable()

    #+----------------------------------------------
    #| rightClickDomainOfDefinition:
    #|   Retrieve the domain of definition of the selected column
    #+----------------------------------------------
    def displayDomainOfDefinition_cb(self, event):
        controller = FieldAnalysisController(self.vocabularyController, self.field)
        controller.run()

    def applyTransformationFunction_cb(self, object, function):
        appliedFunctions = self.field.getTransformationFunctions()
        found = False
        for appliedFunction in appliedFunctions:
            if appliedFunction.getName() == function.getName():
                found = True
        if found:
            #deactivate the selected function
            self.field.removeTransformationFunction(function)
        else:
            self.field.addTransformationFunction(function)
        self.vocabularyController.view.updateSelectedMessageTable()

    def displayPopupToCreateLayer_cb(self, event):
        # If fields header are selected, we get it
        selectedFields = self.vocabularyController.view.selectedMessageTable.treeViewHeaderGroup.getSelectedFields()
        if selectedFields is None or len(selectedFields) == 0:
            # Either, we only consider the current field
            selectedFields = [self.field]
        # We retrieve the first and last fields selected
        firstField = selectedFields[0]
        lastField = selectedFields[0]
        for field in selectedFields:
            if field.getIndex() < firstField.getIndex():
                firstField = field
            if field.getIndex() > lastField.getIndex():
                lastField = field
        # Update selected fields to the entire range
        selectedFields = []
        for field in self.getSymbol().getExtendedFields():
            if field.getIndex() >= firstField.getIndex() and field.getIndex() <= lastField.getIndex():
                selectedFields.append(field)
        # Verify that selected field range does not overlap existing layers (i.e. if the selected fields have the same parent)
        parent = selectedFields[0].getParentField()
        for selectedField in selectedFields:
            if parent != selectedField.getParentField():
                NetzobErrorMessage(_("Selected field range overlaps existing layer."))
                return
        # Retrieve layer's name
        dialog = Gtk.Dialog(title=_("Layer creation"), flags=0, buttons=(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK))
        dialog.set_size_request(200, 50)
        label = Gtk.Label("Name:")
        entry = Gtk.Entry()
        dialog.vbox.pack_start(label, True, True, 0)
        dialog.vbox.pack_start(entry, True, True, 0)
        dialog.show_all()
        result = dialog.run()
        if (result == Gtk.ResponseType.OK):
            name = entry.get_text()
            dialog.destroy()
            if name == "":
                return
        else:
            dialog.destroy()
            return
        # Create a new layer
        regex = ""
        for selectedField in selectedFields:
            regex += "(?:" + selectedField.getRegex()[1:]
        fieldLayer = Field(str(name), "(" + regex + ")", self.getSymbol())
        index_newField = 999999
        parentField = None
        for selectedField in selectedFields:
            parentField = selectedField.getParentField()
            if parentField.getLocalFields().index(selectedField) < index_newField:
                index_newField = parentField.getLocalFields().index(selectedField)  # Retrieve the lowest index of the new fields
            fieldLayer.addField(selectedField)
            parentField.getLocalFields().remove(selectedField)
        parentField.getLocalFields().insert(index_newField, fieldLayer)
#        self.getSymbol().getField().addField(fieldLayer, index_newField)
        self.vocabularyController.view.updateLeftPanel()

    def displayPopupToEditField_cb(self, event):
        popup = PopupEditFieldController(self.vocabularyController, self.field)
        popup.run()

    def displayPopupToEditVariable_cb(self, event):
        creationPanel = VariableTreeController(self.vocabularyController.netzob, self.getSymbol(), self.field)

    def deleteMessage_cb(self, event):
        """Callback executed when the user requests
        to delete the current message"""
        for message in self.messages:
            self.getSymbol().removeMessage(message)
        self.vocabularyController.view.updateSelectedMessageTable()
        self.vocabularyController.view.updateLeftPanel()

    def exportSelectedFields_cb(self, event):
        # If fields header are selected, we get it
        fields = self.vocabularyController.view.selectedMessageTable.treeViewHeaderGroup.getSelectedFields()
        if fields is None or len(fields) == 0:
            # Either, we only consider the current field
            fields = [self.field]
        # We retrieve the first and last fields selected
        firstField = fields[0]
        lastField = fields[0]
        for field in fields:
            if field.getIndex() < firstField.getIndex():
                firstField = field
            if field.getIndex() > lastField.getIndex():
                lastField = field
        # We initialize the correct number of new messages
        newMessages = []
        for message in self.getSymbol().getMessages():
            mUuid = str(uuid.uuid4())
            newMessages.append(RawMessage(mUuid, message.getTimestamp(), ""))
        # We concatenate between the first and last cells
        for index in range(firstField.getIndex(), lastField.getIndex() + 1):
            cells = self.getSymbol().getFieldByIndex(index).getCells()
            for i in range(len(cells)):
                newMessages[i].setData(str(newMessages[i].getStringData()) + str(cells[i]))
        # We create a new symbol and register it
        currentWorkspace = self.vocabularyController.getCurrentWorkspace()
        currentProject = self.vocabularyController.netzob.getCurrentProject()
        confirmController = ConfirmImportMessagesController(currentWorkspace, currentProject, "RAW", newMessages)
        confirmController.run()
        # Update UI
        self.vocabularyController.view.updateSelectedMessageTable()
        self.vocabularyController.view.updateLeftPanel()
