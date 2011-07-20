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
sys.path.append('lib/libNeedleman')

#+---------------------------------------------- 
#| Local Imports
#+----------------------------------------------
from netzob.Sequencing import UIseqMessage
from netzob.Dumping import UIDumpingMessage
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
        # Main window definition
        window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        window.set_title("NETZOB : NETwork protocol modeliZatiOn By reverse engineering")
        window.set_size_request(1200, 800) 
        window.connect("delete_event", self.evnmt_delete)
        window.connect("destroy", self.destroy)
        
        # UI Header definition
        vbox = gtk.VBox(False, spacing=10)
        toolbar = gtk.HBox(False, spacing=0)
        vbox.pack_start(toolbar, False, False, 5)

        label = gtk.Label("Select target : ")
        self.zone_saisie = gtk.combo_box_entry_new_text()
        self.zone_saisie.set_size_request(300, -1)
        self.zone_saisie.set_model(gtk.ListStore(str))

        # retrieves the trace directory path
        tracesDirectoryPath = ConfigurationParser.ConfigurationParser().get("traces", "path")        
        
        for tmpDir in os.listdir(tracesDirectoryPath):
            if tmpDir == '.svn':
                continue
            self.zone_saisie.append_text(tmpDir)

        self.label_analyse = gtk.Label("...")
        button_valid = gtk.Button(gtk.STOCK_OK)
        button_valid.set_label("Select")
        button_valid.connect("clicked", self.traceSelected)
        label_text = gtk.Label("     Current target : ")

        # Progress Bar handling inside UI Header
        progressBox = gtk.VBox(False, 5)
        progressBox.set_border_width(10)
        align = gtk.Alignment(0.5, 0.5, 0, 0)
        progressBox.pack_start(align, False, False, 5)
        self.progressBar = gtk.ProgressBar()
        align.add(self.progressBar)

        # Widget for choosing the anlysed protocole type
        label2 = gtk.Label("Protocol type : ")
        zone_saisie2 = gtk.combo_box_entry_new_text()
        zone_saisie2.set_size_request(300, -1)
        zone_saisie2.set_model(gtk.ListStore(str))

        zone_saisie2.append_text("Text based (HTTP, FTP)")
        zone_saisie2.append_text("Fixed fields binary based (IP, TCP)")
        zone_saisie2.append_text("Variable fields binary based (ASN.1)")

        toolbar.pack_start(label, False, False, 0)
        toolbar.pack_start(self.zone_saisie, False, False, 0)
        toolbar.pack_start(button_valid, False, False, 0)
        toolbar.pack_start(label_text, False, False, 0)
        toolbar.pack_start(self.label_analyse, False, False, 0)
        toolbar.pack_start(progressBox, False, False, 0)
        toolbar.pack_start(label2, False, False, 0)
        toolbar.pack_start(zone_saisie2, False, False, 0)

        # Notebook definition
        self.notebook = gtk.Notebook()
        self.notebook.set_tab_pos(gtk.POS_TOP)
        self.notebook.connect("switch-page", self.notebookFocus)
        vbox.pack_start(self.notebook, True, True, 0)

        self.pageList = []
        # Adding the message sequencing "onglet"
        self.uiseqmessage = UIseqMessage.UIseqMessage(self)
        self.pageList.append(["Message Sequencing", self.uiseqmessage])
        
        # Adding the message dumping "onglet"
        self.uiDumpingMessage = UIDumpingMessage.UIDumpingMessage(self)
        self.pageList.append(["Message XML Dumping", self.uiDumpingMessage])
        
        for page in self.pageList:
                self.notebook.append_page(page[1].panel, gtk.Label(page[0]))

        # Show every widgets
        toolbar.show()
        self.zone_saisie.show()
        label.show()
        zone_saisie2.show()
        label2.show()
        label_text.show()
        self.label_analyse.show()
        button_valid.show()
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


    #+---------------------------------------------- 
    #| Called when user select a new trace for analysis
    #+----------------------------------------------
    def traceSelected(self, null):
        # retrieve the new trace path
        target = self.zone_saisie.get_active_text()
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
