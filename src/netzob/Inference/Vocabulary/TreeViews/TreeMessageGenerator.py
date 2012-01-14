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
import pango
import gobject
import gtk

#+---------------------------------------------- 
#| Local Imports
#+----------------------------------------------
from netzob.Common.Field import Field

#+---------------------------------------------- 
#| TreeMessageGenerator :
#|     update and generates the treeview and its 
#|     treestore dedicated to the messages
#+---------------------------------------------- 
class TreeMessageGenerator():
    
    #+---------------------------------------------- 
    #| Constructor :
    #| @param vbox : where the treeview will be hold
    #+---------------------------------------------- 
    def __init__(self):
        self.symbol = None
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Modelization.TreeStores.TreeMessageGenerator.py')
   
    #+---------------------------------------------- 
    #| initialization :
    #| builds and configures the treeview
    #+----------------------------------------------     
    def initialization(self):
        # creation of the treestore
        self.treestore = gtk.TreeStore(str, str, str)     
        # creation of the treeview   
        self.treeview = gtk.TreeView(self.treestore)
        self.treeview.set_reorderable(True)
        # Creation of a cell rendered and of a column
        cell = gtk.CellRendererText()
        column = gtk.TreeViewColumn('Messages')
        column.pack_start(cell, True)
        column.set_attributes(cell, text=0)
        column.set_attributes(cell, markup=0)
        self.treeview.append_column(column)
        self.treeview.show()
        self.treeview.set_reorderable(True)
        self.treeview.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
        self.scroll = gtk.ScrolledWindow()
        self.scroll.set_size_request(-1, 200)
        self.scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)        
        self.scroll.add(self.treeview)
        self.scroll.show()

    #+---------------------------------------------- 
    #| clear :
    #|         Clear the class
    #+---------------------------------------------- 
    def clear(self):
        self.symbol = None
        self.treestore.clear()
        
    #+---------------------------------------------- 
    #| error :
    #|         Update the treestore in error mode
    #+---------------------------------------------- 
    def error(self):
        self.log.warning("The treeview for the messages is in error mode")      
        self.treestore.clear()
    
    #+---------------------------------------------- 
    #| default :
    #|         Update the treestore in normal mode
    #+---------------------------------------------- 
    def default(self, symbol):
        self.treestore.clear()
        if symbol == None :
            return
        
        self.symbol = symbol
        self.log.debug("Updating the treestore of the messages in default mode with the messages from the symbol " + self.symbol.getName())
        
        # Verifies we have everything needed for the creation of the treeview
        if (self.symbol == None) :
            self.log.warn("Error while trying to update the list of messages")
            return

        if (len(self.symbol.getMessages()) < 1 or len(self.symbol.getFields()) == 0) :
            self.log.debug("It's an empty symbol so nothing to display")
            return

        # Create a TreeStore with N cols, with N := len(self.symbol.getFields())
        treeStoreTypes = [str, str, int, gobject.TYPE_BOOLEAN]
        for field in self.symbol.getFields():
            treeStoreTypes.append(str)
        self.treestore = gtk.TreeStore(*treeStoreTypes)

        # Build the regex row
        regex_row = []
        regex_row.append("HEADER REGEX")
        regex_row.append("#c8c8c8")
        regex_row.append(pango.WEIGHT_BOLD)
        regex_row.append(True)
        
        for field in self.symbol.getFields():
            if field.getRegex().find("{") != -1: # This is a real regex
                regex_row.append(field.getRegex())
            else: # This is a simple value
                regex_row.append(field.getEncodedVersionOfTheRegex())
        self.treestore.append(None, regex_row)

        # Build the types row
        types_line = []
        types_line.append("HEADER TYPE")
        types_line.append("#DEDEDE")
        types_line.append(pango.WEIGHT_BOLD)
        types_line.append(True)        
        for field in self.symbol.getFields():
#            types_line.append(self.getSymbol().getStyledPossibleTypesForAField(field))
            types_line.append(field.getFormat())
        self.treestore.append(None, types_line)
        
        # Build the next rows from messages after applying the regex
        for message in self.symbol.getMessages():
            # for each message we create a line and computes its cols
            line = []
            line.append(message.getID())
            line.append("#ffffff")
            line.append(pango.WEIGHT_NORMAL)
            line.append(False)
            line.extend(message.applyAlignment(styled=True, encoded=True))
            self.treestore.append(None, line)

        # Remove all the columns of the current treeview
        for col in self.treeview.get_columns() :
            self.treeview.remove_column(col)
            
        iField = 4
        for field in self.symbol.getFields() :
            # Define cellRenderer object
            textCellRenderer = gtk.CellRendererText()
            textCellRenderer.set_property('background-set' , True)

            # Column Messages
            lvcolumn = gtk.TreeViewColumn(field.getName())
            lvcolumn.pack_start(textCellRenderer, True)
            lvcolumn.set_attributes(textCellRenderer, markup=iField, background=1, weight=2, editable=3)
            self.treeview.append_column(lvcolumn)
            iField = iField + 1

        self.treeview.set_model(self.treestore)

    def updateDefault(self):
        self.default(self.symbol)
    
    #+---------------------------------------------- 
    #| GETTERS : 
    #+----------------------------------------------
    def getTreeview(self):
        return self.treeview

    def getScrollLib(self):
        return self.scroll

    def getSymbol(self):
        return self.symbol
