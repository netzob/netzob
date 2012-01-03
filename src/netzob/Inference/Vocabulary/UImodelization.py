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
import gtk
import pango
import pygtk
pygtk.require('2.0')
import logging
import threading
import copy
import os
import time
import random
import uuid

#+---------------------------------------------- 
#| Local Imports
#+----------------------------------------------
from netzob.Common.ConfigurationParser import ConfigurationParser
from netzob.Common.TypeConvertor import TypeConvertor
from netzob.Common.Symbol import Symbol
from netzob.Common.ProjectConfiguration import ProjectConfiguration
from netzob.Common.Models.RawMessage import RawMessage
from netzob.Common.MMSTD.Dictionary.Variables.WordVariable import WordVariable
from netzob.Inference.Vocabulary.SearchView import SearchView
from netzob.Inference.Vocabulary.Entropy import Entropy
from netzob.Inference.Vocabulary.TreeViews.TreeSymbolGenerator import TreeSymbolGenerator
from netzob.Inference.Vocabulary.TreeViews.TreeMessageGenerator import TreeMessageGenerator
from netzob.Inference.Vocabulary.TreeViews.TreeTypeStructureGenerator import TreeTypeStructureGenerator
from netzob.Inference.Vocabulary.VariableView import VariableView

#+---------------------------------------------- 
#| UImodelization :
#|     GUI for message modelization
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.2
#+---------------------------------------------- 
class UImodelization:
    TARGET_TYPE_TEXT = 80
    TARGETS = [('text/plain', 0, TARGET_TYPE_TEXT)]
    
    #+---------------------------------------------- 
    #| Called when user select a new trace
    #+----------------------------------------------
    def new(self):
        pass

    def update(self):
        self.updateTreeStoreSymbol()
        self.updateTreeStoreMessage()
        self.updateTreeStoreTypeStructure()

    def clear(self):
        self.selectedSymbol = None

    def kill(self):
        pass
    
    def save(self, aFile):
        self.log.info("Saving the vocabulary infered")
    
    #+---------------------------------------------- 
    #| Constructor :
    #| @param netzob: the netzob main class
    #+----------------------------------------------   
    def __init__(self, netzob):
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Modelization.UImodelization.py')
        self.netzob = netzob
        self.selectedSymbol = None
        self.selectedMessage = None
        self.treeMessageGenerator = TreeMessageGenerator()
        self.treeMessageGenerator.initialization()
        self.treeTypeStructureGenerator = TreeTypeStructureGenerator()
        self.treeTypeStructureGenerator.initialization()
        self.treeSymbolGenerator = TreeSymbolGenerator(self.netzob)
        self.treeSymbolGenerator.initialization()
        
        # Definition of the Sequence Onglet
        # First we create an VBox which hosts the two main children
        self.panel = gtk.VBox(False, spacing=0)
        self.panel.show()
        self.defer_select = False

        configParser = ConfigurationParser()
        
        #+---------------------------------------------- 
        #| TOP PART OF THE GUI : BUTTONS
        #+----------------------------------------------
        topPanel = gtk.HBox(False, spacing=5)
        topPanel.show()
        self.panel.pack_start(topPanel, False, False, 0)

        ## Message format inference
        frame = gtk.Frame()
        frame.set_label("1 - Message format inference")
        frame.show()
        topPanel.pack_start(frame, False, False, 0)
        table = gtk.Table(rows=3, columns=2, homogeneous=False)
        table.show()
        frame.add(table)

        # Widget for discovering the alignment
        but = gtk.Button(gtk.STOCK_OK)
        but.set_label("Discover alignment")
        but.connect("clicked", self.discoverAlignment_cb)
        but.show()
        table.attach(but, 0, 2, 0, 1, xoptions=gtk.FILL | gtk.EXPAND, yoptions=gtk.FILL, xpadding=5, ypadding=5)

        # Widget for forcing alignment delimiter
        but = gtk.Button(gtk.STOCK_OK)
        but.set_label("Force alignment")
        but.connect("clicked", self.forceAlignment_cb)
        but.show()
        table.attach(but, 0, 2, 1, 2, xoptions=gtk.FILL | gtk.EXPAND, yoptions=gtk.FILL, xpadding=5, ypadding=5)

        # Widget button slick regex
        but = gtk.Button("Slick regexes")
        but.connect("clicked", self.slickRegex_cb)
        but.show()
        table.attach(but, 0, 2, 2, 3, xoptions=gtk.FILL | gtk.EXPAND, yoptions=gtk.FILL, xpadding=5, ypadding=5)
       
        ## Field type inference
        frame = gtk.Frame()
        frame.set_label("3 - Field type inference")
        frame.show()
        topPanel.pack_start(frame, False, False, 0)
        table = gtk.Table(rows=5, columns=2, homogeneous=False)
        table.show()
        frame.add(table)

        # Widget button refine regex
        but = gtk.Button("Refine regexes")
        but.connect("clicked", self.refineRegexes_cb)
        but.show()
        table.attach(but, 0, 1, 0, 1, xoptions=0, yoptions=0, xpadding=5, ypadding=5)

        # Widget button to show message distribution
        but = gtk.Button("Messages distribution")
        but.connect("clicked", self.messagesDistribution_cb)
        but.show()
        table.attach(but, 0, 1, 1, 2, xoptions=0, yoptions=0, xpadding=5, ypadding=5)

        # Widget button to analyze for ASN.1 presence
        but = gtk.Button("Find ASN.1 fields")
        but.connect("clicked", self.findASN1Fields_cb)
        but.show()
        table.attach(but, 0, 1, 2, 3, xoptions=0, yoptions=0, xpadding=5, ypadding=5)

        # Widget for choosing the analysed protocole type
        label = gtk.Label("Protocol type : ")
        label.show()
        combo = gtk.combo_box_entry_new_text()
