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
from netzob.Common.Field import Field

#+---------------------------------------------- 
#| Local Imports
#+----------------------------------------------

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
        self.symbol = None
        self.message = None
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Modelization.TreeViews.TreeTypeStructureGenerator.py')
   
    #+---------------------------------------------- 
    #| initialization :
    #| builds and configures the treeview
    #+----------------------------------------------     
    def initialization(self):
        # creation of the treestore
        self.treestore = gtk.TreeStore(int, str, str, str) # iCol, Name, Data, Description
        # creation of the treeview   
        self.treeview = gtk.TreeView(self.treestore)
        self.treeview.set_reorderable(True)
        # Creation of a cell rendered and of a column
        cell = gtk.CellRendererText()
        columns = ["iCol", "Name", "Value", "Description"]
        for i in range(1, len(columns)):
            column = gtk.TreeViewColumn(columns[i])
            column.pack_start(cell, True)
            column.set_attributes(cell, markup=i)
            self.treeview.append_column(column)
        self.treeview.show()
        self.treeview.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
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
        self.symbol = None
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
    def update(self):
        if self.getSymbol() == None or self.getMessage() == None:
            self.clear()
            return

        splittedMessage = self.getMessage().applyRegex(styled=True, encoded=True)

        if str(self.message.getID).find("HEADER") != -1:
            self.clear()
            return

        self.treestore.clear()

        for field in self.getSymbol().getFields():
            tab = ""
            for k in range(field.getEncapsulationLevel()):
                tab += " "
            messageElt = splittedMessage[field.getNumber()]
            if not field.isRegexStatic():
                self.treestore.append(None, [field.getNumber(), tab + field.getName() + ":", field.getRegex() + " / " + messageElt, field.getDescription()])
            else:
                self.treestore.append(None, [field.getNumber(), tab + field.getName() + ":", messageElt, field.getDescription()])

    #+---------------------------------------------- 
    #| GETTERS : 
    #+----------------------------------------------
    def getTreeview(self):
        return self.treeview
    def getScrollLib(self):
        return self.scroll
    def getSymbol(self):
        return self.symbol
    def getMessage(self):
        return self.message

    #+---------------------------------------------- 
    #| SETTERS : 
    #+----------------------------------------------
    def setTreeview(self, treeview):
        self.treeview = treeview
    def setScrollLib(self, scroll):
        self.scroll = scroll
    def setSymbol(self, symbol):
        self.symbol = symbol
    def setMessage(self, message):
        self.message = message
    def setMessageByID(self, message_id):
        self.message = self.symbol.getMessageByID(message_id)

