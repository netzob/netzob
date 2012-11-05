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
import logging

#+----------------------------------------------
#| Local Imports
#+----------------------------------------------
from netzob.Fuzzing.TreeViews.TreeSymbolGenerator import TreeSymbolGenerator
from netzob.Fuzzing.TreeViews.TreeTypeStructureGenerator import TreeTypeStructureGenerator


#+----------------------------------------------
#| FileImport:
#|     GUI for capturing messages
#+----------------------------------------------
class File(object):

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
    #| Constructor:
    #| @param netzob: the netzob main object
    #+----------------------------------------------
    def __init__(self, netzob):
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Fuzzing.File.py')
        self.netzob = netzob
        self.symbols = []
        self.selectedSymbol = None

        self.panel = Gtk.HPaned()
        self.panel.show()

        #+----------------------------------------------
        #| LEFT PART OF THE GUI : TREEVIEW
        #+----------------------------------------------
        vb_left_panel = Gtk.VBox(False, spacing=0)
        self.panel.add(vb_left_panel)
        vb_left_panel.set_size_request(-1, -1)
        vb_left_panel.show()

        # Initialize the treeview generator for the symbols
        # Create the treeview
        self.treeSymbolGenerator = TreeSymbolGenerator(self.netzob)
        self.treeSymbolGenerator.initialization()
        vb_left_panel.pack_start(self.treeSymbolGenerator.getScrollLib(), True, True, 0)
        selection = self.treeSymbolGenerator.getTreeview().get_selection()
        selection.connect("changed", self.symbolSelected)
#        self.treeSymbolGenerator.getTreeview().connect('button-press-event', self.button_press_on_treeview_symbols)

        #+----------------------------------------------
        #| RIGHT PART OF THE GUI : TYPE STRUCTURE OUTPUT
        #+----------------------------------------------
        vb_right_panel = Gtk.VBox(False, spacing=0)
        vb_right_panel.show()
        # Initialize the treeview for the type structure
        self.treeTypeStructureGenerator = TreeTypeStructureGenerator(self.netzob)
        self.treeTypeStructureGenerator.initialization()
        self.treeTypeStructureGenerator.getTreeview().connect('button-press-event', self.button_press_on_field)
        vb_right_panel.add(self.treeTypeStructureGenerator.getScrollLib())
        self.panel.add(vb_right_panel)

    def symbolSelected(self, selection):
        (model, iter) = selection.get_selected()
        if(iter):
            if(model.iter_is_valid(iter)):
                # Retrieve the selected symbol
                idSymbol = model.get_value(iter, 0)
                self.selectedSymbol = idSymbol
                symbol = None

                for tmp_symbol in self.netzob.getCurrentProject().getVocabulary().getSymbols():
                    if str(tmp_symbol.getID()) == idSymbol:
                        symbol = tmp_symbol

                # Retrieve a random message in order to show a type structure
                message = symbol.getMessages()[-1]
                self.treeTypeStructureGenerator.setSymbol(symbol)
                self.treeTypeStructureGenerator.setMessage(message)
                self.treeTypeStructureGenerator.update()

    #+----------------------------------------------
    #| button_press_on_field:
    #|   Create a menu to display available operations
    #|   on the treeview symbols
    #+----------------------------------------------
    def button_press_on_field(self, button, event):
        if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 3:
            # Retrieves the symbol on which the user has clicked on
            x = int(event.x)
            y = int(event.y)
            (path, treeviewColumn, x, y) = self.treeTypeStructureGenerator.getTreeview().get_path_at_pos(x, y)
            aIter = self.treeTypeStructureGenerator.getTreeview().get_model().get_iter(path)
            field = self.treeTypeStructureGenerator.getTreeview().get_model().get_value(aIter, 0)
            self.menu = Gtk.Menu()
            item = Gtk.MenuItem(_("Fuzz field"))
            item.connect("activate", self.fuzz_field_cb, field)
            item.show()
            self.menu.append(item)
            self.menu.popup(None, None, None, None, event.button, event.time)

    def fuzz_field_cb(self, widget, field):
        self.log.debug("Fuzz field : {0}".format(str(field)))

    #+----------------------------------------------
    #| GETTERS
    #+----------------------------------------------
    def getPanel(self):
        return self.panel
