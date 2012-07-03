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

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+

from netzob.Common.Plugins.Importers.AbstractImporterView import AbstractImporterView

class PCAPImporterView(AbstractImporterView):
    """View of PCAP importer plugin"""

    def __init__(self, controller):
        super(PCAPImporterView, self).__init__(controller)

        # Import and add configuration widget
        self.builderConfWidget = Gtk.Builder()
        curDir = os.path.dirname(__file__)
        self.builderConfWidget.add_from_file(os.path.join(curDir, "PCAPImportConfigurationWidget.glade"))
        self._getObjects(self.builderConfWidget, ["pcapConfigurationBox",
                                                  "filterEntry"])
        self.builderConfWidget.connect_signals(self.controller)
        self.setImportConfigurationWidget(self.pcapConfigurationBox)

        # Configure treeview
        def add_text_column(text, modelColumn):
            column = Gtk.TreeViewColumn(text)
            column.pack_start(cell, True)
            column.add_attribute(cell, "text", modelColumn)
            column.set_sort_column_id(modelColumn)
            self.listTreeView.append_column(column)

        self.listListStore = Gtk.ListStore(
                str, 'gboolean', str, str, str, str, str, str)
        self.listTreeView.set_model(self.listListStore)
        toggleCellRenderer = Gtk.CellRendererToggle()
        toggleCellRenderer.set_activatable(True)
        toggleCellRenderer.connect("toggled", self.controller.selectMessage)
        # Selected column
        column = Gtk.TreeViewColumn()
        column.pack_start(toggleCellRenderer, True)
        column.add_attribute(toggleCellRenderer, "active", 1)
        self.listTreeView.append_column(column)
        cell = Gtk.CellRendererText()
        add_text_column("Protocol", 2)
        add_text_column("Source IP", 3)
        add_text_column("Destination IP", 4)
        add_text_column("Source Port", 5)
        add_text_column("Destination Port", 6)
        add_text_column("Payload", 7)
