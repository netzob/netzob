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
import logging
import gtk
import pygtk
pygtk.require('2.0')

#+---------------------------------------------- 
#| Local Imports
#+----------------------------------------------
from ..Common import ConfigurationParser
from Searcher import Searcher

#+---------------------------------------------- 
#| Configuration of the logger
#+----------------------------------------------
loggingFilePath = ConfigurationParser.ConfigurationParser().get("logging", "path")
logging.config.fileConfig(loggingFilePath)

#+---------------------------------------------- 
#| SearchView :
#|     Class dedicated to host the search view
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.2
#+---------------------------------------------- 
class SearchView(object):
    
    #+---------------------------------------------- 
    #| Constructor :
    #+----------------------------------------------   
    def __init__(self, messages):
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Modelization.SearchView.py')
        self.messages = messages
    
    def getPanel(self):
        # Create the main panel
        panel = gtk.Table(rows=2, columns=3, homogeneous=False)
        panel.show()
        
        # Create the header (first row) with the search form
        # Search entry
        self.searchEntry = gtk.Entry()
        self.searchEntry.show()
        
        # Combo to select the type of the input
        self.typeCombo = gtk.combo_box_entry_new_text()
        self.typeCombo.show()
        self.typeStore = gtk.ListStore(str)
        self.typeCombo.set_model(self.typeStore)
        self.typeCombo.get_model().append(["Binary"])
        self.typeCombo.get_model().append(["Octal"])
        self.typeCombo.get_model().append(["Hexadecimal"])
        self.typeCombo.get_model().append(["ASCII"])
        self.typeCombo.get_model().append(["IP"])
        
        # Search button        
        searchButton = gtk.Button("Search")
        searchButton.show()
        searchButton.connect("clicked", self.prepareSearchingOperation)

        panel.attach(self.searchEntry, 0, 1, 0, 1, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        panel.attach(self.typeCombo, 1, 2, 0, 1, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        panel.attach(searchButton, 2, 3, 0, 1, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        
        return panel
    
    def prepareSearchingOperation(self, button):
        
        searchedPattern = self.searchEntry.get_text()
        if len(searchedPattern) == 0 :
            self.log.info("Do not start the searching process since no pattern was provided by the user")
            return
        
        typeOfPattern = self.typeCombo.get_active_text()
        if len(typeOfPattern) == 0 :
            self.log.info("Do not start the searching process since no type was provided by the user")
            return        
        
        self.log.debug("User searches for " + searchedPattern + " of type " + typeOfPattern)        
        self.search(searchedPattern, typeOfPattern)
        
    def search(self, pattern, typeOfPattern):
        
        # Initialize the searcher
        searcher = Searcher(self.messages)
        
        if typeOfPattern == "IP" :
            searcher.searchIP(pattern)
        elif typeOfPattern == "Binary":
            searcher.searchBinary(pattern)
        elif typeOfPattern == "Octal":
            searcher.searchOctal(pattern)
        elif typeOfPattern == "Hexadecimal":
            searcher.searchHexdecimal(pattern)
        elif typeOfPattern == "ASCII":
            searcher.searchASCII(pattern)
        else :
            self.log.warn("The provided type of the searched pattern is not yet supported")
        
        
        
        


