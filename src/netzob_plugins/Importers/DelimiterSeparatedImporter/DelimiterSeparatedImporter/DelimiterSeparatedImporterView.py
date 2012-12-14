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
from gettext import gettext as _

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+
from gi.repository import Gtk
import gi
from DelimiterSeparatedImporter import DelimiterSeparatedImporter
gi.require_version('Gtk', '3.0')

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.Plugins.Importers.AbstractFileImporterView import AbstractFileImporterView


class DelimiterSeparatedImporterView(AbstractFileImporterView):
    """View of file importer plugin"""

    # Name of the associated glade file
    GLADE_FILENAME = "FileImportConfigurationWidget.glade"

    def __init__(self, plugin, controller):
        super(DelimiterSeparatedImporterView, self).__init__(plugin, controller)

        # Import and add configuration widget
        self.builderConfWidget = Gtk.Builder()
        curDir = os.path.dirname(__file__)
        self.builderConfWidget.add_from_file(os.path.join(self.getPlugin().getPluginStaticResourcesPath(), "ui", DelimiterSeparatedImporterView.GLADE_FILENAME))
        self._getObjects(self.builderConfWidget, ["fileConfigurationBox", "separatorEntry", "keepSeparatorComboBox", "keepSeparatorListStore", ""])
        self.builderConfWidget.connect_signals(self.controller)
        self.setDialogTitle(_("Import messages from raw file"))
        self.setImportConfigurationWidget(self.fileConfigurationBox)

        # Configure treeview
        def add_text_column(text, modelColumn):
            column = Gtk.TreeViewColumn(text)
            column.pack_start(cell, True)
            column.add_attribute(cell, "text", modelColumn)
            column.set_sort_column_id(modelColumn)
            self.listTreeView.append_column(column)

        # Configure the list of "strategy" with separators
        self.keepSeparatorListStore.append([DelimiterSeparatedImporter.SEPARATOR_STRATEGY_DELETE])
        self.keepSeparatorListStore.append([DelimiterSeparatedImporter.SEPARATOR_STRATEGY_KEEP_START])
        self.keepSeparatorListStore.append([DelimiterSeparatedImporter.SEPARATOR_STRATEGY_KEEP_END])
        self.keepSeparatorComboBox.set_active(0)

        self.listListStore = Gtk.ListStore('gboolean', str, str)
        self.listTreeView.set_model(self.listListStore)
        toggleCellRenderer = Gtk.CellRendererToggle()
        toggleCellRenderer.set_activatable(True)
        toggleCellRenderer.connect("toggled", self.controller.selectMessage)
        # Selected column
        column = Gtk.TreeViewColumn()
        column.pack_start(toggleCellRenderer, True)
        column.add_attribute(toggleCellRenderer, "active", 0)
        self.listTreeView.append_column(column)
        cell = Gtk.CellRendererText()
        add_text_column(_("ID"), 1)
        add_text_column(_("Contents"), 2)
