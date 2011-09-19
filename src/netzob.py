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

#+---------------------------------------------------------------------------+ 
#| Standard library imports
#+---------------------------------------------------------------------------+
import gtk
import gobject
import os
import logging.config
import threading
import sys

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+
sys.path.append('lib/libNeedleman/')
sys.path.append('resources/scapy/')

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Modelization import UImodelization
from netzob.Export import UIexport
from netzob.Import import UIimport
from netzob.Fuzzing import UIfuzzing
from netzob.Common import ConfigurationParser
from netzob.Common import StateParser
from netzob.Common import Groups

#+---------------------------------------------- 
#| Configuration of the logger
#+----------------------------------------------
loggingFilePath = ConfigurationParser.ConfigurationParser().get("logging", "path")
logging.config.fileConfig(loggingFilePath)

#+---------------------------------------------- 
#| Netzob :
#|     runtime class
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.2
#+---------------------------------------------- 
class Netzob():

    #+---------------------------------------------- 
    #| Constructor :
    #| @param path: path of the directory containing traces to parse 
    #+----------------------------------------------   
    def __init__(self):
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.py')
        self.tracePath = ""

        # Groups of messages are handled with the following object
        self.groups = Groups.Groups(self)

        # Main window definition
        window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        window.set_title("NETZOB : NETwork protocol modeliZatiOn By reverse engineering")
        window.connect("delete_event", self.evnmtDelete)
        window.connect("destroy", self.destroy)
        
        ## UI Header definition
        vbox = gtk.VBox(False, spacing=0)
        toolbar = gtk.HBox(False, spacing=0)
        vbox.pack_start(toolbar, False, False, 2)

        label = gtk.Label("Select trace : ")
#        menu = gtk.Menu()
#        gtk.MenuItem("")

        liststore = gtk.ListStore(str, str)
        self.entry = gtk.ComboBox(liststore)
        cellText = gtk.CellRendererText()
        self.entry.pack_start(cellText, True)
        self.entry.add_attribute(cellText, 'text', 0)
        cellImage = gtk.CellRendererPixbuf()
        self.entry.pack_start(cellImage, False)
        self.entry.add_attribute(cellImage, 'stock_id', 1)

