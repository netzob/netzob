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
        self.content = None
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
        cell = gtk.CellRendererText()
        column = gtk.TreeViewColumn('Messages')
        column.pack_start(cell, True)
        column.set_attributes(cell, text=0)
        column.set_attributes(cell, markup=0)
        self.treeview.append_column(column)
        self.treeview.show()
        self.scroll = gtk.ScrolledWindow()
        self.scroll.set_size_request(1000, 500)
        self.scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)        
        self.scroll.add(self.treeview)
        self.scroll.show()
        
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
        if (self.group == None or len(self.group.getMessages())<1) or len(self.group.getRegex()) == 0 :
            self.error()
            return
        
        # configuration of the representation format
        # default = binary
        for i in range(0, len(self.group.getRegex())) :
            self.group.selectedType.append("binary")
        
        # Create a TreeStore with N cols, with N := len(self.group.getRegex())
        treeStoreTypes = [str, str, int, gobject.TYPE_BOOLEAN]
        for i in range( len(self.group.getRegex()) ):
            treeStoreTypes.append(str)           
        self.treestore = gtk.TreeStore(*treeStoreTypes)
        
        
        
        compiledRegex = re.compile("".join( self.group.getRegex() ))

        self.group.msgByCol = {}

        # Apply the content matrix to the treestore
        for i in range(0, len(self.group.getMessages())) :
            message = self.group.getMessages()[i]

            # for each message we create a line and computes its cols
            line = []
            line.append(message.getID())
            line.append("#ffffff")
            line.append(pango.WEIGHT_NORMAL)
            line.append(False)

            # We apply the regex to the message
            data = message.getStringData()
            
            self.log.warning("DATA : "+data)
            self.log.warning("R-DATA : "+message.getReducedStringData())
            
            
            m = compiledRegex.match(data)

            # If the regex doesn't match the message, we activate the error mode
            if (m == None) :
                self.log.warning("The regex of the group doesn't match the message : " + data)
                self.log.warning("The regex of the group is : " + "".join(self.group.getRegex()))
                self.error()
                return 
            
            iCol = 0
            dynamicCol = 1
            for regexElt in self.group.getRegex():
                # (init) Aggregate the cells content to a structure dedicacted to identify the column type
                if not iCol in self.group.msgByCol:
                    self.group.msgByCol[iCol] = []

                # Append styled data to the treestore
                if regexElt.find("(") != -1: # Means this column is not static
                    start = m.start(dynamicCol)
                    end = m.end(dynamicCol)
                    line.append('<span foreground="blue" font_family="monospace">' + self.group.getRepresentation( data[start:end], iCol ) + '</span>')
                    self.group.msgByCol[iCol].append( data[start:end] )
                    dynamicCol += 1
                else:
                    line.append('<span font_family="monospace">' + self.group.getRepresentation( regexElt, iCol ) + '</span>')
                    self.group.msgByCol[iCol].append( regexElt )

                iCol = iCol + 1
            self.treestore.append(None, line)
      
        # Creates the header (a line with the type displayed)
        header_line = []
        header_line.append("HEADER TYPE")
        header_line.append("#DEDEDE")
        header_line.append(pango.WEIGHT_BOLD)
        header_line.append(True)        

        # Get the possible types of each column
        for iCol in range( len(self.group.getRegex()) ):
            header_line.append(", ".join(self.group.getAllDiscoveredTypes(iCol)))
        self.treestore.prepend(None, header_line)

        # Creates the header line for the regex
        regex_row = []
        regex_row.append("HEADER REGEX")
        regex_row.append("#c8c8c8")
        regex_row.append(pango.WEIGHT_BOLD)
        regex_row.append(True)

        # Get the Sub-Regex of each column
        for iCol in range( len(self.group.getRegex()) ):
            # Split the regex (this is scrapy...)
            tmpRegex = self.group.getRegex()[iCol]
            if len(tmpRegex) > 0 and tmpRegex[0] == "(": # Means a complex regex (static + dyn)
                tmpRegex = tmpRegex[1:-1] # We exclude the parenthesis

            splittedRegex = re.findall('(,?[0-9a-f]+)', self.group.getRegex()[iCol])

            resRegex = ""
            for elt in splittedRegex:
                if elt[0] == ",":
                    resRegex += ".{" + elt + "}"
                else:
                    resRegex += self.group.getRepresentation( elt, iCol )
            regex_row.append( resRegex )
        self.treestore.prepend(None, regex_row)

        # Creates the header for naming the column
        name_line = []
        name_line.append("HEADER TYPE")
        name_line.append("#ababab")
        name_line.append(pango.WEIGHT_BOLD)
        name_line.append(True)        

        # Get the possible types of each column
        for iCol in range( len(self.group.getRegex()) ):
            name_line.append("Name")
        self.treestore.prepend(None, name_line)

        # Remove all the columns of the current treeview
        for col in self.treeview.get_columns() :
            self.treeview.remove_column(col)
            
        # Define cellRenderer objects
        self.textCellRenderer = gtk.CellRendererText()
        self.textCellRenderer.set_property('background-set' , True)

        for i in range(4, 4 + len(self.group.getRegex()) ) :
            # Column Messages
            lvcolumn = gtk.TreeViewColumn('Col'+str(i-4))
            lvcolumn.pack_start(self.textCellRenderer, True)
            lvcolumn.set_attributes(self.textCellRenderer, markup=i, background=1, weight=2, editable=3)
            self.treeview.append_column(lvcolumn)

                 
        # Updates the treeview with the newly created treestore
        self.treeview.set_model(self.treestore)
        self.treeview.set_reorderable(True)

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
