#!/usr/bin/python
# coding: utf8

#+---------------------------------------------- 
#| Global Imports
#+----------------------------------------------
import logging
import gtk

#+---------------------------------------------- 
#| Local Imports
#+----------------------------------------------
from ...Common import ConfigurationParser
from ..NeedlemanWunsch import NeedlemanWunsch

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
        self.log = logging.getLogger('netzob.Sequencing.TreeStores.TreeGroupGenerator.py')
    
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
        self.treestore = gtk.TreeStore(str, str, str, str)
        self.treeview  = gtk.TreeView(self.treestore)

        # messages list
        self.scroll_lib = gtk.ScrolledWindow()
        self.scroll_lib.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.scroll_lib.show()
        self.scroll_lib.set_size_request(500, 500)
        self.scroll_lib.add(self.treeview)        
        
        

        lvcolumn = gtk.TreeViewColumn('Messages')
        lvcolumn.set_sort_column_id(1)
        cell1 = gtk.CellRendererText()
        lvcolumn.pack_start(cell1, True)
        cell1.set_property('background-set' , True)
        cell1.set_property('foreground-set' , True)            
        lvcolumn.set_attributes(cell1, text=0, foreground=2, background=3)
        self.treeview.append_column(lvcolumn)
        self.treeview.show()
    
    
    #+---------------------------------------------- 
    #| default :
    #|         Update the treestore in normal mode
    #+---------------------------------------------- 
    def default(self):
        self.log.debug("Updating the treestore of the group in default mode")        
        self.treestore.clear()
        for group in self.groups :
            iter = self.treestore.append(None, ["{0}".format(group.getName()),"{0}".format(group.getScore()), '#000000', '#FF00FF'])
           

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
                iter = self.treestore.append(None, ["{0}".format(group.getName()),"{0}".format(group.getScore()), '#000000', color])
    
    
    
    #+---------------------------------------------- 
    #| GETTERS : 
    #+----------------------------------------------
    def getTreeview(self):
        return self.treeview
    def getScrollLib(self):
        return self.scroll_lib
    
        