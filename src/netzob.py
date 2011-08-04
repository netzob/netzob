#!/usr/bin/python
# coding: utf8

#+----------------------------------------------
#| Global Imports
#+----------------------------------------------
import gtk
import gobject
import os
import pygtk
pygtk.require('2.0')
import logging.config
import threading
import sys

#+---------------------------------------------- 
#| Configure the Python path
#+----------------------------------------------
import sys
sys.path.append('lib/libNeedleman/')
sys.path.append('resources/scapy/')

#+---------------------------------------------- 
#| Local Imports
#+----------------------------------------------
from netzob.Sequencing import UIsequencing
from netzob.Dumping import UIDumpingMessage
from netzob.Capturing import UIcapturing
from netzob.Fuzzing import UIfuzzing
from netzob.Common import ConfigurationParser

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
class Netzob:

    #+---------------------------------------------- 
    #| Constructor :
    #| @param path: path of the directory containing traces to parse 
    #+----------------------------------------------   
    def __init__(self):
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.py')
        # Main window definition
        window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        window.set_title("NETZOB : NETwork protocol modeliZatiOn By reverse engineering")
#        window.set_size_request(1200, 800) 
        window.connect("delete_event", self.evnmt_delete)
        window.connect("destroy", self.destroy)
        
        # UI Header definition
        vbox = gtk.VBox(False, spacing=10)
        toolbar = gtk.HBox(False, spacing=0)
        vbox.pack_start(toolbar, False, False, 6)

        label = gtk.Label("Select target : ")
        entry = gtk.combo_box_entry_new_text()
        entry.set_size_request(300, -1)
        entry.set_model(gtk.ListStore(str))

        # retrieves the trace directory path
        tracesDirectoryPath = ConfigurationParser.ConfigurationParser().get("traces", "path")        
        
        for tmpDir in os.listdir(tracesDirectoryPath):
            if tmpDir == '.svn':
                continue
            entry.append_text(tmpDir)

        self.label_analyse = gtk.Label("...")
        button_valid = gtk.Button(gtk.STOCK_OK)
        button_valid.set_label("Start analysis")
        button_valid.connect("clicked", self.traceSelected, entry)
        
        button_save = gtk.Button(gtk.STOCK_OK)
        button_save.set_label("Save analysis")
        button_save.connect("clicked", self.saveTrace, entry)
        
        label_text = gtk.Label("     Current trace : ")

        # Progress Bar handling inside UI Header
        progressBox = gtk.VBox(False, 5)
        progressBox.set_border_width(10)
        align = gtk.Alignment(0.5, 0.5, 0, 0)
        progressBox.pack_start(align, False, False, 5)
        self.progressBar = gtk.ProgressBar()
        align.add(self.progressBar)

        toolbar.pack_start(label, False, False, 0)
        toolbar.pack_start(entry, False, False, 0)
        toolbar.pack_start(button_valid, False, False, 0)
        toolbar.pack_start(button_save, False, False, 0)
        toolbar.pack_start(label_text, False, False, 0)
        toolbar.pack_start(self.label_analyse, False, False, 0)
        toolbar.pack_start(progressBox, False, False, 0)

        # Notebook definition
        self.notebook = gtk.Notebook()
        self.notebook.set_tab_pos(gtk.POS_TOP)
        self.notebook.connect("switch-page", self.notebookFocus)
        vbox.pack_start(self.notebook, True, True, 0)

        self.pageList = []
        # Adding the different notebook
        self.capturing = UIcapturing.UIcapturing(self)
        self.sequencing = UIsequencing.UIsequencing(self)
        self.dumping = UIDumpingMessage.UIDumpingMessage(self)
        self.fuzzing = UIfuzzing.UIfuzzing(self)

        self.pageList.append(["Import", self.capturing])
        self.pageList.append(["Sequencing", self.sequencing])
        self.pageList.append(["Fuzzing", self.fuzzing])
        self.pageList.append(["Export", self.dumping])
        
        for page in self.pageList:
                self.notebook.append_page(page[1].panel, gtk.Label(page[0]))

        # Show every widgets
        toolbar.show()
        entry.show()
        label.show()
        label_text.show()
        self.label_analyse.show()
        button_valid.show()
        button_save.show()
        self.notebook.show()
        vbox.show()
        window.add(vbox)
        window.show()
        progressBox.show()
        align.show()
        self.progressBar.show()

    def startGui(self):
        # UI thread launching
        self.uiThread = threading.Thread(None, self.guiThread, None, (), {})
        self.uiThread.start()

    def evnmt_delete(self, widget, event, data=None):
        return False

    def destroy(self, widget, data=None):
        for page in self.pageList:
            page[1].kill()
        gtk.main_quit()

    def guiThread(self):
        gtk.main()


#+---------------------------------------------- 
#| Callbacks
#+----------------------------------------------

    #+---------------------------------------------- 
    #| Called when user select a notebook
    #+----------------------------------------------
    def notebookFocus(self, notebook, page, pagenum):
        nameTab = notebook.get_tab_label_text(notebook.get_nth_page(pagenum))
        for page in self.pageList:
            if page[0] == nameTab:
                page[1].update()
                
    def saveTrace(self, null, entry):
        self.log.info("Starting the saving process of all the application")
        
        # retrieve the new trace path
        target = entry.get_active_text()
        if target == "":
            return

        tracesDirectoryPath = ConfigurationParser.ConfigurationParser().get("traces", "path")
        configPath = os.path.abspath(".") + os.sep + tracesDirectoryPath + os.sep + target+ os.sep +"config.xml"
        
        
        
        for page in self.pageList:
            page[1].save(configPath)
            

    #+---------------------------------------------- 
    #| Called when user select a new trace for analysis
    #+----------------------------------------------
    def traceSelected(self, null, entry):
        # retrieve the new trace path
        target = entry.get_active_text()
        if target == "":
            return

        tracesDirectoryPath = ConfigurationParser.ConfigurationParser().get("traces", "path")

        self.label_analyse.set_text(tracesDirectoryPath + os.sep + target)
        self.tracePath = os.path.abspath(".") + os.sep + tracesDirectoryPath + os.sep + target
        
        # clear past analysis and initialize the active notebook analysis
        for page in self.pageList:
            page[1].clear()
            nameTab = self.notebook.get_tab_label_text(self.notebook.get_nth_page(self.notebook.get_current_page()))
            if page[0] == nameTab:
                page[1].new()


#+---------------------------------------------- 
#| RUNTIME
#+----------------------------------------------
if __name__ == "__main__":
    # create logger with the given configuration
    logger = logging.getLogger('netzob.py')
    logger.info("Logging module configured and loaded .")
    
    # for handling GUI access from threads
    gobject.threads_init()
    
    netZob = Netzob()
    netZob.startGui()
