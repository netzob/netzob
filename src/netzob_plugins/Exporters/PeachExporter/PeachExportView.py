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
#| Global Imports                                                            |
#+---------------------------------------------------------------------------+
from gettext import gettext as _
import gtk
import pygtk
pygtk.require('2.0')

#+---------------------------------------------------------------------------+
#| Local Imports                                                             |
#+---------------------------------------------------------------------------+
from netzob.UI.NetzobWidgets import NetzobLabel, NetzobComboBoxEntry


class PeachExportView:
    """
    PeachExportView:
        GUI for exporting results in Peach pit XML.

    """

    def __init__(self):
        """
            Constructor of PeachExportView:

        """
        self.buildPanel()

        self.dialog = gtk.Dialog(title=_("Export project as Peach pit XML"), flags=0, buttons=None)
        self.dialog.show()
        self.dialog.vbox.pack_start(self.panel, True, True, 0)
        self.dialog.set_size_request(600, 400)

    def buildPanel(self):
        """
            buildPanel:
                Build and display the Peach exporter GUI.

        """
        # First we create a VPaned which hosts the two main children
        self.panel = gtk.VPaned()
        self.panel.show()

        self.hpanel = gtk.HPaned()
        self.hpanel.show()

        # Create the symbol selection treeview
        self.buildSymbolTreeview()
        self.hpanel.add1(self.symbolTreeviewScroll)

        # Create the hbox content in order to display dissector data
        bottomFrame = gtk.Frame()
        bottomFrame.show()
        bottomFrame.set_size_request(450, -1)
        self.hpanel.add2(bottomFrame)
        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.textarea = gtk.TextView()
        self.textarea.get_buffer().create_tag("normalTag", family="Courier")
        self.textarea.show()
        self.textarea.set_editable(False)
        sw.add(self.textarea)
        sw.show()
        bottomFrame.add(sw)

        self.buildOptionsView()
        self.panel.add1(self.hpanel)
        self.panel.pack2(self.optionsTable, resize=False)
        self.panel.set_position(350)

    def buildSymbolTreeview(self):
        """
            builSymbolTreeView:
                Build a symbol tree view in the GUI (left column). This tree view lists all the symbol of the project.

        """
        # Tree store contains:
        # str : text (symbol Name)
        # str : text (score)
        # str : color foreground
        # str : color background
        self.treestore = gtk.TreeStore(str, str, str, str, str)
        self.symbolTreeview = gtk.TreeView(self.treestore)

        # Symbol list
        self.symbolTreeviewScroll = gtk.ScrolledWindow()
        self.symbolTreeviewScroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.symbolTreeviewScroll.show()
        self.symbolTreeviewScroll.add(self.symbolTreeview)

        lvcolumn = gtk.TreeViewColumn(_("Symbols"))
        lvcolumn.set_sort_column_id(1)
        cell = gtk.CellRendererText()
        lvcolumn.pack_start(cell, True)
        cell.set_property('background-set', True)
        cell.set_property('foreground-set', True)
        lvcolumn.set_attributes(cell, text=1, foreground=3, background=4)
        self.symbolTreeview.append_column(lvcolumn)
        self.symbolTreeview.show()

    def buildOptionsView(self):
        """
            buildOptionsView:
                Build the options view (bottom of the main view). This view proposes some options to sharpen the fuzzing.
        """
        self.optionsTable = gtk.Table(rows=1, columns=3, homogeneous=False)
        self.optionsTable.show()

        label = NetzobLabel(_("Fuzzing based on : "))
        self.comboFuzzingBase = NetzobComboBoxEntry()
        self.comboFuzzingBase.append_text("Variable")
        self.comboFuzzingBase.append_text("Regex")
        self.comboFuzzingBase.set_active(0)
        self.optionsTable.attach(label, 0, 1, 0, 1, xoptions=gtk.FILL, yoptions=0, xpadding=2, ypadding=0)
        self.optionsTable.attach(self.comboFuzzingBase, 1, 2, 0, 1, xoptions=gtk.FILL, yoptions=0, xpadding=2, ypadding=0)

        self.exportButton = gtk.Button("Export")
        self.exportButton.show()
        self.optionsTable.attach(self.exportButton, 2, 3, 0, 1, xoptions=gtk.FILL, yoptions=0, xpadding=2, ypadding=0)
