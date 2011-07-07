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
import NeedlemanWunsch
from ..Common import ConfigurationParser
from ..Common import TypeIdentifier
from TreeStores import TreeStoreGroupGenerator
from TreeStores import TreeStoreMessageGenerator


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

        self.panel = gtk.HBox(False, spacing=10)
        self.vb_sortie = gtk.VBox(False, spacing=0)
        self.vb_filter = gtk.VBox(False, spacing=0)

        self.panel.pack_start(self.vb_filter, True, True, 0)
        self.panel.pack_start(self.vb_sortie, True, True, 0)

        self.vb_sortie.set_size_request(-1, -1)
        self.vb_filter.set_size_request(-1, -1)

        self.vb_sortie.show()
        self.vb_filter.show()
        self.panel.show()
        
        #+---------------------------------------------- 
        #| LEFT PART OF THE GUI : TREEVIEW
        #+----------------------------------------------        
        
        # Tree store contains :
        # str : type {"group" or "message"}
        # str : text ( group/message )
        # str : text ( score )
        # str : color foreground
        # str : color background
        self.treestoreGroup = gtk.TreeStore(str, str, str, str, str)
       
        self.treeViewGroups = gtk.TreeView(self.treestoreGroup)
        # enable dropping data in a group
        self.treeViewGroups.enable_model_drag_dest(self.TARGETS, gtk.gdk.ACTION_DEFAULT | gtk.gdk.ACTION_MOVE)
        self.treeViewGroups.connect("drag_data_received", self.drop_fromDND)

        # messages list
        scroll_lib = gtk.ScrolledWindow()
        scroll_lib.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scroll_lib.show()
        scroll_lib.set_size_request(500, 500)
        scroll_lib.add(self.treeViewGroups)
        
        self.vb_filter.pack_start(scroll_lib, True, True, 0)
        

        self.treeViewGroups.connect("cursor-changed", self.messageChanged)
        self.treeViewGroups.connect('button-press-event',self.button_press_on_treeview_groups)

        lvcolumn = gtk.TreeViewColumn('Messages')
        lvcolumn.set_sort_column_id(1)
        cell1 = gtk.CellRendererText()
        cell2 = gtk.CellRendererText()
        lvcolumn.pack_start(cell1, True)
        lvcolumn.pack_start(cell2,True)
        cell1.set_property('background-set' , True)
        cell1.set_property('foreground-set' , True)
        
        cell2.set_property('background-set' , True)
        cell2.set_property('foreground-set' , True)
        
        lvcolumn.set_attributes(cell1, text=1, foreground=3, background=4)
        lvcolumn.set_attributes(cell2, text=2, foreground=3, background=4)
        self.treeViewGroups.append_column(lvcolumn)
        self.treeViewGroups.show()


        #+---------------------------------------------- 
        #| RIGHT PART OF THE GUI : TREEVIEW
        #+----------------------------------------------      

        # messages output
        self.sortie_frame = gtk.Frame()
        self.sortie_frame.set_label("Message output")
        self.sortie_frame.show()
        
        # Tree store contains :
        # str : text
        # str : text
        self.treestoreMessage = gtk.TreeStore(str, str, str)        
        self.treeViewDetail = gtk.TreeView(self.treestoreMessage)
        self.treeViewDetail.set_reorderable(True)
        
        
        
        # enable dragging message out of current group
        self.treeViewDetail.enable_model_drag_source(gtk.gdk.BUTTON1_MASK,self.TARGETS,
                  gtk.gdk.ACTION_DEFAULT | gtk.gdk.ACTION_MOVE)
        self.treeViewDetail.connect("drag-data-get", self.drag_fromDND)      
        self.treeViewDetail.connect("cursor-changed", self.messageSelected)
        self.treeViewDetail.connect('button-press-event',self.button_press_on_treeview_messages)
        
        
        self.cellDetail2 = gtk.CellRendererText()
        # Column Messages
        self.lvcolumnDetail2 = gtk.TreeViewColumn('Messages')
        self.lvcolumnDetail2.pack_start(self.cellDetail2, True)
        self.lvcolumnDetail2.set_attributes(self.cellDetail2, text=0)
        self.lvcolumnDetail2.set_attributes(self.cellDetail2, markup=0)
        self.treeViewDetail.append_column(self.lvcolumnDetail2)
        
        self.treeViewDetail.show()
        
        scroll_sortie = gtk.ScrolledWindow()
        scroll_sortie.set_size_request(1000, 500)
        scroll_sortie.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        
        scroll_sortie.add(self.treeViewDetail)
        self.sortie_frame.add(scroll_sortie)
        self.vb_sortie.pack_start(self.sortie_frame, True, True, 0)
        scroll_sortie.show()
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
            iCol = 4
            # Get the selected column number
            for col in treeview.get_columns():
                if col == treeviewColumn:
                    break
                iCol += 1

            # Build a context menu to change the string rendering of a specific column
            i = treeview.get_model().iter_next( treeview.get_model().get_iter_first() )
            typesList = treeview.get_model().get_value(i, iCol)
            menu = gtk.Menu()
            for type in typesList.split(","):
                item = gtk.MenuItem(type)
                item.show()
                menu.append(item)
            menu.popup(None, None, None, event.button, event.time)

            # Change the string rendering of the selected column according to the selected type
