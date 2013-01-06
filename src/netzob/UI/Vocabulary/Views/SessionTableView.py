# -*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|          01001110 01100101 01110100 01111010 01101111 01100010            |
#|                                                                           |
#|               Netzob : Inferring communication protocols                  |
#+---------------------------------------------------------------------------+
#| Copyright (C) 2011 Georges Bossert and Frédéric Guihéry                   |
#| This program is free software: you can redistribute it and/or modify      |
#| it under the terms of the GNU General Public License as published by      |
#| the Free Software Foundation, either version 3 of the License, or         |
#| (at your option) any later version.                                       |
#|                                                                           |
#| This program is distributed in the hope that it will be useful,           |
#| but WITHOUT ANY WARRANTY; without even the implied warranty of            |
#| MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the              |
#| GNU General Public License for more details.                              |
#|                                                                           |
#| You should have received a copy of the GNU General Public License         |
#| along with this program. If not, see <http://www.gnu.org/licenses/>.      |
#+---------------------------------------------------------------------------+
#| @url      : http://www.netzob.org                                         |
#| @contact  : contact@netzob.org                                            |
#| @sponsors : Amossys, http://www.amossys.fr                                |
#|             Supélec, http://www.rennes.supelec.fr/ren/rd/cidre/           |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Standard library imports
#+---------------------------------------------------------------------------+
import os
import logging

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+
from gi.repository import Gtk, Gdk, GLib, Pango
import gi
from netzob.Common.SignalsManager import SignalsManager
gi.require_version('Gtk', '3.0')

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.NetzobException import NetzobException
from netzob.Common.ResourcesConfiguration import ResourcesConfiguration
from netzob.Common.Type.Format import Format
from netzob.Common.Type.TypeConvertor import TypeConvertor


