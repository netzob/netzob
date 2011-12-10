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
import gtk
import pygtk
import logging
pygtk.require('2.0')

#+---------------------------------------------- 
#| Local Imports
#+----------------------------------------------
from netzob.Export.TreeViews.TreeGroupGenerator import TreeGroupGenerator

#+---------------------------------------------- 
#| RawExport :
#|     GUI for exporting results in raw mode
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.2
#+---------------------------------------------- 
class RawExport:

    #+---------------------------------------------- 
    #| Called when user select a new trace
    #+----------------------------------------------
    def new(self):
        pass

    def update(self):
        self.treeGroupGenerator.update()
    
    def clear(self):
        pass

    def kill(self):
        pass
    
    #+---------------------------------------------- 
    #| Constructor :
    #| @param netzob: the main netzob object
    #+----------------------------------------------   
    def __init__(self, netzob):
        self.netzob = netzob
        self.log = logging.getLogger('netzob.Export.RawExport.py')
        
        self.init()
        
        self.dialog = gtk.Dialog(title="Export project as raw XML", flags=0, buttons=None)
        self.dialog.show()
        self.dialog.vbox.pack_start(self.getPanel(), True, True, 0)
        self.dialog.set_size_request(800, 700)
        self.update()
        
    def init (self):
        
        self.selectedGroup = None
        
        # First we create an VPaned which hosts the two main children
        self.panel = gtk.HBox()        
        self.panel.show()
        
        # Create the group selection treeview
        self.treeGroupGenerator = TreeGroupGenerator(self.netzob)
        self.treeGroupGenerator.initialization()
        self.panel.pack_start(self.treeGroupGenerator.getScrollLib(), True, True, 0)
        self.treeGroupGenerator.getTreeview().connect("cursor-changed", self.groupSelected) 
        
        # Create the hbox content in order to display dissector data
        bottomFrame = gtk.Frame()
        bottomFrame.show()
        bottomFrame.set_size_request(550, -1)
        self.panel.add(bottomFrame)
        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.textarea = gtk.TextView()
        self.textarea.get_buffer().create_tag("normalTag", family="Courier")
        self.textarea.show()
        self.textarea.set_editable(False)
        sw.add(self.textarea)
        sw.show()
        bottomFrame.add(sw)

    def groupSelected(self, treeview):
        (model, iter) = treeview.get_selection().get_selected()
        if(iter):
            if(model.iter_is_valid(iter)):
                idGroup = model.get_value(iter, 0)
                self.selectedGroup = idGroup
                self.updateTextArea()

    def updateTextArea(self):
        if self.selectedGroup == None :
            self.log.debug("No selected group")
            self.textarea.get_buffer().set_text("Select a group to see its XML definition")

        else :
            found = False
            for group in self.netzob.groups.getGroups() :
                if str(group.getID()) == self.selectedGroup :
                    self.textarea.get_buffer().set_text(group.getXMLDefinition())
                    found = True
            if found == False :
                self.log.warning("Impossible to retrieve the group having the id {0}".format(str(self.selectedGroup)))

    #+---------------------------------------------- 
    #| GETTERS
    #+----------------------------------------------
    def getPanel(self):
        return self.panel
