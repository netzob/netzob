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
import os
import time
import random

#+---------------------------------------------- 
#| Local Imports
#+----------------------------------------------
from ..Common import ConfigurationParser
from ..Common import ConfigurationParser, TypeIdentifier
from TreeViews import TreeGroupGenerator
from TreeViews import TreeTypeStructureGenerator

#+---------------------------------------------- 
#| Configuration of the logger
#+----------------------------------------------
#loggingFilePath = ConfigurationParser.ConfigurationParser().get("logging", "path")
#logging.config.fileConfig(loggingFilePath)

#+---------------------------------------------- 
#| FileImport :
#|     GUI for capturing messages
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.2
#+---------------------------------------------- 
class File:

    def new(self):
        pass

    def update(self):
        self.treeGroupGenerator.update()
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
        self.log = logging.getLogger('netzob.Fuzzing.File.py')
        self.netzob = netzob
        self.groups = []
        self.selectedGroup = None
 
        self.panel = gtk.HPaned()
        self.panel.show()

        #+---------------------------------------------- 
        #| LEFT PART OF THE GUI : TREEVIEW
        #+----------------------------------------------           
        vb_left_panel = gtk.VBox(False, spacing=0)
        self.panel.add(vb_left_panel)
        vb_left_panel.set_size_request(-1, -1)
        vb_left_panel.show()

        # Initialize the treeview generator for the groups
        # Create the treeview
        self.treeGroupGenerator = TreeGroupGenerator.TreeGroupGenerator(self.netzob)
        self.treeGroupGenerator.initialization()
        vb_left_panel.pack_start(self.treeGroupGenerator.getScrollLib(), True, True, 0)
        self.treeGroupGenerator.getTreeview().connect("cursor-changed", self.groupSelected) 
#        self.treeGroupGenerator.getTreeview().connect('button-press-event', self.button_press_on_treeview_groups)

        #+---------------------------------------------- 
        #| RIGHT PART OF THE GUI : TYPE STRUCTURE OUTPUT
        #+----------------------------------------------
        vb_right_panel = gtk.VBox(False, spacing=0)
        vb_right_panel.show()
        # Initialize the treeview for the type structure
        self.treeTypeStructureGenerator = TreeTypeStructureGenerator.TreeTypeStructureGenerator()
        self.treeTypeStructureGenerator.initialization()
        self.treeTypeStructureGenerator.getTreeview().connect('button-press-event', self.button_press_on_field)
        vb_right_panel.add(self.treeTypeStructureGenerator.getScrollLib())
        self.panel.add(vb_right_panel)

    def groupSelected(self, treeview):
        (model, iter) = treeview.get_selection().get_selected()
        if(iter):
            if(model.iter_is_valid(iter)):
                # Retrieve the selected group
                idGroup = model.get_value(iter, 0)
                self.selectedGroup = idGroup
                group = None
                for tmp_group in self.netzob.groups.getGroups() :
                    if str(tmp_group.getID()) == idGroup :
                        group = tmp_group

                # Retrieve a random message in order to show a type structure
                message = group.getMessages()[-1]
                self.treeTypeStructureGenerator.setGroup(group)
                self.treeTypeStructureGenerator.setMessage(message)
                self.treeTypeStructureGenerator.update()

    #+---------------------------------------------- 
    #| button_press_on_field :
    #|   Create a menu to display available operations
    #|   on the treeview groups
    #+----------------------------------------------
    def button_press_on_field(self, button, event):
        if event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:        
            # Retrieves the group on which the user has clicked on
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