class SessionTableView(object):

    def __init__(self, controller):
        self.controller = controller
        self.builder = Gtk.Builder()
        self.builder.add_from_file(os.path.join(
            ResourcesConfiguration.getStaticResources(),
            "ui", "vocabulary",
            "sessionTable.glade"))
        self._getObjects(self.builder, ["sessionTableBox",
                                        "fieldNameLabel",
                                        "sessionTableScrolledWindow"])
        self.builder.connect_signals(self.controller)
        self.displayedObject = None
        # Make an empty treeview
        self.sessionTableTreeView = self.__makeMessageTreeView()
        self.sessionTableScrolledWindow.add(self.sessionTableTreeView)
        self.sessionTableTreeView.show()
        self.treeViewHeaderGroup = TreeViewHeaderWidgetGroup()

    def _getObjects(self, builder, objectsList):
        for object in objectsList:
            setattr(self, object, builder.get_object(object))

    def __makeMessageTreeView(self):
        # Instanciate treeview
        sessionTableTreeView = Gtk.TreeView()
        sessionTableTreeView.connect("enter-notify-event", self.controller.sessionTableTreeView_enter_notify_event_cb)
        sessionTableTreeView.connect("leave-notify-event", self.controller.sessionTableTreeView_leave_notify_event_cb)
        sessionTableTreeView.connect("button-press-event", self.controller.sessionTableTreeView_button_press_event_cb)
        sessionTableTreeView.get_selection().set_mode(Gtk.SelectionMode.MULTIPLE)
        sessionTableTreeView.get_selection().connect("changed", self.controller.sessionTableTreeView_changed_event_cb)
        sessionTableTreeView.set_rules_hint(True)
        sessionTableTreeView.set_grid_lines(Gtk.TreeViewGridLines.BOTH)
        # Configures it as a Drag Source
        sessionTableTreeView.enable_model_drag_source(Gdk.ModifierType.BUTTON1_MASK, [], Gdk.DragAction.MOVE)
        sessionTableTreeView.connect("drag-data-get", self.__drag_data_get_event)
        sessionTableTreeView.drag_source_add_text_targets()

        # Create columns
        if self.displayedObject is None:
            return sessionTableTreeView
        startOfColumns = 1 + 1
        numOfColumns = startOfColumns + 1

        self.treeViewHeaderGroup.clear()
        for colIdx in range(startOfColumns, numOfColumns):
            (tvc, head) = self.__makeTreeViewColumn(startOfColumns, colIdx)
            #tvc.set_clickable(True)
            sessionTableTreeView.append_column(tvc)
            but = tvc.get_button()
            box = but.get_children()[0]
            align = box.get_children()[0]
            align.connect("size-allocate", propagate_size_allocation)
            self.treeViewHeaderGroup.add(head)

        # Setup column headers.
        columns = sessionTableTreeView.get_columns()
        for column in columns:
            column_widget = column.get_widget()
            column_header = find_closest_ancestor(column_widget, Gtk.Button)
            if column_header:
                column_header.connect('button-press-event', propagate_button_press_event)
                column_header.set_focus_on_click(False)
        return sessionTableTreeView

    def refreshProperties(self):
        """refresh the properties like background color"""
        self.sessionTableTreeView.queue_draw()

    def __makeTreeViewColumn(self, startOfColumns, i):
        i = i - 1
        markupCellRenderer = Gtk.CellRendererText()
        treeViewColumn = Gtk.TreeViewColumn()
        session = self.displayedObject
        headerWidget = TreeViewHeaderWidget(session,
                                            treeViewColumn,
                                            self)
        treeViewColumn.set_widget(headerWidget)
        treeViewColumn.set_resizable(True)
        treeViewColumn.pack_start(markupCellRenderer, True)
        treeViewColumn.add_attribute(markupCellRenderer, "markup", i + 2 - startOfColumns)
        markupCellRenderer.set_property("font", "monospace")
        return (treeViewColumn, headerWidget)

    def setDisplayedObject(self, session):
        """Memorizes session as the displayed session in this message table
        and updates itself to display this session."""
        self.displayedObject = session
        self.update()

    def getDisplayedObject(self):
        """Returns the currently displayed session in this message table"""
        return self.displayedObject

    def updateSessionTableTreeView(self):
        """Performs a full update on the treeview displaying messages.
        You should call this method only if you need a full update
        of the table"""
        logging.debug("Start to update the message table")
        ## Remove former TreeView if necessary
        if self.sessionTableTreeView is not None:
            self.sessionTableScrolledWindow.remove(self.sessionTableTreeView)
        if self.displayedObject is None:
            return
        ## Create a new treeview
        self.sessionTableTreeView = self.__makeMessageTreeView()
        ## Create and fill store for the create tree view
        self.updateSessionTableListStore()
        ## Display newly created treeview
        self.sessionTableScrolledWindow.add(self.sessionTableTreeView)
        self.sessionTableTreeView.show()
        logging.debug("End to update the message table")

    def updateSessionTableListStore(self):
        """Updates the liststore containing the displayed messages.
        You should call this method when you need the messages
        displayed in the treeview to be refreshed and the session have
        not changed. (ie the columns of the treeview won't be updated)"""
        splitMessagesMatrix = []

        messages = self.displayedObject.getMessages()

        # Setup listStore
        numOfColumns = 1
        # The list store must include the ID and a column for every field
        listStoreTypes = [str] * (numOfColumns + 1)
        self.sessionTableListStore = Gtk.ListStore(*listStoreTypes)
        # Fill listStore with messages
        session = self.getDisplayedObject()
        for message in messages:
            data = TypeConvertor.encodeNetzobRawToGivenType(message.getStringData(), session.getFormat())
            self.sessionTableListStore.append([str(message.getID()), data])
        self.sessionTableTreeView.set_model(self.sessionTableListStore)

    def updateFieldNameLabel(self):
        """Udpates the label displaying the field name."""
        if self.displayedObject is None:
            fieldName = "Empty Message Table"
        else:
            fieldName = self.displayedObject.getName()
        self.fieldNameLabel.set_text(fieldName)

    def setSelected(self, selected):
        """Selects or unselects the message table."""
        if selected:
            boldFont = Pango.FontDescription()
            boldFont.set_weight(Pango.Weight.BOLD)
            self.fieldNameLabel.modify_font(boldFont)
        else:
            selection = self.sessionTableTreeView.get_selection()
            if selection is not None:
                selection.unselect_all()
            for header in self.treeViewHeaderGroup.getSelectedHeaders():
                header.setSelected(False)
            normalFont = Pango.FontDescription()
            normalFont.set_weight(Pango.Weight.NORMAL)
            self.fieldNameLabel.modify_font(normalFont)

    def __drag_data_get_event(self, widget, drag_context, data, info, time):
        """Callback executed when the user request this treeview as the the
        source of its drag and drop operation"""
        (model, rows) = widget.get_selection().get_selected_rows()
        if rows is not None:
            for row in rows:
                msgID = model[row][0]
                if msgID is not None:
                    data.set_text("m:{0}".format(msgID), -1)

    def updateBackgroundColor(self, currentSelectedHeader):
        # Retrieve first and last selected headers
        selectedHeaders = []
        for header in self.treeViewHeaderGroup.getHeaders():
            if header.getSelected():
                selectedHeaders.append(header)
        if len(selectedHeaders) < 1:
            firstSelectedHeader = None
            lastSelectedHeader = None
        else:
            firstSelectedHeader = selectedHeaders[0]
            lastSelectedHeader = selectedHeaders[-1]

        # Retrieve selected header range
        goSelect = False
        for header in self.treeViewHeaderGroup.getHeaders():
            if header == firstSelectedHeader:
                goSelect = True
            if header == currentSelectedHeader and not currentSelectedHeader.getSelected():
                goSelect = False
            if goSelect:
                header.setSelected(True)
                # change background of column
                if header.treeViewColumn is not None and header.treeViewColumn.get_cells() is not None and len(header.treeViewColumn.get_cells()) > 0:
                    cellRenderer = header.treeViewColumn.get_cells()[0]
                    cellRenderer.set_property("background", "grey")
                    self.refreshProperties()
                boldFont = Pango.FontDescription()
                boldFont.set_weight(Pango.Weight.BOLD)
            else:
                header.setSelected(False)
               # change background of column
                if header.treeViewColumn is not None and header.treeViewColumn.get_cells() is not None and len(header.treeViewColumn.get_cells()) > 0:
                    cellRenderer = header.treeViewColumn.get_cells()[0]
                    cellRenderer.set_property("background", "white")
                    self.refreshProperties()
                normalFont = Pango.FontDescription()
                normalFont.set_weight(Pango.Weight.NORMAL)
            if header == lastSelectedHeader:
                goSelect = False

    def update(self):
        self.updateFieldNameLabel()
        self.updateSessionTableTreeView()

    def getPanel(self):
        return self.sessionTableBox

    def destroy(self):
        self.sessionTableBox.destroy()


