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
import logging
import gtk
import uuid

#+---------------------------------------------------------------------------+
#| Local Imports
#+---------------------------------------------------------------------------+
from netzob.Common.MMSTD.Dictionary.Memory import Memory
from netzob.Common.Type.TypeConvertor import TypeConvertor
from netzob.Common.Field import Field
from netzob.Inference.Vocabulary.TreeViews.AbstractViewGenerator import AbstractViewGenerator


#+---------------------------------------------------------------------------+
#| TreePropertiesGenerator:
#|     update and generates the treeview and its
#|     treestore dedicated to the properties
#+---------------------------------------------------------------------------+
class TreePropertiesGenerator(AbstractViewGenerator):

    #+-----------------------------------------------------------------------+
    #| Constructor:
    #+-----------------------------------------------------------------------+
    def __init__(self, netzob):
        AbstractViewGenerator.__init__(self, uuid.uuid4(), "Properties")
        self.netzob = netzob
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Inference.Vocabulary.TreeViews.TreePropertiesGenerator.py')
        self.tree = None

    #+----------------------------------------------
    #| initialization:
    #| builds and configures the treeview
    #+----------------------------------------------
    def initialization(self):
        self.tree = gtk.TreeView()
        colResult = gtk.TreeViewColumn()
        colResult.set_title("Properties")

        cell = gtk.CellRendererText()
        colResult.pack_start(cell, True)
        colResult.add_attribute(cell, "text", 0)

        cell = gtk.CellRendererText()
        colResult.pack_start(cell, True)
        colResult.add_attribute(cell, "text", 1)

        cell = gtk.CellRendererText()
        colResult.pack_start(cell, True)
        colResult.add_attribute(cell, "text", 2)

        self.treestore = gtk.TreeStore(str, str, str)  # name, value, format

        self.tree.append_column(colResult)
        self.tree.set_model(self.treestore)
        self.tree.show()

        self.scroll = gtk.ScrolledWindow()
        self.scroll.set_size_request(-1, 100)
        self.scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.scroll.add(self.tree)
        self.scroll.show()

    #+----------------------------------------------
    #| clear:
    #|         Clear the class
    #+----------------------------------------------
    def clear(self):
        self.treestore.clear()

    #+----------------------------------------------
    #| error:
    #|         Update the treestore in error mode
    #+----------------------------------------------
    def error(self):
        self.log.warning("The treeview for the properties is in error mode")
        pass

    #+----------------------------------------------
    #| default:
    #|         Update the treestore in normal mode
    #+----------------------------------------------
    def update(self, message):
        self.treestore.clear()
        if message == None:
            return

        for property in message.getProperties():
            propertyName = property[0]
            propertyFormat = property[1]
            propertyValue = property[2]
            self.treestore.append(None, [propertyName, propertyValue, propertyFormat])

    #+----------------------------------------------
    #| GETTERS:
    #+----------------------------------------------
    def getTreeview(self):
        return self.tree

    def getScrollLib(self):
        return self.scroll

    def getWidget(self):
        return self.scroll

    #+----------------------------------------------
    #| SETTERS:
    #+----------------------------------------------
    def setTreeview(self, tree):
        self.tree = tree

    def setScrollLib(self, scroll):
        self.scroll = scroll
