#!/usr/bin/ python
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
import uuid
import logging
import re
import gtk
import pango
import gobject
import pygtk
pygtk.require('2.0')

#+---------------------------------------------- 
#| Local Imports
#+----------------------------------------------
import ConfigurationParser, TypeIdentifier
from ..Modelization import TracesExtractor

#+---------------------------------------------- 
#| Configuration of the logger
#+----------------------------------------------
loggingFilePath = ConfigurationParser.ConfigurationParser().get("logging", "path")
logging.config.fileConfig(loggingFilePath)

#+---------------------------------------------- 
#| Groups :
#|     definition of the groups of messages
#+---------------------------------------------- 
class Groups(object):
    
    #+----------------------------------------------
    #| Fields in a group message definition :
    #|     - groups
    #+----------------------------------------------
    
    #+---------------------------------------------- 
    #| Constructor :
    #+----------------------------------------------   
    def __init__(self, netzob):
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Common.Groups.py')
        self.netzob = netzob
        self.groups = []

    def clear(self):
        del self.groups[:] # Just clean the object without deleting it

    def initGroupsWithTraces(self):
        tracesExtractor = TracesExtractor.TracesExtractor(self.netzob)
        self.setGroups(  tracesExtractor.parse() )
        self.netzob.update()

    def addGroup(self, group):
        self.groups.append( group )

    def removeGroup(self, group):
        self.groups.remove( group )

    #+---------------------------------------------- 
    #| slickRegexes:
    #|  try to make smooth the regexes, by deleting tiny static
    #|  sequences that are between big dynamic sequences
    #+----------------------------------------------
    def slickRegexes(self, button, ui):
        for group in self.getGroups():
            group.slickRegex()
        ui.update()

    #+---------------------------------------------- 
    #| mergeCommonRegexes:
    #|  try to merge identical regexes
    #+----------------------------------------------
    def mergeCommonRegexes(self, button, ui):
        self.log.info("Merging not implemented yet")

    #+---------------------------------------------- 
    #| findSizeField:
    #|  try to find the size field of each regex
    #+----------------------------------------------    
    def findSizeFields(self, store):
        for group in self.getGroups():
            group.findSizeFields(store)

    #+---------------------------------------------- 
    #| dataCarvingResults:
    #|  try to find the data hidden in the messages
    #+----------------------------------------------    
    def dataCarvingResults(self):
        notebook = gtk.Notebook()
        notebook.show()
        notebook.set_tab_pos(gtk.POS_TOP)
        for group in self.getGroups():
            scroll = group.dataCarving()
            if scroll != None:
                notebook.append_page(scroll, gtk.Label(group.getName()))
        return notebook

    #+---------------------------------------------- 
    #| searchView:
    #|  search data in messages, for each group
    #+----------------------------------------------    
    def searchView(self):
        hbox = gtk.HBox(False, spacing=5)
        hbox.show()

        ## Search form
        vbox = gtk.VBox(False, spacing=5)
        vbox.show()
        hbox.pack_start(vbox, False, False, 0)
        entry = gtk.Entry()
        entry.show()
        vbox.pack_start(entry, False, False, 0)
        but = gtk.Button("Search")
        but.show()
        vbox.pack_start(but, False, False, 0)

        ## Notebook for the results per groups
        notebook = gtk.Notebook()
        but.connect("clicked", self.search_cb, entry, notebook)
        hbox.pack_start(notebook, False, False, 0)
        notebook.show()
        notebook.set_tab_pos(gtk.POS_TOP)
        return hbox

    #+---------------------------------------------- 
    #| search_cb:
    #|  launch the search
    #+----------------------------------------------    
    def search_cb(self, but, entry, notebook):
        if entry.get_text() == "":
            return

        # Clear the notebook
        for i in range(notebook.get_n_pages()):
            notebook.remove_page(i)

        # Fill the notebook
        for group in self.getGroups():
            vbox = group.search( entry.get_text() )
            if vbox != None:
                notebook.append_page(vbox, gtk.Label(group.getName()))

    #+---------------------------------------------- 
    #| GETTERS :
    #+----------------------------------------------    
    def getGroups(self):
        return self.groups

    #+---------------------------------------------- 
    #| SETTERS :
    #+----------------------------------------------    
    def setGroups(self, groups):
        self.groups = groups