#        self.entry = gtk.combo_box_entry_new_text()
        self.entry.set_size_request(200, -1)
        self.entry.connect("changed", self.traceSelected)
        self.updateListOfAvailableTraces()       
      
        label_text = gtk.Label("     Current trace : ")
        self.label_analyse = gtk.Label("...")

        button_save = gtk.Button(gtk.STOCK_OK)
        button_save.set_label("Save trace")
        button_save.connect("clicked", self.saveTrace)

        # Progress Bar handling inside UI Header
        progressBox = gtk.VBox(False, 0)
        progressBox.set_border_width(0)
        align = gtk.Alignment(0.5, 0.5, 0, 0)
        progressBox.pack_start(align, False, False, 5)
        self.progressBar = gtk.ProgressBar()
        align.add(self.progressBar)

        toolbar.pack_start(label, False, False, 5)
        toolbar.pack_start(self.entry, False, False, 5)
        toolbar.pack_start(label_text, False, False, 5)
        toolbar.pack_start(self.label_analyse, False, False, 5)
        toolbar.pack_start(button_save, False, False, 5)
        toolbar.pack_start(progressBox, False, False, 5)

        # Notebook definition
        self.notebook = gtk.Notebook()
        self.notebook.set_tab_pos(gtk.POS_TOP)
        self.notebook.connect("switch-page", self.notebookFocus)
        vbox.pack_start(self.notebook, True, True, 0)

        self.pageList = []
        # Adding the different notebook
        self.Import = UIimport.UIimport(self)
        self.modelization = UImodelization.UImodelization(self)
        self.export = UIexport.UIexport(self)
        self.fuzzing = UIfuzzing.UIfuzzing(self)

        self.pageList.append(["Import", self.Import])
        self.pageList.append(["Modelization", self.modelization])
        self.pageList.append(["Fuzzing", self.fuzzing])
        self.pageList.append(["Export", self.export])
        
        for page in self.pageList:
                self.notebook.append_page(page[1].panel, gtk.Label(page[0]))

        # Show every widgets
        toolbar.show()
        self.entry.show()
        label.show()
        label_text.show()
        self.label_analyse.show()
        button_save.show()
        self.notebook.show()
        vbox.show()
        window.add(vbox)
        window.show()
        progressBox.show()
        align.show()
        self.progressBar.show()
        
    #+------------------------------------------------------------------------ 
    #| updateListOfAvailableTraces :
    #| @param entry the GTK entry in which the name of the available traces
    #|              will be added
    #+------------------------------------------------------------------------
    def updateListOfAvailableTraces(self):
        self.entry.get_model().clear()
        # retrieves the trace directory path
        tracesDirectoryPath = ConfigurationParser.ConfigurationParser().get("traces", "path")       
        # a temporary list in which all the folders will be stored and after sorted
        temporaryListOfFolders = []
         
        # list all the directories (except .svn)
        for tmpDir in os.listdir(tracesDirectoryPath):
            stateSaved = False
            pathOfTrace = tracesDirectoryPath + "/" + tmpDir
            
            if os.path.isfile(pathOfTrace) or tmpDir == '.svn':
                continue
            
            
            for aFile in os.listdir(pathOfTrace):
                if aFile == "config.xml":
                    stateSaved = True
                    continue
            if stateSaved == True:
                temporaryListOfFolders.append([tmpDir, gtk.STOCK_INFO])
            else:
                temporaryListOfFolders.append([tmpDir, ''])
        
        # Sort and add to the entry
        for folder in sorted(temporaryListOfFolders) :
            self.entry.get_model().append(folder)

    def startGui(self):
        # UI thread launching
        self.uiThread = threading.Thread(None, self.guiThread, None, (), {})
        self.uiThread.start()

    def evnmtDelete(self, widget, event, data=None):
        return False

    def destroy(self, widget, data=None):
        for page in self.pageList:
            page[1].kill()
        gtk.main_quit()

    def guiThread(self):
        gtk.main()

    #+---------------------------------------------- 
    #| Called when user select a notebook
    #+----------------------------------------------
    def notebookFocus(self, notebook, page, pagenum):
        nameTab = notebook.get_tab_label_text(notebook.get_nth_page(pagenum))
        for page in self.pageList:
            if page[0] == nameTab:
                page[1].update()
                
    def saveTrace(self, null):
        self.log.info("Starting the saving process of all the application")
        
        # retrieve the new trace path
        target = self.entry.get_active_text()
        if target == "":
            self.log.info("No trace selected")
            return

        tracesDirectoryPath = ConfigurationParser.ConfigurationParser().get("traces", "path")
        configPath = os.path.abspath(".") + os.sep + tracesDirectoryPath + os.sep + target + os.sep + "config.xml"
        
        for page in self.pageList:
            page[1].save(configPath)

    #+---------------------------------------------- 
    #| Called when user select a new trace for analysis
    #+----------------------------------------------
    def traceSelected(self, null):
        # retrieve the new trace path
        target = self.entry.get_active_text()
        if target == "":
            return
        tracesDirectoryPath = ConfigurationParser.ConfigurationParser().get("traces", "path")
        self.label_analyse.set_text(target)
        self.tracePath = os.path.abspath(".") + os.sep + tracesDirectoryPath + os.sep + target
        
        # clear past analysis and initialize the each notebook
        self.groups.clear()
        for page in self.pageList:
            page[1].clear()
            #nameTab = self.notebook.get_tab_label_text(self.notebook.get_nth_page(self.notebook.get_current_page()))
            #if page[0] == nameTab:
            page[1].new()

        # If a state saving exists, loads it
        for file in os.listdir(self.tracePath):
            filePath = self.tracePath + "/" + file
            if file == "config.xml":
                self.log.info("A configuration file has been found.")
                stateParser = StateParser.StateParser(self.tracePath + "/config.xml")
                stateParser.loadConfiguration()
                self.groups.setGroups(stateParser.getGroups())
        self.update()

    #+---------------------------------------------- 
    #| Update each panels
    #+----------------------------------------------
    def update(self):
        for page in self.pageList:
            page[1].update()

#+---------------------------------------------- 
#| RUNTIME
#+----------------------------------------------
if __name__ == "__main__":
    # create logger with the given configuration
    logger = logging.getLogger('netzob.py')
    logger.info("Logging module configured and loaded")
    
    # for handling GUI access from threads
    gobject.threads_init()
    
    netZob = Netzob()
    netZob.startGui()
