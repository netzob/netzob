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


class MessageTableView(object):

    MAX_DISPLAYED_FIELDS = 200

    def __init__(self, controller):
        self.controller = controller
        self.builder = Gtk.Builder()
        self.builder.add_from_file(os.path.join(
            ResourcesConfiguration.getStaticResources(),
            "ui", "vocabulary",
            "messageTable.glade"))
        self._getObjects(self.builder, ["messageTableBox",
                                        "fieldNameLabel",
                                        "messageTableScrolledWindow"])
        self.builder.connect_signals(self.controller)
        self.displayedField = None
        # Make an empty treeview
        self.messageTableTreeView = self.__makeMessageTreeView()
        self.messageTableScrolledWindow.add(self.messageTableTreeView)
        self.messageTableTreeView.show()
        self.treeViewHeaderGroup = TreeViewHeaderWidgetGroup()

    def _getObjects(self, builder, objectsList):
        for object in objectsList:
            setattr(self, object, builder.get_object(object))

    def __makeMessageTreeView(self):
        # Instanciate treeview
        messageTableTreeView = Gtk.TreeView()
        messageTableTreeView.connect("enter-notify-event", self.controller.messageTableTreeView_enter_notify_event_cb)
        messageTableTreeView.connect("leave-notify-event", self.controller.messageTableTreeView_leave_notify_event_cb)
        messageTableTreeView.connect("button-press-event", self.controller.messageTableTreeView_button_press_event_cb)
        messageTableTreeView.get_selection().set_mode(Gtk.SelectionMode.MULTIPLE)
        messageTableTreeView.get_selection().connect("changed", self.controller.messageTableTreeView_changed_event_cb)
        messageTableTreeView.set_rules_hint(True)
        messageTableTreeView.set_grid_lines(Gtk.TreeViewGridLines.BOTH)
        # Configures it as a Drag Source
        messageTableTreeView.enable_model_drag_source(Gdk.ModifierType.BUTTON1_MASK, [], Gdk.DragAction.MOVE)
        messageTableTreeView.connect("drag-data-get", self.__drag_data_get_event)
        messageTableTreeView.drag_source_add_text_targets()

        # Create columns
        if self.displayedField is None or len(self.displayedField.getExtendedFields()) < 1:
            return messageTableTreeView
        startOfColumns = 1 + self.displayedField.getExtendedFields()[0].getIndex()
        numOfColumns = startOfColumns + min(self.MAX_DISPLAYED_FIELDS, len(self.displayedField.getExtendedFields()))

        self.treeViewHeaderGroup.clear()
        for colIdx in range(startOfColumns, numOfColumns):
            (tvc, head) = self.__makeTreeViewColumn(startOfColumns, colIdx)
            #tvc.set_clickable(True)
            messageTableTreeView.append_column(tvc)
            but = tvc.get_button()
            box = but.get_children()[0]
            align = box.get_children()[0]
            align.connect("size-allocate", propagate_size_allocation)
            self.treeViewHeaderGroup.add(head)

        # Setup column headers.
        columns = messageTableTreeView.get_columns()
        for column in columns:
            column_widget = column.get_widget()
            column_header = find_closest_ancestor(column_widget, Gtk.Button)
            if column_header:
                column_header.connect('button-press-event', propagate_button_press_event)
                column_header.set_focus_on_click(False)
        return messageTableTreeView

    def refreshProperties(self):
        """refresh the properties like background color"""
        self.messageTableTreeView.queue_draw()

    def __makeTreeViewColumn(self, startOfColumns, i):
        i = i - 1
        markupCellRenderer = Gtk.CellRendererText()
        treeViewColumn = Gtk.TreeViewColumn()
        field = self.displayedField.getFieldByIndex(i)
        headerWidget = TreeViewHeaderWidget(field,
                                            treeViewColumn,
                                            self)
        treeViewColumn.set_widget(headerWidget)
        treeViewColumn.set_resizable(True)
        treeViewColumn.pack_start(markupCellRenderer, True)
        treeViewColumn.add_attribute(markupCellRenderer, "markup", i + 2 - startOfColumns)
        markupCellRenderer.set_property("font", "monospace")
        return (treeViewColumn, headerWidget)

    def setDisplayedField(self, field):
        """Memorizes field as the displayed field in this message table
        and updates itself to display this field."""
        self.displayedField = field
        self.update()

    def getDisplayedField(self):
        """Returns the currently displayed field in this message table"""
        return self.displayedField

    def updateMessageTableTreeView(self):
        """Performs a full update on the treeview displaying messages.
        You should call this method only if you need a full update
        of the table"""
        logging.debug("Start to update the message table")
        ## Remove former TreeView if necessary
        if self.messageTableTreeView is not None:
            self.messageTableScrolledWindow.remove(self.messageTableTreeView)
        if self.displayedField is None:
            return
        ## Create a new treeview
        self.messageTableTreeView = self.__makeMessageTreeView()
        ## Create and fill store for the create tree view
        self.updateMessageTableListStore()
        ## Display newly created treeview
        self.messageTableScrolledWindow.add(self.messageTableTreeView)
        self.messageTableTreeView.show()
        logging.debug("End to update the message table")

    def updateMessageTableListStore(self):
        """Updates the liststore containing the displayed messages.
        You should call this method when you need the messages displayed
        in the treeview to be refreshed and the fields of the symbol have not
        changed. (ie the columns of the treeview won't be updated)"""
        splitMessagesMatrix = []

        messages = self.displayedField.getMessages()

        # Split every message
        logging.debug("Align {0} messages with regex {1}".format(len(messages), self.displayedField.getRegex()))
        for message in messages:
            try:
                splitMessage = [str(message.getID())]
                tmpSplitMessage = message.applyAlignment(styled=True, encoded=True)
                tmpSplitMessage = tmpSplitMessage[self.displayedField.getExtendedFields()[0].getIndex():self.displayedField.getExtendedFields()[-1].getIndex() + 1]
                splitMessage.extend(tmpSplitMessage)
            except NetzobException:
                logging.warn("Impossible to display one of messages since it cannot be cut according to the computed regex.")
                logging.warn("Message: {0}".format(str(message.getStringData())))
                continue  # We don't display the message in error
            splitMessagesMatrix.append(splitMessage)
        logging.debug("Alignent computed")
        # Setup listStore
        numOfColumns = min(self.MAX_DISPLAYED_FIELDS,
                           len(self.displayedField.getExtendedFields()))
        # the list store must include the ID and a column for every field
        listStoreTypes = [str] * (numOfColumns + 1)
        self.messageTableListStore = Gtk.ListStore(*listStoreTypes)
        # Fill listStore with split messages
        for splitMessage in splitMessagesMatrix:
            self.messageTableListStore.append(splitMessage)
        self.messageTableTreeView.set_model(self.messageTableListStore)

    def sortMessagesByField(self, field, sortType):
        """Sorts the messages displayed in the treeview by field field in the
        order specified by sortType.
        If field is None, the treeview is restored to its original
        "unsorted" state."""
        sortTypeMap = {TreeViewHeaderWidget.SORT_ASCENDING: Gtk.SortType.ASCENDING,
                       TreeViewHeaderWidget.SORT_DESCENDING: Gtk.SortType.DESCENDING}
        if field == None:
            sortIndex = -2
        else:
            sortIndex = field.getIndex()
        self.messageTableListStore.set_sort_column_id(sortIndex, sortTypeMap[sortType])
        self.treeViewHeaderGroup.setAllColumnsSortIndicator(sortIndex, sortType)

    def updateFieldNameLabel(self):
        """Udpates the label displaying the field name."""
        if self.displayedField is None:
            fieldName = "Empty Message Table"
        else:
            fieldName = self.displayedField.getName()
        self.fieldNameLabel.set_text(fieldName)

    def setSelected(self, selected):
        """Selects or unselects the message table."""
        if selected:
            boldFont = Pango.FontDescription()
            boldFont.set_weight(Pango.Weight.BOLD)
            self.fieldNameLabel.modify_font(boldFont)
        else:
            selection = self.messageTableTreeView.get_selection()
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
                header.titleLabel.modify_font(boldFont)
            else:
                header.setSelected(False)
               # change background of column
                if header.treeViewColumn is not None and header.treeViewColumn.get_cells() is not None and len(header.treeViewColumn.get_cells()) > 0:
                    cellRenderer = header.treeViewColumn.get_cells()[0]
                    cellRenderer.set_property("background", "white")
                    self.refreshProperties()
                normalFont = Pango.FontDescription()
                normalFont.set_weight(Pango.Weight.NORMAL)
                header.titleLabel.modify_font(normalFont)
            if header == lastSelectedHeader:
                goSelect = False

    def update(self):
        self.updateFieldNameLabel()
        self.updateMessageTableTreeView()

    def getPanel(self):
        return self.messageTableBox

    def destroy(self):
        self.messageTableBox.destroy()


