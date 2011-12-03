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
import pygtk
pygtk.require('2.0')
import logging
import os
import random

#+---------------------------------------------- 
#| Local Imports
#+----------------------------------------------
from netzob.Common.TypeIdentifier import TypeIdentifier
from netzob.Common.ConfigurationParser import ConfigurationParser
from netzob.Common.Models.FileMessage import FileMessage
from netzob.Common.Models.Factories.FileMessageFactory import FileMessageFactory

#+---------------------------------------------- 
#| FileImport :
#|     GUI for capturing messages
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.2
#+---------------------------------------------- 
class File:
    
    #+---------------------------------------------- 
    #| Called when user select a new trace
    #+----------------------------------------------
    def new(self):
        pass

    def update(self):
        pass

    def clear(self):
        pass

    def kill(self):
        pass

    #+---------------------------------------------- 
    #| Constructor :
    #| @param groups: list of all groups 
    #+----------------------------------------------   
    def __init__(self, zob):        
        self.zob = zob
        
        # Default line separator is <CR>
        self.lineSeparator = []
        self.fileName = ""

        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Capturing.File.py')
        self.messages = []
        
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Main panel
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        self.panel = gtk.Table(rows=10, columns=8, homogeneous=True)
        self.panel.show()
        
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Select a file
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        but = gtk.Button("Select file")
        but.show()
        entry_filepath = gtk.Entry()
#        entry_filepath.set_width_chars(50)
        entry_filepath.set_text("")
        entry_filepath.show()
        but.connect("clicked", self.select_file, entry_filepath)
        self.panel.attach(but, 0, 1, 0, 1, xoptions=0, yoptions=0, xpadding=5, ypadding=5)
        self.panel.attach(entry_filepath, 1, 2, 0, 1, xoptions=0, yoptions=0, xpadding=5, ypadding=5)
        
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Separator
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        label_separator = gtk.Label("Line-separator :")
        label_separator.show()
        entry_separator = gtk.Entry()
