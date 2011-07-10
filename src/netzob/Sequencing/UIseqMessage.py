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
import logging

pygtk.require('2.0')

#+---------------------------------------------- 
#| Local Imports
#+----------------------------------------------
import MessageGroup
import TracesExtractor
from ..Common import ConfigurationParser
from TreeViews import TreeGroupGenerator
from TreeViews import TreeMessageGenerator


#+---------------------------------------------- 
#| Configuration of the logger
#+----------------------------------------------
loggingFilePath = ConfigurationParser.ConfigurationParser().get("logging", "path")
logging.config.fileConfig(loggingFilePath)


#+---------------------------------------------- 
#| UIseqMessage :
#|     GUI for message sequencing
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.2
#+---------------------------------------------- 
class UIseqMessage:
    TARGET_TYPE_TEXT = 80
    TARGETS = [('text/plain', 0, TARGET_TYPE_TEXT)]
    
    #+---------------------------------------------- 
    #| Called when user select a new trace
    #+----------------------------------------------
    def new(self):
        # Parse the traces and store the results
        tracesExtractor = TracesExtractor.TracesExtractor(self.zob)
        self.selectedGroup = ""
        task = tracesExtractor.parse(self.groups, self)
        gobject.idle_add(task.next)

    def update(self):
        self.updateTreeStoreGroup()
        self.updateTreeStoreMessage()

    def clear(self):
        pass

    def kill(self):
        pass
    
    #+---------------------------------------------- 
    #| Constructor :
    #| @param groups: list of all groups 
    #+----------------------------------------------   
    def __init__(self, zob):
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Sequencing.UIseqMessage.py')
        
        self.zob = zob
        self.groups = []
        self.selectedGroup = ""
        
        self.selectedMessage = ""
        
        # Definition of the Sequence Onglet
        # First we create an HPaned which hosts the two main children
        self.panel = gtk.HPaned()        
        
        # Creation of the two children
        self.vb_sortie = gtk.VBox(False, spacing=0)
        self.vb_filter = gtk.VBox(False, spacing=0)

        # includes the two children
        self.panel.add(self.vb_filter)
        self.panel.add(self.vb_sortie)

        self.vb_sortie.set_size_request(-1, -1)
        self.vb_filter.set_size_request(-1, -1)

        self.vb_sortie.show()
        self.vb_filter.show()
        self.panel.show()
        
        #+---------------------------------------------- 
        #| LEFT PART OF THE GUI : TREEVIEW
        #+----------------------------------------------           
        # Initialize the treeview generator for the groups
        self.treeGroupGenerator = TreeGroupGenerator.TreeGroupGenerator(self.groups)
        self.treeGroupGenerator.initialization()
        self.vb_filter.pack_start(self.treeGroupGenerator.getScrollLib(), True, True, 0)
        # Attach to the treeview few actions (DnD, cursor and buttons handlers...)
        self.treeGroupGenerator.getTreeview().enable_model_drag_dest(self.TARGETS, gtk.gdk.ACTION_DEFAULT | gtk.gdk.ACTION_MOVE)
        self.treeGroupGenerator.getTreeview().connect("drag_data_received", self.drop_fromDND)
        self.treeGroupGenerator.getTreeview().connect("cursor-changed", self.messageChanged)
        self.treeGroupGenerator.getTreeview().connect('button-press-event',self.button_press_on_treeview_groups)
       
        #+---------------------------------------------- 
        #| RIGHT PART OF THE GUI : TREEVIEW
        #+----------------------------------------------
        # messages output
        self.sortie_frame = gtk.Frame()
