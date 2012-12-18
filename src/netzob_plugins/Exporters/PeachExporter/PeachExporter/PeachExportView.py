# -*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|          01001110 01100101 01110100 01111010 01101111 01100010            |
#|                                                                           |
#|               Netzob : Inferring communication protocols                  |
#+---------------------------------------------------------------------------+
#| Copyright (C) 2011 AMOSSYS                                                |
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
#| Standard library imports                                                  |
#+---------------------------------------------------------------------------+
from gettext import gettext as _

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+
from gi.repository import Gtk, Pango

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.UI.NetzobWidgets import NetzobLabel, NetzobComboBoxEntry
from netzob.Common.Plugins.Exporters.AbstractExporterView import AbstractExporterView


class PeachExportView(AbstractExporterView):
    """PeachExportView:
            GUI for exporting results in Peach pit XML.
    """

    def __init__(self):
        """Constructor of PeachExportView:
        """
        self.buildPanel()

        self.dialog = Gtk.Dialog(title=_("Export project as Peach pit XML"), flags=0, buttons=None)
        self.dialog.vbox.pack_start(self.panel, True, True, 0)
        self.dialog.set_size_request(800, 600)

    def buildPanel(self):
        """buildPanel:
                Build and display the Peach exporter GUI.
        """
        # First we create a VPaned which hosts the two main children
        self.panel = Gtk.VPaned()
        self.panel.show()

        self.hpanel = Gtk.HPaned()
        self.hpanel.show()

        # Create the symbol selection treeview
        self.buildSymbolTreeview()
        self.hpanel.add1(self.symbolTreeviewScroll)

        # Create the hbox content in order to display dissector data
        bottomFrame = Gtk.Frame()
        bottomFrame.show()
        self.hpanel.add2(bottomFrame)
        sw = Gtk.ScrolledWindow()
        self.textarea = Gtk.TextView()
        self.textarea.get_buffer().create_tag("normalTag", family="Courier")
        self.textarea.show()
        self.textarea.set_editable(False)
        sw.add(self.textarea)
        sw.show()
        bottomFrame.add(sw)

        self.buildOptionsView()
        self.panel.add1(self.hpanel)
        self.panel.pack2(self.optionsTable, resize=False)
        self.panel.set_position(550)
        self.hpanel.set_position(300)

    def buildSymbolTreeview(self):
        """builSymbolTreeView:
                Build a symbol tree view in the GUI (left column). This tree view lists all the symbol of the project.
        """
        # Tree store contains:
        # str : text (symbol Name)
        # str : color foreground
        # str : color background
        self.treestore = Gtk.TreeStore(str, str, str, str)
        self.symbolTreeview = Gtk.TreeView(self.treestore)

        renderer = Gtk.CellRendererText()
        columnSymbols = Gtk.TreeViewColumn(_("Fuzzer type"), renderer, text=1)
        self.symbolTreeview.append_column(columnSymbols)

        # Symbol list
        self.symbolTreeviewScroll = Gtk.ScrolledWindow()
        self.symbolTreeviewScroll.show()
        self.symbolTreeviewScroll.add(self.symbolTreeview)

        self.symbolTreeview.show()

    def buildOptionsView(self):
        """buildOptionsView:
                Build the options view (bottom of the main view). This view proposes some options to sharpen the fuzzing.
        """
        self.optionsTable = Gtk.Table(rows=1, columns=4, homogeneous=False)
        self.optionsTable.show()

        label = NetzobLabel(_("Fuzzing based on: "))
        self.comboFuzzingBase = NetzobComboBoxEntry()
        self.comboFuzzingBase.append_text("Variable")
        self.comboFuzzingBase.append_text("Regex")
        self.comboFuzzingBase.set_active(0)
        self.optionsTable.attach(label, 0, 1, 0, 1)
        self.optionsTable.attach(self.comboFuzzingBase, 1, 2, 0, 1)

        self.checkMutateStaticFields = Gtk.CheckButton(_("Mutate static fields"))
        self.checkMutateStaticFields.show()
        self.checkMutateStaticFields.set_active(True)
        self.optionsTable.attach(self.checkMutateStaticFields, 2, 3, 0, 1)

        self.exportButton = Gtk.Button(_("Export"))
        self.exportButton.show()
        self.optionsTable.attach(self.exportButton, 3, 4, 0, 1)
