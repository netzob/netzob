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
from netzob.Inference.Vocabulary.TreeViews.AbstractViewGenerator import AbstractViewGenerator


#+----------------------------------------------
#| TreeSymbolGenerator:
#+----------------------------------------------
class TreeSymbolGenerator(AbstractViewGenerator):

    #+----------------------------------------------
    #| Constructor:
    #+----------------------------------------------
    def __init__(self, netzob):
        AbstractViewGenerator.__init__(self, uuid.uuid4(), "Symbols")
        self.netzob = netzob
        self.treestore = None
        self.treeview = None
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Inference.Vocabulary.TreeViews.TreeSymbolGenerator.py')

    #+----------------------------------------------
    #| initialization:
    #| builds and configures the treeview
    #+----------------------------------------------
    def initialization(self):
        # Tree store contains:
        # str : text (symbol Name)
        # str : text (score)
        # str : color foreground
        # str : color background
        self.treestore = gtk.TreeStore(str, str, str, str, str)
        self.treeview = gtk.TreeView(self.treestore)

        # messages list
        self.scroll = gtk.ScrolledWindow()
        self.scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.scroll.show()
        self.scroll.set_size_request(200, 300)
        self.scroll.add(self.treeview)

        self.lvcolumn = gtk.TreeViewColumn('Symbols')
        self.lvcolumn.set_sort_column_id(1)
        cell = gtk.CellRendererText()
        cell.set_property('background-set', True)
        self.lvcolumn.pack_start(cell, True)
        self.lvcolumn.set_attributes(cell, markup=1, background=4)
        self.treeview.append_column(self.lvcolumn)
        self.treeview.show()

    #+----------------------------------------------
    #| clear:
    #|         Clear the class
    #+----------------------------------------------
    def clear(self):
        pass

    #+----------------------------------------------
    #| default:
    #|         Update the treestore in normal mode
    #+----------------------------------------------
    def default(self, selectedSymbol=None):
        self.log.debug("Updating the treestore of the symbol in default mode")
        self.treestore.clear()

        # We retrieve the current project
        project = self.netzob.getCurrentProject()

        if project != None:
            # We retrieve the vocabulary of the project
            vocabulary = project.getVocabulary()

            # Include the name of the project
            self.lvcolumn.set_title(project.getName())

            # We retrieve the symbols declared in (symbol = symbol)
            symbols = vocabulary.getSymbols()

            toSelectEntry = None
            for symbol in symbols:
                symbolName = symbol.getName()

                for filter in symbol.getVisualizationFilters():
                    symbolName = filter.apply(symbolName)

                symbolName = symbolName + " (" + str(len(symbol.getMessages())) + ")"
                symbolEntry = [str(symbol.getID()), symbolName, str(symbol.getScore()), '#000000', '#DEEEF0']
                symbolIter = self.treestore.append(None, symbolEntry)
                if selectedSymbol != None and str(symbol.getID()) == str(selectedSymbol.getID()):
                    toSelectEntry = symbolIter

            # if a selection entry has been found, we highlight it
            if toSelectEntry != None:
                self.treeview.get_selection().select_iter(toSelectEntry)

    #+----------------------------------------------
    #| getSymbolAtPosition:
    #|         retrieves the symbol wich is inserted
    #|         in the treeview at the given position
    #| @param x the position in X
    #| @param y the position in Y
    #| @return the symbol if it exists (or None)
    #+----------------------------------------------
    def getSymbolAtPosition(self, x, y):
        self.log.debug("Search for the symbol referenced at position {0};{1}".format(str(x), str(y)))
        vocabulary = self.netzob.getCurrentProject().getVocabulary()

        info = self.treeview.get_path_at_pos(x, y)
        if info is not None:
            path = info[0]
            iter = self.treeview.get_model().get_iter(path)
            idSymbol = str(self.treeview.get_model().get_value(iter, 0))
            if idSymbol is not None:
                self.log.debug("An entry with the ID {0} has been found.".format(idSymbol))
                for symbol in vocabulary.getSymbols():
                    if (str(symbol.getID()) == idSymbol):
                        self.log.debug("The requested symbol with ID {0} has been found".format(symbol.getID()))
                        return symbol
        return None

    #+----------------------------------------------
    #| GETTERS:
    #+----------------------------------------------
    def getTreeview(self):
        return self.treeview

    def getScrollLib(self):
        return self.scroll

    def getWidget(self):
        return self.scroll