class TreeViewHeaderWidget(Gtk.VBox):
    """Header Widget for columns of TreeViews displaying symbol messages.
    This header is designed to display properties of a symbol field, like :
    - Name
    - Corresponding Regex
    - Display format
    The following actions can by perform of the field/column:
    - Sort messages
    - Change display format
    - Collapse column

    This header widget has different "display" state controlling its size,
    and the amount of information displayed:
    - In collapsed state, the column is collapsed horizontally and the only
    widget displayed is an arrow to expand it
    - In unfocused state, the field name and it regex are displayed as well
    as arrow controls to collapse the column and sort it.
    - In focused state, the display format is added to the information displayed
    in unfocused state.
    """

    # This header has different states, controlling the amount
    # of information displayed and therefore its size
    STATE_FOCUSED = 0    # Fully displayed header (ie including display format)
    STATE_UNFOCUSED = 1  # "Reduced" header (display format hidden)
    STATE_COLLAPSED = 2  # Collapsed column

    # Constants defining the sort status (not sorted, sorted in ascending order,
    # sorted in descending order).
    SORT_NONE = 0
    SORT_ASCENDING = 1
    SORT_DESCENDING = 2

    def __init__(self, field, treeViewColumn, messageTableView):
        Gtk.VBox.__init__(self)
        self.field = field
        self.treeViewColumn = treeViewColumn
        self.messageTableView = messageTableView
        self.__setupUI()
        self.__setState(self.STATE_FOCUSED)
        self.__setRegexMarkup(field.getEncodedVersionOfTheRegex())
        self.__setTitle(field.getName())
        self.setFormat(field.getFormat())
        self.focused = True
        self.collapsed = False
        self.setSortIndicator(self.SORT_NONE)
        self.setSelected(False)

    def __setupUI(self):
        """Setup GTK widgets"""
        # Title and arrows
        self.titleLabel = Gtk.Label()
        self.titleLabel.set_property("margin-right", 20)
        self.titleEventBox = Gtk.EventBox()
        self.titleEventBox.add(self.titleLabel)
        self.titleEventBox.connect("button-press-event", self.titleEventBox_button_press_event_cb)
        self.titleEventBox.set_visible_window(False)
        self.collapseArrow = Gtk.Arrow(Gtk.ArrowType.LEFT, Gtk.ShadowType.NONE)
        self.sortArrow = Gtk.Arrow(Gtk.ArrowType.DOWN, Gtk.ShadowType.NONE)
        self.collapseEventBox = Gtk.EventBox()
        self.collapseEventBox.add(self.collapseArrow)
        self.collapseEventBox.connect("button-press-event", self.collapseEventBox_button_press_event_cb)
        self.collapseEventBox.set_visible_window(False)
        self.sortEventBox = Gtk.EventBox()
        self.sortEventBox.add(self.sortArrow)
        self.sortEventBox.connect("button-press-event", self.sortEventBox_button_press_event_cb)
        self.sortEventBox.set_visible_window(False)
        self.titleArrowBox = Gtk.HBox()

        # Regex
        self.regexEventBox = Gtk.EventBox()
        self.regexEventBox.modify_bg(Gtk.StateType.NORMAL, Gdk.Color.parse("#c8c8c8")[1])
        self.regexLabel = Gtk.Label()
        self.regexEventBox.add(self.regexLabel)
        boldFont = Pango.FontDescription()
        boldFont.set_weight(Pango.Weight.BOLD)
        self.regexLabel.modify_font(boldFont)
        # Format button
        self.formatLabel = Gtk.Label()
        self.formatEventBox = Gtk.EventBox()
        self.formatEventBox.add(self.formatLabel)
        self.formatEventBox.connect("button-press-event", self.formatEventBox_button_press_event_cb)

    def __setState(self, state):
        """Set the display state, see comment in class header
        (ie collapsed, focused, unfocused) and update
        its contents accordingly"""
        self.state = state
        # Remove all children
        for child in self.get_children():
            self.remove(child)
        for child in self.titleArrowBox.get_children():
            self.titleArrowBox.remove(child)

        if state == self.STATE_COLLAPSED:
            self.collapseArrow.set(Gtk.ArrowType.RIGHT, Gtk.ShadowType.NONE)
            self.pack_start(self.collapseEventBox, False, False, 0)
            w, _ = self.get_preferred_width()
            self.treeViewColumn.set_max_width(w + 6)
            self.treeViewColumn.set_min_width(w + 6)
        if state == self.STATE_FOCUSED or state == self.STATE_UNFOCUSED:
            self.collapseArrow.set(Gtk.ArrowType.LEFT, Gtk.ShadowType.NONE)
            self.titleArrowBox.pack_start(self.titleEventBox, True, True, 0)
            self.titleArrowBox.pack_start(self.sortEventBox, False, False, 0)
            self.titleArrowBox.pack_start(self.collapseEventBox, False, False, 0)
            self.treeViewColumn.set_max_width(-1)
            self.treeViewColumn.set_min_width(-1)
        if state == self.STATE_UNFOCUSED:
            self.pack_start(self.titleArrowBox, False, False, 0)
            self.pack_start(self.regexEventBox, False, False, 0)
        if state == self.STATE_FOCUSED:
            self.pack_start(self.titleArrowBox, False, False, 0)
            self.pack_start(self.regexEventBox, False, False, 0)
            self.pack_start(self.formatEventBox, False, False, 0)
        self.show_all()

    def __resetSortArrow(self):
        """Re-create the arrow widget used to display the current.
        This method"""
        self.sortEventBox.remove(self.sortArrow)
        self.sortArrow = Gtk.Arrow(Gtk.ArrowType.DOWN, Gtk.ShadowType.NONE)
        self.sortArrow.show()
        self.sortEventBox.add(self.sortArrow)

    def __setTitle(self, title):
        """Sets the string displayed in the title label"""
        self.titleLabel.set_text(title)

    def __setRegexMarkup(self, regex):
        """"Sets the string displayed in the regex label"""
        self.regexLabel.set_text(GLib.markup_escape_text(regex))

    def setFormat(self, format_):
        """Sets the string displayed in the format label"""
        self.formatLabel.set_text(format_)

    def setSortIndicator(self, sortStatus):
        """Sets the sort indicator arrow to reflect sortStatus."""
        self.sortStatus = sortStatus
        if sortStatus == self.SORT_ASCENDING:
            self.sortArrow.set(Gtk.ArrowType.UP, Gtk.ShadowType.NONE)
            self.sortArrow.modify_fg(Gtk.StateType.NORMAL, Gdk.Color.parse("red")[1])
        elif sortStatus == self.SORT_DESCENDING:
            self.sortArrow.set(Gtk.ArrowType.DOWN, Gtk.ShadowType.NONE)
            self.sortArrow.modify_fg(Gtk.StateType.NORMAL, Gdk.Color.parse("red")[1])
        elif sortStatus == self.SORT_NONE:
            self.__resetSortArrow()

    def setFocus(self, focused):
        """Set the 'focused' state of the header, and modify its appearance
        accordingly. If a column header is in unfocused mode, some information
        in contains will be hidden. The header widget remembers its focused state,
        after it was collapsed. For example, in you set the state of a header
        to unfocused, collapse it and the expand it, it will be restored in
        unfocused mode"""
        self.focused = focused
        if focused and not self.collapsed:
            self.__setState(self.STATE_FOCUSED)
        elif not focused and not self.collapsed:
