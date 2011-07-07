#!/usr/bin/python
# coding: utf8

#+----------------------------------------------
#| Global Imports
#+----------------------------------------------
import gtk
import gobject
import os
import pygtk
import logging.config

pygtk.require('2.0')

#+---------------------------------------------- 
#| Local Imports
#+----------------------------------------------
from netzob.Sequencing import UIseqMessage
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
        self.fenetre = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.fenetre.set_size_request(1200, 800) 
        self.fenetre.connect("delete_event", self.evnmt_delete)
        self.fenetre.connect("destroy", self.destroy)
        
        # UI Header definition
        self.boite_poing = gtk.HandleBox()
        self.vbox = gtk.VBox(False, spacing=10)
        self.vbox.pack_start(self.boite_poing, False, False, 0)
        self.barre_outil = gtk.Toolbar();
        self.barre_outil.set_orientation(gtk.ORIENTATION_HORIZONTAL)
        self.barre_outil.set_style(gtk.TOOLBAR_BOTH)
        self.barre_outil.set_border_width(5)
        self.boite_poing.add(self.barre_outil)

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
        self.button_valid = gtk.Button(stock=gtk.STOCK_OK)
        self.button_valid.set_label("Valider")
        self.button_valid.connect("clicked", self.traceSelected)
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

        self.barre_outil.append_widget(label, "", "")
        self.barre_outil.append_widget(self.zone_saisie, "Select trace", "Privé")
        self.barre_outil.append_widget(self.button_valid, "Validation du choix de l'analyse", "Privé")
        self.barre_outil.append_space()
        self.barre_outil.append_widget(label_text, "", "")
        self.barre_outil.append_widget(self.label_analyse, "", "")
        self.barre_outil.append_widget(progressBox, None, None)
        self.barre_outil.append_widget(label2, "", "")
        self.barre_outil.append_widget(zone_saisie2, "Select type", "Privé")

        # Notebook definition
        self.notebook = gtk.Notebook()
        self.notebook.set_tab_pos(gtk.POS_TOP)
        self.notebook.connect("switch-page", self.notebookFocus)
        self.vbox.pack_start(self.notebook, True, True, 0)

        self.pageList = []
        uiseqmessage = UIseqMessage.UIseqMessage(self)
        self.pageList.append(["Message Sequencing", uiseqmessage])

        for page in self.pageList:
                self.notebook.append_page(page[1].panel, gtk.Label(page[0]))

        # Show every widgets
        self.barre_outil.show()
        self.boite_poing.show()
        self.zone_saisie.show()
        label.show()
        zone_saisie2.show()
        label2.show()
        label_text.show()
        self.label_analyse.show()
        self.button_valid.show()
        self.notebook.show()
        self.vbox.show()
        self.fenetre.add(self.vbox)
        self.fenetre.show()
        progressBox.show()
        align.show()
        self.progressBar.show()

    def startGui(self):
        gtk.main()

    def evnmt_delete(self, widget, event, data=None):
        return False




    def destroy(self, widget, data=None):
        for page in self.pageList:
            page[1].kill()
        gtk.main_quit()


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
