#!/usr/bin/python
# coding: utf8

#+---------------------------------------------- 
#| Global Imports
#+----------------------------------------------
import gtk
import pango
import gobject
import re
import pygtk
pygtk.require('2.0')
import logging
import threading

#+---------------------------------------------- 
#| Local Imports
#+----------------------------------------------
from ..Common import ConfigurationParser
from ..Sequencing.TreeViews import TreeGroupGenerator
from ..Sequencing.TreeViews import TreeTypeStructureGenerator

#+---------------------------------------------- 
#| Configuration of the logger
#+----------------------------------------------
loggingFilePath = ConfigurationParser.ConfigurationParser().get("logging", "path")
logging.config.fileConfig(loggingFilePath)

#+---------------------------------------------- 
#| UIfuzzing :
#|     GUI for fuzzing applications
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.2
#+---------------------------------------------- 
class UIfuzzing:
    #+---------------------------------------------- 
    #| Called when user select a new trace
    #+----------------------------------------------
    def new(self):
        pass

    def update(self):
        pass

    def clear(self):
        pass

    def kill(self):
        pass
    
    def save(self, file):
        pass

    #+---------------------------------------------- 
    #| updateGroups :
    #|  update the content of the UI with new groups
    #| @param groups: list of all groups 
    #+----------------------------------------------   
    def updateGoups(self, groups):
        self.groups = groups
        self.treeGroupGenerator.groups = self.groups
        self.treeGroupGenerator.default()
    
    #+---------------------------------------------- 
    #| Constructor :
    #| @param groups: list of all groups 
    #+----------------------------------------------   
    def __init__(self, zob):
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Sequencing.UIfuzzing.py')
        self.zob = zob
        self.groups = []
        self.selectedGroup = None
 
        self.panel = gtk.HPaned()
        self.panel.show()

        #+---------------------------------------------- 
        #| LEFT PART OF THE GUI : TREEVIEW
        #+----------------------------------------------           
        vb_left_panel = gtk.VBox(False, spacing=0)
        self.panel.add(vb_left_panel)
        vb_left_panel.set_size_request(-1, -1)
        vb_left_panel.show()

        # Initialize the treeview generator for the groups
        # Create the treeview
        self.treeGroupGenerator = TreeGroupGenerator.TreeGroupGenerator(self.groups)
        self.treeGroupGenerator.initialization()
        vb_left_panel.pack_start(self.treeGroupGenerator.getScrollLib(), True, True, 0)
        self.treeGroupGenerator.getTreeview().connect("cursor-changed", self.groupSelected) 
#        self.treeGroupGenerator.getTreeview().connect('button-press-event', self.button_press_on_treeview_groups)

        #+---------------------------------------------- 
        #| RIGHT PART OF THE GUI : TYPE STRUCTURE OUTPUT
        #+----------------------------------------------
        vb_right_panel = gtk.VBox(False, spacing=0)
        vb_right_panel.show()
        # Initialize the treeview for the type structure
        self.treeTypeStructureGenerator = TreeTypeStructureGenerator.TreeTypeStructureGenerator()
        self.treeTypeStructureGenerator.initialization()
        self.treeTypeStructureGenerator.getTreeview().connect('button-press-event', self.button_press_on_field)
        vb_right_panel.add(self.treeTypeStructureGenerator.getScrollLib())
        self.panel.add(vb_right_panel)

    def groupSelected(self, treeview):
        (model, iter) = treeview.get_selection().get_selected()
        if(iter):
            if(model.iter_is_valid(iter)):
                # Retrieve the selected group
                idGroup = model.get_value(iter, 0)
                self.selectedGroup = idGroup
                group = None
                for tmp_group in self.treeGroupGenerator.getGroups() :
                    if str(tmp_group.getID()) == idGroup :
                        group = tmp_group

                # Retrieve a random message in order to show a type structure
                message = group.getMessages()[-1]
                self.treeTypeStructureGenerator.setGroup(group)
                self.treeTypeStructureGenerator.setMessage(message)
                self.treeTypeStructureGenerator.buildTypeStructure()
                self.treeTypeStructureGenerator.default()

    #+---------------------------------------------- 
    #| button_press_on_field :
    #|   Create a menu to display available operations
    #|   on the treeview groups
    #+----------------------------------------------
    def button_press_on_field(self, button, event):
        if event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:        
            # Retrieves the group on which the user has clicked on
            x = int(event.x)
            y = int(event.y)
            (path, treeviewColumn, x, y) = self.treeTypeStructureGenerator.getTreeview().get_path_at_pos(x, y)
            aIter = self.treeTypeStructureGenerator.getTreeview().get_model().get_iter(path)
            field = self.treeTypeStructureGenerator.getTreeview().get_model().get_value(aIter, 0)
            menu = gtk.Menu()
            item = gtk.MenuItem("Fuzz field")
            item.connect("activate", self.fuzz_field_cb, field)
            item.show()
            menu.append(item)
            menu.popup(None, None, None, event.button, event.time)

    def fuzz_field_cb(self, widget, field):
        print "Fuzz field : " + str(field)
