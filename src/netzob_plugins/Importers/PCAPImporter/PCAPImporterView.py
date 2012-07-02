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

class PCAPImporterView(object):
    """View of PCAP importer plugin"""

    def __init__(self, controller):
        self.builder = Gtk.Builder()
        curDir = os.path.dirname(__file__)
        self.builder.add_from_file(os.path.join(curDir, "PCAPImportView.glade"))
        self.controller = controller
        self._getObjects(["pcapImportDialog", "openFileEntry", "filterEntry",
            "listTreeView", "detailTextView", "cancelButton", "warnAlign",
            "warnLabel", "displayCountLabel", "selectCountLabel", "importButton"])
        # Change packet details textview font
        monoFontDesc = Pango.FontDescription("monospace")
        self.detailTextView.modify_font(monoFontDesc)
        self.builder.connect_signals(controller)
        self.cancelButton.connect_object("clicked", Gtk.Widget.destroy,
            self.pcapImportDialog)
        self.initPacketTreeview()

    def _getObjects(self, objectsList):
        for object in objectsList:
            setattr(self, object, self.builder.get_object(object))

    def initPacketTreeview(self):
        self.listListStore = Gtk.ListStore(
                str, 'gboolean', str, str, str, str, str, str)
        self.listTreeView.set_model(self.listListStore)
        selection = self.listTreeView.get_selection()
        cell = Gtk.CellRendererText()
        toggleCellRenderer = Gtk.CellRendererToggle()
        toggleCellRenderer.set_activatable(True)
        toggleCellRenderer.connect("toggled", self.controller.selectPacket)
        # Col selected
        column = Gtk.TreeViewColumn()
        column.pack_start(toggleCellRenderer, True)
        column.add_attribute(toggleCellRenderer, "active", 1)
        self.listTreeView.append_column(column)
        # Col proto
        column = Gtk.TreeViewColumn('Protocol')
        column.pack_start(cell, True)
        column.add_attribute(cell, "text", 2)
        self.listTreeView.append_column(column)
        # Col IP.src
        column = Gtk.TreeViewColumn('Source IP')
        column.pack_start(cell, True)
        column.add_attribute(cell, "text", 3)
        self.listTreeView.append_column(column)
        # Col IP.dst
        column = Gtk.TreeViewColumn('Destination IP')
        column.pack_start(cell, True)
        column.add_attribute(cell, "text", 4)
        self.listTreeView.append_column(column)
        # Col {TCP,UDP}.sport
        column = Gtk.TreeViewColumn('Source Port')
        column.pack_start(cell, True)
        column.add_attribute(cell, "text", 5)
        self.listTreeView.append_column(column)
        # Col {TCP,UDP}.dport
        column = Gtk.TreeViewColumn('Destination Port')
        column.pack_start(cell, True)
        column.add_attribute(cell, "text", 6)
        self.listTreeView.append_column(column)
        # Col Payload
        column = Gtk.TreeViewColumn('Payload')
        column.pack_start(cell, True)
        column.add_attribute(cell, "text", 7)
        self.listTreeView.append_column(column)

    def run(self):
        self.pcapImportDialog.show_all()

    def showWarning(self, text):
        self.warnLabel.set_text(text)
        self.warnAlign.show_all()

    def hideWarning(self):
        self.warnAlign.hide()

    def clearPacketView(self):
        self.listListStore.clear()
        self.detailTextView.get_buffer().set_text("")

    def updateCounters(self, displayedPackets, selectedPackets):
        if selectedPackets == 0:
            self.importButton.set_sensitive(False)
        else:
            self.importButton.set_sensitive(True)

        self.displayCountLabel.set_text(str(displayedPackets))
        self.selectCountLabel.set_text(str(selectedPackets))
