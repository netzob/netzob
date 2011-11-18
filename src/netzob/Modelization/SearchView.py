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
        self.panel = gtk.Table(rows=3, columns=3, homogeneous=False)
        self.panel.show()
        
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

        self.panel.attach(self.searchEntry, 0, 1, 0, 1, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        self.panel.attach(self.typeCombo, 1, 2, 0, 1, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        self.panel.attach(searchButton, 2, 3, 0, 1, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        
        return self.panel
    
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
        
        searchResults = []
        if typeOfPattern == "IP" :
            searchResults = searcher.searchIP(pattern)
        elif typeOfPattern == "Binary":
            searchResults = searcher.searchBinary(pattern)
        elif typeOfPattern == "Octal":
            searchResults = searcher.searchOctal(pattern)
        elif typeOfPattern == "Hexadecimal":
            searchResults = searcher.searchHexadecimal(pattern)
        elif typeOfPattern == "ASCII":
            searchResults = searcher.searchASCII(pattern)
        else :
            self.log.warn("The provided type of the searched pattern is not yet supported")
        
        self.log.debug("A number of " + str(len(searchResults)) + " results were found")
        
        self.updateView(searchResults)
        
    def updateView(self, results):
        
        self.tree = gtk.TreeView()
        
        colResult = gtk.TreeViewColumn()
        colResult.set_title("Search results")
 
        cell = gtk.CellRendererText()
        colResult.pack_start(cell, True)
        colResult.add_attribute(cell, "text", 0)
 
        treestore = gtk.TreeStore(str)
        
        
        for result in results :
            it = treestore.append(None, [result.getGroup().getName()])
            it2 = treestore.append(it, [result.getMessage().getID()])
            treestore.append(it2, [result.getStringResult()])
 
#        it = treestore.append(None, ["Groupe REQUEST"])
#        it2 = treestore.append(it, ["Message 1"])
#        treestore.append(it2, ["3273787382737277323223782988083987265325436"])
#        it2 = treestore.append(it, ["Message 2"])
#        treestore.append(it2, ["3273787382737277323223782988083987265325436"])
# 
#        it = treestore.append(None, ["Groupe RESPONSE"])
#        it2 = treestore.append(it, ["Message 1"])
#        treestore.append(it2, ["3273787382737277323223782988083987265325436"])
#        it2 = treestore.append(it, ["Message 2"])
#        treestore.append(it2, ["3273787382737277323223782988083987265325436"])
 
        self.tree.append_column(colResult)
        self.tree.set_model(treestore)
        self.tree.show()
        
        self.panel.attach(self.tree, 0, 3, 1, 2, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
            
        
        
        