class TreeViewHeaderWidget(Gtk.VBox):
    """Header Widget for columns of TreeViews displaying session messages.
    This header is designed to display properties of a session session, like :
    - Name
    - Display format
    The following actions can by perform of the session/column:
    - Change display format

    This header widget has different "display" state controlling its size,
    and the amount of information displayed:
    - In unfocused state, the session name is displayed as well
    as arrow controls to collapse the column.
    - In focused state, the display format is added to the information displayed
    in unfocused state.
    """

    # This header has different states, controlling the amount
    # of information displayed and therefore its size
    STATE_FOCUSED = 0    # Fully displayed header (ie including display format)
    STATE_UNFOCUSED = 1  # "Reduced" header (display format hidden)

    def __init__(self, session, treeViewColumn, sessionTableView):
        Gtk.VBox.__init__(self)
        self.session = session
        self.treeViewColumn = treeViewColumn
        self.sessionTableView = sessionTableView
        self.__setupUI()
        self.__setState(self.STATE_FOCUSED)
        self.setFormat(session.getFormat())
        self.focused = True
        self.setSelected(False)

    def __setupUI(self):
        """Setup GTK widgets"""
        # Format button
        self.formatLabel = Gtk.Label()
        self.formatEventBox = Gtk.EventBox()
        self.formatEventBox.add(self.formatLabel)
        self.formatEventBox.connect("button-press-event", self.formatEventBox_button_press_event_cb)

    def __setState(self, state):
        """Set the display state, see comment in class header
        (ie focused, unfocused) and update
        its contents accordingly"""
        self.state = state
        # Remove all children
        for child in self.get_children():
            self.remove(child)

        if state == self.STATE_FOCUSED or state == self.STATE_UNFOCUSED:
            self.treeViewColumn.set_max_width(-1)
            self.treeViewColumn.set_min_width(-1)
        if state == self.STATE_UNFOCUSED:
            pass
        if state == self.STATE_FOCUSED:
            self.pack_start(self.formatEventBox, False, False, 0)
        self.show_all()

    def setFormat(self, format_):
        """Sets the string displayed in the format label"""
        self.formatLabel.set_text(format_)

    def setFocus(self, focused):
        """Set the 'focused' state of the header, and modify its appearance
        accordingly. If a column header is in unfocused mode, some information
        in contains will be hidden. The header widget remembers its focused state,
        after it was collapsed. For example, in you set the state of a header
        to unfocused, collapse it and the expand it, it will be restored in
        unfocused mode"""
        self.focused = focused
        if focused:
            self.__setState(self.STATE_FOCUSED)
        elif not focused:
