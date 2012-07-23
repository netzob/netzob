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
from collections import OrderedDict


#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.ResourcesConfiguration import ResourcesConfiguration

class NewVocabularyView(object):
    SYMBOLLISTSTORE_SELECTED_COLUMN = 0
    SYMBOLLISTSTORE_NAME_COLUMN = 1
    SYMBOLLISTSTORE_MESSAGE_COLUMN = 2
    SYMBOLLISTSTORE_FIELD_COLUMN = 3
    SYMBOLLISTSTORE_ID_COLUMN = 4

    PROJECTPROPERTIESLISTSTORE_NAME_COLUMN = 0
    PROJECTPROPERTIESLISTSTORE_VALUE_COLUMN = 1

    SYMBOLPROPERTIESLISTSTORE_NAME_COLUMN = 0
    SYMBOLPROPERTIESLISTSTORE_VALUE_COLUMN = 1

    MESSAGEPROPERTIESLISTSTORE_NAME_COLUMN = 0
    MESSAGEPROPERTIESLISTSTORE_VALUE_COLUMN = 1

    FIELDPROPERTIESLISTSTORE_NAME_COLUMN = 0
    FIELDPROPERTIESLISTSTORE_VALUE_COLUMN = 1

    def __init__(self, controller):
        self.controller = controller
        self.netzob = self.controller.netzob
        self.builder = Gtk.Builder()
        self.builder.add_from_file(os.path.join(
            ResourcesConfiguration.getStaticResources(),
            "ui",
            "VocabularyView.glade"))
        self._getObjects(self.builder, ["vocabularyPanel", "symbolListStore",
            "renameSymbolButton", "concatSymbolButton", "deleteSymbolButton", "newMessageList",
            "projectTreeview", "symbolTreeview", "messageTreeview", "fieldTreeview",
            "projectPropertiesListstore", "symbolPropertiesListstore", "messagePropertiesListstore",
            "fieldPropertiesListstore"
            ])
        self._loadActionGroupUIDefinition()
        self.builder.connect_signals(self.controller)
        # List of currently displayed message tables
        self.messageTableLists = []
        # Set the focus symbol
        if self.getCurrentProject().getVocabulary().getSymbols()[0] != None:
            self.focusMessageTable = self.getCurrentProject().getVocabulary().getSymbols()[0]
        else :
            self.focusMessageTable = None
        # Todo create the focus attribute



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
    ## remove and modify
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
        self.updateProjectProperties()
        self.updateSymbolProperties()
        self.updateMessageProperties()
        self.updateFieldProperties()

    ## Symbol List
    def updateSymbolList(self):
        """Updates the symbol list of the left panel, preserving the current
        selection"""
        symbolList = self.getCurrentProject().getVocabulary().getSymbols()
        selectionIdList = []
        for row in self.symbolListStore:
            if (row[self.SYMBOLLISTSTORE_SELECTED_COLUMN]):
                selectionIdList.append(row[self.SYMBOLLISTSTORE_ID_COLUMN])
        self.symbolListStore.clear()
        for sym in symbolList:
            self.addRowSymbolList(selectionIdList, sym.getName(),
                                  len(sym.getMessages()),
                                  len(sym.getFields()),
                                  sym.getID())

    def addRowSymbolList(self, selectionIdList, name, message, field, symID):
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
        self.symbolListStore.set(i, self.SYMBOLLISTSTORE_SELECTED_COLUMN, (symID in selectionIdList))
        self.symbolListStore.set(i, self.SYMBOLLISTSTORE_NAME_COLUMN, name)
        self.symbolListStore.set(i, self.SYMBOLLISTSTORE_MESSAGE_COLUMN, message)
        self.symbolListStore.set(i, self.SYMBOLLISTSTORE_FIELD_COLUMN, field)
        self.symbolListStore.set(i, self.SYMBOLLISTSTORE_ID_COLUMN, symID)

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
        currentVocabulary = self.getCurrentProject().getVocabulary()
        selectedSymbolList = []
        for row in self.symbolListStore:
            if row[self.SYMBOLLISTSTORE_SELECTED_COLUMN]:
                symID = row[self.SYMBOLLISTSTORE_ID_COLUMN]
                sym = currentVocabulary.getSymbolByID(symID)
                selectedSymbolList.append(sym)
        return selectedSymbolList

    def getProjectProperties(self):
        project = self.getCurrentProject()
        properties = OrderedDict()
        if project != None:
            configuration = project.getConfiguration()
            properties = OrderedDict()
            properties['workspace'] = self.controller.netzob.getCurrentWorkspace().getPath()
            properties['name'] = project.getName()
            properties['date'] = project.getCreationDate()
            properties['symbol'] = len(project.getVocabulary().getSymbols())
            properties['message'] = len(project.getVocabulary().getMessages())
            field = 0
            for sym in project.getVocabulary().getSymbols():
                field = field + len(sym.getFields())
            properties['field'] = field
            properties[configuration.VOCABULARY_GLOBAL_FORMAT] = configuration.getVocabularyInferenceParameter(configuration.VOCABULARY_GLOBAL_FORMAT)
            properties[configuration.VOCABULARY_GLOBAL_UNITSIZE] = configuration.getVocabularyInferenceParameter(configuration.VOCABULARY_GLOBAL_UNITSIZE)
            properties[configuration.VOCABULARY_GLOBAL_SIGN] = configuration.getVocabularyInferenceParameter(configuration.VOCABULARY_GLOBAL_SIGN)
            properties[configuration.VOCABULARY_GLOBAL_ENDIANESS] = configuration.getVocabularyInferenceParameter(configuration.VOCABULARY_GLOBAL_ENDIANESS)
        return properties


    ## TODO
    def updateProjectProperties(self):
        # clean store
        self.projectPropertiesListstore.clear()
        # get project properties
        properties = self.getProjectProperties()
        # add project properties
        for key in properties:
            line = self.projectPropertiesListstore.append()
            self.projectPropertiesListstore.set(line, self.PROJECTPROPERTIESLISTSTORE_NAME_COLUMN, key)
            self.projectPropertiesListstore.set(line, self.PROJECTPROPERTIESLISTSTORE_VALUE_COLUMN, str(properties[key]))

    def getSymbolProperties(self):
        symbol = self.focusMessageTable.getFocusSymbol()#TODO METHOD
        properties = OrderedDict()
        if symbol != None:
            properties['name'] = symbol.getName()
            # ++CODE HERE++
            # ADD PROPERTIES FROM symbol
            # ADD LIST [ Type Structure , number of field , number of message , score , alignement type , 4 format variable ]
        return properties

    def updateSymbolProperties(self):
        # clean store
        self.symbolPropertiesListstore.clear()
        # get symbol properties
        properties = self.getSymbolProperties()
        # add symbol properties
        for key in properties:
            line = self.symbolPropertiesListstore.append()
            self.symbolPropertiesListstore.set(line, self.SYMBOLPROPERTIESLISTSTORE_NAME_COLUMN, key)
            self.symbolPropertiesListstore.set(line, self.SYMBOLPROPERTIESLISTSTORE_VALUE_COLUMN, str(properties[key]))

    def getMessageProperties(self):
        message = self.focusMessageTable.getFocusMessage()#TODO METHOD
        properties = OrderedDict()
        if message != None:
            properties['name'] = message.getName()
            # ++CODE HERE++
            # ADD PROPERTIES FROM message
            # ADD LIST [ Type ,TimeStamp,Filename of the source,Creation date ,Modification date,Owner,size,line number,data ]
        return properties

    def updateMessageProperties(self):
        # clean store
        self.messagePropertiesListstore.clear()
        # get message properties
        properties = self.getMessageProperties()
        # add message properties
        for key in properties:
            line = self.messagePropertiesListstore.append()
            self.messagePropertiesListstore.set(line, self.MESSAGEPROPERTIESLISTSTORE_NAME_COLUMN, key)
            self.messagePropertiesListstore.set(line, self.MESSAGEPROPERTIESLISTSTORE_VALUE_COLUMN, str(properties[key]))


    def getFieldProperties(self):
        field = self.focusMessageTable.getFocusField()#TODO METHOD
        properties = OrderedDict()
        if field != None:
            properties['name'] = field.getName()
            # ++CODE HERE++
            # ADD PROPERTIES FROM message
            # ADD LIST [ regex, 4 format variable, idea? ]
        return properties



    def updateFieldProperties(self):
        # clean store
        self.fieldPropertiesListstore.clear()
        # get field properties
        properties = self.getFieldProperties()
        # add field properties
        for key in properties:
            line = self.fieldPropertiesListstore.append()
            self.fieldPropertiesListstore.set(line, 0, key)
            self.fieldPropertiesListstore.set(line, 1, str(properties[key]))

    def getCurrentProject(self):
        return self.controller.netzob.getCurrentProject()
