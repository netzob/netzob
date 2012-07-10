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
import logging
from gi.repository import Gtk
import uuid

#+----------------------------------------------
#| Local Imports
#+----------------------------------------------
from netzob.UI.Vocabulary.Views.AbstractViewGenerator import AbstractViewGenerator


#+----------------------------------------------
#| TreeSymbolView:
#+----------------------------------------------
class TreeSymbolView(AbstractViewGenerator):

    #+----------------------------------------------
    #| Constructor:
    #+----------------------------------------------
    def __init__(self, netzob):
        self.netzob = netzob
        self.treeview = None
        self.treestore = None
        self.scroll = None
        self.log = logging.getLogger('netzob.UI.Vocabulary.Views.TreeSymbolView.py')
        AbstractViewGenerator.__init__(self, uuid.uuid4(), "Symbols")
        self.buildPanel()

    #+----------------------------------------------
    #| buildPanel:
    #| builds and configures the treeview
    #+----------------------------------------------
    def buildPanel(self):
        # Tree store contains:
        # str : text (symbol Name)
        # str : text (score)
        # str : color foreground
        # str : color background
        self.treestore = Gtk.TreeStore(str, str, str, str, str)
        self.treeview = Gtk.TreeView(self.treestore)

        # messages list
        self.scroll = Gtk.ScrolledWindow()
        self.scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.scroll.show()
        self.scroll.set_size_request(200, 300)
        self.scroll.add(self.treeview)

        self.lvcolumn = Gtk.TreeViewColumn(_("Symbols"))
        self.lvcolumn.set_sort_column_id(1)
        cell = Gtk.CellRendererText()
        cell.set_property('background-set', True)
        self.lvcolumn.pack_start(cell, True)
        self.lvcolumn.add_attribute(cell, "markup", 1)
        self.lvcolumn.add_attribute(cell, "background", 4)
        self.treeview.append_column(self.lvcolumn)
        self.treeview.show()

    #+----------------------------------------------
    #| GETTERS:
    #+----------------------------------------------
    def getTreeview(self):
        return self.treeview

    def getScrollLib(self):
        return self.scroll

    def getWidget(self):
        return self.scroll
