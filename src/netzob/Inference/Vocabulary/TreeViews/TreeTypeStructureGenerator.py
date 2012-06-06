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
import logging
import gtk
import uuid

#+----------------------------------------------
#| Local Imports
#+----------------------------------------------
from netzob.Common.MMSTD.Dictionary.Memory import Memory
from netzob.Inference.Vocabulary.TreeViews.AbstractViewGenerator import AbstractViewGenerator


#+----------------------------------------------
#| TreeTypeStructureGenerator:
#|     update and generates the treeview and its
#|     treestore dedicated to the type structure
#+----------------------------------------------
class TreeTypeStructureGenerator(AbstractViewGenerator):

    #+----------------------------------------------
    #| Constructor:
    #| @param vbox : where the treeview will be hold
    #+----------------------------------------------
    def __init__(self):
        AbstractViewGenerator.__init__(self, uuid.uuid4(), "Type Structure")
        self.symbol = None
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Modelization.TreeViews.TreeTypeStructureGenerator.py')

    #+----------------------------------------------
    #| initialization:
    #| builds and configures the treeview
    #+----------------------------------------------
    def initialization(self):
        # creation of the treestore
        self.treestore = gtk.TreeStore(int, str, str, str)  # iCol, Name, Description, Variable
        # creation of the treeview
        self.treeview = gtk.TreeView(self.treestore)
        self.treeview.set_reorderable(True)
        # Creation of a cell rendered and of a column
        cell = gtk.CellRendererText()
        cell.set_property("size-points", 9)
        columns = ["iCol", "Name", "Description", "Variable"]
        for i in range(1, len(columns)):
            column = gtk.TreeViewColumn(columns[i])
            column.set_resizable(True)
            column.pack_start(cell, True)
            column.set_attributes(cell, markup=i)
            self.treeview.append_column(column)
        self.treeview.show()
        self.treeview.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
        self.scroll = gtk.ScrolledWindow()
        self.scroll.set_size_request(-1, 250)
        self.scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.scroll.add(self.treeview)
        self.scroll.show()

    #+----------------------------------------------
    #| clear:
    #|         Clear the class
    #+----------------------------------------------
    def clear(self):
        self.symbol = None
        self.treestore.clear()

    #+----------------------------------------------
    #| error:
    #|         Update the treestore in error mode
    #+----------------------------------------------
    def error(self):
        self.log.warning("The treeview for the symbol is in error mode")
        # TODO : delete pass statement if useless
        #pass

    #+----------------------------------------------
    #| default:
    #|         Update the treestore in normal mode
    #+----------------------------------------------
    def update(self):
        if self.getSymbol() == None:
            self.clear()
            return

        self.treestore.clear()
        for field in self.getSymbol().getFields():
            tab = ""
            for k in range(field.getEncapsulationLevel()):
                tab += "        "
            if field.getName() == "__sep__":  # Do not show the delimiter fields
                continue

            # Define the background color
            if field.getBackgroundColor() != None:
                backgroundColor = 'background="' + field.getBackgroundColor() + '"'
            else:
                backgroundColor = ""

            # Compute the associated variable (specified or automatically computed)
            variableDescription = "-"
            if field.getVariable() != None:
                variableDescription = field.getVariable().getUncontextualizedDescription()
            elif field.getDefaultVariable(self.getSymbol()) != None:
                variableDescription = field.getDefaultVariable(self.getSymbol()).getUncontextualizedDescription()

            self.treestore.append(None, [field.getIndex(), tab + field.getName() + ":", field.getDescription(), '<span ' + backgroundColor + ' font_family="monospace">' + variableDescription + '</span>'])

    #+----------------------------------------------
    #| GETTERS:
    #+----------------------------------------------
    def getTreeview(self):
        return self.treeview

    def getScrollLib(self):
        return self.scroll

    def getWidget(self):
        return self.scroll

    def getSymbol(self):
        return self.symbol

    #+----------------------------------------------
    #| SETTERS:
    #+----------------------------------------------
    def setTreeview(self, treeview):
        self.treeview = treeview

    def setScrollLib(self, scroll):
        self.scroll = scroll

    def setSymbol(self, symbol):
        self.symbol = symbol
