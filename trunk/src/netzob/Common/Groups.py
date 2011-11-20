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
import logging
import gtk
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
#loggingFilePath = ConfigurationParser.ConfigurationParser().get("logging", "path")
#logging.config.fileConfig(loggingFilePath)

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
        self.setGroups(tracesExtractor.parse())
        self.netzob.update()

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
    #| envDependenciesResults:
    #|  try to find the environmental dependencies
    #+----------------------------------------------    
    def envDependenciesResults(self):
        notebook = gtk.Notebook()
        notebook.show()
        notebook.set_tab_pos(gtk.POS_TOP)
        for group in self.getGroups():
            scroll = group.envDependencies()
            if scroll != None:
                notebook.append_page(scroll, gtk.Label(group.getName()))
        return notebook

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
            vbox = group.search(entry.get_text())
            if vbox != None:
                notebook.append_page(vbox, gtk.Label(group.getName()))

    #+---------------------------------------------- 
    #| Groups management :
    #+----------------------------------------------    
    def addGroup(self, group):
        self.groups.append(group)

    def removeGroup(self, group):
        self.groups.remove(group)
    #+---------------------------------------------- 
    #| getMessageByID:
    #|     Retrieves the message given its ID
    #| @param id_message the id of the message to retrieve
    #| @return the message or None if not found
    #+----------------------------------------------    
    def getMessageByID(self, id_message):
        for group in self.getGroups() :
            for msg in group.getMessages() :
                if str(msg.getID()) == id_message :
                    return msg
        return None
    #+---------------------------------------------- 
    #| getMessages:
    #|     Retrieves all the messages
    #| @param id_message the id of the message to retrieve
    #| @return the message or None if not found
    #+----------------------------------------------                   
    def getMessages(self):
        messages = []
        for group in self.getGroups() :
            for msg in group.getMessages() :
                messages.append(msg)
        
        return messages


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
