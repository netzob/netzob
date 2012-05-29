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
import glib
import uuid
import time

#+----------------------------------------------
#| Local Imports
#+----------------------------------------------
from netzob.Common.Field import Field
from netzob.Common.NetzobException import NetzobException
from netzob.Inference.Vocabulary.TreeViews.AbstractViewGenerator import AbstractViewGenerator


#+----------------------------------------------
#| TreeMessageGenerator:
#|     update and generates the treeview and its
#|     treestore dedicated to the messages
#+----------------------------------------------
class TreeMessageGenerator(AbstractViewGenerator):

    #+----------------------------------------------
    #| Constructor:
    #| @param vbox : where the treeview will be hold
    #+----------------------------------------------
    def __init__(self):
        AbstractViewGenerator.__init__(self, uuid.uuid4(), "Messages")
        self.symbol = None
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Modelization.TreeStores.TreeMessageGenerator.py')
        self.currentColumns = []

    #+----------------------------------------------
    #| initialization:
    #| builds and configures the treeview
    #+----------------------------------------------
    def initialization(self):
        # creation of the treestore
        self.treestore = gtk.TreeStore(str, str, str)
        # creation of the treeview
        self.treeview = gtk.TreeView(self.treestore)
        self.treeview.set_reorderable(True)

        # maximum number of columns = 200
        for i_col in range(4, 204):
            # Define cellRenderer object
            textCellRenderer = gtk.CellRendererText()
            textCellRenderer.set_property("size-points", 9)
            textCellRenderer.set_property('background-set', True)
            textCellRenderer.set_property('family', 'Courier')

            # Column Messages
            lvcolumn = gtk.TreeViewColumn(str("#" + str(i_col - 4)))
            lvcolumn.set_resizable(True)
            lvcolumn.set_sort_column_id(i_col)
            lvcolumn.set_clickable(True)
            lvcolumn.pack_start(textCellRenderer, True)
            lvcolumn.set_attributes(textCellRenderer, markup=i_col, background=1, weight=2, editable=3)

#            self.treeview.append_column(lvcolumn)
            self.currentColumns.append(lvcolumn)

        self.treeview.show()
        self.treeview.set_reorderable(True)
        self.treeview.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
        self.scroll = gtk.ScrolledWindow()
        self.scroll.set_size_request(-1, 200)
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
        self.log.warning("The treeview for the messages is in error mode")
        self.treestore.clear()

    #+----------------------------------------------
    #| show:
    #|   Display the panel
    #+----------------------------------------------
    def show(self):
        self.scroll.show_all()

    #+----------------------------------------------
    #| hide:
    #|   Hide the panel
    #+----------------------------------------------
    def hide(self):
        self.scroll.hide_all()

    #+----------------------------------------------
    #| default:
    #|         Update the treestore in normal mode
    #+----------------------------------------------
    def default(self, symbol, messageToHighlight=None):
        self.treestore.clear()

        if symbol == None:
            return

        self.symbol = symbol
        self.log.debug("Updating the treestore of the messages in default mode with the messages from the symbol " + self.symbol.getName())

        # Verifies we have everything needed for the creation of the treeview
        if (len(self.symbol.getMessages()) < 1):
            self.log.debug("It's an empty symbol so nothing to display")
            return

        # id number of the line to highlight
        nbLineMessageToHighlight = -1

        # Build the next rows from messages after applying the regex
        content_lines = []
        maxNumberOfCol = 0
        idLineMessage = 0
        for message in self.symbol.getMessages():
            # For each message we create a line and computes its cols
            try:
                messageTable = message.applyAlignment(styled=True, encoded=True)
#                for i in range(0, len(messageTable)):
#                    messageTable[i] = glib.markup_escape_text(messageTable[i])

            except NetzobException:
                self.log.warn("Impossible to display one of messages since it cannot be cut according to the computed regex.")
                self.log.warn("Message : " + str(message.getStringData()))
                continue  # We don't display the message in error

            if messageToHighlight != None and str(message.getID()) == str(messageToHighlight.getID()):
                nbLineMessageToHighlight = idLineMessage

            line = []
            line.append(message.getID())
            line.append("#ffffff")
            line.append(pango.WEIGHT_NORMAL)
            line.append(False)
            line.extend(messageTable)
            content_lines.append(line)
            idLineMessage = idLineMessage + 1
            if len(messageTable) > maxNumberOfCol:
                maxNumberOfCol = len(messageTable)

        # Create a TreeStore with N cols, with N := len(self.symbol.getFields())
        # str : Name of the row
        # str : Color of the row
        # int : pango type (weight bold)
        # bool : is row editable
        # [str...str] : value of cols

        treeStoreTypes = [str, str, int, gobject.TYPE_BOOLEAN]
        for i in range(0, maxNumberOfCol):
            treeStoreTypes.append(str)
        self.treestore = gtk.TreeStore(*treeStoreTypes)

        # Build the regex row
        regex_row = []
        regex_row.append("HEADER REGEX")
        regex_row.append("#c8c8c8")
        regex_row.append(pango.WEIGHT_BOLD)
        regex_row.append(True)
        for field in self.symbol.getFields():
            regex_row.append(glib.markup_escape_text(field.getEncodedVersionOfTheRegex()))

        # Build the types row
        types_line = []
        types_line.append("HEADER TYPE")
        types_line.append("#dedede")
        types_line.append(pango.WEIGHT_BOLD)
        types_line.append(True)
        for field in self.symbol.getFields():
            types_line.append(field.getFormat())

        self.treestore.append(None, regex_row)
        self.treestore.append(None, types_line)
        idLine = 0
        messageEntryToHighlight = None
        for line in content_lines:
            messageEntry = self.treestore.append(None, line)
            if nbLineMessageToHighlight == idLine:
                messageEntryToHighlight = messageEntry
            idLine = idLine + 1

        # activate or deactivate the perfect number of columns = nb Field
        for col in self.treeview.get_columns():
            self.treeview.remove_column(col)
        for i in range(0, min(200, len(self.symbol.getFields()))):
            self.treeview.append_column(self.currentColumns[i])
            self.treeview.get_column(i).set_title(self.symbol.getFieldByIndex(i).getName())

        self.treeview.set_model(self.treestore)

        # highlight the message entry
        if messageEntryToHighlight != None:
            self.treeview.get_selection().select_iter(messageEntryToHighlight)

    def updateDefault(self):
        self.default(self.symbol)

    #+----------------------------------------------
    #| GETTERS:
    #+----------------------------------------------
    def getTreeview(self):
        return self.treeview

    def getScrollLib(self):
        return self.scroll

    def getSymbol(self):
        return self.symbol

    def getWidget(self):
        return self.scroll