"""
    #+---------------------------------------------- 
    #| Constructor :
    #| @param groups: list of all groups 
    #+----------------------------------------------   
    def __init__(self, zob):        
        self.zob = zob

        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Capturing.FileImport.py')
        self.packets = []

        # Network Capturing Panel
        self.panel = gtk.Table(rows=3, columns=3, homogeneous=False)
        self.panel.show()

        # Scapy filter
        but = gtk.Button("Select file")
        but.show()
        label_file = gtk.Label("...")
        label_file.show()
        but.connect("clicked", self.select_file, label_file)
        self.panel.attach(but, 0, 1, 0, 1, xoptions=0, yoptions=0, xpadding=5, ypadding=5)
        self.panel.attach(label_file, 1, 2, 0, 1, xoptions=0, yoptions=0, xpadding=5, ypadding=5)

        # Packet detail
        scroll = gtk.ScrolledWindow()
        self.textview = gtk.TextView()
        self.textview.show()
        self.textview.get_buffer().create_tag("normalTag", family="Courier")
        scroll.add(self.textview)
        scroll.show()
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.panel.attach(scroll, 0, 3, 1, 2, xoptions=gtk.FILL|gtk.EXPAND, yoptions=gtk.FILL|gtk.EXPAND, xpadding=5, ypadding=5)

        # Button select packets for further analysis
        but = gtk.Button(label="Import file")
        but.show()
        but.connect("clicked", self.import_file)
        self.panel.attach(but, 0, 2, 2, 3, xoptions=0, yoptions=0, xpadding=5, ypadding=5)

    #+---------------------------------------------- 
    #| Called when user select a list of packet
    #+----------------------------------------------
    def import_file(self, button):
        dialog = gtk.Dialog(title="Save selected packet as a new trace", flags=0, buttons=None)
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
        but.connect("clicked", self.add_packets_to_existing_trace, entry, dialog)
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
        but.connect("clicked", self.create_new_trace, entry, dialog)
        but.show()
        table.attach(label, 0, 1, 1, 2, xoptions=0, yoptions=0, xpadding=5, ypadding=5)
        table.attach(entry, 1, 2, 1, 2, xoptions=0, yoptions=0, xpadding=5, ypadding=5)
        table.attach(but, 2, 3, 1, 2, xoptions=0, yoptions=0, xpadding=5, ypadding=5)

        dialog.action_area.pack_start(table, True, True, 0)

    #+---------------------------------------------- 
    #| Add a selection of packets to an existing trace
    #+----------------------------------------------
    def add_packets_to_existing_trace(self, button, entry, dialog):
        tracesDirectoryPath = ConfigurationParser.ConfigurationParser().get("traces", "path")
        existingTraceDir = tracesDirectoryPath + "/" + entry.get_active_text()
        # Create the new XML structure
        # Create the new XML structure
        res = "<datas>\n"
        res += "<data proto=\"file\" sourceIp=\"local\" sourcePort=\"local\" targetIp=\"local\" targetPort=\"local\" timestamp=\"" + str(time.time()) + "\">\n"
        res += self.packet.encode("hex") + "\n"
        res += "</data>\n"
        res += "</datas>\n"
        # Dump into a random XML file
        fd = open(existingTraceDir +"/"+ str(random.randint(100000, 9000000)) + ".xml"  , "w")
        fd.write(res)
        fd.close()
        dialog.destroy()

    #+---------------------------------------------- 
    #| Creation of a new trace from a selection of packets
    #+----------------------------------------------
    def create_new_trace(self, button, entry, dialog):
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
        os.mkdir( newTraceDir )
        # Create the new XML structure
        res = "<datas>\n"
        res += "<data proto=\"file\" sourceIp=\"local\" sourcePort=\"local\" targetIp=\"local\" targetPort=\"local\" timestamp=\"" + str(time.time()) + "\">\n"
        res += self.packet.encode("hex") + "\n"
        res += "</data>\n"
        res += "</datas>\n"
        # Dump into a random XML file
        fd = open(newTraceDir +"/"+ str(random.randint(100000, 9000000)) + ".xml"  , "w")
        fd.write(res)
        fd.close()
        dialog.destroy()
        self.zob.updateListOfAvailableTraces()

    #+---------------------------------------------- 
    #| Called when user import a pcap file
    #+----------------------------------------------
    def select_file(self, button, label):
        aFile = ""
        chooser = gtk.FileChooserDialog(title=None,action=gtk.FILE_CHOOSER_ACTION_OPEN,
                                        buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))
        res = chooser.run()
        if res == gtk.RESPONSE_OK:
            aFile = chooser.get_filename()
            label.set_text(aFile)
        chooser.destroy()

        if aFile != "" and aFile != None:
            pktFD = open(aFile, 'r')
            self.packet =  pktFD.read()
            pktFD.close()

            if len(self.packet) > 4096:
                tmp_pkt = self.packet[:4095] + "..."
            else:
                tmp_pkt = self.packet
            typer = TypeIdentifier.TypeIdentifier()
            self.textview.get_buffer().insert_with_tags_by_name(self.textview.get_buffer().get_start_iter(), typer.hexdump( tmp_pkt ), "normalTag")
"""