#            self.__setState(self.STATE_UNFOCUSED)
            pass

    def getSelected(self):
        """Returns True if the column is selected, False otherwise."""
        return self.selected

    def setSelected(self, selected):
        """Selects or unselects the column"""
        self.selected = selected

    ## Callbacks
    def formatEventBox_button_press_event_cb(self, *args):
        supportedFormats = Format.getSupportedFormats()
        currentFormat = self.session.getFormat()
        currentFormatIdx = supportedFormats.index(currentFormat)
        newFormat = supportedFormats[(currentFormatIdx + 1) % len(supportedFormats)]
        self.session.setFormat(newFormat)
        self.setFormat(newFormat)
        self.sessionTableView.updateSessionTableListStore()


class TreeViewHeaderWidgetGroup(object):

    def __init__(self):
        self.headerList = []

    def add(self, headerWidget):
        """Adds a header widget in the group"""
        self.headerList.append(headerWidget)

    def remove(self, headerWidget):
        """Removes a header widget from the group"""
        self.headerList.remove(headerWidget)

    def clear(self):
        """Empties the group"""
        self.headerList = []

    def getHeaders(self):
        """Returns the header list"""
        return self.headerList

    def getSelectedHeaders(self):
        """Returns the header widgets which are selected"""
        return [header for header in self.headerList
                if header.getSelected()]

    def getSelectedSessions(self):
        """Returns the sessions displayed in columns whose header are selected"""
        return [header.session for header in self.getSelectedHeaders()]

    def setAllColumnsFocus(self, focused):
        """Set the focused state of all the headers in the group"""
        for header in self.headerList:
            header.setFocus(focused)


## The following functions are GTK utility functions, which are "hacks"
## to allow the treeview header widget to work properly
def propagate_button_press_event(parent, event, *data):
    """Propagates a button-press-event from the widget parent
    to the first Gtk.Button or Gtk.EventBox child encountered"""
    parent_alloc = parent.get_allocation()
    x = parent_alloc.x + int(event.x)
    y = parent_alloc.y + int(event.y)
    children = parent.get_children()
    while children:
        for child in children:
            child_alloc = child.get_allocation()
            if child_alloc.x <= x <= child_alloc.x + child_alloc.width and \
                    child_alloc.y <= y <= child_alloc.y + child_alloc.height:
                if isinstance(child, Gtk.Button) or isinstance(child, Gtk.EventBox):
                    cevent = Gdk.Event()
                    cevent.type = Gdk.EventType.FOCUS_CHANGE
                    cevent.send_event = True
                    cevent.in_ = True
                    cevent.window = event.window
                    child.emit('button-press-event', cevent, *data)
                    return True
                else:
                    if hasattr(child, 'get_children') and callable(child.get_children):
                        children = child.get_children()
                    else:
                        None
        else:
            children = None
    return False


def propagate_size_allocation(parent, allocation, *data):
    """Force the child widget of parent to occupy the same space as its
    parent."""
    children = parent.get_children()
    for child in children:
        gdkRectangle = Gdk.Rectangle()
        gdkRectangle.x = allocation.x
        gdkRectangle.y = allocation.y
        gdkRectangle.height = allocation.height
        gdkRectangle.width = allocation.width
        child.size_allocate(allocation)


def find_closest_ancestor(widget, ancestor_class):
    """Returns the closest parent of widget
    which inherit from ancestor_class"""
    if not isinstance(widget, Gtk.Widget):
        raise TypeError("%r is not a Gtk.Widget" % widget)
    ancestor = widget.get_parent()
    while ancestor is not None:
        if isinstance(ancestor, ancestor_class):
            break
        if hasattr(ancestor, 'get_parent') and callable(ancestor.get_parent):
            ancestor = ancestor.get_parent()
        else:
            None
    return ancestor