#        combo.set_size_request(300, -1)
        combo.set_model(gtk.ListStore(str))
        combo.append_text("Text based (HTTP, FTP)")
        combo.append_text("Fixed fields binary based (IP, TCP)")
        combo.append_text("Variable fields binary based (ASN.1)")
        combo.connect("changed", self.updateProtocolType)
        protocol_type_ID = configParser.getInt("clustering", "protocol_type")
        combo.set_active(protocol_type_ID)
        combo.show()
        table.attach(label, 0, 1, 3, 4, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        table.attach(combo, 0, 1, 4, 5, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        ## Dependencies inference
        frame = gtk.Frame()
        frame.set_label("4 - Dependencies inference")
        frame.show()
        topPanel.pack_start(frame, False, False, 0)
        table = gtk.Table(rows=4, columns=4, homogeneous=False)
        table.show()
        frame.add(table)

        # Widget button find size fields
        but = gtk.Button("Find size fields")
        # TODO: just try to use an ASN.1 parser to find the simple TLV protocols
        but.connect("clicked", self.findSizeFields)
        but.show()
        table.attach(but, 0, 1, 0, 1, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        # Widget button for environment dependencies
        but = gtk.Button("Environment dependencies")
        but.connect("clicked", self.env_dependencies_cb)
        but.show()
        table.attach(but, 0, 1, 1, 2, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        ## Semantic inference
        frame = gtk.Frame()
        frame.set_label("5 - Semantic inference")
        frame.show()
        topPanel.pack_start(frame, False, False, 0)
        table = gtk.Table(rows=4, columns=4, homogeneous=False)
        table.show()
        frame.add(table)

        # Widget button data carving
        but = gtk.Button("Data carving")
        but.connect("clicked", self.dataCarving_cb)
        but.show()
        table.attach(but, 0, 1, 0, 1, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        # Widget button for search
        but = gtk.Button("Search")
        but.connect("clicked", self.search_cb)
        but.show()
        table.attach(but, 0, 1, 1, 2, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        #+---------------------------------------------- 
        #| LEFT PART OF THE GUI : SYMBOL TREEVIEW
        #+----------------------------------------------           
        bottomPanel = gtk.HPaned()
        bottomPanel.show()
        self.panel.pack_start(bottomPanel, True, True, 0)
        leftPanel = gtk.VBox(False, spacing=0)
#        leftPanel.set_size_request(-1, -1)
        leftPanel.show()
        bottomPanel.add(leftPanel)
        # Initialize the treeview generator for the symbols
        leftPanel.pack_start(self.treeSymbolGenerator.getScrollLib(), True, True, 0)
        # Attach to the treeview few actions (DnD, cursor and buttons handlers...)
        self.treeSymbolGenerator.getTreeview().enable_model_drag_dest(self.TARGETS, gtk.gdk.ACTION_DEFAULT | gtk.gdk.ACTION_MOVE)
        self.treeSymbolGenerator.getTreeview().connect("drag_data_received", self.drop_fromDND)
#        self.treeSymbolGenerator.getTreeview().connect("cursor-changed", self.symbolChanged)
        self.treeSymbolGenerator.getTreeview().connect('button-press-event', self.button_press_on_treeview_symbols)

        #+---------------------------------------------- 
        #| RIGHT PART OF THE GUI : MESSAGE TREEVIEW MESSAGE
        #+----------------------------------------------
        rightPanel = gtk.VPaned()
        rightPanel.show()
        bottomPanel.add(rightPanel)
        rightPanel.add(self.treeMessageGenerator.getScrollLib())
        
        # Attach to the treeview few actions (DnD, cursor and buttons handlers...)
        self.treeMessageGenerator.getTreeview().enable_model_drag_source(gtk.gdk.BUTTON1_MASK, self.TARGETS, gtk.gdk.ACTION_DEFAULT | gtk.gdk.ACTION_MOVE)
        self.treeMessageGenerator.getTreeview().connect("drag-data-get", self.drag_fromDND)      
        self.treeMessageGenerator.getTreeview().connect('button-press-event', self.button_press_on_treeview_messages)
        self.treeMessageGenerator.getTreeview().connect('button-release-event', self.button_release_on_treeview_messages)
        self.treeMessageGenerator.getTreeview().connect("row-activated", self.dbClickToChangeType)

        #+---------------------------------------------- 
        #| RIGHT PART OF THE GUI : TYPE STRUCTURE OUTPUT
        #+----------------------------------------------
        rightPanel.add(self.treeTypeStructureGenerator.getScrollLib())        
        self.treeTypeStructureGenerator.getTreeview().connect('button-press-event', self.button_press_on_treeview_typeStructure)
        self.log.debug("GUI for sequential part is created")

    #+---------------------------------------------- 
    #| discoverAlignment :
    #|   Parse the traces and store the results
    #+----------------------------------------------
    def discoverAlignment_cb(self, widget):
        if self.netzob.getCurrentProject() == None:
            self.log.info("A project must be loaded to start an analysis")
            return
        self.selectedSymbol = None
        self.treeMessageGenerator.clear()
        self.treeSymbolGenerator.clear()
        self.treeTypeStructureGenerator.clear()
        self.update()

        dialog = gtk.Dialog(title="Search", flags=0, buttons=None)
        panel = gtk.Table(rows=3, columns=3, homogeneous=False)
        panel.show()
        configParser = ConfigurationParser()

        ## Similarity threshold
        label = gtk.Label("Similarity threshold:")
        label.show()
        combo = gtk.combo_box_entry_new_text()
        combo.set_model(gtk.ListStore(str))
        combo.connect("changed", self.updateScoreLimit)
        possible_choices = [100, 95, 90, 85, 80, 75, 70, 65, 60, 55, 50, 45, 40, 35, 30, 25, 20, 15, 10, 5]
        min_equivalence = configParser.getFloat("clustering", "equivalence_threshold")
        for i in range(len(possible_choices)):
            combo.append_text(str(possible_choices[i]))
            if str(possible_choices[i]) == str(int(min_equivalence)):
                combo.set_active(i)
        combo.show()
        panel.attach(label, 0, 1, 0, 1, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        panel.attach(combo, 1, 2, 0, 1, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        # Widget button activate orphan reduction
        butOrphanReduction = gtk.CheckButton("Orphan reduction")
        doOrphanReduction = configParser.getInt("clustering", "orphan_reduction")
        if doOrphanReduction == 1:
            butOrphanReduction.set_active(True)
        else:
            butOrphanReduction.set_active(False)
        butOrphanReduction.connect("toggled", self.activeOrphanReduction)
        butOrphanReduction.show()
        panel.attach(butOrphanReduction, 0, 1, 1, 2, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        # Widget checkbox for selecting the slickery during alignement process
        but = gtk.CheckButton("Slick regexes")
        doInternalSlick = configParser.getInt("clustering", "do_internal_slick")
        if doInternalSlick == 1:
            but.set_active(True)
        else:
            but.set_active(False)
        but.connect("toggled", self.activeInternalSlickRegexes)
        but.show()
        panel.attach(but, 1, 2, 1, 2, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        # Widget button merge common regexes
#        but = gtk.Button("Merge common regexes")
#        but.connect("clicked", self.netzob.symbols.mergeCommonRegexes, self)
        ## TODO: merge common regexes (if it is really usefull)
#        but.show()
#        but.set_sensitive(False)
#        panel.attach(but, 0, 1, 2, 3, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        # Button
        searchButton = gtk.Button("Discover alignment")
        searchButton.show()
        searchButton.connect("clicked", self.discoverAlignment_cb_cb, dialog)
        panel.attach(searchButton, 0, 2, 2, 3, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        dialog.vbox.pack_start(panel, True, True, 0)
        dialog.show()

    #+---------------------------------------------- 
    #| discoverAlignment_cb_cb :
    #|   Force the delimiter for sequence alignment
    #+----------------------------------------------
    def discoverAlignment_cb_cb(self, widget, dialog):
        vocabulary = self.netzob.getCurrentProject().getVocabulary()
        self.alignThread = threading.Thread(None, vocabulary.alignWithNeedlemanWunsh, None, ([self.netzob.getCurrentProject().getConfiguration(), self.update]), {})
        dialog.destroy()
        self.alignThread.start()
        
    #+---------------------------------------------- 
    #| forceAlignment_cb :
    #|   Force the delimiter for sequence alignment
    #+----------------------------------------------
    def forceAlignment_cb(self, widget):
        if self.netzob.getCurrentProject() == None:
            logging.info("A project must be loaded to start an analysis")
            return

        self.selectedSymbol = None
        self.treeMessageGenerator.clear()
        self.treeSymbolGenerator.clear()
        self.treeTypeStructureGenerator.clear()
        self.update()
        dialog = gtk.Dialog(title="Search", flags=0, buttons=None)
        panel = gtk.Table(rows=3, columns=3, homogeneous=False)
        panel.show()

        # Label
        label = gtk.Label("Delimiter: ")
        label.show()
        panel.attach(label, 0, 1, 0, 1, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        # Entry for delimiter
        entry = gtk.Entry(4)
        entry.show()
        panel.attach(entry, 1, 2, 0, 1, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        # Label
        label = gtk.Label("Encoding type: ")
        label.show()
        panel.attach(label, 0, 1, 1, 2, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        # Delimiter type
        typeCombo = gtk.combo_box_entry_new_text()
        typeCombo.show()
        typeStore = gtk.ListStore(str)
        typeCombo.set_model(typeStore)
        typeCombo.get_model().append(["ascii"])
        typeCombo.get_model().append(["binary"])
        typeCombo.set_active(0)
        panel.attach(typeCombo, 1, 2, 1, 2, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        # Button
        searchButton = gtk.Button("Force alignment")
        searchButton.show()
        searchButton.connect("clicked", self.forceAlignment_cb_cb, dialog, typeCombo, entry)
        panel.attach(searchButton, 0, 2, 2, 3, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        dialog.vbox.pack_start(panel, True, True, 0)
        dialog.show()

    #+---------------------------------------------- 
    #| forceAlignment_cb_cb :
    #|   Force the delimiter for sequence alignment
    #+----------------------------------------------
    def forceAlignment_cb_cb(self, widget, dialog, encodingType, delimiter):
        encodingType = encodingType.get_active_text()
        delimiter = delimiter.get_text()

        if encodingType == "ascii":
            delimiter = TypeConvertor.ASCIIToNetzobRaw(delimiter)            

        vocabulary = self.netzob.getCurrentProject().getVocabulary()
        vocabulary.alignWithDelimiter(self.netzob.getCurrentProject().getConfiguration(),
                                      encodingType,
                                      delimiter)
        self.update()
        dialog.destroy()
    
    #+---------------------------------------------- 
    #| button_press_on_treeview_symbols :
    #|   operation when the user click on the treeview.
    #|   mainly to open a contextual menu
    #+----------------------------------------------
    def button_press_on_treeview_symbols(self, treeview, event):
        self.log.debug("User requested a contextual menu (treeview symbol)")
        
        project = self.netzob.getCurrentProject()
        if project == None :
            self.log.warn("No current project loaded")
            return 
        if project.getVocabulary() == None :
            self.log.warn("The current project doesn't have any referenced vocabulary")
            return
        
        
        x = int(event.x)
        y = int(event.y)
        clickedSymbol = self.treeSymbolGenerator.getSymbolAtPosition(x, y)
        
        if event.type == gtk.gdk.BUTTON_PRESS and event.button == 1 and clickedSymbol != None :
            self.selectedSymbol = clickedSymbol
            self.updateTreeStoreMessage()
            self.treeTypeStructureGenerator.clear()
            self.updateTreeStoreTypeStructure()
        if event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
            self.build_context_menu_for_symbols(event, clickedSymbol)

    def button_release_on_treeview_messages(self, treeview, event):
        # re-enable selection
        treeview.get_selection().set_select_function(lambda * ignore: True)
        target = treeview.get_path_at_pos(int(event.x), int(event.y))
        if (self.defer_select and target and self.defer_select == target[0] and not (event.x == 0 and event.y == 0)): # certain drag and drop
            treeview.set_cursor(target[0], target[1], False)
            self.defer_select = False

    #+---------------------------------------------- 
    #| button_press_on_treeview_messages :
    #|   operation when the user click on the treeview.
    #|   mainly to open a contextual menu
    #+----------------------------------------------
    def button_press_on_treeview_messages(self, treeview, event):
        target = treeview.get_path_at_pos(int(event.x), int(event.y))
        if (target and event.type == gtk.gdk.BUTTON_PRESS and not (event.state & (gtk.gdk.CONTROL_MASK | gtk.gdk.SHIFT_MASK)) and treeview.get_selection().path_is_selected(target[0])):
            # disable selection
            treeview.get_selection().set_select_function(lambda * ignore: False)
            self.defer_select = target[0]

        # Display the details of a packet
        if event.type == gtk.gdk.BUTTON_PRESS and event.button == 1:
            x = int(event.x)
            y = int(event.y)
            (path, treeviewColumn, x, y) = treeview.get_path_at_pos(x, y)
            aIter = treeview.get_model().get_iter(path)
            if aIter:
                if treeview.get_model().iter_is_valid(aIter):
                    message_id = treeview.get_model().get_value(aIter, 0)
                    symbol = self.treeMessageGenerator.getSymbol()
                    self.treeTypeStructureGenerator.setSymbol(symbol)
                    self.treeTypeStructureGenerator.setMessageByID(message_id)
                    self.updateTreeStoreTypeStructure()

        # Popup a menu
        elif event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
            self.log.debug("User requested a contextual menu (treeview messages)")
            x = int(event.x)
            y = int(event.y)
            (path, treeviewColumn, x, y) = treeview.get_path_at_pos(x, y)
            
            # Retrieve the selected message
            message_id = None
            aIter = treeview.get_model().get_iter(path)
            if aIter:
                if treeview.get_model().iter_is_valid(aIter):
                    message_id = treeview.get_model().get_value(aIter, 0)
            

            # Retrieve the selected column number
            iField = 0
            for col in treeview.get_columns():
                if col == treeviewColumn:
                    break
                iField += 1
                
            selectedField = None
            for field in self.treeMessageGenerator.getSymbol().getFields() :
                if field.getIndex() == iField :
                    selectedField = field
            if selectedField == None :
                self.log.warn("Impossible to retrieve the clicked field !")
                return
                
            menu = gtk.Menu()
            # Add sub-entries to change the type of a specific column
            typesList = self.treeMessageGenerator.getSymbol().getPossibleTypesForAField(selectedField)
            typeMenu = gtk.Menu()
            for aType in typesList:
                item = gtk.MenuItem(str(aType))
                item.show()
                item.connect("activate", self.rightClickToChangeType, selectedField, aType)   
                typeMenu.append(item)
            item = gtk.MenuItem("Render in ...")
            item.set_submenu(typeMenu)
            item.show()
            menu.append(item)

            # Add entries to concatenate column
            concatMenu = gtk.Menu()
            if selectedField.getIndex() > 0 :
                item = gtk.MenuItem("with precedent field")
                item.show()
                item.connect("activate", self.rightClickToConcatColumns, selectedField, "left")
                concatMenu.append(item)
                
            if selectedField.getIndex() < len(self.treeMessageGenerator.getSymbol().getFields()) - 1:
                item = gtk.MenuItem("with next field")
                item.show()
                item.connect("activate", self.rightClickToConcatColumns, selectedField, "right")
                concatMenu.append(item)
            item = gtk.MenuItem("Concatenate")
            item.set_submenu(concatMenu)
            item.show()
            menu.append(item)

            # Add entry to split the column
            item = gtk.MenuItem("Split column")
            item.show()
            item.connect("activate", self.rightClickToSplitColumn, selectedField)
            menu.append(item)

            # Add entry to retrieve the field domain of definition
            item = gtk.MenuItem("Domain of definition")
            item.show()
            item.connect("activate", self.rightClickDomainOfDefinition, selectedField)
            menu.append(item)
            
            
            # Add sub-entries to change the variable of a specific column
            typeMenuVariable = gtk.Menu()
            itemVariable = gtk.MenuItem("Create a variable")
            itemVariable.show()
            itemVariable.connect("activate", self.rightClickCreateVariable, selectedField)   
            typeMenuVariable.append(itemVariable)
            
            existingVariables = self.netzob.getCurrentProject().getVocabulary().getVariables()
            
            if len(existingVariables) > 0 :
                listMenuVariable = gtk.Menu()
                for variable in existingVariables :
                    itemVariableToAttach = gtk.MenuItem(variable.getName())
                    itemVariableToAttach.show()
                    itemVariableToAttach.connect("activate", self.rightClickCreateVariable, selectedField)   
                    listMenuVariable.append(itemVariableToAttach)
                
                itemVariable2 = gtk.MenuItem("Attach to an existing variable")
                itemVariable2.show()
                itemVariable2.set_submenu(listMenuVariable)
                itemVariable2.connect("activate", self.rightClickAttachVariable, selectedField)   
                typeMenuVariable.append(itemVariable2)
            
            itemVariable3 = gtk.MenuItem("Remove variable")
            itemVariable3.show()
            itemVariable3.connect("activate", self.rightClickRemoveVariable, selectedField)   
            typeMenuVariable.append(itemVariable3)
            
            item = gtk.MenuItem("Configure variation ...")
            item.set_submenu(typeMenuVariable)
            item.show()
            menu.append(item)
            
            # Add entry to show properties of the message
            item = gtk.MenuItem("Properties")
            item.show()
            item.connect("activate", self.rightClickShowPropertiesOfMessage, message_id)
            menu.append(item)
            
            # Add entry to delete the message
            item = gtk.MenuItem("Delete message")
            item.show()
            item.connect("activate", self.rightClickDeleteMessage, message_id)
            menu.append(item)

            menu.popup(None, None, None, event.button, event.time)

    #+---------------------------------------------- 
    #| button_press_on_treeview_typeStructure :
    #|   operation when the user click on the treeview.
    #|   mainly to open a contextual menu
    #+----------------------------------------------
    def button_press_on_treeview_typeStructure(self, treeview, event):
        if self.treeTypeStructureGenerator.getMessage() == None:
            return

        # Popup a menu
        if event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
            self.log.debug("User requested a contextual menu (on treeview typeStructure)")
            x = int(event.x)
            y = int(event.y)
            (path, treeviewColumn, x, y) = treeview.get_path_at_pos(x, y)
            (iField,) = path
            
            
            selectedField = None
            for field in self.treeMessageGenerator.getSymbol().getFields() :
                if field.getIndex() == iField :
                    selectedField = field
            if selectedField == None :
                self.log.warn("Impossible to retrieve the clicked field !")
                return
            
            menu = gtk.Menu()
            # Add sub-entries to change the type of a specific field
            typesList = self.treeMessageGenerator.getSymbol().getPossibleTypesForAField(selectedField)
            typeMenu = gtk.Menu()
            for aType in typesList:
                item = gtk.MenuItem("Render in : " + str(aType))
                item.show()
                item.connect("activate", self.rightClickToChangeType, selectedField, aType)   
                typeMenu.append(item)
            item = gtk.MenuItem("Change Type")
            item.set_submenu(typeMenu)
            item.show()
            menu.append(item)

            # Add entries to concatenate fields
            concatMenu = gtk.Menu()
            item = gtk.MenuItem("with precedent field")
            item.show()
            item.connect("activate", self.rightClickToConcatColumns, selectedField, "left")
            concatMenu.append(item)
            item = gtk.MenuItem("with next field")
            item.show()
            item.connect("activate", self.rightClickToConcatColumns, selectedField, "right")
            concatMenu.append(item)
            item = gtk.MenuItem("Concatenate")
            item.set_submenu(concatMenu)
            item.show()
            menu.append(item)

            # Add entry to split the field
            item = gtk.MenuItem("Split column")
            item.show()
            item.connect("activate", self.rightClickToSplitColumn, selectedField)
            menu.append(item)

            # Add entry to export fields
            item = gtk.MenuItem("Export selected fields")
            item.show()
            item.connect("activate", self.exportSelectedFields_cb)
            menu.append(item)

            menu.popup(None, None, None, event.button, event.time)

    #+---------------------------------------------- 
    #| exportSelectedFields_cb :
    #|   Callback to export the selected fields
    #|   as a new trace
    #+----------------------------------------------
    def exportSelectedFields_cb(self, event):
        # Retrieve associated messages of selected fields
        aggregatedCells = {}
        (model, paths) = self.treeTypeStructureGenerator.getTreeview().get_selection().get_selected_rows()
        for path in paths:
            aIter = model.get_iter(path)
            if(model.iter_is_valid(aIter)):
                iField = model.get_value(aIter, 0)
                
                selectedField = None
                for field in self.treeMessageGenerator.getSymbol().getFields() :
                    if field.getIndex() == iField :
                        selectedField = field
                if selectedField == None :
                    self.log.warn("Impossible to retrieve the clicked field !")
                    return
                
                cells = self.treeTypeStructureGenerator.getSymbol().getMessagesValuesByField(selectedField)
                for i in range(len(cells)):
                    if not i in aggregatedCells:
                        aggregatedCells[i] = ""
                    aggregatedCells[i] += str(cells[i])

        # Popup a menu to save the data
        dialog = gtk.Dialog(title="Save selected data", flags=0, buttons=None)
        dialog.show()
        table = gtk.Table(rows=2, columns=3, homogeneous=False)
        table.show()

        # Add to an existing trace
        label = gtk.Label("Add to an existing trace")
        label.show()
        entry = gtk.combo_box_entry_new_text()
        entry.show()
        entry.set_size_request(300, -1)
        entry.set_model(gtk.ListStore(str))
        projectsDirectoryPath = ConfigurationParser().get("projects", "path")
        for tmpDir in os.listdir(projectsDirectoryPath):
            if tmpDir == '.svn':
                continue
            entry.append_text(tmpDir)
        but = gtk.Button("Save")
        but.connect("clicked", self.add_packets_to_existing_trace, entry, aggregatedCells, dialog)
        but.show()
        table.attach(label, 0, 1, 0, 1, xoptions=0, yoptions=0, xpadding=5, ypadding=5)
        table.attach(entry, 1, 2, 0, 1, xoptions=0, yoptions=0, xpadding=5, ypadding=5)
        table.attach(but, 2, 3, 0, 1, xoptions=0, yoptions=0, xpadding=5, ypadding=5)

        # Create a new trace
        label = gtk.Label("Create a new trace")
        label.show()
        entry = gtk.Entry()
        entry.show()
        but = gtk.Button("Save")
        but.connect("clicked", self.create_new_trace, entry, aggregatedCells, dialog)
        but.show()
        table.attach(label, 0, 1, 1, 2, xoptions=0, yoptions=0, xpadding=5, ypadding=5)
        table.attach(entry, 1, 2, 1, 2, xoptions=0, yoptions=0, xpadding=5, ypadding=5)
        table.attach(but, 2, 3, 1, 2, xoptions=0, yoptions=0, xpadding=5, ypadding=5)

        dialog.action_area.pack_start(table, True, True, 0)

    #+---------------------------------------------- 
    #| Add a selection of packets to an existing trace
    #+----------------------------------------------
    def add_packets_to_existing_trace(self, button, entry, messages, dialog):
        projectsDirectoryPath = ConfigurationParser().get("projects", "path")
        existingTraceDir = projectsDirectoryPath + os.sep + entry.get_active_text()
        # Create the new XML structure
        res = "<datas>\n"
        for message in messages:
            res += "<data proto=\"ipc\" sourceIp=\"local\" sourcePort=\"local\" targetIp=\"local\" targetPort=\"local\" timestamp=\"" + str(time.time()) + "\">\n"
            res += message + "\n"
            res += "</data>\n"
        res += "</datas>\n"
        # Dump into a random XML file
        fd = open(existingTraceDir + os.sep + str(random.randint(100000, 9000000)) + ".xml"  , "w")
        fd.write(res)
        fd.close()
        dialog.destroy()

    #+---------------------------------------------- 
    #| Creation of a new trace from a selection of packets
    #+----------------------------------------------
    def create_new_trace(self, button, entry, messages, dialog):
        projectsDirectoryPath = ConfigurationParser().get("projects", "path")
        for tmpDir in os.listdir(projectsDirectoryPath):
            if tmpDir == '.svn':
                continue
            if entry.get_text() == tmpDir:
                dialogBis = gtk.Dialog(title="This trace already exists", flags=0, buttons=None)
                dialogBis.set_size_request(250, 50)
                dialogBis.show()
                return

        # Create the dest Dir
        newTraceDir = projectsDirectoryPath + os.sep + entry.get_text()
        os.mkdir(newTraceDir)
        # Create the new XML structure
        res = "<datas>\n"
        for message in messages.values():
            res += "<data proto=\"ipc\" sourceIp=\"local\" sourcePort=\"local\" targetIp=\"local\" targetPort=\"local\" timestamp=\"" + str(time.time()) + "\">\n"
            res += message + "\n"
            res += "</data>\n"
        res += "</datas>\n"
        # Dump into a random XML file
        fd = open(newTraceDir + os.sep + str(random.randint(100000, 9000000)) + ".xml"  , "w")
        fd.write(res)
        fd.close()
        dialog.destroy()
        self.netzob.updateListOfAvailableProjects()

    #+---------------------------------------------- 
    #| rightClickDomainOfDefinition :
    #|   Retrieve the domain of definition of the selected column
    #+----------------------------------------------
    def rightClickDomainOfDefinition(self, event, field):
        cells = self.treeMessageGenerator.getSymbol().getMessagesValuesByField(field)
        tmpDomain = set()
        for cell in cells:
            tmpDomain.add(TypeConvertor.encodeNetzobRawToGivenType(cell, field.getSelectedType()))
        domain = sorted(tmpDomain)

        dialog = gtk.Dialog(title="Domain of definition for the column " + field.getName(), flags=0, buttons=None)
         
        # Text view containing domain of definition 
        ## ListStore format :
        # str: symbol.id
        treeview = gtk.TreeView(gtk.ListStore(str)) 
        treeview.set_size_request(500, 300)
        treeview.show()
        
        cell = gtk.CellRendererText()
        cell.set_sensitive(True)
        cell.set_property('editable', True)
        
        column = gtk.TreeViewColumn("Column " + str(field.getIndex()))
        column.pack_start(cell, True)
        column.set_attributes(cell, text=0)        
        
        treeview.append_column(column)

        currentProject = self.netzob.getCurrentProject()
        if currentProject == None :
            self.log.warn("No current project found")
            return
        if currentProject.getVocabulary() == None :
            self.log.warn("The project has no vocbaulary to work with.")
            return
        
        for elt in domain:
            treeview.get_model().append([elt])

        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scroll.show()
        scroll.add(treeview)
        
        dialog.vbox.pack_start(scroll, True, True, 0)
        dialog.show()

    #+---------------------------------------------- 
    #| rightClickShowPropertiesOfMessage :
    #|   Show a popup to present the properties of the selected message
    #+----------------------------------------------
    def rightClickShowPropertiesOfMessage(self, event, id_message):
        self.log.debug("The user wants to see the properties of message " + str(id_message))
        
        # Retrieve the selected message
        message = self.selectedSymbol.getMessageByID(id_message)
        if message == None :
            self.log.warning("Impossible to retrieve the message based on its ID [{0}]".format(id_message))
            return
        
        # Create the dialog
        dialog = gtk.Dialog(title="Properties of message " + str(message.getID()), flags=0, buttons=None)
        ## ListStore format : (str=key, str=value)
        treeview = gtk.TreeView(gtk.ListStore(str, str)) 
        treeview.set_size_request(500, 300)
        treeview.show()
        
        cell = gtk.CellRendererText()
        
        columnProperty = gtk.TreeViewColumn("Property")
        columnProperty.pack_start(cell, True)
        columnProperty.set_attributes(cell, text=0)
        
        columnValue = gtk.TreeViewColumn("Value")
        columnValue.pack_start(cell, True)
        columnValue.set_attributes(cell, text=1)        
        
        treeview.append_column(columnProperty)
        treeview.append_column(columnValue)
         
        # Retrieves all the properties of current message and 
        # insert them in the treeview
        for property in message.getProperties():
            treeview.get_model().append(property)
                
        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scroll.show()
        scroll.add(treeview)
        
        dialog.vbox.pack_start(scroll, True, True, 0)
        dialog.show()
            
        
    #+---------------------------------------------- 
    #| rightClickDeleteMessage :
    #|   Delete the requested message
    #+----------------------------------------------
    def rightClickDeleteMessage(self, event, id_message):
        self.log.debug("The user wants to delete the message " + str(id_message))
        
        message_symbol = self.selectedSymbol
        message = self.selectedSymbol.getMessageByID(id_message)
        
        # Break if the message to move was not found
        if message == None :
            self.log.warning("Impossible to retrieve the message to remove based on its ID [{0}]".format(id_message))
            return
        
        questionMsg = "Click yes to confirm the deletion of message {0}".format(id_message)
        md = gtk.MessageDialog(None, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_QUESTION, gtk.BUTTONS_YES_NO, questionMsg)
        result = md.run()
        md.destroy()
        if result == gtk.RESPONSE_YES:
            self.log.debug("The user has confirmed !")
            message_symbol.removeMessage(message)
            self.update()
            

    #+---------------------------------------------- 
    #| rightClickToChangeType :
    #|   Callback to change the column type
    #|   by doing a right click
    #+----------------------------------------------
    def rightClickToChangeType(self, event, field, aType):
        field.setSelectedType(aType)
        self.update()

    #+---------------------------------------------- 
    #|  rightClickToConcatColumns:
    #|   Callback to concatenate two columns
    #+----------------------------------------------
    def rightClickToConcatColumns(self, event, field, strOtherCol):
        self.log.debug("Concatenate the column " + str(field.getIndex()) + " with the " + str(strOtherCol) + " column")

        if field.getIndex() == 0 and strOtherCol == "left":
            self.log.debug("Can't concatenate the first column with its left column")
            return

        if field.getIndex() + 1 == len(self.selectedSymbol.getFields()) and strOtherCol == "right":
            self.log.debug("Can't concatenate the last column with its right column")
            return

        if strOtherCol == "left":
            self.selectedSymbol.concatFields(field.getIndex() - 1)
        else:
            self.selectedSymbol.concatFields(field.getIndex())
        self.treeMessageGenerator.updateDefault()
        self.update()

    #+---------------------------------------------- 
    #|  rightClickToSplitColumn:
    #|   Callback to split a column
    #+----------------------------------------------
    def rightClickToSplitColumn(self, event, field):
        dialog = gtk.Dialog(title="Split column " + str(field.getIndex()), flags=0, buttons=None)
        textview = gtk.TextView()
        textview.set_editable(False)
        textview.get_buffer().create_tag("redTag", weight=pango.WEIGHT_BOLD, foreground="red", family="Courier")
        textview.get_buffer().create_tag("greenTag", weight=pango.WEIGHT_BOLD, foreground="#006400", family="Courier")
        self.split_position = 2
        self.split_max_len = 0

        # Find the size of the longest message
        cells = self.selectedSymbol.getMessagesValuesByField(field)
        for m in cells:
            if len(m) > self.split_max_len:
                self.split_max_len = len(m)

        # Left arrow
        arrow = gtk.Arrow(gtk.ARROW_LEFT, gtk.SHADOW_OUT)
        arrow.show()
        but = gtk.Button()
        but.add(arrow)
        but.connect("clicked", self.adjustSplitColumn, textview, "left", field)
        but.show()
        dialog.action_area.pack_start(but, True, True, 0)

        # Right arrow
        arrow = gtk.Arrow(gtk.ARROW_RIGHT, gtk.SHADOW_OUT)
        arrow.show()
        but = gtk.Button()
        but.add(arrow)
        but.connect("clicked", self.adjustSplitColumn, textview, "right", field)
        but.show()
        dialog.action_area.pack_start(but, True, True, 0)

        # Split button
        but = gtk.Button(label="Split column")
        but.show()
        but.connect("clicked", self.doSplitColumn, textview, field, dialog)
        dialog.action_area.pack_start(but, True, True, 0)

        # Text view containing selected column messages
        frame = gtk.Frame()
        frame.set_label("Content of the column to split")
        frame.show()
        textview.set_size_request(400, 300)
#        cells = self.treeMessageGenerator.getSymbol().getCellsByCol(iCol)

        for m in cells:
            textview.get_buffer().insert_with_tags_by_name(textview.get_buffer().get_end_iter(), TypeConvertor.encodeNetzobRawToGivenType(m[:self.split_position], field.getSelectedType()) + "  ", "redTag")
            textview.get_buffer().insert_with_tags_by_name(textview.get_buffer().get_end_iter(), TypeConvertor.encodeNetzobRawToGivenType(m[self.split_position:], field.getSelectedType()) + "\n", "greenTag")
        textview.show()
        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scroll.show()
        scroll.add(textview)
        frame.add(scroll)
        dialog.vbox.pack_start(frame, True, True, 0)
        dialog.show()
    
    def rightClickCreateVariable(self, widget, field):
        self.log.debug("Opening the dialog for the creation of a variable")
        dialog = gtk.MessageDialog(None, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_QUESTION, gtk.BUTTONS_OK, None)
        dialog.set_markup('Definition of the new variable')
        
        # Create the ID of the new variable
        variableID = str(uuid.uuid4())
        
        mainTable = gtk.Table(rows=3, columns=2, homogeneous=False)
        # id of the variable
        variableIDLabel = gtk.Label("ID :")
        variableIDLabel.show()
        variableIDValueLabel = gtk.Label(variableID)
        variableIDValueLabel.set_sensitive(False)
        variableIDValueLabel.show()
        mainTable.attach(variableIDLabel, 0, 1, 0, 1, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        mainTable.attach(variableIDValueLabel, 1, 2, 0, 1, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        # name of the variable
        variableNameLabel = gtk.Label("Name : ")
        variableNameLabel.show()
        variableNameEntry = gtk.Entry()
        variableNameEntry.show()
        mainTable.attach(variableNameLabel, 0, 1, 1, 2, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        mainTable.attach(variableNameEntry, 1, 2, 1, 2, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        
        # is a mutable variable
        isMutableVariableLabel = gtk.Label("Mutable : ")
        isMutableVariableLabel.show()
        isMutableVariableButton = gtk.CheckButton("")
        isMutableVariableButton.show()
        
        mainTable.attach(isMutableVariableLabel, 0, 1, 2, 3, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        mainTable.attach(isMutableVariableButton, 1, 2, 2, 3, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        
        dialog.vbox.pack_end(mainTable, True, True, 0)
        dialog.show_all()
        result = dialog.run()
        
        if result != gtk.RESPONSE_OK :
            dialog.destroy()
            return 
        
        # We retrieve the value of the variable
        varName = variableNameEntry.get_text()
        varMutable = isMutableVariableButton.get_active()
        
        # We close the current dialog
        dialog.destroy()
        
        # We display the dedicated dialog for the creation of a variable
        dialog = gtk.Dialog(title="Creation of a variable", flags=0, buttons=None)
        
        creationPanel = VariableView(self.netzob.getCurrentProject(), variableID, varName, varMutable)
        dialog.vbox.pack_start(creationPanel.getPanel(), True, True, 0)
        dialog.show()
        
        
    def rightClickRemoveVariable(self, widget, field):
        pass
    def rightClickAttachVariable(self, widget, field):
        pass


    def doSplitColumn(self, widget, textview, field, dialog):
        if self.split_max_len <= 2:
            dialog.destroy()
            return

        self.selectedSymbol.splitField(field, self.split_position)
        self.treeMessageGenerator.updateDefault()            
        dialog.destroy()
        self.update()

    def adjustSplitColumn(self, widget, textview, direction, field):
        if self.split_max_len <= 2:
            return
        messages = self.selectedSymbol.getMessagesValuesByField(field)

        # Bounds checking
        if direction == "left":
            self.split_position -= 2
            if self.split_position < 2:
                self.split_position = 2
        else:
            self.split_position += 2
            if self.split_position > self.split_max_len - 2:
                self.split_position = self.split_max_len - 2

        # Colorize text according to position
        textview.get_buffer().set_text("")
        for m in messages:
            textview.get_buffer().insert_with_tags_by_name(textview.get_buffer().get_end_iter(), TypeConvertor.encodeNetzobRawToGivenType(m[:self.split_position], field.getSelectedType()) + "  ", "redTag")
            textview.get_buffer().insert_with_tags_by_name(textview.get_buffer().get_end_iter(), TypeConvertor.encodeNetzobRawToGivenType(m[self.split_position:], field.getSelectedType()) + "\n", "greenTag")

    #+---------------------------------------------- 
    #| dbClickToChangeType :
    #|   Called when user double click on a row
    #|    in order to change the column type
    #+----------------------------------------------
    def dbClickToChangeType(self, treeview, path, treeviewColumn):
        # Retrieve the selected column number
        iField = 0
        for col in treeview.get_columns():
            if col == treeviewColumn:
                break
            iField += 1
                
        selectedField = None
        for field in self.treeMessageGenerator.getSymbol().getFields() :
            if field.getIndex() == iField :
                selectedField = field
        
        if selectedField == None :
            self.log.warn("Impossible to retrieve the clicked field !")
            return
        
        # Find the next possible type for this column
        possibleTypes = self.treeMessageGenerator.getSymbol().getPossibleTypesForAField(selectedField)
        i = 0
        chosedType = selectedField.getSelectedType()
        for aType in possibleTypes:
            if aType == chosedType:
                chosedType = possibleTypes[(i + 1) % len(possibleTypes)]
                break
            i += 1

        # Apply the new choosen type for this column
        selectedField.setSelectedType(chosedType)
        self.treeMessageGenerator.updateDefault()
        
    #+---------------------------------------------- 
    #| build_context_menu_for_symbols :
    #|   Create a menu to display available operations
    #|   on the treeview symbols
    #+----------------------------------------------
    def build_context_menu_for_symbols(self, event, symbol):
        # Retrieves the symbol on which the user has clicked on
        
        entries = [        
                  (gtk.STOCK_EDIT, self.displayPopupToEditSymbol, (symbol != None)),
                  (gtk.STOCK_ADD, self.displayPopupToCreateSymbol, (symbol == None)),
                  (gtk.STOCK_REMOVE, self.displayPopupToRemoveSymbol, (symbol != None))
        ]

        menu = gtk.Menu()
        for stock_id, callback, sensitive in entries:
            item = gtk.ImageMenuItem(stock_id)
            item.connect("activate", callback, symbol)  
            item.set_sensitive(sensitive)
            item.show()
            menu.append(item)
        menu.popup(None, None, None, event.button, event.time)


    #+---------------------------------------------- 
    #| displayPopupToCreateSymbol_ResponseToDialog :
    #|   pygtk is so good ! arf :( <-- clap clap :D
    #+----------------------------------------------
    def displayPopupToCreateSymbol_ResponseToDialog(self, entry, dialog, response):
        dialog.response(response)

    def displayPopupToEditSymbol(self, event, symbol):
        dialog = gtk.MessageDialog(
        None,
        gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
        gtk.MESSAGE_QUESTION,
        gtk.BUTTONS_OK,
        None)
        dialog.set_markup("<b>Please enter the name of the symbol :</b>")
        #create the text input field
        entry = gtk.Entry()
        entry.set_text(symbol.getName())
        #allow the user to press enter to do ok
        entry.connect("activate", self.responseToDialog, dialog, gtk.RESPONSE_OK)
        #create a horizontal box to pack the entry and a label
        hbox = gtk.HBox()
        hbox.pack_start(gtk.Label("Name : "), False, 5, 5)
        hbox.pack_end(entry)
        dialog.vbox.pack_end(hbox, True, True, 0)
        dialog.show_all()
        #go go go
        dialog.run()
        text = entry.get_text()
        if (len(text) > 0) :
            self.selectedSymbol.setName(text)
        dialog.destroy()
        
        self.update()

    def responseToDialog(self, entry, dialog, response):
        dialog.response(response)
    
    
    #+---------------------------------------------- 
    #| displayPopupToCreateSymbol :
    #|   Display a form to create a new symbol.
    #|   Based on the famous dialogs
    #+----------------------------------------------
    def displayPopupToCreateSymbol(self, event, symbol):
        
        #base this on a message dialog
        dialog = gtk.MessageDialog(
                                   None,
                                   gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                   gtk.MESSAGE_QUESTION,
                                   gtk.BUTTONS_OK,
                                   None)
        dialog.set_markup("<b>Please enter symbol's name</b> :")
        #create the text input field
        entry = gtk.Entry()
        #allow the user to press enter to do ok
        entry.connect("activate", self.displayPopupToCreateSymbol_ResponseToDialog, dialog, gtk.RESPONSE_OK)
        #create a horizontal box to pack the entry and a label
        hbox = gtk.HBox()
        hbox.pack_start(gtk.Label("Name :"), False, 5, 5)
        hbox.pack_end(entry)
        #add it and show it
        dialog.vbox.pack_end(hbox, True, True, 0)
        dialog.show_all()
        #go go go
        dialog.run()
        newSymbolName = entry.get_text()
        dialog.destroy()
        
        if (len(newSymbolName) > 0) :
            newSymbolId = str(uuid.uuid4())
            self.log.debug("a new symbol will be created with the given name : {0}".format(newSymbolName))
            newSymbol = Symbol(newSymbolId, newSymbolName)
            
            self.netzob.getCurrentProject().getVocabulary().addSymbol(newSymbol)
            
            #Update Left and Right
            self.update()
        
    #+---------------------------------------------- 
    #| displayPopupToRemoveSymbol :
    #|   Display a popup to remove a symbol
    #|   the removal of a symbol can only occurs
    #|   if its an empty symbol
    #+----------------------------------------------    
    def displayPopupToRemoveSymbol(self, event, symbol):
        
        if (len(symbol.getMessages()) == 0) :
            self.log.debug("Can remove the symbol {0} since it's an empty one.".format(symbol.getName()))
            questionMsg = "Click yes to confirm the removal of the symbol {0}".format(symbol.getName())
            md = gtk.MessageDialog(None, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_QUESTION, gtk.BUTTONS_YES_NO, questionMsg)
            result = md.run()
            md.destroy()
            if result == gtk.RESPONSE_YES:
                self.netzob.getCurrentProject().getVocabulary().removeSymbol(symbol)
                #Update Left and Right
                self.update()
            else :
                self.log.debug("The user didn't confirm the deletion of the symbol " + symbol.getName())                
            
        else :
            self.log.debug("Can't remove the symbol {0} since its not an empty one.".format(symbol.getName()))
            errorMsg = "The selected symbol cannot be removed since it contains messages."
            md = gtk.MessageDialog(None, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_ERROR, gtk.BUTTONS_CLOSE, errorMsg)
            md.run()
            md.destroy()
        
    #+---------------------------------------------- 
    #| drop_fromDND :
    #|   defines the operation executed when a message is
    #|   is dropped out current symbol to the selected symbol 
    #+----------------------------------------------
    def drop_fromDND(self, treeview, context, x, y, selection, info, etime):
        ids = selection.data
        for msg_id in ids.split(";") :
            
            modele = treeview.get_model()
            info_depot = treeview.get_dest_row_at_pos(x, y)
            
            # First we search for the message to move
            message = None
            message_symbol = self.selectedSymbol
            for msg in message_symbol.getMessages() :
                if str(msg.getID()) == msg_id :
                    message = msg
            
            # Break if the message to move was not found
            if message == None :
                self.log.warning("Impossible to retrieve the message to move based on its ID [{0}]".format(msg_id))
                return
            
            self.log.debug("The message having the ID [{0}] has been found !".format(msg_id))
            
            # Now we search for the new symbol of the message
            if info_depot :
                chemin, position = info_depot
                iter = modele.get_iter(chemin)
                new_symbol_id = str(modele.get_value(iter, 0))
                
                new_message_symbol = self.netzob.getCurrentProject().getVocabulary().getSymbol(new_symbol_id)
                    
            if new_message_symbol == None :
                self.log.warning("Impossible to retrieve the symbol in which the selected message must be moved out.")
                return
            
            self.log.debug("The new symbol of the message is {0}".format(str(new_message_symbol.getID())))
            #Removing from its old symbol
            message_symbol.removeMessage(message)
            
            #Adding to its new symbol
            new_message_symbol.addMessage(message)            
        
        message_symbol.buildRegexAndAlignment(self.netzob.getCurrentProject().getConfiguration())
        new_message_symbol.buildRegexAndAlignment(self.netzob.getCurrentProject().getConfiguration())
        #Update Left and Right
        self.update()
        return
   
    #+---------------------------------------------- 
    #| drag_fromDND :
    #|   defines the operation executed when a message is
    #|   is dragged out current symbol 
    #+----------------------------------------------
    def drag_fromDND(self, treeview, contexte, selection, info, dateur):   
        ids = []             
        treeview.get_selection().selected_foreach(self.foreach_drag_fromDND, ids)
        selection.set(selection.target, 8, ";".join(ids))
    
    def foreach_drag_fromDND(self, model, path, iter, ids):
        texte = str(model.get_value(iter, 0))
        ids.append(texte)
        return
    
    #+---------------------------------------------- 
    #| Update the content of the tree store for symbols
    #+----------------------------------------------
    def updateTreeStoreSymbol(self):        
        # Updates the treestore with a selected message
        if (self.selectedMessage != None) :
            self.treeSymbolGenerator.messageSelected(self.selectedMessage)
            self.selectedMessage = None
        else :
            # Default display of the symbols
            self.treeSymbolGenerator.default()
 
    #+---------------------------------------------- 
    #| Update the content of the tree store for messages
    #+----------------------------------------------
    def updateTreeStoreMessage(self):     
        # If we found it we can update the content of the treestore        
        if self.selectedSymbol != None :
            self.treeMessageGenerator.default(self.selectedSymbol)
#            # enable dragging message out of current symbol
#            self.treeMessageGenerator.getTreeview().enable_model_drag_source(gtk.gdk.BUTTON1_MASK, self.TARGETS, gtk.gdk.ACTION_DEFAULT | gtk.gdk.ACTION_MOVE)
#            self.treeMessageGenerator.getTreeview().connect("drag-data-get", self.drag_fromDND)      
        else :
            self.treeMessageGenerator.default(None)
            
            

    #+---------------------------------------------- 
    #| Update the content of the tree store for type structure
    #+----------------------------------------------
    def updateTreeStoreTypeStructure(self):
        self.treeTypeStructureGenerator.update()
       
    
    #+---------------------------------------------- 
    #| Called when user select a new score limit
    #+----------------------------------------------
    def updateScoreLimit(self, combo):
        val = combo.get_active_text()
        if self.netzob.getCurrentProject() != None :
            self.netzob.getCurrentProject().getConfiguration().setVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_EQUIVALENCE_THRESHOLD, int(val))

    #+---------------------------------------------- 
    #| Called when user wants to slick internally in libNeedleman
    #+----------------------------------------------
    def activeInternalSlickRegexes(self, checkButton):
        if self.netzob.getCurrentProject() != None :
            self.netzob.getCurrentProject().getConfiguration().setVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_DO_INTERNAL_SLICK, checkButton.get_active())
        
    #+---------------------------------------------- 
    #| Called when user wants to activate orphan reduction
    #+----------------------------------------------
    def activeOrphanReduction(self, checkButton):
        if self.netzob.getCurrentProject() != None :
            self.netzob.getCurrentProject().getConfiguration().setVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_ORPHAN_REDUCTION, checkButton.get_active())

    #+---------------------------------------------- 
    #| Called when user wants to modify the expected protocol type
    #+----------------------------------------------
    def updateProtocolType(self, combo):
        valID = combo.get_active()
        if valID == 0:
            display = "ascii"
        else:
            display = "binary"
        
        if self.netzob.getCurrentProject() != None :
            self.netzob.getCurrentProject().getConfiguration().setVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_GLOBAL_DISPLAY, display)
        
            for symbol in self.netzob.getCurrentProject().getVocabulary().getSymbols():
                for field in symbol.getFields() :
                    field.setSelectedType(display)
            self.update()

    #+---------------------------------------------- 
    #| Called when user wants to refine regexes
    #+----------------------------------------------
    def refineRegexes_cb(self, button):
        for symbol in self.netzob.getCurrentProject().getVocabulary().getSymbols():
            symbol.refineRegexes()
        dialog = gtk.Dialog(title="Refinement done", flags=0, buttons=None)
        dialog.set_size_request(250, 50)
        dialog.show()
        self.update()

    #+---------------------------------------------- 
    #| Called when user wants to execute data carving
    #+----------------------------------------------
    def dataCarving_cb(self, button):
        dialog = gtk.Dialog(title="Data carving results", flags=0, buttons=None)
        
        if self.netzob.getCurrentProject() == None :
            return  
        
        notebook = gtk.Notebook()
        notebook.show()
        notebook.set_tab_pos(gtk.POS_TOP)
        for symbol in self.netzob.getCurrentProject().getVocabulary().getSymbols():
            scroll = symbol.dataCarving()
            if scroll != None:
                notebook.append_page(scroll, gtk.Label(symbol.getName()))
        

        dialog.vbox.pack_start(notebook, True, True, 0)
        dialog.show()

    #+---------------------------------------------- 
    #| Called when user wants to search data in messages
    #+----------------------------------------------
    def search_cb(self, button):
        dialog = gtk.Dialog(title="Search", flags=0, buttons=None)

        if self.netzob.getCurrentProject() == None :
            return
        
        searchPanel = SearchView(self.netzob.getCurrentProject())
        dialog.vbox.pack_start(searchPanel.getPanel(), True, True, 0)
        dialog.show()

    #+---------------------------------------------- 
    #| Called when user wants to identifies environment dependencies
    #+----------------------------------------------
    def env_dependencies_cb(self, button):
        dialog = gtk.Dialog(title="Search", flags=0, buttons=None)

        if self.netzob.getCurrentProject() == None :
            return

        notebook = gtk.Notebook()
        notebook.show()
        notebook.set_tab_pos(gtk.POS_TOP)
        for symbol in self.netzob.getCurrentProject().getVocabulary().getSymbols():
            scroll = symbol.envDependencies(self.netzob.getCurrentProject())
            if scroll != None:
                notebook.append_page(scroll, gtk.Label(symbol.getName())) 
            
        dialog.vbox.pack_start(notebook, True, True, 0)
        dialog.show()

    #+---------------------------------------------- 
    #| Called when user wants to see the distribution of a symbol of messages
    #+----------------------------------------------
    def messagesDistribution_cb(self, but):
        if self.selectedSymbol == None:
            self.log.info("No symbol selected")
            return
        entropy = Entropy(self.selectedSymbol)
        entropy.buildDistributionView()

    #+---------------------------------------------- 
    #| Called when user wants to slick the current regexes
    #+----------------------------------------------
    def slickRegex_cb(self, but):
        if self.netzob.getCurrentProject() == None :
            return

        for symbol in self.netzob.getCurrentProject().getVocabulary().getSymbols():
            symbol.slickRegex(self.netzob.getCurrentProject())

    #+---------------------------------------------- 
    #| Called when user wants to find ASN.1 fields
    #+----------------------------------------------
    def findASN1Fields_cb(self, button):
        if self.netzob.getCurrentProject() == None :
            return

        dialog = gtk.Dialog(title="Find ASN.1 fields", flags=0, buttons=None)
        notebook = gtk.Notebook()
        notebook.show()
        notebook.set_tab_pos(gtk.POS_TOP)
        for symbol in self.netzob.getCurrentProject().getVocabulary().getSymbols():
            scroll = symbol.findASN1Fields(self.netzob.getCurrentProject())
            if scroll != None:
                notebook.append_page(scroll, gtk.Label(symbol.getName())) 
            
        dialog.vbox.pack_start(notebook, True, True, 0)
        dialog.show()

    #+---------------------------------------------- 
    #| Called when user wants to find the potential size fields
    #+----------------------------------------------
    def findSizeFields(self, button):
        if self.netzob.getCurrentProject() == None :
            return  

        # Create a temporary symbol for testing size fields
        tmp_symbol = Symbol("tmp_symbol", "tmp_symbol")

        dialog = gtk.Dialog(title="Potential size fields and related payload", flags=0, buttons=None)
        ## ListStore format :
        # str: symbol.id
        # int: size field column
        # int: size field size
        # int: start column
        # int: substart column
        # int: end column
        # int: subend column
        # str: message rendered in cell
        treeview = gtk.TreeView(gtk.ListStore(str, int, int, int, int, int, int, str)) 
        cell = gtk.CellRendererText()
        treeview.connect("cursor-changed", self.sizeField_selected, tmp_symbol)
        column = gtk.TreeViewColumn('Size field and related payload')
        column.pack_start(cell, True)
        column.set_attributes(cell, text=7)
        treeview.append_column(column)

        # Chose button
        but = gtk.Button(label="Apply size field")
        but.show()
        but.connect("clicked", self.applySizeField, dialog, tmp_symbol)
        dialog.action_area.pack_start(but, True, True, 0)

        # Text view containing potential size fields
        treeview.set_size_request(800, 300)
        
        self.netzob.getCurrentProject().getVocabulary().findSizeFields(treeview.get_model())
        
        treeview.show()
        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scroll.show()
        scroll.add(treeview)
        dialog.vbox.pack_start(scroll, True, True, 0)
        dialog.show()

    #+---------------------------------------------- 
    #| Called when user wants to try to apply a size field on a symbol
    #+----------------------------------------------
    def sizeField_selected(self, treeview, symbol):
        (model, iter) = treeview.get_selection().get_selected()
        if(iter):
            if(model.iter_is_valid(iter)):
                symbol_id = model.get_value(iter, 0)
                size_field = model.get_value(iter, 1)
                size_field_len = model.get_value(iter, 2)
                start_field = model.get_value(iter, 3)
                start_field_len = model.get_value(iter, 4)
                end_field = model.get_value(iter, 5)
                end_field_len = model.get_value(iter, 6)
                
                ## Select the related symbol
                self.selectedSymbol = symbol
                self.update()

                ## Select the first message for details (after the 3 header rows)
                it = self.treeMessageGenerator.treestore.get_iter_first()
                if it == None:
                    return
                it = self.treeMessageGenerator.treestore.iter_next(it)
                if it == None:
                    return
                it = self.treeMessageGenerator.treestore.iter_next(it)
                if it == None:
                    return
                it = self.treeMessageGenerator.treestore.iter_next(it)
                if it == None:
                    return

                # Build a temporary symbol
                symbol.clear()
                for message in self.treeMessageGenerator.getSymbol().getMessages():
                    tmp_message = RawMessage("tmp", 329832, message.getData())
                    symbol.addMessage(tmp_message)
                symbol.setAlignment(copy.deepcopy(self.treeMessageGenerator.getSymbol().getAlignment()))
                symbol.setFields(copy.deepcopy(list(self.treeMessageGenerator.getSymbol().getFields())))

                self.treeTypeStructureGenerator.setSymbol(symbol)
                self.treeTypeStructureGenerator.setMessageByID(symbol.getMessages()[-1].getID())

                # Optionaly splits the columns if needed, and handles columns propagation
#                if symbol.splitColumn(size_field, size_field_len) == True:
#                    if size_field < start_field:
#                        start_field += 1
#                    if end_field != -1:
#                        end_field += 1
#                symbol.setDescriptionByCol(size_field, "Size field")
#                symbol.setColorByCol(size_field, "red")
#                if symbol.splitColumn(start_field, start_field_len) == True:
#                    start_field += 1
#                    if end_field != -1:
#                        end_field += 1
#                symbol.setDescriptionByCol(start_field, "Start of payload")
#                symbol.splitColumn(end_field, end_field_len)
#
#                # Adapt tabulation for encapsulated payloads
#                if end_field != -1:
#                    for iCol in range(start_field, end_field + 1):
#                        symbol.setTabulationByCol(iCol, symbol.getTabulationByCol(iCol) + 10)
#                else:
#                    symbol.setTabulationByCol(start_field, symbol.getTabulationByCol(start_field) + 10)

                # View the proposed protocol structuration
                self.update()

    #+---------------------------------------------- 
    #| Called when user wants to apply a size field on a symbol
    #+----------------------------------------------
    def applySizeField(self, button, dialog, symbol):
#        self.treeMessageGenerator.getSymbol().setColumns(copy.deepcopy(list(symbol.getColumns())))
        dialog.destroy()
