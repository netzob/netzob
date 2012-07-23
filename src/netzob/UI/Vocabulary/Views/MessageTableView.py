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
import os

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+
from gi.repository import Gtk, Pango
import gi
gi.require_version('Gtk', '3.0')

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.NetzobException import NetzobException
from netzob.Common.ResourcesConfiguration import ResourcesConfiguration

# IDEA : Add a picture in the header to tell whether the symbol
# is locked or not

class MessageTableView(object):

    MAX_DISPLAYED_FIELDS = 200

    def __init__(self, controller):
        self.controller = controller
        self.builder = Gtk.Builder()
        self.builder.add_from_file(os.path.join(
            ResourcesConfiguration.getStaticResources(),
            "ui",
            "MessageTable.glade"))
        self._getObjects(self.builder, ["messageTableTreeView",
                                        "messageTableBox",
                                        "symbolNameLabel"])
        self.builder.connect_signals(self.controller)
        self.displayedSymbol = None
        self.messageTableTreeView.set_rules_hint(True)

    def _getObjects(self, builder, objectsList):
        for object in objectsList:
            setattr(self, object, builder.get_object(object))

    def _setupMessageTreeView(self):
        self._clearTreeView()
        ## Set up the message TreeView
        # Each field is displayed in its own column
        if self.displayedSymbol is None:
            return
        numOfColumns = min(self.MAX_DISPLAYED_FIELDS,
                           len(self.displayedSymbol.getFields()))
        for colIdx in range(0, numOfColumns):
            self.messageTableTreeView.append_column(self._makeTreeViewColumn(colIdx))

    def _makeTreeViewColumn(self, i):
        # Cell renderer used to display field of messages         
        markupCellRenderer = Gtk.CellRendererText()
        markupCellRenderer.set_property("font", "monospace")
        #markupCellRenderer.set_property("height", 16)
        markupCellRenderer.set_padding(2, 2)
        # GtkTreeViewColumn object
        name = self.displayedSymbol.getFieldByIndex(i).getName()
        treeViewColumn = Gtk.TreeViewColumn(name)
        treeViewColumn.pack_start(markupCellRenderer, True)
        treeViewColumn.add_attribute(markupCellRenderer, "markup", i)
        treeViewColumn.set_resizable(True)
        return treeViewColumn

    def _clearTreeView(self):
        for column in self.messageTableTreeView.get_columns():
            self.messageTableTreeView.remove_column(column)
        self.messageTableTreeView.set_model(None)

    def setDisplayedSymbol(self, symbol):
        """Memorizes symbol as the displayed symbol in this message table"""
        self.displayedSymbol = symbol
        self.update()

    def getDisplayedSymbol(self):
        return self.displayedSymbol

    def updateMessageTableTreeView(self):
        self._setupMessageTreeView()
        if self.displayedSymbol is None:
            return
        splitMessagesMatrix = []
        # Split every message 
        for message in self.displayedSymbol.getMessages():
            try:
                splitMessage = message.applyAlignment(styled=True, encoded=True)
            except NetzobException:
                self.log.warn("Impossible to display one of messages since it "
                              + "cannot be cut according to the computed regex.")
                self.log.warn("Message : " + str(message.getStringData()))
                continue  # We don't display the message in error
            splitMessagesMatrix.append(splitMessage)

        # Setup listStore
        numOfColumns = min(self.MAX_DISPLAYED_FIELDS,
                           len(self.displayedSymbol.getFields()))
        listStoreTypes = [str] * numOfColumns
        self.messageTableListStore = Gtk.ListStore(*listStoreTypes)
        self.messageTableTreeView.set_model(self.messageTableListStore)
        # Fill listStore with split messages
        for splitMessage in splitMessagesMatrix:
            self.messageTableListStore.append(splitMessage)

    def updateSymbolNameLabel(self):
        if self.displayedSymbol is None:
            symbolName = "Empty Message Table"
        else:
            symbolName = self.displayedSymbol.getName()
        self.symbolNameLabel.set_text(symbolName)

    def setSelected(self, selected):
        if selected:
            boldFont = Pango.FontDescription()
            boldFont.set_weight(Pango.Weight.SEMIBOLD)
            self.symbolNameLabel.modify_font(boldFont)
        else:
            selection = self.messageTableTreeView.get_selection()
            if selection is not None:
                selection.unselect_all()
            normalFont = Pango.FontDescription()
            normalFont.set_weight(Pango.Weight.NORMAL)
            self.symbolNameLabel.modify_font(normalFont)

    def update(self):
        self.updateSymbolNameLabel()
        self.updateMessageTableTreeView()

    def getPanel(self):
        return self.messageTableBox

    def destroy(self):
        self.messageTableBox.destroy()
