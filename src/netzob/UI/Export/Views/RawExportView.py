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

#+----------------------------------------------
#| Global Imports
#+----------------------------------------------
from gettext import gettext as _
from gi.repository import Gtk
import gi
gi.require_version('Gtk', '3.0')


#+----------------------------------------------
#| RawExportView:
#|     GUI for exporting results in raw mode
#+----------------------------------------------
class RawExportView(object):

    #+----------------------------------------------
    #| Constructor:
    #| @param netzob: the main netzob object
    #+----------------------------------------------
    def __init__(self):
        self.buildPanel()

        self.dialog = Gtk.Dialog(title=_("Export project as raw XML"), flags=0, buttons=None)
        self.dialog.show()
        self.dialog.vbox.pack_start(self.panel, True, True, 0)
        self.dialog.set_size_request(600, 400)

    def buildPanel(self):
        # First we create an VPaned which hosts the two main children
        self.panel = Gtk.HBox()
        self.panel.show()

        # Create the symbol selection treeview
        self.buildSymbolTreeview()
        self.panel.pack_start(self.symbolTreeviewScroll, True, True, 0)

        # Create the hbox content in order to display dissector data
        bottomFrame = Gtk.Frame()
        bottomFrame.show()
        bottomFrame.set_size_request(450, -1)
        self.panel.add(bottomFrame)
        sw = Gtk.ScrolledWindow()
        sw.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.textarea = Gtk.TextView()
        self.textarea.get_buffer().create_tag("normalTag", family="Courier")
        self.textarea.show()
        self.textarea.set_editable(False)
        sw.add(self.textarea)
        sw.show()
        bottomFrame.add(sw)

    def buildSymbolTreeview(self):
        # Tree store contains:
        # str : text (symbol Name)
        # str : color foreground
        # str : color background
        self.treestore = Gtk.TreeStore(str, str, str, str)
        self.symbolTreeview = Gtk.TreeView(self.treestore)

        # Symbol list
        self.symbolTreeviewScroll = Gtk.ScrolledWindow()
        self.symbolTreeviewScroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.symbolTreeviewScroll.show()
        self.symbolTreeviewScroll.add(self.symbolTreeview)

        lvcolumn = Gtk.TreeViewColumn(_("Symbols"))
        lvcolumn.set_sort_column_id(1)
        cell = Gtk.CellRendererText()
        lvcolumn.pack_start(cell, True)
        cell.set_property('background-set', True)
        cell.set_property('foreground-set', True)
        lvcolumn.add_attribute(cell, "text", 1)
        lvcolumn.add_attribute(cell, "foreground", 2)
        lvcolumn.add_attribute(cell, "background", 3)
        self.symbolTreeview.append_column(lvcolumn)
        self.symbolTreeview.show()