#        entry_separator.set_width_chars(50)
        entry_separator.set_text("".join(self.lineSeparator))
        entry_separator.show()
        entry_separator.connect("activate", self.entry_separator_callback, entry_separator)

        self.panel.attach(label_separator, 2, 3, 0, 1, xoptions=gtk.FILL | gtk.EXPAND, yoptions=gtk.FILL | gtk.EXPAND, xpadding=5, ypadding=5)
        self.panel.attach(entry_separator, 3, 4, 0, 1, xoptions=gtk.FILL | gtk.EXPAND, yoptions=gtk.FILL | gtk.EXPAND, xpadding=5, ypadding=5)

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # File details
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        scroll = gtk.ScrolledWindow()
        self.textview = gtk.TextView()
        self.textview.show()
        self.textview.get_buffer().create_tag("normalTag", family="Courier")
        scroll.add(self.textview)
        scroll.show()
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.panel.attach(scroll, 0, 4, 1, 10, xoptions=gtk.FILL | gtk.EXPAND, yoptions=gtk.FILL | gtk.EXPAND, xpadding=5, ypadding=5)

       

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Extracted data
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        scroll2 = gtk.ScrolledWindow()
        self.lineView = gtk.TreeView(gtk.TreeStore(str, str)) # line number, content
        self.lineView.get_selection().set_mode(gtk.SELECTION_NONE)
        cell = gtk.CellRendererText()
        # Col file descriptor
        column = gtk.TreeViewColumn('Line number')
        column.pack_start(cell, True)
        column.set_attributes(cell, text=0)
        self.lineView.append_column(column)
        # Col type
        column = gtk.TreeViewColumn('Content')
        column.pack_start(cell, True)
        column.set_attributes(cell, text=1)
        self.lineView.append_column(column)
        self.lineView.show()

        scroll2.add(self.lineView)
        scroll2.show()
        scroll2.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.panel.attach(scroll2, 4, 8, 0, 10, xoptions=gtk.FILL, yoptions=gtk.FILL | gtk.EXPAND, xpadding=5, ypadding=5)

        # Button select packets for further analysis
        but = gtk.Button(label="Import")
        but.show()
        but.connect("clicked", self.import_file)
        self.panel.attach(but, 2, 3, 10, 11, xoptions=0, yoptions=0, xpadding=5, ypadding=5)

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
        projectsDirectoryPath = ConfigurationParser().get("projects", "path")
        for tmpDir in os.listdir(projectsDirectoryPath):
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
        projectsDirectoryPath = ConfigurationParser().get("projects", "path")
        existingTraceDir = projectsDirectoryPath + "/" + entry.get_active_text()
        # Create the new XML structure
        res = []
        res.append("<messages>")
        for message in self.messages :
            res.append(FileMessageFactory.saveInXML(message))
        res.append("</messages>")
        # Dump into a random XML file
        fd = open(existingTraceDir + "/" + str(random.randint(100000, 9000000)) + ".xml"  , "w")
        fd.write("\n".join(res))
        fd.close()
        dialog.destroy()

    #+---------------------------------------------- 
    #| Creation of a new trace from a selection of packets
    #+----------------------------------------------
    def create_new_trace(self, button, entry, dialog):
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
        newTraceDir = projectsDirectoryPath + "/" + entry.get_text()
        os.mkdir(newTraceDir)
        # Create the new XML structure
        res = []
        res.append("<messages>")
        for message in self.messages :
            res.append(FileMessageFactory.saveInXML(message))
        res.append("</messages>")
        # Dump into a random XML file
        fd = open(newTraceDir + "/" + str(random.randint(100000, 9000000)) + ".xml"  , "w")
        fd.write("\n".join(res))
        fd.close()
        dialog.destroy()
        self.zob.updateListOfAvailableProjects()

    #+---------------------------------------------- 
    #| Called when user import a file
    #+----------------------------------------------
    def select_file(self, button, label):
        aFile = ""
        chooser = gtk.FileChooserDialog(title=None, action=gtk.FILE_CHOOSER_ACTION_OPEN,
                                        buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        # Computes the selected file
        res = chooser.run()
        if res == gtk.RESPONSE_OK:
            aFile = chooser.get_filename()
            label.set_text(aFile)
        chooser.destroy()
        
        # Reads the file
        if aFile != "" and aFile != None:
            self.fileName = aFile
            self.size = os.path.getsize(aFile)
            self.creationDate = str(os.path.getctime(aFile))
            self.modificationDate = str(os.path.getmtime(aFile))
            self.owner = "none"
            pktFD = open(aFile, 'r')
            self.content = pktFD.read()
            pktFD.close()
            typer = TypeIdentifier()
           
            self.textview.get_buffer().insert_with_tags_by_name(self.textview.get_buffer().get_start_iter(), typer.hexdump(self.content), "normalTag")
            
            # Fullfill the packets list
            self.updatePacketList()
            
            # 
    def entry_separator_callback(self, widget, entry):
        entry_text = widget.get_text()
        # transforms ; 2043 in [0x20; 0x43]
        i = 0
        self.lineSeparator = []
        while (i < len(entry_text)) :
            d = entry_text[i] + entry_text[i + 1]
            self.lineSeparator.append(int(d, 16))
            i = i + 2
            
        self.updatePacketList()    
        

        print "Entry contents: %s\n" % entry_text
        

    def updatePacketList(self):
        self.log.info("updating packet list")
        typer = TypeIdentifier()
        hexValOfContent = ";".join(str(int(i, 16)) for i in typer.ascii2hex(self.content))
        separator = ";".join(str(i) for i in self.lineSeparator)       
        print hexValOfContent
        ar = hexValOfContent.split(";" + separator + ";")
        # Create a FileMessage for each line
        lineNumber = 1
        self.messages = []        
        ps = []
        i = 0
        for a in ar :
            if i < len(ar) - 1 :
                ps.append(a + ";" + separator)
            else :
                ps.append(a)
            i = i + 1
                
        self.lineView.get_model().clear()
            
        for a in ps :
            # Create a message for each
            message = FileMessage()
            message.setLineNumber(lineNumber)
            message.setFilename(self.fileName)
            message.setCreationDate(self.creationDate)
            message.setOwner(self.owner)
            message.setModificationDate(self.modificationDate)
            message.setSize(self.size)
            
            test = a.split(";")
            fe = []
            for t in test :
                h = hex(int(t))[2:]
                # Add a 0 before an hex value to always have two digit in a hex
                if len(h) == 1 :
                    h = "0" + h
                fe.append(h)
                
            
            message.setData("".join(fe))
            
            self.lineView.get_model().append(None, [lineNumber, ";".join(fe)])
            
            self.messages.append(message)
            lineNumber = lineNumber + 1
        
        for message in self.messages :
            print FileMessageFactory.saveInXML(message)
        
        
        

    #+---------------------------------------------- 
    #| GETTERS
    #+----------------------------------------------
    def getPanel(self):
        return self.panel
