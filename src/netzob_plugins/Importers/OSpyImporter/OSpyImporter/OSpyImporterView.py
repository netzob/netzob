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
gi.require_version('Gtk', '3.0')

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.Plugins.Importers.AbstractFileImporterView import AbstractFileImporterView


class OSpyImporterView(AbstractFileImporterView):

    GLADE_FILENAME = "OSpyImportConfigurationWidget.glade"

    def __init__(self, plugin, controller):
        super(OSpyImporterView, self).__init__(plugin, controller)

        # Import and add configuration widget
        self.builderConfWidget = Gtk.Builder()
        curDir = os.path.dirname(__file__)
        gladePath = os.path.join(self.getPlugin().getPluginStaticResourcesPath(), "ui", OSpyImporterView.GLADE_FILENAME)

        self.builderConfWidget.add_from_file(gladePath)
        self._getObjects(self.builderConfWidget, ["applyAlign"])
        self.builderConfWidget.connect_signals(self.controller)
        self.setDialogTitle(_("Import messages from oSpy file"))
        self.setImportConfigurationWidget(self.applyAlign)

        # Configure treeview
        def add_text_column(text, modelColumn):
            column = Gtk.TreeViewColumn(text)
            column.pack_start(cell, True)
            column.add_attribute(cell, "text", modelColumn)
            column.set_sort_column_id(modelColumn)
            self.listTreeView.append_column(column)

        self.listListStore = Gtk.ListStore('gboolean', str, str, str, str,
                                           str, str, str)
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
        add_text_column(_("Source Address"), 2)
        add_text_column(_("Destination Address"), 3)
        add_text_column(_("Protocol"), 4)
        add_text_column(_("Source Port"), 5)
        add_text_column(_("Destination Port"), 6)
        add_text_column(_("Payload"), 7)
