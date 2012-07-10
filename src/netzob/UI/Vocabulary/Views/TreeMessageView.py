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
from gi.repository import Pango
from gi.repository import GObject
from gi.repository import Gtk
import glib
import uuid

#+----------------------------------------------
#| Local Imports
#+----------------------------------------------
from netzob.Common.NetzobException import NetzobException
from netzob.UI.Vocabulary.Views.AbstractViewGenerator import AbstractViewGenerator


#+----------------------------------------------
#| TreeMessageView:
#|     update and generates the treeview and its
#|     treestore dedicated to the messages
#+----------------------------------------------
class TreeMessageView(AbstractViewGenerator):

    #+----------------------------------------------
    #| Constructor:
    #| @param vbox : where the treeview will be hold
    #+----------------------------------------------
    def __init__(self, netzob):
        self.netzob = netzob
        self.log = logging.getLogger('netzob.UI.Vocabulary.Views.TreeMessageView.py')
        AbstractViewGenerator.__init__(self, uuid.uuid4(), "Messages")
        self.treeview = None
        self.treestore = None
        self.scroll = None
        self.currentColumns = []
        self.buildPanel()

    #+----------------------------------------------
    #| builds and configures the treeview
    #+----------------------------------------------
    def buildPanel(self):
        # creation of the treestore
        self.treestore = Gtk.TreeStore(str, str, str)
        # creation of the treeview
        self.treeview = Gtk.TreeView(self.treestore)
        self.treeview.set_reorderable(True)

        # maximum number of columns = 200
        for i_col in range(4, 204):
            # Define cellRenderer object
            textCellRenderer = Gtk.CellRendererText()
            textCellRenderer.set_property("size-points", 9)
            textCellRenderer.set_property('background-set', True)
            textCellRenderer.set_property('family', 'Courier')

            # Column Messages
            lvcolumn = Gtk.TreeViewColumn(str("#" + str(i_col - 4)))
            lvcolumn.set_resizable(True)
            lvcolumn.set_sort_column_id(i_col)
            lvcolumn.set_clickable(True)
            lvcolumn.pack_start(textCellRenderer, True)
            lvcolumn.add_attribute(textCellRenderer, "markup", i_col)
            lvcolumn.add_attribute(textCellRenderer, "background", 1)
            lvcolumn.add_attribute(textCellRenderer, "weight", 2)
            lvcolumn.add_attribute(textCellRenderer, "editable", 3)

#            self.treeview.append_column(lvcolumn)
            self.currentColumns.append(lvcolumn)

        self.treeview.show()
        self.treeview.set_reorderable(True)
        self.treeview.get_selection().set_mode(Gtk.SelectionMode.MULTIPLE)
        self.scroll = Gtk.ScrolledWindow()
        self.scroll.set_size_request(-1, 200)
        self.scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.scroll.add(self.treeview)
        self.scroll.show()

    #+----------------------------------------------
    #| GETTERS:
    #+----------------------------------------------
    def getTreeview(self):
        return self.treeview

    def getScrollLib(self):
        return self.scroll

    def getWidget(self):
        return self.scroll
