#!/usr/bin/python
# coding: utf8

#+---------------------------------------------- 
#| Global Imports
#+----------------------------------------------
import logging
import re
import pango
import gobject
import gtk
from numpy.core.numeric import zeros

#+---------------------------------------------- 
#| Local Imports
#+----------------------------------------------
from ...Common import ConfigurationParser
from ...Common import TypeIdentifier
from ..Message import Message

#+---------------------------------------------- 
#| Configuration of the logger
#+----------------------------------------------
loggingFilePath = ConfigurationParser.ConfigurationParser().get("logging", "path")
logging.config.fileConfig(loggingFilePath)

#+---------------------------------------------- 
#| TreeTypeStructureGenerator :
#|     update and generates the treeview and its 
#|     treestore dedicated to the type structure
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.2
#+---------------------------------------------- 
class TreeTypeStructureGenerator():
    
    #+---------------------------------------------- 
    #| Constructor :
    #| @param vbox : where the treeview will be hold
    #+---------------------------------------------- 
    def __init__(self):
        self.group = None
        self.message = None
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Sequencing.TreeViews.TreeTypeStructureGenerator.py')
   
    #+---------------------------------------------- 
    #| initialization :
    #| builds and configures the treeview
    #+----------------------------------------------     
    def initialization(self):
        # creation of the treestore
        self.treestore = gtk.TreeStore(str, str, str)     
        # creation of the treeview   
        self.treeview = gtk.TreeView(self.treestore)
        self.treeview.set_reorderable(True)
        # Creation of a cell rendered and of a column
        cell = gtk.CellRendererText()
        columns = ["Name", "Value", "Description"]
        for i in range(len(columns)):
            column = gtk.TreeViewColumn(columns[i])
            column.pack_start(cell, True)
            column.set_attributes(cell, markup=i)
            self.treeview.append_column(column)
        self.treeview.show()
        self.scroll = gtk.ScrolledWindow()
#        self.scroll.set_size_request(1000, 500)
        self.scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)        
        self.scroll.add(self.treeview)
        self.scroll.show()

    #+---------------------------------------------- 
    #| clear :
    #|         Clear the class
    #+---------------------------------------------- 
    def clear(self):
        self.group = None
        self.message = None
        self.treestore.clear()
        
    #+---------------------------------------------- 
    #| error :
    #|         Update the treestore in error mode
    #+---------------------------------------------- 
    def error(self):
        self.log.warning("The treeview for the messages is in error mode")      
        pass
    
    #+---------------------------------------------- 
    #| default :
    #|         Update the treestore in normal mode
    #+---------------------------------------------- 
    def default(self):
        pass

    def buildTypeStructure(self):
        if self.getGroup() == None or self.getMessage() == None:
            self.clear()
            return

        splittedMessage = self.getMessage().applyRegex(styled=True, encoded=True)

        if str(self.message.getID).find("HEADER") != -1:
            self.clear()
            return

        self.treestore.clear()
        iCol = 0
        for col in self.getGroup().getColumns():
            tab = ""
            for k in range(int(col['tabulation'])):
                tab += " "
            messageElt = splittedMessage[iCol]
            if col['regex'].find("{") != -1:
                iter = self.treestore.append(None, [tab + col['name'] + ":", col['regex'] + " / " + messageElt, col['description']])
            else:
                iter = self.treestore.append(None, [tab + col['name'] + ":", col['regex'], col['description']])
            iCol += 1

    #+---------------------------------------------- 
    #| GETTERS : 
    #+----------------------------------------------
    def getTreeview(self):
        return self.treeview
    def getScrollLib(self):
        return self.scroll
    def getGroup(self):
        return self.group
    def getMessage(self):
        return self.message

    #+---------------------------------------------- 
    #| SETTERS : 
    #+----------------------------------------------
    def setTreeview(self, treeview):
        self.treeview = treeview
    def setScrollLib(self, scroll):
        self.scroll = scroll
    def setGroup(self, group):
        self.group = group
    def setMessage(self, message):
        self.message = message
    def setMessageByID(self, message_id):
        self.message = self.group.getMessageByID(message_id)

