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
from gettext import gettext as _
import os

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+
from gi.repository import Gtk, Gdk
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GObject

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.ResourcesConfiguration import ResourcesConfiguration

class NewVocabularyView(object):
    SYMBOLLISTSTORE_SELECTED_COLUMN = 0
    SYMBOLLISTSTORE_ID_COLUMN = 4

    def __init__(self, controller):
        self.controller = controller
        self.netzob = self.controller.netzob
        self.builder = Gtk.Builder()
        self.builder.add_from_file(os.path.join(
            ResourcesConfiguration.getStaticResources(),
            "ui",
            "VocabularyView.glade"))
        self._getObjects(self.builder, ["vocabularyPanel", "symbolListStore",
            "renameSymbolButton", "concatSymbolButton", "deleteSymbolButton",
            "newMessageList"])
        self._loadActionGroupUIDefinition()
        self.builder.connect_signals(self.controller)
        # List of currently displayed message tables
        self.messageTableLists = []

    def _loadActionGroupUIDefinition(self):
        """Loads the action group and the UI definition of menu items
        . This method should only be called in the constructor"""
        # Load actions
        actionsBuilder = Gtk.Builder()
        actionsBuilder.add_from_file(os.path.join(
            ResourcesConfiguration.getStaticResources(),
            "ui",
            "vocabularyActions.glade"))
        self._actionGroup = actionsBuilder.get_object("vocabularyActionGroup")
        uiDefinitionFilePath = os.path.join(
            ResourcesConfiguration.getStaticResources(),
            "ui",
            "vocabularyMenuToolbar.ui")
        with open(uiDefinitionFilePath, "r") as uiDefinitionFile:
            self._uiDefinition = uiDefinitionFile.read()

    def _getObjects(self, builder, objectsList):
        for object in objectsList:
            setattr(self, object, builder.get_object(object))

    ## Mandatory view methods
    def getPanel(self):
        return self.vocabularyPanel

    # Return the actions
    def getActionGroup(self):
        return self._actionGroup

    # Return toolbar and menu
    def getMenuToolbarUIDefinition(self):
        return self._uiDefinition

    ## View manipulation methods
    def addSpreadSheet(self, name, position):
        """
        Add an external spreadsheet on the builder 
        @type  box: string
        @param box: The hbox/vbox where add the widget
        @type  widget: string
        @param widget: The widget to add 
        @type  position: number
        @param position: The position to add the widget on the hbox/vbox
        @type  expand: gboolean
        @param expand: Set the expand properties
        """
        #create a new builder to extract the widget
        builder2 = Gtk.Builder()
        builder2.add_from_file(self.ressourceglade + "/ui/spreadsheet.glade")
        #set the name of the symbol
        label = builder2.get_object("label1")
        label.set_text(name)
        #add the spreadsheet to the main builder
        spreadsheet = builder2.get_object("spreadsheet")
        box = self.builder.get_object("box5")
        box.pack_start(spreadsheet, True, True, 0)
        box.reorder_child(spreadsheet, position)
        #add the message for the treeview
        #add the close button
        closebutton = builder2.get_object("button4")
        closebutton.connect("clicked", self.button_closeview_cb, spreadsheet)
        #focus
        focusbutton = builder2.get_object("button1")
        focusbutton.connect("clicked", self.button_focusview_cb, builder2)

        return builder2

    def update(self):
        self.updateSymbolList()
        self.updateSymbolListToolbar()

    ## Symbol List
    def updateSymbolList(self):
        """Updates the symbol list of the left panel, preserving the current
        selection"""
        symbolList = self.controller.netzob.getCurrentProject().getVocabulary().getSymbols()
        selection = []
        for row in self.symbolListStore:
            if (row[0]): # 0 - Selected column
                selection.append(row[4]) # 4 - Symbol ID column
        self.symbolListStore.clear()
        for sym in symbolList:
            self.addRowSymbolList(selection, sym.getName(),
                                  len(sym.getMessages()),
                                  len(sym.getFields()),
                                  sym.getID())

    def addRowSymbolList(self, selection, name, message, field, symID):
        """Adds a row in the symbol list of left panel
        @type  selection: boolean
        @param selection: if selected symbol
        @type  name: string
        @param name: name of the symbol
        @type  message: string
        @param message: number of message in the symbol
        @type  field: string
        @param field: number of field in the symbol   
        @type  image: string
        @param image: image of the lock button (freeze partitioning)"""
        i = self.symbolListStore.append()
        self.symbolListStore.set(i, 0, (symID in selection))
        self.symbolListStore.set(i, 1, name)
        self.symbolListStore.set(i, 2, message)
        self.symbolListStore.set(i, 3, field)
        self.symbolListStore.set(i, 4, symID)

    def updateSymbolListToolbar(self):
        """Enables or disable buttons of the symbol list toolbar"""
        selectedSymbolsCount = self.countSelectedSymbols()
        self.renameSymbolButton.set_sensitive((selectedSymbolsCount == 1))
        self.concatSymbolButton.set_sensitive((selectedSymbolsCount >= 2))
        self.deleteSymbolButton.set_sensitive((selectedSymbolsCount >= 1))

    def countSelectedSymbols(self):
        count = 0
        for row in self.symbolListStore:
            if row[self.SYMBOLLISTSTORE_SELECTED_COLUMN]:
                count += 1
        return count

    def getSelectedSymbolList(self):
        currentVocabulary = self.controller.netzob.getCurrentProject().getVocabulary()
        selectedSymbolList = []
        for row in self.symbolListStore:
            if row[self.SYMBOLLISTSTORE_SELECTED_COLUMN]:
                symID = row[self.SYMBOLLISTSTORE_ID_COLUMN]
                sym = currentVocabulary.getSymbolByID(symID)
                selectedSymbolList.append(sym)
        return selectedSymbolList

    ## TODO
    def refreshProjectProperties(self):
        liststore = self.builder.get_object("projectproperties")
        liststore.clear()
        properties = self.controller.netzob.getCurrentProject().getProperties()
        #too big
        #line = liststore.append()
        #liststore.set(line, 0, "workspace")
        #liststore.set(line, 1, self.getCurrentWorkspace().getPath())
        for key in properties:
            line = liststore.append()
            liststore.set(line, 0, key)
            liststore.set(line, 1, str(properties[key]))

    def refreshSymbolProperties(self):
        pass

    def refreshMessageProperties(self):
        pass

    def refreshFieldProperties(self):
        pass
