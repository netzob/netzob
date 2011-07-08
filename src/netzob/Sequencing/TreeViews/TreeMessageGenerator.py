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
from ..NeedlemanWunsch import NeedlemanWunsch

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
    def __init__(self, vbox):
        self.vbox = vbox
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Sequencing.TreeStores.TreeMessageGenerator.py')
   
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
        self.cell = gtk.CellRendererText()
        self.column = gtk.TreeViewColumn('Messages')
        self.column.pack_start(self.cell, True)
        self.column.set_attributes(self.cell, text=0)
        self.column.set_attributes(self.cell, markup=0)
        self.treeview.append_column(self.column)
        
        self.treeview.show()
        
        self.scroll_lib = gtk.ScrolledWindow()
        self.scroll_lib.set_size_request(1000, 500)
        self.scroll_lib.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)        
        self.scroll_lib.add(self.treeview)
        self.scroll_lib.show()
    
    #+---------------------------------------------- 
    #| default :
    #|         Update the treestore in normal mode
    #+---------------------------------------------- 
    def default(self, group):
        self.group = group
        self.log.debug("Updating the treestore of the messages in default mode with the messages from the group "+self.group.getName())        
        self.treestore.clear()
        
        # Compile the regex (in order to prepare to the identification of groups in the messages)
        compiledRegex = re.compile(self.group.getRegex())
        
        # the maximum number of groups per message (eq. the nb of displayed cols)
        numberOfGroup = -1
        
        # Matrix (2D array) incluing the content of the treestore
        matchMessages = []
        aggregatedValuesPerCol = {}
        
        # Apply the regex to each message in order to compute the groups
        for message in self.group.getMessages() :
            data = message.getStringData()                    
            m = compiledRegex.match(data)
            if (m == None) :
                self.log.warning("The regex of the group doesn't match one of its message ! ("+data+")")
                return 
            
            # compute the number of group in this message in order to compute the maximum
            if numberOfGroup < len(m.groups()) :
                numberOfGroup = len(m.groups())
            
            # for each message we create a line and computes its cols
            line = []
            line.append(message.getID())
            line.append("#ffffff")
            line.append(pango.WEIGHT_NORMAL)
            line.append(False)
            
            # create a col for each group of the regex
            current = 0
            k=0
            for i_group in range(1, len(m.groups())+1) :
                start = m.start(i_group)
                end = m.end(i_group)
                line.append('<span>' + data[current:start] + '</span>')
                line.append('<span foreground="blue" font_family="monospace">' + data[start:end] + '</span>')
                current = end
                if not k in aggregatedValuesPerCol:
                    aggregatedValuesPerCol[k] = []
                aggregatedValuesPerCol[k].append( data[current:start] )
                k += 1
                if not k in aggregatedValuesPerCol:
                    aggregatedValuesPerCol[k] = []
                aggregatedValuesPerCol[k].append( data[start:end] )
                k += 1
            line.append('<span >' + data[current:] + '</span>')
            
            if not k in aggregatedValuesPerCol:
                aggregatedValuesPerCol[k] = []
            aggregatedValuesPerCol[k].append( data[current:] )
            
            matchMessages.append(line)
            
            # create a TreeStore with N cols, with := (maxNumberOfGroup * 2 + 1)
            treeStoreTypes = [str, str, int, gobject.TYPE_BOOLEAN]
            for i in range( numberOfGroup * 2 + 1):
                treeStoreTypes.append(str)
            
            # Creates a new treestore
            self.treestore = gtk.TreeStore(*treeStoreTypes)
            
            # Updates the treeview with good treestore
            self.treeview.set_model(self.treestore)
            self.treeview.set_reorderable(True)

            # set the content in the treestore
            for i in range(len(matchMessages)):
                self.treestore.append(None, matchMessages[i])
                
            # Type and Regex headers
            ## TODO : divide the regex numbers by 2
            hdr_row = []
            hdr_row.append("HEADER TYPE")
            hdr_row.append("#00ffff")
            hdr_row.append(pango.WEIGHT_BOLD)
            hdr_row.append(True)

            for i in range( len(aggregatedValuesPerCol) ):
                # Identify the type from the strings of the same column
                typesList = TypeIdentifier.TypeIdentifier().getType(aggregatedValuesPerCol[i])
                hdr_row.append( typesList );
            
            self.treestore.prepend(None, hdr_row)
            splittedRegex = re.findall("(\(\.\{\d*,\d*\}\))", self.group.getRegex())

            regex_row = []
            regex_row.append("HEADER REGEX")
            regex_row.append("#00ffff")
            regex_row.append(pango.WEIGHT_BOLD)
            regex_row.append(True)

            for i in range(len(splittedRegex)):
                regex_row.append("")
                # Get the Regex of the current column
                regex_row.append(splittedRegex[i][1:-1])
            
            for i in range((numberOfGroup * 2 + 1 + 4) - len(regex_row)):
                regex_row.append("")
            
            self.treestore.prepend(None, regex_row)
            
            # columns handling
            # remove all the colomns
            for col in self.treeview.get_columns() :
                self.treeview.remove_column(col)
            self.log.debug("test")
            # Define cellRenderer objects
            self.cellDetail2 = gtk.CellRendererText()
            self.cellDetail2.set_property('background-set' , True)

            for i in range(4, 4 + (numberOfGroup * 2) + 1) :
                # Column Messages
                self.lvcolumnDetail2 = gtk.TreeViewColumn('Col'+str(i))
                self.lvcolumnDetail2.pack_start(self.cellDetail2, True)
                self.lvcolumnDetail2.set_attributes(self.cellDetail2, markup=i, background=1, weight=2, editable=3)
                self.treeview.append_column(self.lvcolumnDetail2)

        
    #+---------------------------------------------- 
    #| GETTERS : 
    #+----------------------------------------------
    def getTreeview(self):
        return self.treeview
    def getScrollLib(self):
        return self.scroll_lib