#            
#            i = treeview.get_model().get_iter_first()
#            while True:
#                if i==None:
#                    break
#                if treeview.get_model().get_value(i, 0) == "HEADER REGEX":
#                    pass
#                elif treeview.get_model().get_value(i, 0) == "HEADER TYPE":
#                    pass
#                else:
#                    print treeview.get_model().get_value(i, iCol)
#                i = treeview.get_model().iter_next(i)
#                # TODO : change the rendering
            
    #+---------------------------------------------- 
    #| build_context_menu_for_groups :
    #|   Create a menu to display available operations
    #|   on the treeview groups
    #+----------------------------------------------
    def build_context_menu_for_groups(self, event):
        
        x = int(event.x)
        y = int(event.y)
        pthinfo = self.treeViewGroups.get_path_at_pos(x, y)
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
            new_grp_name = str(modele.get_value(iter, 1))
        
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
            treeStoreGenerator = TreeStoreGroupGenerator.TreeStoreGroupGenerator(self.groups, self.treestoreGroup)
            treeStoreGenerator.messageSelected(self.selectedMessage)
            self.selectedMessage = ""
        else :
        # Default display of the groups
            treeStoreGenerator = TreeStoreGroupGenerator.TreeStoreGroupGenerator(self.groups, self.treestoreGroup)
            treeStoreGenerator.default()
 
    #+---------------------------------------------- 
    #| Update the content of the tree store for messages
    #+----------------------------------------------
    def updateTreeStoreMessage(self):
        self.log.debug("Updating the tree store of messages")
        self.treestoreMessage.clear()
        
        if (self.selectedGroup != "") :
            # Search for the selected group in groups list
            selectedGroup = None
            for group in self.groups :
                if group.getName() == self.selectedGroup :
                    selectedGroup = group
            # If we found it we can update the content of the treestore        
            if selectedGroup != None :
                treeStoreGenerator = TreeStoreMessageGenerator.TreeStoreMessageGenerator(selectedGroup, self.treestoreMessage, self.treeViewDetail)
                treeStoreGenerator.default()
            # Else, quite weird so throw a warning
            else :
                self.log.warning("Impossible to update the treestore message since we cannot find the selected group according to its name "+self.selectedGroup)
            
            