#            self.__setState(self.STATE_UNFOCUSED)
            pass

    def setCollapsed(self, collapsed):
        """Set the 'collapsed' state of the header, and modify its appearance
        accordingly. If a column header is in collapsed mode,
        the column is collapsed horizontally and the only widget displayed
        is an arrow to expand it."""
        self.collapsed = collapsed
        if collapsed:
            self.__setState(self.STATE_COLLAPSED)
        elif not collapsed and not self.focused:
            self.__setState(self.STATE_UNFOCUSED)
        elif not collapsed and self.focused:
            self.__setState(self.STATE_FOCUSED)

    def getSelected(self):
        """Returns True if the column is selected, False otherwise."""
        return self.selected

    def setSelected(self, selected):
        """Selects or unselects the column"""
        self.selected = selected

    ## Callbacks
    def formatEventBox_button_press_event_cb(self, *args):
        supportedFormats = Format.getSupportedFormats()
        currentFormat = self.field.getFormat()
        currentFormatIdx = supportedFormats.index(currentFormat)
        newFormat = supportedFormats[(currentFormatIdx + 1) % len(supportedFormats)]
        self.field.setFormat(newFormat)
        self.setFormat(newFormat)
        self.messageTableView.updateMessageTableListStore()

    def sortEventBox_button_press_event_cb(self, *args):
        if self.sortStatus == self.SORT_NONE:
            self.messageTableView.sortMessagesByField(self.field, self.SORT_DESCENDING)
            self.setSortIndicator(self.SORT_DESCENDING)
        elif self.sortStatus == self.SORT_DESCENDING:
            self.messageTableView.sortMessagesByField(self.field, self.SORT_ASCENDING)
            self.setSortIndicator(self.SORT_ASCENDING)
        elif self.sortStatus == self.SORT_ASCENDING:
            self.messageTableView.sortMessagesByField(None, self.SORT_ASCENDING)
            self.setSortIndicator(self.SORT_NONE)

    def collapseEventBox_button_press_event_cb(self, *args):
        self.setCollapsed(not self.collapsed)

    def titleEventBox_button_press_event_cb(self, *args):
        self.messageTableView.controller.vocabularyPerspective.setSelectedMessageTable(self.messageTableView)
        self.setSelected(not self.selected)
        self.messageTableView.updateBackgroundColor(self)

        # Emit Signals to update toolbar status
        nbSelectedFields = len(self.messageTableView.treeViewHeaderGroup.getSelectedFields())
        signalsManager = self.messageTableView.controller.getSignalsManager()
        if nbSelectedFields == 0:
            signalsManager.emitSignal(SignalsManager.SIG_FIELDS_NO_SELECTION)
        elif nbSelectedFields == 1:
            signalsManager.emitSignal(SignalsManager.SIG_FIELDS_SINGLE_SELECTION)
        elif nbSelectedFields > 1:
            signalsManager.emitSignal(SignalsManager.SIG_FIELDS_MULTIPLE_SELECTION)


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

    def getSelectedFields(self):
        """Returns the fields displayed in columns whose header are selected"""
        return [header.field for header in self.getSelectedHeaders()]

    def setAllColumnsFocus(self, focused):
        """Set the focused state of all the headers in the group"""
        for header in self.headerList:
            header.setFocus(focused)

    def setAllColumnsSortIndicator(self, index, sortType):
        """Sets the sort indicator of all columns belonging to
        this group. It can be used to reset the sort indicator of all columns
        to its unsorted base state"""
        for header in self.headerList:
            if header.field.getIndex() != index:
                header.setSortIndicator(header.SORT_NONE)
            else:
                header.setSortIndicator(sortType)


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
