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
from netzob.Common.Plugins.Importers.AbstractImporterView import AbstractImporterView

class OSpyImporterView(AbstractImporterView):
    def __init__(self, controller):
        super(OSpyImporterView, self).__init__(controller)

        # Import and add configuration widget
        self.builderConfWidget = Gtk.Builder()
        curDir = os.path.dirname(__file__)
        self.builderConfWidget.add_from_file(os.path.join(curDir, "OSpyImportConfigurationWidget.glade"))
        self._getObjects(self.builderConfWidget, ["applyAlign"])
        self.builderConfWidget.connect_signals(self.controller)
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
        add_text_column("ID", 1)
        add_text_column("Source Address", 2)
        add_text_column("Destination Address", 3)
        add_text_column("Protocol", 4)
        add_text_column("Source Port", 5)
        add_text_column("Destination Port", 6)
        add_text_column("Payload", 7)
