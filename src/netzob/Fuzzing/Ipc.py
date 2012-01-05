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
#| Standard library imports
#+---------------------------------------------------------------------------+
import gtk
import pygtk
pygtk.require('2.0')
import logging

#+---------------------------------------------- 
#| Local Imports
#+----------------------------------------------
from netzob.Fuzzing.TreeViews.TreeSymbolGenerator import TreeSymbolGenerator
from netzob.Fuzzing.TreeViews.TreeTypeStructureGenerator import TreeTypeStructureGenerator

#+---------------------------------------------- 
#| Ipc :
#|     ensures the capture of informations through IPC proxing
#+---------------------------------------------- 
class Ipc:
    
    #+---------------------------------------------- 
    #| Called when user select a new trace
    #+----------------------------------------------
    def new(self):
        pass

    def update(self):
        self.treeSymbolGenerator.update()
        self.treeTypeStructureGenerator.update()

    def clear(self):
        pass

    def kill(self):
        pass

    def save(self):
        pass

    #+---------------------------------------------- 
    #| Constructor :
    #| @param netzob: the netzob main object
    #+----------------------------------------------   
    def __init__(self, netzob):
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Fuzzing.Ipc.py')
        self.netzob = netzob
        self.symbols = []
        self.selectedSymbol = None
 
        self.panel = gtk.HPaned()
        self.panel.show()

        #+---------------------------------------------- 
        #| LEFT PART OF THE GUI : TREEVIEW
        #+----------------------------------------------           
        vb_left_panel = gtk.VBox(False, spacing=0)
        self.panel.add(vb_left_panel)
        vb_left_panel.set_size_request(-1, -1)
        vb_left_panel.show()

        # Initialize the treeview generator for the symbols
        # Create the treeview
        self.treeSymbolGenerator = TreeSymbolGenerator(self.netzob)
        self.treeSymbolGenerator.initialization()
        vb_left_panel.pack_start(self.treeSymbolGenerator.getScrollLib(), True, True, 0)
        self.treeSymbolGenerator.getTreeview().connect("cursor-changed", self.symbolSelected) 
#        self.treeSymbolGenerator.getTreeview().connect('button-press-event', self.button_press_on_treeview_symbols)

        #+---------------------------------------------- 
        #| RIGHT PART OF THE GUI : TYPE STRUCTURE OUTPUT
        #+----------------------------------------------
        vb_right_panel = gtk.VBox(False, spacing=0)
        vb_right_panel.show()
        # Initialize the treeview for the type structure
        self.treeTypeStructureGenerator = TreeTypeStructureGenerator(self.netzob)
        self.treeTypeStructureGenerator.initialization()
        self.treeTypeStructureGenerator.getTreeview().connect('button-press-event', self.button_press_on_field)
        vb_right_panel.add(self.treeTypeStructureGenerator.getScrollLib())
        self.panel.add(vb_right_panel)

    def symbolSelected(self, treeview):
        (model, iter) = treeview.get_selection().get_selected()
        if(iter):
            if(model.iter_is_valid(iter)):
                # Retrieve the selected symbol
                idSymbol = model.get_value(iter, 0)
                self.selectedSymbol = idSymbol
                symbol = None

                for tmp_symbol in self.netzob.getCurrentProject().getVocabulary().getSymbols():
                    if str(tmp_symbol.getID()) == idSymbol :
                        symbol = tmp_symbol

                # Retrieve a random message in order to show a type structure
                message = symbol.getMessages()[-1]
                self.treeTypeStructureGenerator.setSymbol(symbol)
                self.treeTypeStructureGenerator.setMessage(message)
                self.treeTypeStructureGenerator.update()

    #+---------------------------------------------- 
    #| button_press_on_field :
    #|   Create a menu to display available operations
    #|   on the treeview symbols
    #+----------------------------------------------
    def button_press_on_field(self, button, event):
        if event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:        
            # Retrieves the symbol on which the user has clicked on
            x = int(event.x)
            y = int(event.y)
            (path, treeviewColumn, x, y) = self.treeTypeStructureGenerator.getTreeview().get_path_at_pos(x, y)
            aIter = self.treeTypeStructureGenerator.getTreeview().get_model().get_iter(path)
            field = self.treeTypeStructureGenerator.getTreeview().get_model().get_value(aIter, 0)
            menu = gtk.Menu()
            item = gtk.MenuItem("Fuzz field")
            item.connect("activate", self.fuzz_field_cb, field)
            item.show()
            menu.append(item)
            menu.popup(None, None, None, event.button, event.time)

    def fuzz_field_cb(self, widget, field):
        print "Fuzz field : " + str(field)

    #+---------------------------------------------- 
    #| GETTERS
    #+----------------------------------------------
    def getPanel(self):
        return self.panel
