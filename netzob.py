#!/usr/bin/python
# coding: utf8

import pygtk
pygtk.require('2.0')

#+---------------------------------------------- 
#| Global Imports
#+----------------------------------------------
import sys
import gtk
import pango
import gobject
import os
#+---------------------------------------------- 
#| Local Imports
#+----------------------------------------------
from Resources import TracesExtractor
from Resources import netzobModel
from Resources import UIseqMessage
from Resources import UIGroupMessage


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
    def __init__(self, path):
        self.tracesPath = path
        
        # Parse the traces and store the results
        tracesExtractor = TracesExtractor.TracesExtractor(self.tracesPath)
        self.messages = tracesExtractor.parse(True) 
        
        self.netzob = netzobModel.netzobModel()
        
        # Definition of the main window
        self.fenetre = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.fenetre.set_size_request(1500, 900) 
        self.fenetre.connect("delete_event", self.evnmt_delete)
        self.fenetre.connect("destroy", self.destroy)
        
        self.vbox = gtk.VBox(False, spacing=10)

        # Mise en place de la barre de sélection de la cible 
        self.boite_poing = gtk.HandleBox()
        self.vbox.pack_start(self.boite_poing, False, False, 0)
        self.barre_outil = gtk.Toolbar();
        self.barre_outil.set_orientation(gtk.ORIENTATION_HORIZONTAL)
        self.barre_outil.set_style(gtk.TOOLBAR_BOTH)
        self.barre_outil.set_border_width(5)
        self.boite_poing.add(self.barre_outil)

        label = gtk.Label("Select target : ")
        self.barre_outil.append_widget(label, "", "")

        self.zone_saisie = gtk.combo_box_entry_new_text()
        self.zone_saisie.set_size_request(300, -1)

        self.barre_outil.append_widget(self.zone_saisie, "Saisie de la cible", "Privé")
        
        self.label_analyse = gtk.Label("...")
        self.button_valid = gtk.Button(stock=gtk.STOCK_OK)
        self.button_valid.set_label("Valider")
#        self.button_valid.connect("clicked", ) ## TODO
        self.barre_outil.append_widget(self.button_valid, "Validation du choix de l'analyse", "Privé")
        self.barre_outil.append_space()
        label_text = gtk.Label("     Current target : ")
        self.barre_outil.append_widget(label_text, "", "")
        self.barre_outil.append_widget(self.label_analyse, "", "")

        # Mise en place des onglets en fonction du type de l'analyse
        self.notebook = gtk.Notebook()
        self.notebook.set_tab_pos(gtk.POS_TOP)
        self.notebook.connect("switch-page", self.notebookFocus)

        self.pageList = []
        
        
        uiseqmessage = UIseqMessage.UIseqMessage(self.messages)
        
        uigroupmessage = UIGroupMessage.UIGroupMessage(self)
        
        self.pageList.append(["Message Sequencing", uiseqmessage])
        self.pageList.append(["Message Grouping", uigroupmessage])

        for page in self.pageList:
                self.notebook.append_page(page[1].panel, gtk.Label(page[0]))

        #self.notebook.append_page(uihome.panel, gtk.Label("Home"))
        self.vbox.pack_start(self.notebook, False, False, 0)

        self.barre_outil.show()
        self.boite_poing.show()
        self.zone_saisie.show()
        label.show()
        label_text.show()
        self.label_analyse.show()
        self.button_valid.show()
        self.notebook.show()
        self.vbox.show()
        self.fenetre.add(self.vbox)
        self.fenetre.show()

    def startGui(self):
        gtk.main()


    def evnmt_delete(self, widget, event, data=None):
        return False

    def destroy(self, widget, data=None):
        for page in self.pageList:
            page[1].kill()
        gtk.main_quit()

############# Callbacks

    def notebookFocus(self, notebook, page, pagenum):
        nameTab = notebook.get_tab_label_text((notebook.get_nth_page(pagenum)))

        for page in self.pageList:
            if page[0] == nameTab:
                page[1].update()


#+---------------------------------------------- 
#| RUNTIME
#+----------------------------------------------
if __name__ == "__main__":
    # for handling GUI access from threads
    gobject.threads_init()

    # parse command line and search for a directory to parse
    # default directory : traces/fgy_2011_05_10/
    directory = os.path.abspath("traces/short/")
    if (len(sys.argv)==2) :
        directory = sys.argv[1]
        
    # verify the directory exists
    if os.path.isdir(directory) :
        netZob = Netzob(directory)
        netZob.startGui()
    else :
        print "[ERROR] The directory {0} doesn't exist.".format(directory)
        
    

