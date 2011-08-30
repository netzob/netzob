#!/usr/bin/python
# -*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|         01001110 01100101 01110100 01111010 01101111 01100010             | 
#+---------------------------------------------------------------------------+
#| NETwork protocol modeliZatiOn By reverse engineering                      |
#| ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~+
#| @license      : GNU GPL v3                                                |
#| @copyright    : Georges Bossert and Frederic Guihery                      |
#| @url          : http://code.google.com/p/netzob/                          |
#| ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~+
#| @author       : {gbt,fgy}@amossys.fr                                      |
#| @organization : Amossys, http://www.amossys.fr                            |
#+---------------------------------------------------------------------------+

#+---------------------------------------------- 
#| Global Imports
#+----------------------------------------------
import gtk
import pango
import gobject
import re
import pygtk
pygtk.require('2.0')
import logging
import threading
import copy
import os
import time
import random

#+---------------------------------------------- 
#| Local Imports
#+----------------------------------------------
import Group
import Message
import TracesExtractor
import ConfigParser
import Entropy
from ..Common import ConfigurationParser
from TreeViews import TreeGroupGenerator
from TreeViews import TreeMessageGenerator
from TreeViews import TreeTypeStructureGenerator

#+---------------------------------------------- 
#| Configuration of the logger
#+----------------------------------------------
loggingFilePath = ConfigurationParser.ConfigurationParser().get("logging", "path")
logging.config.fileConfig(loggingFilePath)

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
        self.updateTreeStoreGroup()
        self.updateTreeStoreMessage()
        self.updateTreeStoreTypeStructure()

    def clear(self):
        pass

    def kill(self):
        pass
    
    def save(self, file):
        self.log = logging.getLogger('netzob.Modelization.UImodelization.py')
        self.log.info("Saving the modelization")
        
        configParser = ConfigParser.ConfigParser(file)
        configParser.saveInConfiguration(self.treeGroupGenerator.getGroups())
        
    
    #+---------------------------------------------- 
    #| Constructor :
    #| @param groups: list of all groups 
    #+----------------------------------------------   
    def __init__(self, zob):
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Modelization.UImodelization.py')
        self.zob = zob
        self.selectedGroup = ""
        self.selectedMessage = ""
        self.treeMessageGenerator = TreeMessageGenerator.TreeMessageGenerator()
        self.treeMessageGenerator.initialization()
        self.treeTypeStructureGenerator = TreeTypeStructureGenerator.TreeTypeStructureGenerator()
        self.treeTypeStructureGenerator.initialization()
        self.treeGroupGenerator = TreeGroupGenerator.TreeGroupGenerator([])
        self.treeGroupGenerator.initialization()
        
        # Definition of the Sequence Onglet
        # First we create an VBox which hosts the two main children
        self.panel = gtk.VBox(False, spacing=0)
        self.panel.show()
        self.defer_select = False

        configParser = ConfigurationParser.ConfigurationParser()
        
        #+---------------------------------------------- 
        #| TOP PART OF THE GUI : BUTTONS
        #+----------------------------------------------
        topPanel = gtk.HBox(False, spacing=5)
        topPanel.show()
        self.panel.pack_start(topPanel, False, False, 0)

        ## Widget for launching the analysis
        but = gtk.Button(gtk.STOCK_OK)
        but.set_label("Start alignment")
        but.connect("clicked", self.startAnalysis_cb)
        but.show()
        topPanel.pack_start(but, False, False, 0)

        ## Options during alignment process
        frame = gtk.Frame()
        frame.set_label("Options during alignment process")
        frame.show()
        topPanel.pack_start(frame, True, True, 0)

        # Sub-panel for specific buttions
        table = gtk.Table(rows=4, columns=4, homogeneous=False)
        table.show()
        frame.add(table)

        # Widget entry for chosing the alignment score sub-limit
        label = gtk.Label("Similarity threshold : ")
        label.show()
        combo = gtk.combo_box_entry_new_text()
        combo.set_size_request(60, -1)
        combo.set_model(gtk.ListStore(str))
        combo.connect("changed", self.updateScoreLimit)
        possible_choices = [100, 95, 90, 85, 80, 75, 70, 65, 60, 55, 50, 45, 40, 35, 30, 25, 20, 15, 10, 5]
        min_equivalence = configParser.getFloat("clustering", "equivalence_threshold")
        for i in range(len(possible_choices)):
            combo.append_text(str(possible_choices[i]))
            if str(possible_choices[i]) == str(int(min_equivalence)):
                combo.set_active(i)
        combo.show()
        table.attach(label, 0, 1, 0, 1, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        table.attach(combo, 1, 2, 0, 1, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        # Widget button activate orphan reduction
        butOrphanReduction = gtk.CheckButton("Orphan reduction")
        doOrphanReduction = configParser.getInt("clustering", "orphan_reduction")
        if doOrphanReduction == 1:
            butOrphanReduction.set_active(True)
        else:
            butOrphanReduction.set_active(False)
        butOrphanReduction.connect("toggled", self.activeOrphanReduction)
        butOrphanReduction.show()
        table.attach(butOrphanReduction, 2, 3, 0, 1, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        # Widget checkbox for selecting the slickery during alignement process
        but = gtk.CheckButton("Slick regexes")
        doInternalSlick = configParser.getInt("clustering", "do_internal_slick")
        if doInternalSlick == 1:
            but.set_active(True)
        else:
            but.set_active(False)
        but.connect("toggled", self.activeInternalSlickRegexes)
        but.show()
        table.attach(but, 2, 3, 1, 2, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        
        ## Options after alignment process
        frame = gtk.Frame()
        frame.set_label("Analyses after alignment process")
        frame.show()
        topPanel.pack_start(frame, True, True, 0)

        # Sub-panel for specific buttions
        table = gtk.Table(rows=4, columns=4, homogeneous=False)
        table.show()
        frame.add(table)

        # Widget button slick regexes
        but = gtk.Button("Slick regexes")
        but.connect("clicked", self.treeGroupGenerator.slickRegexes, self)
        but.show()
        table.attach(but, 0, 1, 0, 1, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        # Widget button find size fields
        but = gtk.Button("Find size fields")
        # TODO: just try to use an ASN.1 parser to find the simple TLV protocols
        but.connect("clicked", self.findSizeFields)
        but.show()
        table.attach(but, 1, 2, 0, 1, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        # Widget button merge common regexes
        but = gtk.Button("Merge common regexes")
        but.connect("clicked", self.treeGroupGenerator.mergeCommonRegexes, self)
        ## TODO: merge common regexes (if it is really usefull)
        but.show()
        but.set_sensitive(False)
        table.attach(but, 2, 3, 0, 1, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        # Widget button refine regex
        but = gtk.Button("Refine regexes")
        but.connect("clicked", self.refineRegexes_cb)
        but.show()
        table.attach(but, 0, 1, 1, 2, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        # Widget button data carving
        but = gtk.Button("Data carving")
        but.connect("clicked", self.dataCarving_cb)
        but.show()
        table.attach(but, 1, 2, 1, 2, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        # Widget button to show fields entropy
        but = gtk.Button("Messages entropy")
        but.connect("clicked", self.messagesEntropy_cb)
        but.show()
        table.attach(but, 2, 3, 1, 2, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        ## Visualization options
        frame = gtk.Frame()
        frame.set_label("Visualization options")
        frame.show()
        topPanel.pack_start(frame, False, False, 0)

        # Sub-panel for specific buttions
        table = gtk.Table(rows=4, columns=4, homogeneous=False)
        table.show()
        frame.add(table)

        # Widget for choosing the analysed protocole type
        label = gtk.Label("Protocol type : ")
        label.show()
        combo = gtk.combo_box_entry_new_text()
        combo.set_size_request(300, -1)
        combo.set_model(gtk.ListStore(str))
        combo.append_text("Text based (HTTP, FTP)")
        combo.append_text("Fixed fields binary based (IP, TCP)")
        combo.append_text("Variable fields binary based (ASN.1)")
        combo.connect("changed", self.updateProtocolType)
        protocol_type_ID = configParser.getInt("clustering", "protocol_type")
        combo.set_active(protocol_type_ID)
        combo.show()
        table.attach(label, 0, 1, 0, 1, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        table.attach(combo, 1, 2, 0, 1, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        #+---------------------------------------------- 
        #| LEFT PART OF THE GUI : GROUP TREEVIEW
        #+----------------------------------------------           
        bottomPanel = gtk.HPaned()
        bottomPanel.show()
        self.panel.pack_start(bottomPanel, True, True, 0)
        leftPanel = gtk.VBox(False, spacing=0)
        leftPanel.set_size_request(-1, -1)
        leftPanel.show()
        bottomPanel.add(leftPanel)
        # Initialize the treeview generator for the groups
        leftPanel.pack_start(self.treeGroupGenerator.getScrollLib(), True, True, 0)
        # Attach to the treeview few actions (DnD, cursor and buttons handlers...)
        self.treeGroupGenerator.getTreeview().enable_model_drag_dest(self.TARGETS, gtk.gdk.ACTION_DEFAULT | gtk.gdk.ACTION_MOVE)
        self.treeGroupGenerator.getTreeview().connect("drag_data_received", self.drop_fromDND)
        self.treeGroupGenerator.getTreeview().connect("cursor-changed", self.groupChanged)
        self.treeGroupGenerator.getTreeview().connect('button-press-event', self.button_press_on_treeview_groups)

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
    #| startAnalysis :
    #|   Parse the traces and store the results
    #+----------------------------------------------
    def startAnalysis_cb(self, widget):
        if self.zob.tracePath == "":
            self.log.info("No trace selected")
            return
        self.selectedGroup = ""
        self.treeMessageGenerator.clear()
        self.treeGroupGenerator.clear()
        self.treeTypeStructureGenerator.clear()
        self.update()
        self.parseThread = threading.Thread(None, self.treeGroupGenerator.initTreeGroupWithTraces, None, (self.zob, self), {})
        self.parseThread.start()
    
    #+---------------------------------------------- 
    #| button_press_on_treeview_groups :
    #|   operation when the user click on the treeview.
    #|   mainly to open a contextual menu
    #+----------------------------------------------
    def button_press_on_treeview_groups(self, obj, event):
        self.log.debug("User requested a contextual menu (treeview group)")
        if event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
            self.build_context_menu_for_groups(event)

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
                    group = self.treeMessageGenerator.getGroup()
                    self.treeTypeStructureGenerator.setGroup(group)
                    self.treeTypeStructureGenerator.setMessageByID(message_id)
                    self.updateTreeStoreTypeStructure()

        # Popup a menu
        elif event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
            self.log.debug("User requested a contextual menu (treeview messages)")
            x = int(event.x)
            y = int(event.y)
            (path, treeviewColumn, x, y) = treeview.get_path_at_pos(x, y)

            # Retrieve the selected column number
            iCol = 0
            for col in treeview.get_columns():
                if col == treeviewColumn:
                    break
                iCol += 1

            menu = gtk.Menu()
            # Add sub-entries to change the type of a specific column
            typesList = self.treeMessageGenerator.getGroup().getPossibleTypesByCol(iCol)
            typeMenu = gtk.Menu()
            for aType in typesList:
                item = gtk.MenuItem("Render in : " + str(aType))
                item.show()
                item.connect("activate", self.rightClickToChangeType, iCol, aType)   
                typeMenu.append(item)
            item = gtk.MenuItem("Change Type")
            item.set_submenu(typeMenu)
            item.show()
            menu.append(item)

            # Add entries to concatenate column
            concatMenu = gtk.Menu()
            item = gtk.MenuItem("with precedent field")
            item.show()
            item.connect("activate", self.rightClickToConcatColumns, iCol, "left")
            concatMenu.append(item)
            item = gtk.MenuItem("with next field")
            item.show()
            item.connect("activate", self.rightClickToConcatColumns, iCol, "right")
            concatMenu.append(item)
            item = gtk.MenuItem("Concatenate")
            item.set_submenu(concatMenu)
            item.show()
            menu.append(item)

            # Add entry to split the column
            item = gtk.MenuItem("Split column")
            item.show()
            item.connect("activate", self.rightClickToSplitColumn, iCol)
            menu.append(item)

            # Add entry to retrieve the field domain of definition
            item = gtk.MenuItem("Domain of definition")
            item.show()
            item.connect("activate", self.rightClickDomainOfDefinition, iCol)
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
            (iCol,) = path
            menu = gtk.Menu()
            # Add sub-entries to change the type of a specific field
            typesList = self.treeMessageGenerator.getGroup().getPossibleTypesByCol(iCol)
            typeMenu = gtk.Menu()
            for aType in typesList:
                item = gtk.MenuItem("Render in : " + str(aType))
                item.show()
                item.connect("activate", self.rightClickToChangeType, iCol, aType)   
                typeMenu.append(item)
            item = gtk.MenuItem("Change Type")
            item.set_submenu(typeMenu)
            item.show()
            menu.append(item)

            # Add entries to concatenate fields
            concatMenu = gtk.Menu()
            item = gtk.MenuItem("with precedent field")
            item.show()
            item.connect("activate", self.rightClickToConcatColumns, iCol, "left")
            concatMenu.append(item)
            item = gtk.MenuItem("with next field")
            item.show()
            item.connect("activate", self.rightClickToConcatColumns, iCol, "right")
            concatMenu.append(item)
            item = gtk.MenuItem("Concatenate")
            item.set_submenu(concatMenu)
            item.show()
            menu.append(item)

            # Add entry to split the field
            item = gtk.MenuItem("Split column")
            item.show()
            item.connect("activate", self.rightClickToSplitColumn, iCol)
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
                iCol = model.get_value(aIter, 0)
                cells = self.treeTypeStructureGenerator.getGroup().getCellsByCol(iCol)
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
        tracesDirectoryPath = ConfigurationParser.ConfigurationParser().get("traces", "path")
        for tmpDir in os.listdir(tracesDirectoryPath):
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
        tracesDirectoryPath = ConfigurationParser.ConfigurationParser().get("traces", "path")
        existingTraceDir = tracesDirectoryPath + "/" + entry.get_active_text()
        # Create the new XML structure
        res = "<datas>\n"
        for message in messages:
            res += "<data proto=\"ipc\" sourceIp=\"local\" sourcePort=\"local\" targetIp=\"local\" targetPort=\"local\" timestamp=\"" + str(time.time()) + "\">\n"
            res += message + "\n"
            res += "</data>\n"
        res += "</datas>\n"
        # Dump into a random XML file
        fd = open(existingTraceDir + "/" + str(random.randint(100000, 9000000)) + ".xml"  , "w")
        fd.write(res)
        fd.close()
        dialog.destroy()

    #+---------------------------------------------- 
    #| Creation of a new trace from a selection of packets
    #+----------------------------------------------
    def create_new_trace(self, button, entry, messages, dialog):
        tracesDirectoryPath = ConfigurationParser.ConfigurationParser().get("traces", "path")
        for tmpDir in os.listdir(tracesDirectoryPath):
            if tmpDir == '.svn':
                continue
            if entry.get_text() == tmpDir:
                dialogBis = gtk.Dialog(title="This trace already exists", flags=0, buttons=None)
                dialogBis.set_size_request(250, 50)
                dialogBis.show()
                return

        # Create the dest Dir
        newTraceDir = tracesDirectoryPath + "/" + entry.get_text()
        os.mkdir(newTraceDir)
        # Create the new XML structure
        res = "<datas>\n"
        for message in messages.values():
            res += "<data proto=\"ipc\" sourceIp=\"local\" sourcePort=\"local\" targetIp=\"local\" targetPort=\"local\" timestamp=\"" + str(time.time()) + "\">\n"
            res += message + "\n"
            res += "</data>\n"
        res += "</datas>\n"
        # Dump into a random XML file
        fd = open(newTraceDir + "/" + str(random.randint(100000, 9000000)) + ".xml"  , "w")
        fd.write(res)
        fd.close()
        dialog.destroy()
        self.zob.updateListOfAvailableTraces()

    #+---------------------------------------------- 
    #| rightClickDomainOfDefinition :
    #|   Retrieve the domain of definition of the selected column
    #+----------------------------------------------
    def rightClickDomainOfDefinition(self, event, iCol):
        cells = self.treeMessageGenerator.getGroup().getCellsByCol(iCol)
        tmpDomain = set()
        for cell in cells:
            tmpDomain.add( self.treeMessageGenerator.getGroup().getRepresentation(cell, iCol) )
        domain = sorted(tmpDomain)

        dialog = gtk.Dialog(title="Domain of definition for the column " + str(iCol), flags=0, buttons=None)
        # Text view containing domain of definition ## ListStore format :
        # str: group.id
        treeview = gtk.TreeView(gtk.ListStore(str)) 
        treeview.set_size_request(800, 300)
        treeview.show()
        treeview.get_selection().set_mode(gtk.SELECTION_NONE)
        cell = gtk.CellRendererText()
        column = gtk.TreeViewColumn("Column " + str(iCol))
        column.pack_start(cell, True)
        column.set_attributes(cell, text=0)
        treeview.append_column(column)

        # Just to force the calculation of each group with its associated messages
        for group in self.treeGroupGenerator.getGroups():
            self.selectedGroup = str(group.getID())
            self.treeMessageGenerator.default(group)

        for elt in domain:
            treeview.get_model().append( [elt] )

        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scroll.show()
        scroll.add(treeview)
        dialog.vbox.pack_start(scroll, True, True, 0)
        dialog.show()

    #+---------------------------------------------- 
    #| rightClickToChangeType :
    #|   Callback to change the column type
    #|   by doing a right click
    #+----------------------------------------------
    def rightClickToChangeType(self, event, iCol, aType):
        self.treeMessageGenerator.getGroup().setTypeForCol(iCol, aType)
        self.update()

    #+---------------------------------------------- 
    #|  rightClickToConcatColumns:
    #|   Callback to concatenate two columns
    #+----------------------------------------------
    def rightClickToConcatColumns(self, event, iCol, strOtherCol):
        self.log.debug("Concatenate the column " + str(iCol) + " with the " + str(strOtherCol) + " column")

        if iCol == 0 and strOtherCol == "left":
            self.log.debug("Can't concatenate the first column with its left column")
            return

        if iCol + 1 == len(self.treeMessageGenerator.getGroup().getColumns()) and strOtherCol == "right":
            self.log.debug("Can't concatenate the last column with its right column")
            return

        if strOtherCol == "left":
            self.treeMessageGenerator.getGroup().concatColumns(iCol - 1)
        else:
            self.treeMessageGenerator.getGroup().concatColumns(iCol)
        self.treeMessageGenerator.updateDefault()
        self.update()

    #+---------------------------------------------- 
    #|  rightClickToSplitColumn:
    #|   Callback to split a column
    #+----------------------------------------------
    def rightClickToSplitColumn(self, event, iCol):
        dialog = gtk.Dialog(title="Split column " + str(iCol), flags=0, buttons=None)
        textview = gtk.TextView()
        textview.set_editable(False)
        textview.get_buffer().create_tag("redTag", weight=pango.WEIGHT_BOLD, foreground="red", family="Courier")
        textview.get_buffer().create_tag("greenTag", weight=pango.WEIGHT_BOLD, foreground="#006400", family="Courier")
        self.split_position = 2
        self.split_max_len = 0

        # Find the size of the longest message
        cells = self.treeMessageGenerator.getGroup().getCellsByCol(iCol)
        for m in cells:
            if len(m) > self.split_max_len:
                self.split_max_len = len(m)

        # Left arrow
        arrow = gtk.Arrow(gtk.ARROW_LEFT, gtk.SHADOW_OUT)
        arrow.show()
        but = gtk.Button()
        but.add(arrow)
        but.connect("clicked", self.adjustSplitColumn, textview, "left", iCol)
        but.show()
        dialog.action_area.pack_start(but, True, True, 0)

        # Right arrow
        arrow = gtk.Arrow(gtk.ARROW_RIGHT, gtk.SHADOW_OUT)
        arrow.show()
        but = gtk.Button()
        but.add(arrow)
        but.connect("clicked", self.adjustSplitColumn, textview, "right", iCol)
        but.show()
        dialog.action_area.pack_start(but, True, True, 0)

        # Split button
        but = gtk.Button(label="Split column")
        but.show()
        but.connect("clicked", self.doSplitColumn, textview, iCol, dialog)
        dialog.action_area.pack_start(but, True, True, 0)

        # Text view containing selected column messages
        frame = gtk.Frame()
        frame.set_label("Content of the column to split")
        frame.show()
        textview.set_size_request(400, 300)
        cells = self.treeMessageGenerator.getGroup().getCellsByCol(iCol)

        for m in cells:
            textview.get_buffer().insert_with_tags_by_name(textview.get_buffer().get_end_iter(), self.treeMessageGenerator.getGroup().getRepresentation(m[:self.split_position], iCol) + "  ", "redTag")
            textview.get_buffer().insert_with_tags_by_name(textview.get_buffer().get_end_iter(), self.treeMessageGenerator.getGroup().getRepresentation(m[self.split_position:], iCol) + "\n", "greenTag")
        textview.show()
        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scroll.show()
        scroll.add(textview)
        frame.add(scroll)
        dialog.vbox.pack_start(frame, True, True, 0)
        dialog.show()

    def doSplitColumn(self, widget, textview, iCol, dialog):
        if self.split_max_len <= 2:
            dialog.destroy()
            return

        self.treeMessageGenerator.getGroup().splitColumn(iCol, self.split_position)
        self.treeMessageGenerator.updateDefault()            
        dialog.destroy()
        self.update()

    def adjustSplitColumn(self, widget, textview, direction, iCol):
        if self.split_max_len <= 2:
            return
        messages = self.treeMessageGenerator.getGroup().getCellsByCol(iCol)

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
            textview.get_buffer().insert_with_tags_by_name(textview.get_buffer().get_end_iter(), self.treeMessageGenerator.getGroup().getRepresentation(m[:self.split_position], iCol) + "  ", "redTag")
            textview.get_buffer().insert_with_tags_by_name(textview.get_buffer().get_end_iter(), self.treeMessageGenerator.getGroup().getRepresentation(m[self.split_position:], iCol) + "\n", "greenTag")

    #+---------------------------------------------- 
    #| dbClickToChangeType :
    #|   Called when user double click on a row
    #|    in order to change the column type
    #+----------------------------------------------
    def dbClickToChangeType(self, treeview, path, paramCol):
        # Retrieve the selected column number
        iCol = 0
        for col in treeview.get_columns():
            if col == paramCol:
                break
            iCol += 1

        # Find the next possible type for this column
        possibleTypes = self.treeMessageGenerator.getGroup().getPossibleTypesByCol(iCol)
        i = 0
        chosedType = self.treeMessageGenerator.getGroup().getSelectedTypeByCol(iCol)
        for aType in possibleTypes:
            if aType == chosedType:
                chosedType = possibleTypes[(i + 1) % len(possibleTypes)]
                break
            i += 1

        # Apply the new chosed type for this column
        self.treeMessageGenerator.getGroup().setTypeForCol(iCol, chosedType)
        self.treeMessageGenerator.updateDefault()
        self.update()
        
    #+---------------------------------------------- 
    #| build_context_menu_for_groups :
    #|   Create a menu to display available operations
    #|   on the treeview groups
    #+----------------------------------------------
    def build_context_menu_for_groups(self, event):
        # Retrieves the group on which the user has clicked on
        x = int(event.x)
        y = int(event.y)
        
        selectedGroup = self.treeGroupGenerator.getGroupAtPosition(x, y)        
        entries = [        
                  (gtk.STOCK_EDIT, self.displayPopupToEditGroup, (selectedGroup != None)),
                  (gtk.STOCK_ADD, self.displayPopupToCreateGroup, (selectedGroup == None)),
                  (gtk.STOCK_REMOVE, self.displayPopupToRemoveGroup, (selectedGroup != None))
        ]

        menu = gtk.Menu()
        for stock_id, callback, sensitive in entries:
            item = gtk.ImageMenuItem(stock_id)
            item.connect("activate", callback, selectedGroup)  
            item.set_sensitive(sensitive)
            item.show()
            menu.append(item)
        menu.popup(None, None, None, event.button, event.time)


    #+---------------------------------------------- 
    #| displayPopupToCreateGroup_ResponseToDialog :
    #|   pygtk is so good ! arf :( <-- clap clap :D
    #+----------------------------------------------
    def displayPopupToCreateGroup_ResponseToDialog(self, entry, dialog, response):
        dialog.response(response)

    def displayPopupToEditGroup(self, event, group):
        self.log.debug("Display a edit to rename a group")
        dialog = gtk.MessageDialog(
        None,
        gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
        gtk.MESSAGE_QUESTION,
        gtk.BUTTONS_OK,
        None)
        dialog.set_markup('Please enter the <b>name</b> of the group:')
        #create the text input field
        entry = gtk.Entry()
        entry.set_text(group.getName())
        #allow the user to press enter to do ok
        entry.connect("activate", self.responseToDialog, dialog, gtk.RESPONSE_OK)
        #create a horizontal box to pack the entry and a label
        hbox = gtk.HBox()
        hbox.pack_start(gtk.Label("Name:"), False, 5, 5)
        hbox.pack_end(entry)
        #some secondary text
#        dialog.format_secondary_markup("Th <i>identification</i> purposes")
        #add it and show it
        dialog.vbox.pack_end(hbox, True, True, 0)
        dialog.show_all()
        #go go go
        dialog.run()
        text = entry.get_text()
        group.setName(text)
        dialog.destroy()
        #Update Left and Right
        self.update()

    def responseToDialog(self, entry, dialog, response):
        dialog.response(response)
    
    
    #+---------------------------------------------- 
    #| displayPopupToCreateGroup :
    #|   Display a form to create a new group.
    #|   Based on the famous dialogs
    #+----------------------------------------------
    def displayPopupToCreateGroup(self, event, group):
        self.log.debug("Display a popup to create a group")
        #base this on a message dialog
        dialog = gtk.MessageDialog(
                                   None,
                                   gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                   gtk.MESSAGE_QUESTION,
                                   gtk.BUTTONS_OK,
                                   None)
        dialog.set_markup('Please enter the <b>new group name</b>:')
        #create the text input field
        entry = gtk.Entry()
        #allow the user to press enter to do ok
        entry.connect("activate", self.displayPopupToCreateGroup_ResponseToDialog, dialog, gtk.RESPONSE_OK)
        #create a horizontal box to pack the entry and a label
        hbox = gtk.HBox()
        hbox.pack_start(gtk.Label("Group Name :"), False, 5, 5)
        hbox.pack_end(entry)
        #some secondary text
        dialog.format_secondary_markup("<b>Warning Grand'Ma</b> : Be sure not to create two groups with the same name.")
        #add it and show it
        dialog.vbox.pack_end(hbox, True, True, 0)
        dialog.show_all()
        #go go go
        dialog.run()
        newGroupName = entry.get_text()
        dialog.destroy()
        
        if (len(newGroupName) > 0) :
            self.log.debug("a new group will be created with the given name : {0}".format(newGroupName))
            
            newGroup = Group.Group(newGroupName, [])
            self.treeGroupGenerator.addGroup(newGroup)
            #Update Left and Right
            self.update()
        
    #+---------------------------------------------- 
    #| displayPopupToRemoveGroup :
    #|   Display a popup to remove a group
    #|   the removal of a group can only occurs
    #|   if its an empty group
    #+----------------------------------------------    
    def displayPopupToRemoveGroup(self, event, group):
        self.log.debug("Display a popup to create a group")
        
        if (len(group.getMessages()) == 0) :
            self.log.debug("Can remove the group {0} since it's an empty one.".format(group.getName()))
            questionMsg = "Click yes to confirm the removal of the group {0}".format(group.getName())
            md = gtk.MessageDialog(None, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_QUESTION, gtk.BUTTONS_YES_NO, questionMsg)
            result = md.run()
            md.destroy()
            if result == gtk.RESPONSE_YES:
                self.treeGroupGenerator.removeGroup(group)
                self.log.debug("The group " + group.getName() + " has been deleted !")
                #Update Left and Right
                self.update()
            else :
                self.log.debug("The user didn't confirm the deletion of the group " + group.getName())                
            
        else :
            self.log.debug("Can't remove the group {0} since its not an empty one.".format(group.getName()))
            errorMsg = "The selected group cannot be removed since it has messages."
            md = gtk.MessageDialog(None, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_ERROR, gtk.BUTTONS_CLOSE, errorMsg)
            md.run()
            md.destroy()
        
    #+---------------------------------------------- 
    #| drop_fromDND :
    #|   defines the operation executed when a message is
    #|   is dropped out current group to the selected group 
    #+----------------------------------------------
    def drop_fromDND(self, treeview, context, x, y, selection, info, etime):
        ids = selection.data
        for msg_id in ids.split(";") :
            
            modele = treeview.get_model()
            info_depot = treeview.get_dest_row_at_pos(x, y)
            
            # First we search for the message to move
            message = None
            message_grp = None
            for group in self.treeGroupGenerator.getGroups() :
                for msg in group.getMessages() :
                    if str(msg.getID()) == msg_id :
                        message = msg
                        message_grp = group
            
            # Break if the message to move was not found
            if message == None :
                self.log.warning("Impossible to retrieve the message to move based on its ID [{0}]".format(msg_id))
                return
            
            self.log.debug("The message having the ID [{0}] has been found !".format(msg_id))
            
            # Now we search for the new group of the message
            if info_depot :
                chemin, position = info_depot
                iter = modele.get_iter(chemin)
                new_grp_id = str(modele.get_value(iter, 0))
                                
                new_message_grp = None
                for tmp_group in self.treeGroupGenerator.getGroups() :
                    if (str(tmp_group.getID()) == new_grp_id) :
                        new_message_grp = tmp_group
                    
            if new_message_grp == None :
                self.log.warning("Impossible to retrieve the group in which the selected message must be moved out.")
                return
            
            self.log.debug("The new group of the message is {0}".format(str(new_message_grp.getID())))
            #Removing from its old group
            message_grp.removeMessage(message)
            
            #Adding to its new group
            new_message_grp.addMessage(message)            
        
        message_grp.buildRegexAndAlignment()
        new_message_grp.buildRegexAndAlignment()
        #Update Left and Right
        self.update()
        return
   
    #+---------------------------------------------- 
    #| drag_fromDND :
    #|   defines the operation executed when a message is
    #|   is dragged out current group 
    #+----------------------------------------------
    def drag_fromDND(self, treeview, contexte, selection, info, dateur):   
        ids = []             
        treeview.get_selection().selected_foreach(self.foreach_drag_fromDND, ids)
        selection.set(selection.target, 8, ";".join(ids))
    
    def foreach_drag_fromDND(self, model, path, iter,  ids):
        texte = str(model.get_value(iter, 0))
        ids.append(texte)
        return
    
    #+---------------------------------------------- 
    #| Update the content of the tree store for groups
    #+----------------------------------------------
    def updateTreeStoreGroup(self):        
        # Updates the treestore with a selected message
        if (self.selectedMessage != "") :
            self.treeGroupGenerator.messageSelected(self.selectedMessage)
            self.selectedMessage = ""
        else :
            # Default display of the groups
            self.treeGroupGenerator.default()
            # TODO: remove the two following lines, as the groups are handled elsewhere
#            self.zob.dumping.updateGoups(self.treeGroupGenerator.getGroups())
#            self.zob.fuzzing.updateGoups(self.treeGroupGenerator.getGroups())
 
    #+---------------------------------------------- 
    #| Update the content of the tree store for messages
    #+----------------------------------------------
    def updateTreeStoreMessage(self):        
        if (self.selectedGroup != "") :
            # Search for the selected group in groups list
            selectedGroup = None
            for group in self.treeGroupGenerator.getGroups() :
                if str(group.getID()) == self.selectedGroup :
                    selectedGroup = group
            # If we found it we can update the content of the treestore        
            if selectedGroup != None :
                self.treeMessageGenerator.default(selectedGroup)
                # enable dragging message out of current group
                self.treeMessageGenerator.getTreeview().enable_model_drag_source(gtk.gdk.BUTTON1_MASK, self.TARGETS, gtk.gdk.ACTION_DEFAULT | gtk.gdk.ACTION_MOVE)
                self.treeMessageGenerator.getTreeview().connect("drag-data-get", self.drag_fromDND)      
            # Else, quite weird so throw a warning
            else :
                self.log.warning("Impossible to update the treestore message since we cannot find the selected group according to its name " + str(self.selectedGroup))

    #+---------------------------------------------- 
    #| Update the content of the tree store for type structure
    #+----------------------------------------------
    def updateTreeStoreTypeStructure(self):
        self.treeTypeStructureGenerator.update()
       
    #+---------------------------------------------- 
    #| Called when user click on a group or on a message
    #+----------------------------------------------
    def groupChanged(self, treeview):
        (model, iter) = treeview.get_selection().get_selected()
        if(iter):
            if(model.iter_is_valid(iter)):
                idGroup = model.get_value(iter, 0)
                score = model.get_value(iter, 1)
                self.selectedGroup = idGroup
                self.treeTypeStructureGenerator.clear()
                self.update()

    #+---------------------------------------------- 
    #| Called when user select a new score limit
    #+----------------------------------------------
    def updateScoreLimit(self, combo):
        val = combo.get_active_text()
        configParser = ConfigurationParser.ConfigurationParser()
        configParser.set("clustering", "equivalence_threshold", val)

    #+---------------------------------------------- 
    #| Called when user wants to slick internally in libNeedleman
    #+----------------------------------------------
    def activeInternalSlickRegexes(self, checkButton):
        configParser = ConfigurationParser.ConfigurationParser()
        configParser.set("clustering", "do_internal_slick", (0, 1)[checkButton.get_active()])
        
    #+---------------------------------------------- 
    #| Called when user wants to activate orphan reduction
    #+----------------------------------------------
    def activeOrphanReduction(self, checkButton):
        configParser = ConfigurationParser.ConfigurationParser()
        configParser.set("clustering", "orphan_reduction", (0, 1)[checkButton.get_active()])

    #+---------------------------------------------- 
    #| Called when user wants to modify the expected protocol type
    #+----------------------------------------------
    def updateProtocolType(self, combo):
        valID = combo.get_active()
        configParser = ConfigurationParser.ConfigurationParser()
        configParser.set("clustering", "protocol_type", valID)

        if valID == 0:
            aType = "ascii"
        else:
            aType = "binary"
        for group in self.treeGroupGenerator.getGroups():
            group.setTypeForCols(aType)
        self.update()

    #+---------------------------------------------- 
    #| Called when user wants to refine regexes
    #+----------------------------------------------
    def refineRegexes_cb(self, button):
        if self.treeMessageGenerator.getGroup() == None:
            self.log.info("No group selected")
            return

        for group in self.treeGroupGenerator.getGroups():
            group.refineRegexes()
        dialog = gtk.Dialog(title="Refinement done", flags=0, buttons=None)
        dialog.set_size_request(250, 50)
        dialog.show()
        self.update()

    #+---------------------------------------------- 
    #| Called when user wants to refine regexes
    #+----------------------------------------------
    def dataCarving_cb(self, button):
        if self.treeMessageGenerator.getGroup() == None:
            self.log.info("No group selected")
            return
        dialog = gtk.Dialog(title="Data carving results", flags=0, buttons=None)

        # Just to force the calculation of the splitted messages by regex
        for group in self.treeGroupGenerator.getGroups():
            self.selectedGroup = str(group.getID())
            self.treeMessageGenerator.default(group)

        dialog.vbox.pack_start(self.treeGroupGenerator.dataCarvingResults(), True, True, 0)
        dialog.show()

    #+---------------------------------------------- 
    #| Called when user wants to see the entropy of a group of messages
    #+----------------------------------------------
    def messagesEntropy_cb(self, but):
        if self.treeMessageGenerator.getGroup() == None:
            self.log.info("No group selected")
            return
        entropy = Entropy.Entropy(self.treeMessageGenerator.getGroup())
        view = entropy.buildView()
        dialog = gtk.Dialog(title="Entropy view", flags=0, buttons=None)
        dialog.set_size_request(800, 600)
        dialog.vbox.pack_start(view, True, True, 0)
        dialog.show()

    #+---------------------------------------------- 
    #| Called when user wants to find the potential size fields
    #+----------------------------------------------
    def findSizeFields(self, button):
        if self.treeMessageGenerator.getGroup() == None:
            self.log.info("No group selected")
            return

        # Create a temporary group for testing size fields
        group = Group.Group('tmp_group', [])

        dialog = gtk.Dialog(title="Potential size fields and related payload", flags=0, buttons=None)
        ## ListStore format :
        # str: group.id
        # int: size field column
        # int: size field size
        # int: start column
        # int: substart column
        # int: end column
        # int: subend column
        # str: message rendered in cell
        treeview = gtk.TreeView(gtk.ListStore(str, int, int, int, int, int, int, str)) 
        cell = gtk.CellRendererText()
        treeview.connect("cursor-changed", self.sizeField_selected, group)
        column = gtk.TreeViewColumn('Size field and related payload')
        column.pack_start(cell, True)
        column.set_attributes(cell, text=7)
        treeview.append_column(column)

        # Chose button
        but = gtk.Button(label="Apply size field")
        but.show()
        but.connect("clicked", self.applySizeField, dialog, group)
        dialog.action_area.pack_start(but, True, True, 0)

        # Just to force the calculation of each group with its associated messages
        for group in self.treeGroupGenerator.getGroups():
            self.selectedGroup = str(group.getID())
            self.treeMessageGenerator.default(group)

        # Text view containing potential size fields
        treeview.set_size_request(800, 300)
        self.treeGroupGenerator.findSizeFields( treeview.get_model() )
        treeview.show()
        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scroll.show()
        scroll.add(treeview)
        dialog.vbox.pack_start(scroll, True, True, 0)
        dialog.show()

    #+---------------------------------------------- 
    #| Called when user wants to try to apply a size field on a group
    #+----------------------------------------------
    def sizeField_selected(self, treeview, group):
        (model, iter) = treeview.get_selection().get_selected()
        if(iter):
            if(model.iter_is_valid(iter)):
                group_id = model.get_value(iter, 0)
                size_field = model.get_value(iter, 1)
                size_field_len = model.get_value(iter, 2)
                start_field = model.get_value(iter, 3)
                start_field_len = model.get_value(iter, 4)
                end_field = model.get_value(iter, 5)
                end_field_len = model.get_value(iter, 6)
                
                ## Select the related group
                self.selectedGroup = group_id
                self.treeGroupGenerator.select_group_by_id(group_id)
                self.updateTreeStoreMessage()

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

                # Build a temporary group
                group.clear()
                for message in self.treeMessageGenerator.getGroup().getMessages():
                    tmp_message = Message.Message()
                    tmp_message.setData( message.getData() )
                    group.addMessage( tmp_message )
                group.setAlignment( copy.deepcopy(self.treeMessageGenerator.getGroup().getAlignment()) )
                group.setColumns( copy.deepcopy(list(self.treeMessageGenerator.getGroup().getColumns())) )

                self.treeTypeStructureGenerator.setGroup(group)
                self.treeTypeStructureGenerator.setMessageByID( group.getMessages()[-1].getID() )

                # Optionaly splits the columns if needed, and handles columns propagation
                if group.splitColumn(size_field, size_field_len) == True:
                    if size_field < start_field:
                        start_field += 1
                    if end_field != -1:
                        end_field += 1
                group.setDescriptionByCol(size_field, "Size field")
                group.setColorByCol(size_field, "red")
                if group.splitColumn(start_field, start_field_len) == True:
                    start_field += 1
                    if end_field != -1:
                        end_field += 1
                group.setDescriptionByCol(start_field, "Start of payload")
                group.splitColumn(end_field, end_field_len)

                # Adapt tabulation for encapsulated payloads
                if end_field != -1:
                    for iCol in range(start_field, end_field + 1):
                        group.setTabulationByCol(iCol, group.getTabulationByCol(iCol) + 10)
                else:
                    group.setTabulationByCol(start_field, group.getTabulationByCol(start_field) + 10)

                # View the proposed protocol structuration
                self.update()

    #+---------------------------------------------- 
    #| Called when user wants to apply a size field on a group
    #+----------------------------------------------
    def applySizeField(self, button, dialog, group):
        self.treeMessageGenerator.getGroup().setColumns( copy.deepcopy(list(group.getColumns())) )
        dialog.destroy()