#            
#        
#        
#        
#        
#        if (self.selectedGroup != "") :
#            self.log.debug("Selected group : {0}".format(self.selectedGroup))
#            
#            groupName = ""
#            groupRegex = ""
#            messages = []
#            
#            for group in self.groups :
#                if (group.getName() == self.selectedGroup) :
#                    groupRegex = group.getRegex()
#                    messages = group.getMessages()
#                    groupName = group.getName()
#            
#            # Verify the requested group is found
#            if (len(groupRegex) == 0 ) :
#                self.log.warning("Error, impossible to retrieve the selected group !")
#                return
#            
#            self.log.debug("Group regex : {0}".format(groupRegex))    
#            needle = NeedlemanWunsch.NeedlemanWunsch()
#            score = needle.computeScore(groupRegex)    
#            self.log.debug("Score du groupe : {0}".format(score))
#            
#            error = False
#            
#            if (score >= 50) :
#                compiledRegex = re.compile(groupRegex)
#                
#                maxNumberOfGroup = 0
#                matchMessages = []
#                aggregatedValuesPerCol = {}
#                
#                for message in messages :
#                    data = message.getStringData()                    
#                    m = compiledRegex.match(data)
#                    if (m == None) :
#                        self.log.warning("The regex of the group doesn't match one of its message")
#                        error = True
#                        break
#                    
#                    nbGroup = len(m.groups())
#                    if maxNumberOfGroup < nbGroup :
#                        maxNumberOfGroup = nbGroup
#                    ar = []
#                    ar.append(message.getID())
#                    ar.append("#ffffff")
#                    ar.append(pango.WEIGHT_NORMAL)
#                    ar.append(False)
#                    current = 0
#                    k = 0
#
#                    for i_group in range(1, nbGroup+1) :
#                        start = m.start(i_group)
#                        end = m.end(i_group)
#                        
#                        ar.append('<span>' + data[current:start] + '</span>')
#                        ar.append('<span foreground="blue" font_family="monospace">' + data[start:end] + '</span>')
#                        if not k in aggregatedValuesPerCol:
#                            aggregatedValuesPerCol[k] = []
#                        aggregatedValuesPerCol[k].append( data[current:start] )
#                        k += 1
#                        if not k in aggregatedValuesPerCol:
#                            aggregatedValuesPerCol[k] = []
#                        aggregatedValuesPerCol[k].append( data[start:end] )
#                        k += 1
#
#                        current = end
#                    ar.append('<span >' + data[current:] + '</span>')
#                    if not k in aggregatedValuesPerCol:
#                        aggregatedValuesPerCol[k] = []
#                    aggregatedValuesPerCol[k].append( data[current:] )
#                    matchMessages.append(ar)
#
#                # create a TreeView with N cols, with := (maxNumberOfGroup * 2 + 1)
#                treeStoreTypes = [str, str, int, gobject.TYPE_BOOLEAN]
#                for i in range( maxNumberOfGroup * 2 + 1):
#                    treeStoreTypes.append(str)
#                self.treestoreMessage = gtk.TreeStore(*treeStoreTypes)
#                self.treeViewDetail.set_model(self.treestoreMessage)
#                self.treeViewDetail.set_reorderable(True)
#
#                for i in range(len(matchMessages)):
#                    self.treestoreMessage.append(None, matchMessages[i])
#
#                # Type and Regex headers
#                ## TODO : divide the regex numbers by 2
#                hdr_row = []
#                hdr_row.append("HEADER TYPE")
#                hdr_row.append("#00ffff")
#                hdr_row.append(pango.WEIGHT_BOLD)
#                hdr_row.append(True)
#
#                for i in range( len(aggregatedValuesPerCol) ):
#                    # Identify the type from the strings of the same column
#                    typesList = TypeIdentifier.TypeIdentifier().getType(aggregatedValuesPerCol[i])
#                     
#                    hdr_row.append( typesList );
#                self.treestoreMessage.prepend(None, hdr_row)
#
#                splittedRegex = re.findall("(\(\.\{\d*,\d*\}\))", groupRegex)
#
#                regex_row = []
#                regex_row.append("HEADER REGEX")
#                regex_row.append("#00ffff")
#                regex_row.append(pango.WEIGHT_BOLD)
#                regex_row.append(True)
#
#                for i in range(len(splittedRegex)):
#                    regex_row.append("")
#                    # Get the Regex of the current column
#                    regex_row.append(splittedRegex[i][1:-1])
#                for i in range((maxNumberOfGroup * 2 + 1 + 4) - len(regex_row)):
#                    regex_row.append("")
#                self.treestoreMessage.prepend(None, regex_row)
#
#                # columns handling
#                if (error != True) :    
#                    # remove all the colomns
#                    for col in self.treeViewDetail.get_columns() :
#                        self.treeViewDetail.remove_column(col)
#
#                    # Define cellRenderer objects
#                    self.cellDetail2 = gtk.CellRendererText()
#                    self.cellDetail2.set_property('background-set' , True)
#
#                    for i in range(4, 4 + (maxNumberOfGroup * 2) + 1) :
#                        # Column Messages
#                        self.lvcolumnDetail2 = gtk.TreeViewColumn('Col'+str(i))
#                        self.lvcolumnDetail2.pack_start(self.cellDetail2, True)
#                        self.lvcolumnDetail2.set_attributes(self.cellDetail2, markup=i, background=1, weight=2, editable=3)
#                        self.treeViewDetail.append_column(self.lvcolumnDetail2)
#                        # enable dragging message out of current group
#                        self.treeViewDetail.enable_model_drag_source(gtk.gdk.BUTTON1_MASK,self.TARGETS,
#                                                                     gtk.gdk.ACTION_DEFAULT | gtk.gdk.ACTION_MOVE)
#                        self.treeViewDetail.connect("drag-data-get", self.drag_fromDND)      
#                        self.treeViewDetail.connect("cursor-changed", self.messageSelected) 
#                
#            if (score < 50 or error == True):
#                # create a view with 30 cols
#                self.treestoreMessage = gtk.TreeStore(str, str, str)        
#                self.treeViewDetail.set_model(self.treestoreMessage)
#                self.treeViewDetail.set_reorderable(True)   
#                
#                # remove all the colomns
#                for col in self.treeViewDetail.get_columns() :
#                    self.treeViewDetail.remove_column(col)
#                
#                # clear all the attributes
#                self.cellDetail2 = gtk.CellRendererText()
#                # Column Messages
#                self.lvcolumnDetail2 = gtk.TreeViewColumn('Message')
#                self.lvcolumnDetail2.pack_start(self.cellDetail2, True)
#                self.lvcolumnDetail2.set_attributes(self.cellDetail2, text=0)
#                self.lvcolumnDetail2.set_attributes(self.cellDetail2, markup=0)
#                self.treeViewDetail.append_column(self.lvcolumnDetail2)
#                
#                # enable dragging message out of current group
#                self.treeViewDetail.enable_model_drag_source(gtk.gdk.BUTTON1_MASK,self.TARGETS,
#                  gtk.gdk.ACTION_DEFAULT | gtk.gdk.ACTION_MOVE)
#                self.treeViewDetail.connect("drag-data-get", self.drag_fromDND)      
#                self.treeViewDetail.connect("cursor-changed", self.messageSelected) 
#                for message in messages :
#                    self.treestoreMessage.append(None, [message.getPangoData(groupRegex), groupRegex, message.getID()])
            
                    
                  
             
#            for group in self.groups :
#                if (group.getName() == self.selectedGroup) :
#                    if (len(group.getRegex())>0) :
#                        needle = NeedlemanWunsch.NeedlemanWunsch()
#                        score = needle.computeScore(group.getRegex())
#                        # if score > 75 : apply regex
#                        if (score < 75) :
#                            
#                            
#                            
#                            
#                        else :
#                            regex = group.getRegex()
#                            groups = regex.split('(.*)')
#                        
#                            # Create all the columns :
#                            nbGroup = len(groups)
#                            
#                            # current bg col
#                            for col in self.treeViewDetail.get_columns() :
#                                self.treeViewDetail.remove_column(col)
#    #                       
#                            for i in range (0, nbGroup) :
#                                cell = gtk.CellRendererText()
#                                # Column Messages
#                                treeViewColumn = gtk.TreeViewColumn("Col "+str(i))
#                                treeViewColumn.pack_start(cell, True)
#                                treeViewColumn.set_attributes(cell, text=0)
#                                treeViewColumn.set_attributes(cell, markup=0)
#                                self.treeViewDetail.append_column(treeViewColumn)
#                  
#                            
#                            self.treestoreMessage.append(None, [group.getName(), "", ""])
#                            
#                            
#                            
#                            self.treestoreMessage = gtk.TreeStore(str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str)        
#                            self.treeViewDetail = gtk.TreeView(self.treestoreMessage)
#                            self.treeViewDetail.set_reorderable(True)    
#                                
#                            # compile the group regex    
#                            compiledRegex = re.compile(regex)
#                            for message in group.getMessages() :
#                                print "- {0}".format(message.getStringData())
#                                data = message.getStringData()
#                                m = compiledRegex.match(data)
#                                nbGroup = len(m.groups())
#                                print "NB GROUP = {0}".format(nbGroup)
#                                ar = []
#                                current = 0
#                                for i_group in range(1, nbGroup+1) :
#                                    start = m.start(i_group)
#                                    end = m.end(i_group)
#                                    ar.append(data[current:start])
#                                    ar.append(data[start:end])
#                                    
#                                    
#                                    current = end
#                                
#                                print "------->"+str(len(ar))    
#                                for t in range(0,30-len(ar)) :
#                                    ar.append("-");
#                                    
#                                print "------->"+str(len(ar))    
#                                    
#                                self.treestoreMessage.append(None, ar)
                            
       
       
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
                
                type = modele.get_value(iter, 0)
                name = modele.get_value(iter, 1)
                score = modele.get_value(iter,2)

                if (type == "Group") :
                    self.selectedGroup = name
                    self.updateTreeStoreMessage()
                    
                if (type == "Message") :   
                    self.selectedMessage = name


