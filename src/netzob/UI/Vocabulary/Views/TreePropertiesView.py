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
#| Global Imports
#+---------------------------------------------------------------------------+
from gettext import gettext as _
import logging
from gi.repository import Gtk
import uuid

#+---------------------------------------------------------------------------+
#| Local Imports
#+---------------------------------------------------------------------------+
from netzob.UI.Vocabulary.Views.AbstractViewGenerator import AbstractViewGenerator


#+---------------------------------------------------------------------------+
#| TreePropertiesView:
#|     update and generates the treeview and its
#|     treestore dedicated to the properties
#+---------------------------------------------------------------------------+
class TreePropertiesView(AbstractViewGenerator):

    #+-----------------------------------------------------------------------+
    #| Constructor:
    #+-----------------------------------------------------------------------+
    def __init__(self, netzob):
        self.netzob = netzob
        self.log = logging.getLogger('netzob.UI.Vocabulary.Views.TreePropertiesView.py')
        AbstractViewGenerator.__init__(self, uuid.uuid4(), "Properties")
        self.treeview = None
        self.treestore = None
        self.scroll = None
        self.buildPanel()

    #+----------------------------------------------
    #| buildPanel:
    #| builds and configures the treeview
    #+----------------------------------------------
    def buildPanel(self):
        self.treeview = Gtk.TreeView()
        colResult = Gtk.TreeViewColumn()
        colResult.set_title(_("Properties"))

        cell = Gtk.CellRendererText()
        colResult.pack_start(cell, True)
        colResult.add_attribute(cell, "text", 0)

        cell = Gtk.CellRendererText()
        colResult.pack_start(cell, True)
        colResult.add_attribute(cell, "text", 1)

        cell = Gtk.CellRendererText()
        colResult.pack_start(cell, True)
        colResult.add_attribute(cell, "text", 2)

        self.treestore = Gtk.TreeStore(str, str, str)  # name, value, format

        self.treeview.append_column(colResult)
        self.treeview.set_model(self.treestore)
        self.treeview.show()

        self.scroll = Gtk.ScrolledWindow()
        self.scroll.set_size_request(-1, 100)
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

    #+----------------------------------------------
    #| SETTERS:
    #+----------------------------------------------
    def setTreeview(self, treeview):
        self.treeview = treeview

    def setScrollLib(self, scroll):
        self.scroll = scroll
