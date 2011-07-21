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
import MessageGroup
import TracesExtractor
from ..Common import ConfigurationParser
from TreeViews import TreeGroupGenerator
from TreeViews import TreeMessageGenerator
from TreeViews import TreeTypeStructureGenerator

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
        self.selectedGroup = ""
        self.treeMessageGenerator.clear()
        self.treeGroupGenerator.clear()
        self.treeTypeStructureGenerator.clear()
        self.update()
        self.parseThread = threading.Thread(None, self.treeGroupGenerator.initTreeGroupWithTraces, None, (self.zob, self), {})
        self.parseThread.start()

    def update(self):
        self.updateTreeStoreGroup()
        self.updateTreeStoreMessage()
        self.updateTreeStoreTypeStructure()

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
        self.selectedGroup = ""
        self.selectedMessage = ""
        self.treeMessageGenerator = None
        self.treeTypeStructureGenerator = None
        
        # Definition of the Sequence Onglet
        # First we create an HPaned which hosts the two main children
        self.panel = gtk.HPaned()
        self.panel.show()

        configParser = ConfigurationParser.ConfigurationParser()
        
        #+---------------------------------------------- 
        #| LEFT PART OF THE GUI : TREEVIEW
        #+----------------------------------------------           
        vb_left_panel = gtk.VBox(False, spacing=0)
        self.panel.add(vb_left_panel)
        vb_left_panel.set_size_request(-1, -1)
        vb_left_panel.show()
        # Initialize the treeview generator for the groups
        self.treeGroupGenerator = TreeGroupGenerator.TreeGroupGenerator( [] )
        self.treeGroupGenerator.initialization()
        vb_left_panel.pack_start(self.treeGroupGenerator.getScrollLib(), True, True, 0)
        # Attach to the treeview few actions (DnD, cursor and buttons handlers...)
        self.treeGroupGenerator.getTreeview().enable_model_drag_dest(self.TARGETS, gtk.gdk.ACTION_DEFAULT | gtk.gdk.ACTION_MOVE)
        self.treeGroupGenerator.getTreeview().connect("drag_data_received", self.drop_fromDND)
        self.treeGroupGenerator.getTreeview().connect("cursor-changed", self.groupChanged)
        self.treeGroupGenerator.getTreeview().connect('button-press-event', self.button_press_on_treeview_groups)
       
        #+---------------------------------------------- 
        #| RIGHT PART OF THE GUI : TOP BUTTONS
        #+----------------------------------------------
        vb_right_panel = gtk.VBox(False, spacing=0)
        self.panel.add(vb_right_panel)
        vb_right_panel.show()
        # Sub-panel for specific buttions
        table = gtk.Table(rows=3, columns=8, homogeneous=False)
        table.show()
        vb_right_panel.pack_start(table, False, False, 0)

        # Widget for choosing the analysed protocole type
        label = gtk.Label("Protocol type : ")
        label.show()
        combo = gtk.combo_box_entry_new_text()
        combo.set_size_request(300, -1)
        combo.set_model(gtk.ListStore(str))
        combo.append_text("Text based (HTTP, FTP)")
        combo.append_text("Fixed fields binary based (IP, TCP)")
        combo.append_text("Variable fields binary based (ASN.1)")
        combo.connect("changed", self.updateProtocolType)
        protocol_type_ID = configParser.getInt("clustering", "protocol_type")
        combo.set_active(protocol_type_ID)
        combo.show()
        table.attach(label, 0, 1, 0, 1, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        table.attach(combo, 1, 3, 0, 1, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        # Widget entry for chosing the alignment score sub-limit
        label = gtk.Label("Score limit : ")
        label.show()
        combo = gtk.combo_box_entry_new_text()
        combo.set_size_request(60, -1)
        combo.set_model(gtk.ListStore(str))
        combo.connect("changed", self.updateScoreLimit)
        possible_choices = [100, 95, 90, 85, 80, 75, 70, 65, 60, 55, 50, 45, 40, 35, 30, 25, 20, 15, 10, 5]
        min_equivalence = configParser.getFloat("clustering", "equivalence_threshold")
        for i in range(len(possible_choices)):
            combo.append_text(str(possible_choices[i]))
            if str(possible_choices[i]) == str(int(min_equivalence)):
                combo.set_active(i)
        combo.show()
        table.attach(label, 4, 5, 0, 1, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        table.attach(combo, 5, 6, 0, 1, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        # Widget checkbox for selecting the slickery during alignement process
        but = gtk.CheckButton("Slick regexes during alignment")
        doInternalSlick = configParser.getInt("clustering", "do_internal_slick")
        if doInternalSlick == 1:
            but.set_active(True)
        else:
            but.set_active(False)
        but.connect("toggled", self.activeInternalSlickRegexes)
        but.show()
        table.attach(but, 6, 7, 0, 1, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        # Widget button slick regexes
        but = gtk.Button("Slick regexes")
        but.connect("clicked", self.treeGroupGenerator.slickRegexes, self)
        but.show()
        table.attach(but, 0, 1, 1, 2, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        # Widget button merge common regexes
        but = gtk.Button("Merge common regexes")
        but.connect("clicked", self.treeGroupGenerator.mergeCommonRegexes, self)
        but.show()
        table.attach(but, 1, 2, 1, 2, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        # Widget button find size fields
        but = gtk.Button("Find size fields")
        # TODO: just try to use an ASN.1 parser to find the simple TLV protocols
        but.connect("clicked", self.findSizeFields)
        but.show()
        table.attach(but, 2, 3, 1, 2, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        #+---------------------------------------------- 
        #| RIGHT PART OF THE GUI : TREEVIEW MESSAGE OUTPUT
        #+----------------------------------------------
        right_sub_vpaned = gtk.VPaned()
        right_sub_vpaned.show()
        vb_right_panel.pack_start(right_sub_vpaned, True, True, 0)
        # Initialize the treeview generator for the messages
        self.treeMessageGenerator = TreeMessageGenerator.TreeMessageGenerator()
        self.treeMessageGenerator.initialization()        
        right_sub_vpaned.add(self.treeMessageGenerator.getScrollLib())
        
        # Attach to the treeview few actions (DnD, cursor and buttons handlers...)
        self.treeMessageGenerator.getTreeview().enable_model_drag_source(gtk.gdk.BUTTON1_MASK, self.TARGETS, gtk.gdk.ACTION_DEFAULT | gtk.gdk.ACTION_MOVE)
        self.treeMessageGenerator.getTreeview().connect("drag-data-get", self.drag_fromDND)      
        self.treeMessageGenerator.getTreeview().connect("cursor-changed", self.messageSelected)
        self.treeMessageGenerator.getTreeview().connect('button-press-event', self.button_press_on_treeview_messages)
        self.treeMessageGenerator.getTreeview().connect("row-activated", self.dbClickToChangeType)

        #+---------------------------------------------- 
        #| RIGHT PART OF THE GUI : TYPE STRUCTURE OUTPUT
        #+----------------------------------------------
        # Initialize the treeview for the type structure
        self.treeTypeStructureGenerator = TreeTypeStructureGenerator.TreeTypeStructureGenerator()
        self.treeTypeStructureGenerator.initialization()
        right_sub_vpaned.add(self.treeTypeStructureGenerator.getScrollLib())
        
        self.log.debug("GUI for sequential part is created")
    
    #+---------------------------------------------- 
    #| button_press_on_treeview_groups :
    #|   operation when the user click on the treeview.
    #|   mainly to open a contextual menu
    #+----------------------------------------------
    def button_press_on_treeview_groups(self, obj, event):
        self.log.debug("User requested a contextual menu (treeview group)")
        
        if event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
            self.build_context_menu_for_groups(event)

    #+---------------------------------------------- 
    #| button_press_on_treeview_messages :
    #|   operation when the user click on the treeview.
    #|   mainly to open a contextual menu
    #+----------------------------------------------
    def button_press_on_treeview_messages(self, treeview, event):
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

            menu = gtk.Menu()
            # Add sub-entries to change the type of a specific column
            typesList = self.treeMessageGenerator.getGroup().getAllDiscoveredTypes(iCol)
            typeMenu = gtk.Menu()
            for aType in typesList:
                item = gtk.MenuItem("Render in : " + str(aType))
                item.show()
                item.connect("activate",self.rightClickToChangeType, iCol, aType)   
                typeMenu.append(item)
            item = gtk.MenuItem("Change Type")
            item.set_submenu(typeMenu)
            item.show()
            menu.append(item)

            # Add entries to concatenate column
            concatMenu = gtk.Menu()
            item = gtk.MenuItem("with left column")
            item.show()
            item.connect("activate", self.rightClickToConcatColumns, iCol, "left")
            concatMenu.append(item)
            item = gtk.MenuItem("with right column")
            item.show()
            item.connect("activate", self.rightClickToConcatColumns, iCol, "right")
            concatMenu.append(item)
            item = gtk.MenuItem("Concatenate")
            item.set_submenu(concatMenu)
            item.show()
            menu.append(item)

            # Add entry to split the column
            item = gtk.MenuItem("Split column")
            item.show()
            item.connect("activate", self.rightClickToSplitColumn, iCol)
            menu.append(item)

            menu.popup(None, None, None, event.button, event.time)

    #+---------------------------------------------- 
    #| rightClickToChangeType :
    #|   Callback to change the column type
    #|   by doing a right click
    #+----------------------------------------------
    def rightClickToChangeType(self, event, iCol, aType):
        self.treeMessageGenerator.getGroup().setTypeForCol(iCol, aType)
        self.treeMessageGenerator.updateDefault()

    #+---------------------------------------------- 
    #|  rightClickToConcatColumns:
    #|   Callback to concatenate two columns
    #+----------------------------------------------
    def rightClickToConcatColumns(self, event, iCol, strOtherCol):
        self.log.debug("Concatenate the column " + str(iCol) + " with the " + str(strOtherCol) + " column")

        if iCol == 0 and strOtherCol == "left":
            self.log.debug("Can't concatenate the first column with its left column")
            return

        if iCol + 1 == len(self.treeMessageGenerator.getGroup().getRegex())  and strOtherCol == "right":
            self.log.debug("Can't concatenate the last column with its right column")
            return

        newRegex = self.treeMessageGenerator.getGroup().getRegex()

        if strOtherCol == "left":
            elt1 = newRegex.pop(iCol - 1)
            elt2 = newRegex.pop(iCol - 1)
            eltResult = self.concatRegexElts(elt1, elt2)
            newRegex.insert(iCol - 1, eltResult)
        else:
            elt1 = newRegex.pop(iCol)
            elt2 = newRegex.pop(iCol)
            eltResult = self.concatRegexElts(elt1, elt2)
            newRegex.insert(iCol, eltResult)

        self.treeMessageGenerator.getGroup().setRegex( newRegex )
        self.treeMessageGenerator.updateDefault()

    #+---------------------------------------------- 
    #| concatRegexElts :
    #|   Concatenate two elements of a regex
    #+----------------------------------------------
    def concatRegexElts(self, elt1, elt2):
        if elt1 == "":
            return elt2
        if elt2 == "":
            return elt1

        if elt1[0] == "(" and elt2[0] != "(": # Dyn + Static fields
            return elt1[:-1] + elt2 + ")"

        if elt1[0] != "(" and elt2[0] == "(": # Static + Dyn fields
            return "(" + elt1 + elt2[1:]

        if elt1[0] == "(" and elt2[0] == "(": # Dyn + Dyn fields
            return elt1[:-1] + elt2[1:]

        if elt1[0] != "(" and elt2[0] != "(": # Static + Static fields (should not happen...)
            return elt1 + elt2

    #+---------------------------------------------- 
    #|  rightClickToSplitColumn:
    #|   Callback to split a column
    #+----------------------------------------------
    def rightClickToSplitColumn(self, event, iCol):
        dialog = gtk.Dialog(title="Split column " + str(iCol), flags=0, buttons=None)
        textview = gtk.TextView()
        textview.get_buffer().create_tag("redTag", weight=pango.WEIGHT_BOLD, foreground="red", family="Courier")
        textview.get_buffer().create_tag("greenTag", weight=pango.WEIGHT_BOLD, foreground="#006400", family="Courier")
        self.positionToSplit = 0

        # Left arrow
        arrow = gtk.Arrow(gtk.ARROW_LEFT, gtk.SHADOW_OUT)
        arrow.show()
        but = gtk.Button()
        but.add(arrow)
        but.connect("clicked", self.adjustSplitColumn, textview, "left", iCol)
        but.show()
        dialog.action_area.pack_start(but, True, True, 0)

        # Right arrow
        arrow = gtk.Arrow(gtk.ARROW_RIGHT, gtk.SHADOW_OUT)
        arrow.show()
        but = gtk.Button()
        but.add(arrow)
        but.connect("clicked", self.adjustSplitColumn, textview, "right", iCol)
        but.show()
        dialog.action_area.pack_start(but, True, True, 0)

        # Split button
        but = gtk.Button(label="Split column")
        but.show()
        but.connect("clicked", self.doSplitColumn, textview, iCol, dialog)
        dialog.action_area.pack_start(but, True, True, 0)

        # Text view containing selected column messages
        frame = gtk.Frame()
        frame.set_label("Content of the column to split")
        frame.show()
        textview.set_size_request(400, 300)
        messages = self.treeMessageGenerator.getGroup().getMessagesFromCol(iCol)
        for m in messages:
            textview.get_buffer().insert_with_tags_by_name( textview.get_buffer().get_end_iter(), self.treeMessageGenerator.getGroup().getRepresentation(m, iCol) + "\n", "greenTag" )
        textview.show()
        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scroll.show()
        scroll.add(textview)
        frame.add(scroll)
        dialog.vbox.pack_start(frame, True, True, 0)
        dialog.show()

    def doSplitColumn(self, widget, textview, iCol, dialog):
        # Find the static/dynamic cols
        messages = self.treeMessageGenerator.getGroup().getMessagesFromCol(iCol)
        ref1 = messages[0][:self.positionToSplit]
        ref2 = messages[0][self.positionToSplit:]
        isStatic1 = True
        isStatic2 = True
        lenDyn1 = 0
        lenDyn2 = 0
        for m in messages[1:]:
            if m[:self.positionToSplit] != ref1:
                isStatic1 = False
                if len(m[:self.positionToSplit]) > lenDyn1:
                    lenDyn1 = len(m[:self.positionToSplit])
            if m[self.positionToSplit:] != ref2:
                isStatic2 = False
                if len(m[self.positionToSplit:]) > lenDyn2:
                    lenDyn2 = len(m[self.positionToSplit:])

        # Build the new sub-regex
        if isStatic1:
            regex1 = ref1
        else:
            regex1 = "(.{," + str(lenDyn1) + "})"
        if isStatic2:
            regex2 = ref2
        else:
            regex2 = "(.{," + str(lenDyn2) + "})"

        # Build the new regex and apply it
        newRegex = self.treeMessageGenerator.getGroup().getRegex()
        newRegex.pop(iCol)
        newRegex.insert(iCol, regex1)
        newRegex.insert(iCol + 1, regex2)
        self.treeMessageGenerator.getGroup().setRegex( newRegex )
        self.treeMessageGenerator.updateDefault()            
        dialog.destroy()

    def adjustSplitColumn(self, widget, textview, direction, iCol):
        messages = self.treeMessageGenerator.getGroup().getMessagesFromCol(iCol)

        # Bounds checking
        if direction == "left":
            self.positionToSplit -= 2
            if self.positionToSplit < 0:
                self.positionToSplit = 0
        else:
            self.positionToSplit += 2
            maxLen = 0
            for m in messages: # Find maxLen
                if len(m) > maxLen:
                    maxLen = len(m)
            if self.positionToSplit > maxLen:
                self.positionToSplit = maxLen

        # Colorize text according to position
        textview.get_buffer().set_text("")
        for m in messages:
            textview.get_buffer().insert_with_tags_by_name( textview.get_buffer().get_end_iter(), self.treeMessageGenerator.getGroup().getRepresentation(m[:self.positionToSplit], iCol) + "  ", "redTag" )
            textview.get_buffer().insert_with_tags_by_name( textview.get_buffer().get_end_iter(), self.treeMessageGenerator.getGroup().getRepresentation(m[self.positionToSplit:], iCol) + "\n", "greenTag" )

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
        possibleTypes = self.treeMessageGenerator.getGroup().getAllDiscoveredTypes(iCol)
        i = 0
        chosedType = self.treeMessageGenerator.getGroup().getSelectedType(iCol)
        for aType in possibleTypes:
            if aType == chosedType:
                chosedType = possibleTypes[(i + 1) % len(possibleTypes)]
                break
            i += 1

        # Apply the new chosed type for this column
        self.treeMessageGenerator.getGroup().setTypeForCol(iCol, chosedType)
        self.treeMessageGenerator.updateDefault()
        
    #+---------------------------------------------- 
    #| build_context_menu_for_groups :
    #|   Create a menu to display available operations
    #|   on the treeview groups
    #+----------------------------------------------
    def build_context_menu_for_groups(self, event):
        
        # Retrieves the group on which the user has clicked on
        x = int(event.x)
        y = int(event.y)
        
        selectedGroup = self.treeGroupGenerator.getGroupAtPosition(x,y)        
        entries = [        
                  (gtk.STOCK_EDIT, self.displayPopupToEditGroup, (selectedGroup != None)),
                  (gtk.STOCK_ADD, self.displayPopupToCreateGroup, (selectedGroup == None)),
                  (gtk.STOCK_REMOVE, self.displayPopupToRemoveGroup, (selectedGroup != None))
        ]

        menu = gtk.Menu()
        for stock_id, callback, sensitive in entries:
            item = gtk.ImageMenuItem(stock_id)
            item.connect("activate", callback, selectedGroup)  
            item.set_sensitive(sensitive)
            item.show()
            menu.append(item)
        menu.popup(None, None, None, event.button, event.time)


    #+---------------------------------------------- 
    #| displayPopupToCreateGroup_ResponseToDialog :
    #|   pygtk is so good ! arf :( <-- clap clap :D
    #+----------------------------------------------
    def displayPopupToCreateGroup_ResponseToDialog(self, entry, dialog, response):
        dialog.response(response)

    def displayPopupToEditGroup(self, event, group):
        self.log.debug("Display a edit to rename a group")
        dialog = gtk.MessageDialog(
        None,
        gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
        gtk.MESSAGE_QUESTION,
        gtk.BUTTONS_OK,
        None)
        dialog.set_markup('Please enter the <b>name</b> of the group:')
        #create the text input field
        entry = gtk.Entry()
        entry.set_text(group.getName())
        #allow the user to press enter to do ok
        entry.connect("activate", self.responseToDialog, dialog, gtk.RESPONSE_OK)
        #create a horizontal box to pack the entry and a label
        hbox = gtk.HBox()
        hbox.pack_start(gtk.Label("Name:"), False, 5, 5)
        hbox.pack_end(entry)
        #some secondary text
#        dialog.format_secondary_markup("Th <i>identification</i> purposes")
        #add it and show it
        dialog.vbox.pack_end(hbox, True, True, 0)
        dialog.show_all()
        #go go go
        dialog.run()
        text = entry.get_text()
        group.setName(text)
        dialog.destroy()
        #Update Left and Right
        self.updateTreeStoreGroup()
        self.updateTreeStoreMessage()

    def responseToDialog(self, entry, dialog, response):
        dialog.response(response)
    
    
    #+---------------------------------------------- 
    #| displayPopupToCreateGroup :
    #|   Display a form to create a new group.
    #|   Based on the famous dialogs
    #+----------------------------------------------
    def displayPopupToCreateGroup(self, event, group):
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
        
        if (len(newGroupName) > 0) :
            self.log.debug("a new group will be created with the given name : {0}".format(newGroupName))
            
            newGroup = MessageGroup.MessageGroup(newGroupName, [])
            self.treeGroupGenerator.addGroup( newGroup )
            #Update Left and Right
            self.updateTreeStoreGroup()
            self.updateTreeStoreMessage()
        
        
    #+---------------------------------------------- 
    #| displayPopupToRemoveGroup :
    #|   Display a popup to remove a group
    #|   the removal of a group can only occurs
    #|   if its an empty group
    #+----------------------------------------------    
    def displayPopupToRemoveGroup(self, event, group):
        self.log.debug("Display a popup to create a group")
        
        if (len(group.getMessages()) == 0) :
            self.log.debug("Can remove the group {0} since it's an empty one.".format(group.getName()))
            questionMsg = "Click yes to confirm the removal of the group {0}".format(group.getName())
            md = gtk.MessageDialog(None, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_QUESTION, gtk.BUTTONS_YES_NO, questionMsg)
            result = md.run()
            md.destroy()
            if result == gtk.RESPONSE_YES:
                self.treeGroupGenerator.removeGroup( group )
                self.log.debug("The group "+group.getName()+" has been deleted !")
                #Update Left and Right
                self.updateTreeStoreGroup()
                self.updateTreeStoreMessage()
            else :
                self.log.debug("The user didn't confirm the deletion of the group "+group.getName())                
            
        else :
            self.log.debug("Can't remove the group {0} since its not an empty one.".format(group.getName()))
            errorMsg = "The selected group cannot be removed since it has messages."
            md = gtk.MessageDialog(None, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_ERROR, gtk.BUTTONS_CLOSE, errorMsg)
            md.run()
            md.destroy()
        
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
            for tmp_group in self.treeGroupGenerator.getGroups() :
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
            self.zob.uiDumpingMessage.updateGoups( self.treeGroupGenerator.getGroups() )
 
    #+---------------------------------------------- 
    #| Update the content of the tree store for messages
    #+----------------------------------------------
    def updateTreeStoreMessage(self):        
        if (self.selectedGroup != "") :
            # Search for the selected group in groups list
            selectedGroup = None
            for group in self.treeGroupGenerator.getGroups() :
                if str(group.getID()) == self.selectedGroup :
                    selectedGroup = group
            # If we found it we can update the content of the treestore        
            if selectedGroup != None :
                self.treeMessageGenerator.default(selectedGroup)
                # enable dragging message out of current group
                self.treeMessageGenerator.getTreeview().enable_model_drag_source(gtk.gdk.BUTTON1_MASK, self.TARGETS, gtk.gdk.ACTION_DEFAULT | gtk.gdk.ACTION_MOVE)
                self.treeMessageGenerator.getTreeview().connect("drag-data-get", self.drag_fromDND)      




#                self.treeMessageGenerator.getTreeview().connect("cursor-changed", self.messageSelected) 




            # Else, quite weird so throw a warning
            else :
                self.log.warning("Impossible to update the treestore message since we cannot find the selected group according to its name " + self.selectedGroup)

    #+---------------------------------------------- 
    #| Update the content of the tree store for type structure
    #+----------------------------------------------
    def updateTreeStoreTypeStructure(self):
        self.treeTypeStructureGenerator.default()
       
    #+---------------------------------------------- 
    #| Called when a message is selected
    #+----------------------------------------------
    def messageSelected(self, treeview) :
        (model, iter) = treeview.get_selection().get_selected()
        if(iter):
            if(model.iter_is_valid(iter)):
                msg_id = model.get_value(iter, 0)
                group = self.treeMessageGenerator.getGroup()
                message = group.getMessageByID( msg_id )
                self.treeTypeStructureGenerator.setGroup( group )
                self.treeTypeStructureGenerator.setMessage( message )
                messageTable = []
                for i in range(len(group.getRegex())):
                    messageTable.append( model.get_value(iter, i + 4) )
                self.treeTypeStructureGenerator.buildTypeStructure(messageTable, msg_id) # Not very clean :)
                self.updateTreeStoreTypeStructure()

                """
                group_regex = modele.get_value(iter, 1)
                pango = modele.get_value(iter, 2)
                
                for group in self.treeGroupGenerator.getGroups() :
                    for message in group.getMessages() :
                        if str(message.getID()) == msg_id :
                            self.selectedMessage = message
                            self.log.debug("selected message {0}".format(self.selectedMessage.getID()))     
                            self.updateTreeStoreGroup()
                """

    #+---------------------------------------------- 
    #| Called when user click on a group or on a message
    #+----------------------------------------------
    def groupChanged(self, treeview):
        (modele, iter) = treeview.get_selection().get_selected()
        if(iter):
            if(modele.iter_is_valid(iter)):
                idGroup = modele.get_value(iter, 0)
                score = modele.get_value(iter, 1)
                self.selectedGroup = idGroup
                self.updateTreeStoreMessage()
                self.treeTypeStructureGenerator.clear()
                self.updateTreeStoreTypeStructure()

    #+---------------------------------------------- 
    #| Called when user select a new score limit
    #+----------------------------------------------
    def updateScoreLimit(self, combo):
        val = combo.get_active_text()
        configParser = ConfigurationParser.ConfigurationParser()
        configParser.set("clustering", "equivalence_threshold", val)

    #+---------------------------------------------- 
    #| Called when user wants to slick internally in libNeedleman
    #+----------------------------------------------
    def activeInternalSlickRegexes(self, checkButton):
        configParser = ConfigurationParser.ConfigurationParser()
        configParser.set("clustering", "do_internal_slick", (0, 1)[checkButton.get_active()])

    #+---------------------------------------------- 
    #| Called when user wants to modify the expected protocol type
    #+----------------------------------------------
    def updateProtocolType(self, combo):
        valID = combo.get_active()
        configParser = ConfigurationParser.ConfigurationParser()
        configParser.set("clustering", "protocol_type", valID)

        if valID == 0:
            aType = "ascii"
        else:
            aType = "binary"
        if self.treeMessageGenerator != None and self.treeMessageGenerator.getGroup() != None:
            self.treeMessageGenerator.getGroup().setTypeForCols( aType )
            self.update()

    #+---------------------------------------------- 
    #| Called when user wants to find the potential size fields
    #+----------------------------------------------
    def findSizeFields(self, button):
        dialog = gtk.Dialog(title="Potential size fields and related payload", flags=0, buttons=None)
        textview = gtk.TextView()

        # Chose button
        but = gtk.Button(label="Apply size field")
        but.show()
#        but.connect("clicked", self.doSplitColumn, textview, iCol, dialog)
        dialog.action_area.pack_start(but, True, True, 0)

        # Text view containing potential size fields
        frame = gtk.Frame()
        frame.set_label("Potential size fields and related payload")
        frame.show()
        textview.set_size_request(800, 300)
        foundSizeFields = self.treeGroupGenerator.findSizeFields()
        if foundSizeFields != None:
            for sizeField in foundSizeFields:
                textview.get_buffer().insert( textview.get_buffer().get_end_iter(), sizeField + "\n" )
        textview.show()
        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scroll.show()
        scroll.add(textview)
        frame.add(scroll)
        dialog.vbox.pack_start(frame, True, True, 0)
        dialog.show()
