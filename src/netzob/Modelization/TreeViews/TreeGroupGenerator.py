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

#+---------------------------------------------- 
#| Global Imports
#+----------------------------------------------
import logging
import gtk

#+---------------------------------------------- 
#| Local Imports
#+----------------------------------------------
from ...Common import ConfigurationParser
from ...Modelization import TracesExtractor
       
#+---------------------------------------------- 
#| Configuration of the logger
#+----------------------------------------------
loggingFilePath = ConfigurationParser.ConfigurationParser().get("logging", "path")
logging.config.fileConfig(loggingFilePath)

#+---------------------------------------------- 
#| TreeStoreGroupGenerator :
#|     update and generates the treestore 
#|     dedicated to the groups
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.2
#+---------------------------------------------- 
class TreeGroupGenerator():
    
    #+---------------------------------------------- 
    #| Constructor :
    #| @param groups : the groups of messages
    #+---------------------------------------------- 
    def __init__(self, groups):
        self.groups = groups
        self.treestore = None
        self.treeview = None
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Modelization.TreeStores.TreeGroupGenerator.py')
    
    #+---------------------------------------------- 
    #| initialization :
    #| builds and configures the treeview
    #+---------------------------------------------- 
    def initialization(self):
        # Tree store contains :
        # str : text ( group Name )
        # str : text ( score )
        # str : color foreground
        # str : color background
        self.treestore = gtk.TreeStore(str, str, str, str, str)
        self.treeview  = gtk.TreeView(self.treestore)

        # messages list
        self.scroll = gtk.ScrolledWindow()
        self.scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.scroll.show()
        self.scroll.set_size_request(200, 300)
        self.scroll.add(self.treeview)        

        lvcolumn = gtk.TreeViewColumn('Groups')
        lvcolumn.set_sort_column_id(1)
        cell = gtk.CellRendererText()
        lvcolumn.pack_start(cell, True)
        cell.set_property('background-set' , True)
        cell.set_property('foreground-set' , True)            
        lvcolumn.set_attributes(cell, text=1, foreground=3, background=4)
        self.treeview.append_column(lvcolumn)
        self.treeview.show()

    #+---------------------------------------------- 
    #| clear :
    #|         Clear the class
    #+---------------------------------------------- 
    def clear(self):
        del self.groups[:]

    #+---------------------------------------------- 
    #| default :
    #|         Update the treestore in normal mode
    #+---------------------------------------------- 
    def default(self):
        self.log.debug("Updating the treestore of the group in default mode")        
        self.treestore.clear()
        for group in self.groups :
            iter = self.treestore.append(None, ["{0}".format(group.getID()),"{0}".format(group.getName()),"{0}".format(group.getScore()), '#000000', '#FF00FF'])

    #+---------------------------------------------- 
    #| messageSelected :
    #|         Update the treestore when a message
    #|         is a selected
    #| @param selectedMessage the selected message
    #+---------------------------------------------- 
    def messageSelected(self, selectedMessage):
        self.log.debug("Updating the treestore of the group with a selected message")
        self.treestore.clear()
        for group in self.groups :
            tmp_sequences = []
            if (len(group.getRegex())>0) :
                    tmp_sequences.append(group.getRegex())

            tmp_sequences.append(self.selectedMessage.getStringData())
            tmp_alignator = NeedlemanWunsch()

            tmp_score = group.getScore()
            if (len(tmp_sequences)>=2) :
                tmp_regex = tmp_alignator.getRegex(tmp_sequences)
                tmp_score = tmp_alignator.computeScore(tmp_regex)
            if (tmp_score >= group.getScore()):
                color = '#66FF00'
            else :
                color = '#FF0000'
                iter = self.treestore.append(None, ["{0}".format(group.getID()),"{0}".format(group.getName()),"{0}".format(group.getScore()), '#000000', color])
    
    #+---------------------------------------------- 
    #| getGroupAtPosition :
    #|         retrieves the group wich is inserted
    #|         in the treeview at the given position
    #| @param x the position in X
    #| @param y the position in Y
    #| @return the group if it exists (or None)
    #+---------------------------------------------- 
    def getGroupAtPosition(self, x, y):
        self.log.debug("Search for the group referenced at position {0};{1}".format(str(x),str(y)))
        info = self.treeview.get_path_at_pos(x, y)
        if info is not None :
            path = info[0]
            iter = self.treeview.get_model().get_iter(path)
            idGroup = str(self.treeview.get_model().get_value(iter, 0))
            if idGroup is not None :
                self.log.debug("An entry with the ID {0} has been found.".format(idGroup))                
                for group in self.groups :
                    if (str(group.getID()) == idGroup) :
                        self.log.debug("The requested group with ID {0} has been found".format(group.getID()))
                        return group
        return None

    def initTreeGroupWithTraces(self, zob, ui):
        tracesExtractor = TracesExtractor.TracesExtractor(zob)
        self.setGroups(  tracesExtractor.parse() )
        ui.update()

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
    #| select_group_by_id:
    #|  Select the given group in the treestore
    #+----------------------------------------------
    def select_group_by_id(self, group_id):
        it = self.treestore.get_iter_first()
        while True:
            if it == None:
                break
            tmp_group_id = self.treestore.get_value(it, 0)
            if tmp_group_id == group_id:
                self.treeview.get_selection().select_iter(it)                
                break
            it = self.treestore.iter_next(it)

    #+---------------------------------------------- 
    #| findSizeField:
    #|  try to find the size field of each regex
    #+----------------------------------------------    
    def findSizeFields(self, store):
        for group in self.getGroups():
            group.findSizeFields(store)

    #+---------------------------------------------- 
    #| dataCarving:
    #|  try to find the data hidden in the messages
    #+----------------------------------------------    
    def dataCarving(self, store):
        for group in self.getGroups():
            group.getID()


            group.dataCarving(store)
            
    #+---------------------------------------------- 
    #| GETTERS : 
    #+----------------------------------------------
    def getTreeview(self):
        return self.treeview
    def getScrollLib(self):
        return self.scroll
    def getGroups(self):
        return self.groups

    #+---------------------------------------------- 
    #| SETTERS : 
    #+----------------------------------------------    
    def setGroups(self, groups):
        self.groups = groups