#        self.sortie_frame.set_label("Message output")
        self.sortie_frame.show()
        # Initialize the treeview generator for the messages
        self.treeMessageGenerator = TreeMessageGenerator.TreeMessageGenerator(self.vb_sortie)
        self.treeMessageGenerator.initialization()        
        self.sortie_frame.add(self.treeMessageGenerator.getScrollLib())
        self.vb_sortie.pack_start(self.sortie_frame, True, True, 0)
        
        # Attach to the treeview few actions (DnD, cursor and buttons handlers...)
        self.treeMessageGenerator.getTreeview().enable_model_drag_source(gtk.gdk.BUTTON1_MASK,self.TARGETS,gtk.gdk.ACTION_DEFAULT | gtk.gdk.ACTION_MOVE)
        self.treeMessageGenerator.getTreeview().connect("drag-data-get", self.drag_fromDND)      
        self.treeMessageGenerator.getTreeview().connect("cursor-changed", self.messageSelected)
        self.treeMessageGenerator.getTreeview().connect('button-press-event',self.button_press_on_treeview_messages)
        self.treeMessageGenerator.getTreeview().connect("row-activated", self.dbClickToChangeType)
        
        self.log.debug("GUI for sequential part is created")
    
    #+---------------------------------------------- 
    #| button_press_on_treeview_groups :
    #|   operation when the user click on the treeview.
    #|   mainly to open a contextual menu
    #+----------------------------------------------
    def button_press_on_treeview_groups(self,obj,event):
        self.log.debug("User requested a contextual menu (treeview group)")
        
        if event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
            self.build_context_menu_for_groups(event)

    #+---------------------------------------------- 
    #| button_press_on_treeview_messages :
    #|   operation when the user click on the treeview.
    #|   mainly to open a contextual menu
    #+----------------------------------------------
    def button_press_on_treeview_messages(self,treeview,event):
        if event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
            self.log.debug("User requested a contextual menu (treeview messages)")
            x = int(event.x)
            y = int(event.y)
            (path, treeviewColumn, x, y) = treeview.get_path_at_pos(x, y)

            # Retrieve the selected column number
            iCol = 0
            for col in treeview.get_columns():
                if col == treeviewColumn:
                    break
                iCol += 1

            # Build a context menu to change the string rendering of a specific column
            typesList = self.treeMessageGenerator.getAllDiscoveredTypes(iCol)
            menu = gtk.Menu()
            for type in typesList:
                item = gtk.MenuItem(type)
                item.show()
                item.connect("activate",self.callbackForTypeModification, iCol, type)   
                menu.append(item)
            menu.popup(None, None, None, event.button, event.time)

    #+---------------------------------------------- 
    #| callbackForTypeModification :
    #|   Callback to change the column type
    #+----------------------------------------------
    def callbackForTypeModification(self, event, iCol, type):
        self.treeMessageGenerator.setTypeForCol(iCol,type)
        self.treeMessageGenerator.updateDefault()

    #+---------------------------------------------- 
    #| dbClickToChangeType :
    #|   Called when user double click on a row
    #|    in order to change the column type
    #+----------------------------------------------
    def dbClickToChangeType(self, treeview, path, paramCol):
        # Retrieve the selected column number
        iCol = 0
        for col in treeview.get_columns():
            if col == paramCol:
                break
            iCol += 1

        # Find the next possible type for this column
        possibleTypes = self.treeMessageGenerator.getAllDiscoveredTypes(iCol)
        print "FGY" + str(len(possibleTypes))
        i = 0
        chosedType = self.treeMessageGenerator.getSelectedType(iCol)
        for type in possibleTypes:
            if type == chosedType:
                chosedType = possibleTypes[(i+1) % len(possibleTypes)]
                break
            i += 1

        # Apply the new chosed type for this column
        self.treeMessageGenerator.setTypeForCol(iCol, chosedType)
        self.treeMessageGenerator.updateDefault()
        
    #+---------------------------------------------- 
    #| build_context_menu_for_groups :
    #|   Create a menu to display available operations
    #|   on the treeview groups
    #+----------------------------------------------
    def build_context_menu_for_groups(self, event):
        
        x = int(event.x)
        y = int(event.y)
        pthinfo = self.treeGroupGenerator.getTreeview().get_path_at_pos(x, y)
        if pthinfo is None:
            canWeDelete = 0
        else :
            canWeDelete = 1    
        entries =[        
                  (gtk.STOCK_ADD, self.displayPopupToCreateGroup,1),
                  (gtk.STOCK_REMOVE, self.displayPopupToRemoveGroup,canWeDelete)
        ]

        menu = gtk.Menu()
        for stock_id,callback,sensitivity in entries:
            item = gtk.ImageMenuItem(stock_id)
            if callback:
                item.connect("activate",callback)   
            item.set_sensitive(sensitivity)
            item.show()
            menu.append(item)
        menu.popup(None,None,None,event.button,event.time)


    #+---------------------------------------------- 
    #| displayPopupToCreateGroup_ResponseToDialog :
    #|   pygtk is so good ! arf :( <-- clap clap :D
    #+----------------------------------------------
    def displayPopupToCreateGroup_ResponseToDialog(self, entry, dialog, response):
        dialog.response(response)

    
    #+---------------------------------------------- 
    #| displayPopupToCreateGroup :
    #|   Display a form to create a new group.
    #|   Based on the famous dialogs
    #+----------------------------------------------
    def displayPopupToCreateGroup(self, event):
        self.log.debug("Display a popup to create a group")
        #base this on a message dialog
        dialog = gtk.MessageDialog(
                                   None,
                                   gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                   gtk.MESSAGE_QUESTION,
                                   gtk.BUTTONS_OK,
                                   None)
        dialog.set_markup('Please enter the <b>new group name</b>:')
        #create the text input field
        entry = gtk.Entry()
        #allow the user to press enter to do ok
        entry.connect("activate", self.displayPopupToCreateGroup_ResponseToDialog, dialog, gtk.RESPONSE_OK)
        #create a horizontal box to pack the entry and a label
        hbox = gtk.HBox()
        hbox.pack_start(gtk.Label("Group Name :"), False, 5, 5)
        hbox.pack_end(entry)
        #some secondary text
        dialog.format_secondary_markup("<b>Warning Grand'Ma</b> : Be sure not to create two groups with the same name.")
        #add it and show it
        dialog.vbox.pack_end(hbox, True, True, 0)
        dialog.show_all()
        #go go go
        dialog.run()
        newGroupName = entry.get_text()
        dialog.destroy()
        
        if (len(newGroupName)>0) :
            self.log.debug("a new group will be created with the given name : {0}".format(newGroupName))
            
            newGroup = MessageGroup.MessageGroup(newGroupName, [])
            self.groups.append(newGroup)
            #Update Left and Right
            self.updateTreeStoreGroup()
            self.updateTreeStoreMessage()
        
    def displayPopupToRemoveGroup(self, event):
        self.log.debug("on delete")
        
    #+---------------------------------------------- 
    #| drop_fromDND :
    #|   defines the operation executed when a message is
    #|   is dropped out current group to the selected group 
    #+----------------------------------------------
    def drop_fromDND(self, treeview, context, x, y, selection, info, etime):
        modele = treeview.get_model()
        donnees = selection.data
        info_depot = treeview.get_dest_row_at_pos(x, y)
        
        if info_depot :
            chemin, position = info_depot
            iter = modele.get_iter(chemin)
            new_grp_name = str(modele.get_value(iter, 0))
        
            found = False
            for tmp_group in self.groups :
                if (tmp_group.getName() == new_grp_name) :
                    new_grp = tmp_group
                for tmp_message in tmp_group.getMessages() :
                    if (str(tmp_message.getID()) == donnees) :
                        msg = tmp_message
                        old_grp = tmp_group
                        found = True
        
        if (found) :
            self.log.debug("The message {0} must be moved out its current group {1} to the new group {2}".format(msg.getID(), old_grp.getName(), new_grp.getName()))
            #Removing from its old group
            old_grp.removeMessage(msg)
            #Adding to its new group
            new_grp.addMessage(msg)
            
            #Update Left and Right
            self.updateTreeStoreGroup()
            self.updateTreeStoreMessage()
        else :
            self.log.warning("Impossible to retrieve the message to Drop")
        return
   
    #+---------------------------------------------- 
    #| drag_fromDND :
    #|   defines the operation executed when a message is
    #|   is dragged out current group 
    #+----------------------------------------------
    def drag_fromDND(self, treeview, contexte, selection, info, dateur):
        treeselection = treeview.get_selection()
        modele, iter = treeselection.get_selected()
        texte = str(modele.get_value(iter, 0))
        selection.set(selection.target, 8, texte)
        return
    
    #+---------------------------------------------- 
    #| Update the content of the tree store for groups
    #+----------------------------------------------
    def updateTreeStoreGroup(self):        
        # Updates the treestore with a selected message
        if (self.selectedMessage != "") :
            self.treeGroupGenerator.messageSelected(self.selectedMessage)
            self.selectedMessage = ""
        else :
        # Default display of the groups
            self.treeGroupGenerator.default()
 
    #+---------------------------------------------- 
    #| Update the content of the tree store for messages
    #+----------------------------------------------
    def updateTreeStoreMessage(self):        
        if (self.selectedGroup != "") :
            # Search for the selected group in groups list
            selectedGroup = None
            for group in self.groups :
                if group.getName() == self.selectedGroup :
                    selectedGroup = group
            # If we found it we can update the content of the treestore        
            if selectedGroup != None :
                self.treeMessageGenerator.default(selectedGroup)
                # enable dragging message out of current group
                self.treeMessageGenerator.getTreeview().enable_model_drag_source(gtk.gdk.BUTTON1_MASK,self.TARGETS,gtk.gdk.ACTION_DEFAULT | gtk.gdk.ACTION_MOVE)
                self.treeMessageGenerator.getTreeview().connect("drag-data-get", self.drag_fromDND)      
                self.treeMessageGenerator.getTreeview().connect("cursor-changed", self.messageSelected) 
            # Else, quite weird so throw a warning
            else :
                self.log.warning("Impossible to update the treestore message since we cannot find the selected group according to its name "+self.selectedGroup)
       
#+---------------------------------------------- 
#| CALLBACKS 
#+----------------------------------------------
    def messageSelected(self, treeview) :
        (modele, iter) = treeview.get_selection().get_selected()
        if(iter):
            if(modele.iter_is_valid(iter)):

                pango = modele.get_value(iter, 0)
                group_regex = modele.get_value(iter,1)
                msg_id = modele.get_value(iter, 2)
                
                for group in self.groups :
                    for message in group.getMessages() :
                        if str(message.getID()) == msg_id :
                            self.selectedMessage = message
                            self.log.debug("selected message {0}".format(self.selectedMessage.getID()))     
                            self.updateTreeStoreGroup()

    #+---------------------------------------------- 
    #| Called when user click on a group or on a message
    #+----------------------------------------------
    def messageChanged(self, treeview):
        (modele, iter) = treeview.get_selection().get_selected()
        if(iter):
            if(modele.iter_is_valid(iter)):
                name = modele.get_value(iter, 0)
                score = modele.get_value(iter,1)
                self.selectedGroup = name
                self.updateTreeStoreMessage()



