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
#| TreeMessageGenerator :
#|     update and generates the treeview and its 
#|     treestore dedicated to the messages
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.2
#+---------------------------------------------- 
class TreeMessageGenerator():
    
    #+---------------------------------------------- 
    #| Constructor :
    #| @param vbox : where the treeview will be hold
    #+---------------------------------------------- 
    def __init__(self):
        self.group = None
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Modelization.TreeStores.TreeMessageGenerator.py')
   
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
        column = gtk.TreeViewColumn('Messages')
        column.pack_start(cell, True)
        column.set_attributes(cell, text=0)
        column.set_attributes(cell, markup=0)
        self.treeview.append_column(column)
        self.treeview.show()
        self.treeview.set_reorderable(True)
        self.treeview.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
        self.scroll = gtk.ScrolledWindow()
        self.scroll.set_size_request(-1, 200)
        self.scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)        
        self.scroll.add(self.treeview)
        self.scroll.show()

    #+---------------------------------------------- 
    #| clear :
    #|         Clear the class
    #+---------------------------------------------- 
    def clear(self):
        self.group = None
        self.treestore.clear()
        
    #+---------------------------------------------- 
    #| error :
    #|         Update the treestore in error mode
    #+---------------------------------------------- 
    def error(self):
        self.log.warning("The treeview for the messages is in error mode")      
        self.treestore.clear()
    
    #+---------------------------------------------- 
    #| default :
    #|         Update the treestore in normal mode
    #+---------------------------------------------- 
    def default(self, group):
        self.group = group
        self.log.debug("Updating the treestore of the messages in default mode with the messages from the group "+self.group.getName())
        self.treestore.clear()

        # Verifies we have everything needed for the creation of the treeview
        if (self.group == None or len(self.group.getMessages())<1) or len(self.group.getColumns()) == 0 :
            self.error()
            return

        # Create a TreeStore with N cols, with N := len(self.group.getColumns())
        treeStoreTypes = [str, str, int, gobject.TYPE_BOOLEAN]
        for i in range( len(self.group.getColumns()) ):
            treeStoreTypes.append(str)
        self.treestore = gtk.TreeStore(*treeStoreTypes)

        # Build the name row
        name_line = []
        name_line.append("HEADER NAME")
        name_line.append("#ababab")
        name_line.append(pango.WEIGHT_BOLD)
        name_line.append(True)
        for col in self.group.getColumns():
            name_line.append( col['name'] )
        self.treestore.append(None, name_line)

        # Build the regex row
        regex_row = []
        regex_row.append("HEADER REGEX")
        regex_row.append("#c8c8c8")
        regex_row.append(pango.WEIGHT_BOLD)
        regex_row.append(True)
        for iCol in range(len(self.group.getColumns())):
            if self.group.isRegexStatic( self.group.getRegexByCol(iCol) ):
                regex_row.append( self.group.getRepresentation( self.group.getRegexByCol(iCol), iCol ))
            else:
                regex_row.append( self.group.getRegexByCol(iCol) )
        self.treestore.append(None, regex_row)

        # Build the types row
        types_line = []
        types_line.append("HEADER TYPE")
        types_line.append("#DEDEDE")
        types_line.append(pango.WEIGHT_BOLD)
        types_line.append(True)        
        for iCol in range(len( self.getGroup().getColumns() )):
            types_line.append( self.getGroup().getStyledPossibleTypesByCol(iCol) )
        self.treestore.append(None, types_line)
        
        # Build the next rows from messages after applying the regex
        for message in self.group.getMessages():
            # for each message we create a line and computes its cols
            line = []
            line.append(message.getID())
            line.append("#ffffff")
            line.append(pango.WEIGHT_NORMAL)
            line.append(False)
            line.extend( message.applyRegex(styled=True, encoded=True) )
            self.treestore.append(None, line)

        # Remove all the columns of the current treeview
        for col in self.treeview.get_columns() :
            self.treeview.remove_column(col)
            
        for iCol in range(4, 4 + len(self.group.getColumns()) ) :
            # Define cellRenderer object
            textCellRenderer = gtk.CellRendererText()
            textCellRenderer.set_property('background-set' , True)
            textCellRenderer.connect('edited', self.column_renaming_cb, iCol - 4)
            # Column Messages
            lvcolumn = gtk.TreeViewColumn('Col'+str(iCol - 4))
            lvcolumn.pack_start(textCellRenderer, True)
            lvcolumn.set_attributes(textCellRenderer, markup=iCol, background=1, weight=2, editable=3)
            self.treeview.append_column(lvcolumn)
        self.treeview.set_model(self.treestore)

    def column_renaming_cb(self, cell, path_string, new_text, iCol):
        print "2"
        self.treestore[path_string][iCol + 4] = new_text
        self.group.setColumnNameByCol(iCol, new_text)

    def updateDefault(self):
        self.default(self.group)
    
    #+---------------------------------------------- 
    #| GETTERS : 
    #+----------------------------------------------
    def getTreeview(self):
        return self.treeview

    def getScrollLib(self):
        return self.scroll

    def getGroup(self):
        return self.group
