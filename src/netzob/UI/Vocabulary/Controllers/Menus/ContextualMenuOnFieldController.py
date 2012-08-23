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
from netzob.Common.Type.TypeConvertor import TypeConvertor
from netzob.UI.Vocabulary.Controllers.PopupEditFieldController import PopupEditFieldController


class ContextualMenuOnFieldController(object):
    """Contextual menu on field (copy to clipboard, message
    visualization, etc.)"""

    def __init__(self, vocabularyController, symbol, message, field):
        self.vocabularyController = vocabularyController
        self.symbol = symbol
        self.message = message
        self.field = field
        self._view = ContextualMenuOnFieldView(self)
        self.log = logging.getLogger(__name__)

    @property
    def view(self):
        return self._view

    def run(self, event):
        self._view.run(event)

    #+----------------------------------------------
    #| rightClickToCopyToClipboard:
    #|   Copy the message to the clipboard
    #+----------------------------------------------
    def copyToClipboard_cb(self, event, aligned, encoded, fieldLevel):
        if aligned is False:  # Copy the entire raw message
            text = self.message.getStringData()
            self.vocabularyController.netzob.clipboard.set_text(text, -1)
        elif fieldLevel is False:  # Copy the entire aligned message
            text = self.message.applyAlignment(styled=False, encoded=encoded)
            text = str(text)
            self.vocabularyController.netzob.clipboard.set_text(text, -1)
        else:  # Just copy the selected field
            text = self.message.applyAlignment(styled=False, encoded=encoded)[self.field.getIndex()]
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
        cells = self.symbol.getUniqValuesByField(self.field)
        tmpDomain = set()
        for cell in cells:
            tmpDomain.add(TypeConvertor.encodeNetzobRawToGivenType(cell, self.field.getFormat()))
        domain = sorted(tmpDomain)

        dialog = Gtk.Dialog(title=_("Domain of definition for the column ") + self.field.getName(), flags=0, buttons=None)

        # Text view containing domain of definition
        ## ListStore format:
        # str: symbol.id
        treeview = Gtk.TreeView(Gtk.ListStore(str))
        treeview.show()

        cell = Gtk.CellRendererText()
        cell.set_sensitive(True)
        cell.set_property('editable', True)

        column = Gtk.TreeViewColumn(_("Column ") + str(self.field.getIndex()))
        column.pack_start(cell, True)
        column.add_attribute(cell, "text", 0)

        treeview.append_column(column)

        for elt in domain:
            treeview.get_model().append([elt])

        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroll.show()
        scroll.add(treeview)

        dialog.set_size_request(500, 300)
        dialog.vbox.pack_start(scroll, True, True, 0)
        dialog.show()

    def applyMathematicalFilter_cb(self, object, filter):
        appliedFilters = self.field.getMathematicFilters()
        found = False
        for appliedFilter in appliedFilters:
            if appliedFilter.getName() == filter.getName():
                found = True
        if found:
            #deactivate the selected filter
            self.field.removeMathematicFilter(filter)
        else:
            self.field.addMathematicFilter(filter)
        self.vocabularyController.view.updateSelectedMessageTable()

    def displayPopupToEditField_cb(self, event):
        popup = PopupEditFieldController(self.vocabularyController, self.field)
        popup.run()
