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

#+----------------------------------------------
#| Global Imports
#+----------------------------------------------
from gettext import gettext as _
from gi.repository import GObject, Gtk, Gdk, Pango
from netzob.Common.Field import Field
from netzob.Common.Filters.Mathematic.B22Filter import BZ2Filter
from netzob.Common.Filters.Mathematic.Base64Filter import Base64Filter
from netzob.Common.Filters.Mathematic.GZipFilter import GZipFilter
from netzob.Common.Models.RawMessage import RawMessage
from netzob.Common.NetzobException import NetzobException
from netzob.Common.ProjectConfiguration import ProjectConfiguration
from netzob.Common.Symbol import Symbol
from netzob.Common.Type.Endianess import Endianess
from netzob.Common.Type.Format import Format
from netzob.Common.Type.Sign import Sign
from netzob.Common.Type.TypeConvertor import TypeConvertor
from netzob.Common.Type.UnitSize import UnitSize
from netzob.Inference.Vocabulary.Alignment.NeedlemanAndWunsch import \
    NeedlemanAndWunsch
from netzob.Inference.Vocabulary.SizeFieldIdentifier import SizeFieldIdentifier
from netzob.UI.NetzobWidgets import NetzobErrorMessage, NetzobLabel, \
    NetzobComboBoxEntry, NetzobButton, NetzobFrame
from netzob.UI.Vocabulary.Controllers.VariableController import \
    VariableTreeController
from netzob.UI.Vocabulary.Views.TreeMessageView import TreeMessageView
import glib
import logging
import time
import uuid

#+----------------------------------------------
#| Local Imports
#+----------------------------------------------


#+----------------------------------------------
#| TreeMessageController:
#|     update and generates the treeview and its
#|     treestore dedicated to the messages
#+----------------------------------------------
class TreeMessageController(object):

    #+----------------------------------------------
    #| Constructor:
    #| @param vbox : where the treeview will be hold
    #+----------------------------------------------
    def __init__(self, netzob, vocabularyController):
        self.netzob = netzob
        self.vocabularyController = vocabularyController
        self.log = logging.getLogger('netzob.UI.Vocabulary.Controllers.TreeMessageController.py')
        self.symbol = None
        self.selectedMessage = None
        self.defer_select = False
        self.view = TreeMessageView(self.netzob)
        self.initCallbacks()

    def initCallbacks(self):
        self.getTreeview().connect("drag-data-get", self.dragFromDND_cb)
        self.getTreeview().connect('button-press-event', self.buttonPressOnTreeviewMessages_cb)
        self.getTreeview().connect('button-release-event', self.buttonReleaseOnTreeviewMessages_cb)
        self.getTreeview().connect("row-activated", self.dbClickToChangeFormat_cb)

    #+----------------------------------------------
    #| Update the content of the tree store for messages
    #+----------------------------------------------
    def update(self):
        if self.netzob.getCurrentProject() is not None:
            isActive = self.netzob.getCurrentProject().getConfiguration().getVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_DISPLAY_MESSAGES)
            if isActive:
                self.view.show()
                self.default(self.vocabularyController.treeSymbolController.selectedSymbol, self.selectedMessage)
            else:
                self.view.hide()

    #+----------------------------------------------
    #| clear:
    #|         Clear the class
    #+----------------------------------------------
    def clear(self):
        self.symbol = None
        self.view.treestore.clear()

    #+----------------------------------------------
    #| error:
    #|         Update the treestore in error mode
    #+----------------------------------------------
    def error(self):
        self.log.warning("The treeview for the messages is in error mode")
        self.view.treestore.clear()

    #+----------------------------------------------
    #| show:
    #|   Display the panel
    #+----------------------------------------------
    def show(self):
        self.view.scroll.show_all()

    #+----------------------------------------------
    #| hide:
    #|   Hide the panel
    #+----------------------------------------------
    def hide(self):
        self.view.scroll.hide()

    #+----------------------------------------------
    #| default:
    #|         Update the treestore in normal mode
    #+----------------------------------------------
    def default(self, symbol, messageToHighlight=None):
        self.view.treestore.clear()

        if symbol is None:
            return

        self.symbol = symbol
        self.log.debug("Updating the treestore of the messages in default mode with the messages from the symbol " + self.symbol.getName())

        # Verifies we have everything needed for the creation of the treeview
        if (len(self.symbol.getMessages()) < 1):
            self.log.debug("It's an empty symbol so nothing to display")
            return

        # id number of the line to highlight
        nbLineMessageToHighlight = -1

        # Build the next rows from messages after applying the regex
        content_lines = []
        maxNumberOfCol = 0
        idLineMessage = 0
        for message in self.symbol.getMessages():
            # For each message we create a line and computes its cols
            try:
                messageTable = message.applyAlignment(styled=True, encoded=True)
#                for i in range(0, len(messageTable)):
#                    messageTable[i] = glib.markup_escape_text(messageTable[i])

            except NetzobException:
                self.log.warn("Impossible to display one of messages since it cannot be cut according to the computed regex.")
                self.log.warn("Message : " + str(message.getStringData()))
                continue  # We don't display the message in error

            if messageToHighlight is not None and str(message.getID()) == str(messageToHighlight.getID()):
                nbLineMessageToHighlight = idLineMessage

            line = []
            line.append(str(message.getID()))
            line.append("#ffffff")
            line.append(Pango.Weight.NORMAL)
            line.append(False)
            line.extend(messageTable)
            content_lines.append(line)
            idLineMessage = idLineMessage + 1
            if len(messageTable) > maxNumberOfCol:
                maxNumberOfCol = len(messageTable)

        # Create a TreeStore with N cols, with N := len(self.symbol.getFields())
        # str : Name of the row
        # str : Color of the row
        # int : pango type (weight bold)
        # bool : is row editable
        # [str...str] : value of cols

        treeStoreTypes = [str, str, int, GObject.TYPE_BOOLEAN]
        for i in range(0, maxNumberOfCol):
            treeStoreTypes.append(str)
        self.view.treestore = Gtk.TreeStore(*treeStoreTypes)

        # Build the regex row
        regex_row = []
        regex_row.append("HEADER REGEX")
        regex_row.append("#c8c8c8")
        regex_row.append(Pango.Weight.BOLD)
        regex_row.append(True)
        for field in self.symbol.getFields():
            regex_row.append(glib.markup_escape_text(field.getEncodedVersionOfTheRegex()))

        # Build the types row
        types_line = []
        types_line.append("HEADER TYPE")
        types_line.append("#dedede")
        types_line.append(Pango.Weight.BOLD)
        types_line.append(True)
        for field in self.symbol.getFields():
            types_line.append(field.getFormat())

        self.view.treestore.append(None, regex_row)
        self.view.treestore.append(None, types_line)
        idLine = 0
        messageEntryToHighlight = None
        for line in content_lines:
            messageEntry = self.view.treestore.append(None, line)
            if nbLineMessageToHighlight == idLine:
                messageEntryToHighlight = messageEntry
            idLine = idLine + 1

        # activate or deactivate the perfect number of columns = nb Field
        for col in self.view.treeview.get_columns():
            self.view.treeview.remove_column(col)
        for i in range(0, min(200, len(self.symbol.getFields()))):
            self.view.treeview.append_column(self.view.currentColumns[i])
            self.view.treeview.get_column(i).set_title(self.symbol.getFieldByIndex(i).getName())

        self.view.treeview.set_model(self.view.treestore)

        # highlight the message entry
        if messageEntryToHighlight is not None:
            self.view.treeview.get_selection().select_iter(messageEntryToHighlight)

    def updateDefault(self):
        self.default(self.symbol)

    def buttonReleaseOnTreeviewMessages_cb(self, treeview, event):
        # re-enable selection
        treeview.get_selection().set_select_function(lambda * ignore: True, None)
        target = treeview.get_path_at_pos(int(event.x), int(event.y))
        if (self.defer_select and target and self.defer_select == target[0] and not (event.x == 0 and event.y == 0)):  # certain drag and drop
            treeview.set_cursor(target[0], target[1], False)
            self.defer_select = False

    #+----------------------------------------------
    #| buttonPressOnTreeviewMessages_cb:
    #|   operation when the user click on the treeview.
    #|   mainly to open a contextual menu
    #+----------------------------------------------
    def buttonPressOnTreeviewMessages_cb(self, treeview, event):
        target = treeview.get_path_at_pos(int(event.x), int(event.y))
        if (target and event.type == Gdk.EventType.BUTTON_PRESS and not (event.get_state() & (Gdk.ModifierType.CONTROL_MASK | Gdk.ModifierType.SHIFT_MASK)) and treeview.get_selection().path_is_selected(target[0])):
            # disable selection
            treeview.get_selection().set_select_function(lambda * ignore: False, None)
            self.defer_select = target[0]

        # Display the details of a packet
        if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 1:
            x = int(event.x)
            y = int(event.y)
            try:
                (path, treeviewColumn, x, y) = treeview.get_path_at_pos(x, y)
            except:
                # No message selected
                pass
            else:
                # A message is selected
                aIter = treeview.get_model().get_iter(path)
                if aIter:
                    if treeview.get_model().iter_is_valid(aIter):
                        message_id = treeview.get_model().get_value(aIter, 0)

                        # search for the message in the vocabulary
                        message = self.netzob.getCurrentProject().getVocabulary().getMessageByID(message_id)
                        logging.debug("Selected message found :  {0}".format(message))
                        self.selectedMessage = message
                        self.vocabularyController.update()
                        return

        # Popup a menu
        elif event.type == Gdk.EventType.BUTTON_PRESS and event.button == 3:
            self.log.debug(_("User requested a contextual menu (treeview messages)"))
            x = int(event.x)
            y = int(event.y)

            try:
                (path, treeviewColumn, x, y) = treeview.get_path_at_pos(x, y)
            except:
                return

            # Retrieve the selected message
            message_id = None
            aIter = treeview.get_model().get_iter(path)
            if aIter:
                if treeview.get_model().iter_is_valid(aIter):
                    message_id = treeview.get_model().get_value(aIter, 0)

            # Retrieve the selected column number
            iField = 0
            for col in treeview.get_columns():
                if col == treeviewColumn:
                    break
                iField += 1

            selectedField = None
            for field in self.getSymbol().getFields():
                if field.getIndex() == iField:
                    selectedField = field
            if selectedField is None:
                self.log.warn(_("Impossible to retrieve the clicked field !"))
                return

            # Add entry to move seleted messages
            self.menu = Gtk.Menu()
            listmessages = []
            (model, paths) = self.getTreeview().get_selection().get_selected_rows()
            for path in paths:
                aIter = model.get_iter(path)
                if(model.iter_is_valid(aIter)):
                    id_message = model.get_value(aIter, 0)
                    listmessages.append(id_message)

            subMenu = self.build_moveto_submenu(self.vocabularyController.treeSymbolController.selectedSymbol, listmessages)
            item = Gtk.MenuItem(_("Move to..."))
            item.set_submenu(subMenu)
            item.show()
            self.menu.append(item)

            # Add entry to edit field
            item = Gtk.MenuItem(_("Edit field"))
            item.show()
            item.connect("activate", self.displayPopupToEditField, selectedField)
            self.menu.append(item)

            # Add sub-entries to change the type of a specific column
            subMenu = self.build_encoding_submenu(selectedField, message_id)
            item = Gtk.MenuItem(_("Field visualization"))
            item.set_submenu(subMenu)
            item.show()
            self.menu.append(item)

            # Add sub-entries to add mathematic filters on a  specific column
            subMenuMathematicFilters = self.build_mathematicFilter_submenu(selectedField)
            item = Gtk.MenuItem("Configure mathematic filters")
            item.set_submenu(subMenuMathematicFilters)
            item.show()
            self.menu.append(item)

            # Add entries to concatenate column
            concatMenu = Gtk.Menu()
            if selectedField.getIndex() > 0:
                item = Gtk.MenuItem(_("with precedent field"))
                item.show()
                item.connect("activate", self.rightClickToConcatColumns, selectedField, "left")
                concatMenu.append(item)

                item = Gtk.MenuItem(_("with all precedent field"))
                item.show()
                item.connect("activate", self.rightClickToConcatColumns, selectedField, "allleft")
                concatMenu.append(item)

            if selectedField.getIndex() < len(self.getSymbol().getFields()) - 1:
                item = Gtk.MenuItem(_("with next field"))
                item.show()
                item.connect("activate", self.rightClickToConcatColumns, selectedField, "right")
                concatMenu.append(item)

                item = Gtk.MenuItem(_("with all next fields"))
                item.show()
                item.connect("activate", self.rightClickToConcatColumns, selectedField, "allright")
                concatMenu.append(item)

            # Personalize the fields to be concatenated
            item = Gtk.MenuItem(_("personalize selection"))
            item.show()
            item.connect("activate", self.ConcatChosenColumns)
            concatMenu.append(item)

            item = Gtk.MenuItem(_("Concatenate field"))
            item.set_submenu(concatMenu)
            item.show()
            self.menu.append(item)

            # Add entry to split the column
            item = Gtk.MenuItem(_("Split field"))
            item.show()
            item.connect("activate", self.rightClickToSplitColumn, selectedField)
            self.menu.append(item)

            # Add sub-entries to do partitioning of field cells
            subMenu = self.build_partitioning_submenu_for_field(selectedField)
            item = Gtk.MenuItem(_("Partitioning"))
            item.set_submenu(subMenu)
            item.show()
            self.menu.append(item)

            # Add entry to retrieve the field domain of definition
            item = Gtk.MenuItem(_("Field's domain of definition"))
            item.show()
            item.connect("activate", self.rightClickDomainOfDefinition, selectedField)
            self.menu.append(item)

            # Add sub-entries to change the variable of a specific column
            if selectedField.getVariable() is None:
                typeMenuVariable = Gtk.Menu()
                itemVariable = Gtk.MenuItem(_("Create a variable"))
                itemVariable.show()
                itemVariable.connect("activate", self.rightClickCreateVariable, self.getSymbol(), selectedField)
                typeMenuVariable.append(itemVariable)
            else:
                typeMenuVariable = Gtk.Menu()
                itemVariable = Gtk.MenuItem(_("Edit variable"))
                itemVariable.show()
                itemVariable.connect("activate", self.rightClickEditVariable, selectedField)
                typeMenuVariable.append(itemVariable)

            if selectedField.getVariable() is not None:
                itemVariable3 = Gtk.MenuItem(_("Remove variable"))
                itemVariable3.show()
                itemVariable3.connect("activate", self.rightClickRemoveVariable, selectedField)
                typeMenuVariable.append(itemVariable3)

            item = Gtk.MenuItem(_("Configure variation of field"))
            item.set_submenu(typeMenuVariable)
            item.show()
            self.menu.append(item)

            item = Gtk.SeparatorMenuItem()
            item.show()
            self.menu.append(item)

            # Add entries for copy functions
            copyMenu = Gtk.Menu()
            item = Gtk.MenuItem(_("Raw message"))
            item.show()
            item.connect("activate", self.rightClickToCopyToClipboard, message_id, False, False, None)
            copyMenu.append(item)
            item = Gtk.MenuItem(_("Aligned message"))
            item.show()
            item.connect("activate", self.rightClickToCopyToClipboard, message_id, True, False, None)
            copyMenu.append(item)
            item = Gtk.MenuItem(_("Aligned formatted message"))
            item.show()
            item.connect("activate", self.rightClickToCopyToClipboard, message_id, True, True, None)
            copyMenu.append(item)
            item = Gtk.MenuItem(_("Field"))
            item.show()
            item.connect("activate", self.rightClickToCopyToClipboard, message_id, True, False, selectedField)
            copyMenu.append(item)
            item = Gtk.MenuItem(_("Formatted field"))
            item.show()
            item.connect("activate", self.rightClickToCopyToClipboard, message_id, True, True, selectedField)
            copyMenu.append(item)
            item = Gtk.MenuItem(_("Copy to clipboard"))
            item.set_submenu(copyMenu)
            item.show()
            self.menu.append(item)

            # Add entry to show properties of the message
            item = Gtk.MenuItem(_("Message properties"))
            item.show()
            item.connect("activate", self.rightClickShowPropertiesOfMessage, message_id)
            self.menu.append(item)

            # Add entry to delete the message
            item = Gtk.MenuItem(_("Delete message"))
            item.show()
            item.connect("activate", self.rightClickDeleteMessage)
            self.menu.append(item)

            self.menu.popup(None, None, None, None, event.button, event.time)

    #+----------------------------------------------
    #| build_partitioning_submenu_for_field:
    #|   Build a submenu for field cell partitioning.
    #+----------------------------------------------
    def build_moveto_submenu(self, symbol_src, listmessages):
        project = self.netzob.getCurrentProject()

        # Sanity checks
        if project is None:
            NetzobErrorMessage(_("No project selected."))
            return
        menu = Gtk.Menu()

        for symbol in project.getVocabulary().getSymbols():
            item = Gtk.MenuItem(symbol.getName())
            item.show()
            item.connect("activate", self.moveTo, symbol, symbol_src, listmessages)
            menu.append(item)

        return menu

    #+----------------------------------------------
    #| build_partitioning_submenu_for_field:
    #|   Build a submenu for field cell partitioning.
    #+----------------------------------------------
    def build_partitioning_submenu_for_field(self, field):
        menu = Gtk.Menu()

        # Sequence alignment
        item = Gtk.MenuItem(_("Sequence Alignment"))
        item.show()
        item.connect("activate", self.fieldPartitioning, field, "alignment")
        menu.append(item)

        # Force partitioning
        # TODO
#        item = Gtk.MenuItem("Force Partitioning")
#        item.show()
#        item.connect("activate", self.fieldPartitioning, field, "force")
#        menu.append(item)

        # Simple partitioning
        item = Gtk.MenuItem(_("Simple Partitioning"))
        item.show()
        item.connect("activate", self.fieldPartitioning, field, "simple")
        menu.append(item)

        return menu

    #+----------------------------------------------
    #| build_mathematicFilter_submenu:
    #|   Build a submenu for field/symbol mathematic filters
    #|   param field: the selected field
    #+----------------------------------------------
    def build_mathematicFilter_submenu(self, field):
        menu = Gtk.Menu()

        # Build the list of available filters
        mathematicalFilters = []
        mathematicalFilters.append(Base64Filter("Base64 Filter"))
        mathematicalFilters.append(GZipFilter("GZip Filter"))
        mathematicalFilters.append(BZ2Filter("BZ2 Filter"))

        for mathFilter in mathematicalFilters:

            operation = "Add"
            for f in field.getMathematicFilters():
                if f.getName() == mathFilter.getName():
                    operation = "Remove"

            mathFilterItem = Gtk.MenuItem(operation + " " + mathFilter.getName())
            mathFilterItem.connect("activate", self.applyMathematicalFilterOnField, mathFilter, field)
            mathFilterItem.show()
            menu.append(mathFilterItem)

        return menu

    def applyMathematicalFilterOnField(self, object, filter, field):
        appliedFilters = field.getMathematicFilters()
        found = False
        for appliedFilter in appliedFilters:
            if appliedFilter.getName() == filter.getName():
                found = True
        if found:
            #deactivate the selected filter
            field.removeMathematicFilter(filter)
        else:
            field.addMathematicFilter(filter)
        self.update()

    #+----------------------------------------------
    #| rightClickToChangeFormat:
    #|   Callback to change the field/symbol format
    #|   by doing a right click on it.
    #+----------------------------------------------
    def rightClickToChangeFormat(self, event, aObject, aFormat):
        aObject.setFormat(aFormat)
        self.update()

    #+----------------------------------------------
    #| rightClickToChangeUnitSize:
    #|   Callback to change the field/symbol unitsize
    #|   by doing a right click on it.
    #+----------------------------------------------
    def rightClickToChangeUnitSize(self, event, aObject, unitSize):
        aObject.setUnitSize(unitSize)
        self.update()

    #+----------------------------------------------
    #| rightClickToChangeSign:
    #|   Callback to change the field/symbol sign
    #|   by doing a right click on it.
    #+----------------------------------------------
    def rightClickToChangeSign(self, event, aObject, sign):
        aObject.setSign(sign)
        self.update()

    #+----------------------------------------------
    #| rightClickToChangeEndianess:
    #|   Callback to change the field/symbol endianess
    #|   by doing a right click on it.
    #+----------------------------------------------
    def rightClickToChangeEndianess(self, event, aObject, endianess):
        aObject.setEndianess(endianess)
        self.update()

    #+----------------------------------------------
    #| build_encoding_submenu:
    #|   Build a submenu for field/symbol data visualization.
    #|   param aObject: either a field or a symbol
    #+----------------------------------------------
    def build_encoding_submenu(self, aObject, message_id):
        menu = Gtk.Menu()

        # Retrieve the selected message and field content
        message = self.vocabularyController.treeSymbolController.selectedSymbol.getMessageByID(message_id)
        if message is not None:
            # Retrieve content of the field
            field_content = message.getFields(False)[aObject.getIndex()]
        else:
            field_content = None

        # Format submenu
        possible_choices = Format.getSupportedFormats()
        subMenu = Gtk.Menu()
        for value in possible_choices:
            if field_content is not None:
                # Get preview of field content
                text_preview = TypeConvertor.encodeNetzobRawToGivenType(field_content, value)
                if len(text_preview) > 10:
                    text_preview = text_preview[:10] + "..."

                item = Gtk.MenuItem(value + " (" + text_preview + ")")
            else:
                item = Gtk.MenuItem(value)
            item.show()
            item.connect("activate", self.rightClickToChangeFormat, aObject, value)
            subMenu.append(item)
        item = Gtk.MenuItem(_("Format"))
        item.set_submenu(subMenu)
        item.show()
        menu.append(item)

        # Unitsize submenu
        possible_choices = [UnitSize.NONE, UnitSize.BIT, UnitSize.BITS8, UnitSize.BITS16, UnitSize.BITS32, UnitSize.BITS64]
        subMenu = Gtk.Menu()
        for value in possible_choices:
            item = Gtk.MenuItem(value)
            item.show()
            item.connect("activate", self.rightClickToChangeUnitSize, aObject, value)
            subMenu.append(item)
        item = Gtk.MenuItem(_("UnitSize"))
        item.set_submenu(subMenu)
        item.show()
        menu.append(item)

        # Sign submenu
        possible_choices = [Sign.SIGNED, Sign.UNSIGNED]
        subMenu = Gtk.Menu()
        for value in possible_choices:
            item = Gtk.MenuItem(value)
            item.show()
            item.connect("activate", self.rightClickToChangeSign, aObject, value)
            subMenu.append(item)
        item = Gtk.MenuItem(_("Sign"))
        item.set_submenu(subMenu)
        item.show()
        menu.append(item)

        # Endianess submenu
        possible_choices = [Endianess.BIG, Endianess.LITTLE]
        subMenu = Gtk.Menu()
        for value in possible_choices:
            item = Gtk.MenuItem(value)
            item.show()
            item.connect("activate", self.rightClickToChangeEndianess, aObject, value)
            subMenu.append(item)
        item = Gtk.MenuItem(_("Endianess"))
        item.set_submenu(subMenu)
        item.show()
        menu.append(item)
        return menu

    def displayPopupToEditField(self, event, field):
        dialog = Gtk.MessageDialog(None,
                                   Gtk.DialogFlags.MODAL,
                                   Gtk.MessageType.INFO,
                                   Gtk.ButtonsType.CANCEL,
                                   _("Modify field attributes"))
        vbox = Gtk.VBox()

        # Create hbox for field name
        hbox = Gtk.HBox()
        vbox.pack_start(hbox, False, 5, 5)
        hbox.pack_start(NetzobLabel(_("Name : ")), False, 5, 5)
        entryName = Gtk.Entry()
        entryName.set_text(field.getName())
        # Allow the user to press enter to do ok
        entryName.connect("activate", self.responseToDialog, dialog, Gtk.ResponseType.OK)
        hbox.pack_end(entryName, True, True, 0)

        # Create hbox for field description
        hbox = Gtk.HBox()
        vbox.pack_start(hbox, False, 5, 5)
        hbox.pack_start(NetzobLabel(_("Description : ")), False, 5, 5)
        entryDescr = Gtk.Entry()
        if field.getDescription():
            entryDescr.set_text(field.getDescription())
        else:
            entryDescr.set_text("")
        # Allow the user to press enter to do ok
        entryDescr.connect("activate", self.responseToDialog, dialog, Gtk.ResponseType.OK)
        hbox.pack_end(entryDescr, True, True, 0)

        # Create hbox for field regex
        hbox = Gtk.HBox()
        vbox.pack_start(hbox, False, 5, 5)
        hbox.pack_start(NetzobLabel(_("Regex (be careful !) : ")), False, 5, 5)
        entryRegex = Gtk.Entry()
        entryRegex.set_text(field.getRegex())
        # Allow the user to press enter to do ok
        entryRegex.connect("activate", self.responseToDialog, dialog, Gtk.ResponseType.OK)
        hbox.pack_end(entryRegex, True, True, 0)

        # Create hbox for field encapsulation level
        hbox = Gtk.HBox()
        vbox.pack_start(hbox, False, 5, 5)
        hbox.pack_start(NetzobLabel(_("Encapsulation level : ")), False, 5, 5)
        comboEncap = NetzobComboBoxEntry()
        for i in range(10):
            comboEncap.append_text(str(i))
            if i == field.getEncapsulationLevel():
                comboEncap.set_active(i)
        hbox.pack_end(comboEncap, True, True, 0)

        # Run the dialog
        dialog.vbox.pack_end(vbox, True, True, 0)
        dialog.show_all()
        dialog.add_button(Gtk.STOCK_OK, Gtk.ResponseType.OK)
        result = dialog.run()
        if result != Gtk.ResponseType.OK:
            dialog.destroy()
            return

        # Update field name
        text = entryName.get_text()
        if (len(text) > 0):
            field.setName(text)

        # Update field description
        text = entryDescr.get_text()
        if (len(text) > 0):
            field.setDescription(text)

        # Update field regex
        text = entryRegex.get_text()
        if (len(text) > 0):
            field.setRegex(text)
        dialog.destroy()
        self.update()

        # Update field encapsulation level
        try:
            encapLevel = int(comboEncap.get_active())
        except TypeError:
            pass
        else:
            if encapLevel >= 0:
                field.setEncapsulationLevel(encapLevel)
        self.update()

    #+----------------------------------------------
    #| responseToDialog:
    #|   pygtk is so good ! arf :(<-- clap clap :D
    #+----------------------------------------------
    def responseToDialog(self, entry, dialog, response):
        dialog.response(response)

    #+----------------------------------------------
    #| rightClickDomainOfDefinition:
    #|   Retrieve the domain of definition of the selected column
    #+----------------------------------------------
    def rightClickDomainOfDefinition(self, event, field):
        # Sanity checks
        project = self.netzob.getCurrentProject()
        if project is None:
            NetzobErrorMessage(_("No project selected."))
            return

        cells = self.getSymbol().getUniqValuesByField(field)
        tmpDomain = set()
        for cell in cells:
            tmpDomain.add(TypeConvertor.encodeNetzobRawToGivenType(cell, field.getFormat()))
        domain = sorted(tmpDomain)

        dialog = Gtk.Dialog(title=_("Domain of definition for the column ") + field.getName(), flags=0, buttons=None)

        # Text view containing domain of definition
        ## ListStore format:
        # str: symbol.id
        treeview = Gtk.TreeView(Gtk.ListStore(str))
        treeview.set_size_request(500, 300)
        treeview.show()

        cell = Gtk.CellRendererText()
        cell.set_sensitive(True)
        cell.set_property('editable', True)

        column = Gtk.TreeViewColumn(_("Column ") + str(field.getIndex()))
        column.pack_start(cell, True)
        column.add_attribute(cell, "text", 0)

        treeview.append_column(column)

        for elt in domain:
            treeview.get_model().append([elt])

        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroll.show()
        scroll.add(treeview)

        dialog.vbox.pack_start(scroll, True, True, 0)
        dialog.show()

    #+----------------------------------------------
    #| rightClickToCopyToClipboard:
    #|   Copy the message to the clipboard
    #+----------------------------------------------
    def rightClickToCopyToClipboard(self, event, id_message, aligned, encoded, field):
        self.log.debug(_("The user wants to copy the following message to the clipboard: {0}").format(str(id_message)))

        # Retrieve the selected message
        message = self.vocabularyController.treeSymbolController.selectedSymbol.getMessageByID(id_message)
        if message is None:
            self.log.warning(_("Impossible to retrieve the message based on its ID [{0}]".format(id_message)))
            return

        if not aligned:  # Copy the entire raw message
            self.netzob.clipboard.set_text(message.getStringData(), -1)
        elif field is None:  # Copy the entire aligned message
            self.netzob.clipboard.set_text(str(message.applyAlignment(styled=False, encoded=encoded)), -1)
        else:  # Just copy the selected field
            self.netzob.clipboard.set_text(message.applyAlignment(styled=False, encoded=encoded)[field.getIndex()], -1)

    #+----------------------------------------------
    #| rightClickShowPropertiesOfMessage:
    #|   Show a popup to present the properties of the selected message
    #+----------------------------------------------
    def rightClickShowPropertiesOfMessage(self, event, id_message):
        self.log.debug(_("The user wants to see the properties of message {0}").format(str(id_message)))

        # Retrieve the selected message
        message = self.vocabularyController.treeSymbolController.selectedSymbol.getMessageByID(id_message)
        if message is None:
            self.log.warning(_("Impossible to retrieve the message based on its ID [{0}]").format(id_message))
            return

        # Create the dialog
        dialog = Gtk.Dialog(title=_("Properties of message ") + str(message.getID()), flags=0, buttons=None)
        ## ListStore format : (str=key, str=type, str=value)
        treeview = Gtk.TreeView(Gtk.ListStore(str, str, str))
        treeview.set_size_request(500, 300)
        treeview.show()

        cell = Gtk.CellRendererText()

        columnProperty = Gtk.TreeViewColumn(_("Property"))
        columnProperty.pack_start(cell, True)
        columnProperty.add_attribute(cell, "text", 0)

        columnType = Gtk.TreeViewColumn(_("Type"))
        columnType.pack_start(cell, True)
        columnType.add_attribute(cell, "text", 1)

        columnValue = Gtk.TreeViewColumn(_("Value"))
        columnValue.pack_start(cell, True)
        columnValue.add_attribute(cell, "text", 2)

        treeview.append_column(columnProperty)
        treeview.append_column(columnType)
        treeview.append_column(columnValue)

        # Retrieves all the properties of current message and
        # insert them in the treeview
        for property in message.getProperties():
            strProperty = [str(e) for e in property]
            treeview.get_model().append(strProperty)

        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroll.show()
        scroll.add(treeview)

        dialog.vbox.pack_start(scroll, True, True, 0)
        dialog.show()

    #+----------------------------------------------
    #| rightClickDeleteMessage:
    #|   Delete the requested message
    #+----------------------------------------------
    def rightClickDeleteMessage(self, event):
        questionMsg = _("Click yes to confirm the deletion of the selected messages")
        md = Gtk.MessageDialog(None, Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT, Gtk.MessageType.QUESTION, Gtk.ButtonsType.YES_NO, questionMsg)
        result = md.run()
        md.destroy()
        if result != Gtk.ResponseType.YES:
            return

        # Else, retrieve the selected messages
        (model, paths) = self.getTreeview().get_selection().get_selected_rows()
        for path in paths:
            aIter = model.get_iter(path)
            if(model.iter_is_valid(aIter)):
                id_message = model.get_value(aIter, 0)
                self.log.debug(_("The user wants to delete the message {0}").format(str(id_message)))

                message_symbol = self.vocabularyController.treeSymbolController.selectedSymbol
                message = self.vocabularyController.treeSymbolController.selectedSymbol.getMessageByID(id_message)

                # Break if the message to move was not found
                if message is None:
                    self.log.warning(_("Impossible to retrieve the message to remove based on its ID [{0}]".format(id_message)))
                    return
                message_symbol.removeMessage(message)
                self.netzob.getCurrentProject().getVocabulary().removeMessage(message)
        self.update()

    #+----------------------------------------------
    #| concatenateChosenFields:
    #|   Ask the user which field to concatenate
    #+----------------------------------------------
    def ConcatChosenColumns(self, event=None, errormessage=""):
        nrows = 2
        if(errormessage):
            nrows = 3
        dialog = Gtk.Dialog(title=_("Concatenation of Fields"), flags=0, buttons=None)
        panel = Gtk.Table(rows=nrows, columns=4, homogeneous=False)
        panel.show()

        ## Label for indexes of the fields
        label = NetzobLabel(_("Fields from:"))
        index1 = Gtk.Entry()
        index1.set_max_length(4)
        index1.show()
        label2 = NetzobLabel(_("to:"))
        index2 = Gtk.Entry()
        index2.set_max_length(4)
        index2.show()
        if(errormessage):
            label3 = NetzobLabel(errormessage)

        panel.attach(label, 0, 1, 0, 1, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)
        panel.attach(index1, 1, 2, 0, 1, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)
        panel.attach(label2, 2, 3, 0, 1, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)
        panel.attach(index2, 3, 4, 0, 1, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)

        if(errormessage):
            panel.attach(label3, 2, 4, 2, 7, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)

        # Button
        searchButton = NetzobButton(_("Concatenate fields"))
        searchButton.connect("clicked", self.clickToConcatChosenColumns, index1, index2, dialog)
        panel.attach(searchButton, 0, 2, 1, 2, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)

        dialog.vbox.pack_start(panel, True, True, 0)
        dialog.show()

    #+--------------------------------------------
    #|  clickToConcatChosenColumns:
    #|	try to concatenate wanted fields.
    #+-------------------------------------------
    def clickToConcatChosenColumns(self, event, index1, index2, dialog):
        try:
            nfirst = int(index1.get_text())
            nlast = int(index2.get_text())
            self.log.debug(_("Concatenate from {0} to the column {1}").format(str(nfirst), str(nlast)))
            if max(nlast, nfirst) >= len(self.vocabularyController.treeSymbolController.selectedSymbol.fields):
                dialog.destroy()
                self.ConcatChosenColumns(errormessage=_("Error: {0} > Last field index".format(str(max(nlast, nfirst)))))
                return 1
            if(nlast > nfirst):
                for i_concatleft in range(nlast - nfirst):
                    if not self.vocabularyController.treeSymbolController.selectedSymbol.concatFields(nfirst):
                        break
                    else:
                        for i_concatleft in range(nfirst - nlast):
                            if not self.vocabularyController.treeSymbolController.selectedSymbol.concatFields(nlast):
                                break
                self.updateDefault()
                self.update()
                dialog.destroy()
        except:
            dialog.destroy()
            self.ConcatChosenColumns(errormessage=_("Error: You must put integers in forms"))

    #+----------------------------------------------
    #|  rightClickToConcatColumns:
    #|   Callback to concatenate two columns
    #+----------------------------------------------
    def rightClickToConcatColumns(self, event, field, strOtherCol):
        self.log.debug(_("Concatenate the column {0} with the {1} column").format(str(field.getIndex()), str(strOtherCol)))
        if field.getIndex() == 0 and (strOtherCol == "left" or strOtherCol == "allleft"):
            self.log.debug(_("Can't concatenate the first column with its left column"))
            return

        if field.getIndex() + 1 == len(self.vocabularyController.treeSymbolController.selectedSymbol.getFields()) and (strOtherCol == "right" or strOtherCol == "allright"):
            self.log.debug(_("Can't concatenate the last column with its right column"))
            return

        if strOtherCol == "left":
            self.vocabularyController.treeSymbolController.selectedSymbol.concatFields(field.getIndex() - 1)
        elif strOtherCol == "allleft":
            for i_concatleft in range(field.getIndex()):
                self.vocabularyController.treeSymbolController.selectedSymbol.concatFields(0)
        elif strOtherCol == "allright":
            cont = self.vocabularyController.treeSymbolController.selectedSymbol.concatFields(field.getIndex())
            while(cont):
                cont = self.vocabularyController.treeSymbolController.selectedSymbol.concatFields(field.getIndex())
        else:
            self.vocabularyController.treeSymbolController.selectedSymbol.concatFields(field.getIndex())
        self.updateDefault()
        self.update()

    #+----------------------------------------------
    #|  rightClickToSplitColumn:
    #|   Callback to split a column
    #+----------------------------------------------
    def rightClickToSplitColumn(self, event, field):
        dialog = Gtk.Dialog(title=_("Split column ") + str(field.getIndex()), flags=0, buttons=None)
        textview = Gtk.TextView()
        textview.set_editable(False)
        textview.get_buffer().create_tag("redTag", weight=Pango.Weight.BOLD, foreground="red", family="Courier")
        textview.get_buffer().create_tag("greenTag", weight=Pango.Weight.BOLD, foreground="#006400", family="Courier")
        self.split_position = 1
        self.split_max_len = 0

        # Find the size of the longest message
        cells = self.vocabularyController.treeSymbolController.selectedSymbol.getCellsByField(field)
        for m in cells:
            if len(m) > self.split_max_len:
                self.split_max_len = len(m)

        # Padding orientation
        self.split_align = "left"
        but = NetzobButton(_("Align to right"))
        but.connect("clicked", self.doAlignSplit, textview, field, but)
        dialog.action_area.pack_start(but, True, True, 0)

        # Left arrow
        arrow = Gtk.Arrow(Gtk.ArrowType.LEFT, Gtk.ShadowType.OUT)
        arrow.show()
        but = Gtk.Button()
        but.show()
        but.add(arrow)
        but.connect("clicked", self.adjustSplitColumn, textview, "left", field)
        dialog.action_area.pack_start(but, True, True, 0)

        # Right arrow
        arrow = Gtk.Arrow(Gtk.ArrowType.RIGHT, Gtk.ShadowType.OUT)
        arrow.show()
        but = Gtk.Button()
        but.show()
        but.add(arrow)
        but.connect("clicked", self.adjustSplitColumn, textview, "right", field)
        dialog.action_area.pack_start(but, True, True, 0)

        # Split button
        but = NetzobButton(_("Split column"))
        but.connect("clicked", self.doSplitColumn, textview, field, dialog)
        dialog.action_area.pack_start(but, True, True, 0)

        # Text view containing selected column messages
        frame = NetzobFrame(_("Content of the column to split"))
        textview.set_size_request(600, 300)
#        cells = self.getSymbol().getCellsByCol(iCol)

        for m in cells:
            textview.get_buffer().insert_with_tags_by_name(textview.get_buffer().get_end_iter(), TypeConvertor.encodeNetzobRawToGivenType(m[:self.split_position], field.getFormat()) + "  ", "redTag")
            textview.get_buffer().insert_with_tags_by_name(textview.get_buffer().get_end_iter(), TypeConvertor.encodeNetzobRawToGivenType(m[self.split_position:], field.getFormat()) + "\n", "greenTag")
        textview.show()
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroll.show()
        scroll.add(textview)
        frame.add(scroll)
        dialog.vbox.pack_start(frame, True, True, 0)
        dialog.show()

    def rightClickCreateVariable(self, widget, symbol, field):
        self.log.debug(_("Opening the dialog for the creation of a variable"))
#===============================================================================
#        dialog = Gtk.MessageDialog(None, Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT, Gtk.MessageType.QUESTION, Gtk.ButtonsType.OK, None)
#        dialog.set_markup(_("Definition of the new variable"))
# 
#        # Create the ID of the new variable
#        variableID = uuid.uuid4()
# 
#        mainTable = Gtk.Table(rows=3, columns=2, homogeneous=False)
#        # id of the variable
#        variableIDLabel = NetzobLabel(_("ID :"))
#        variableIDValueLabel = NetzobLabel(str(variableID))
#        variableIDValueLabel.set_sensitive(False)
#        mainTable.attach(variableIDLabel, 0, 1, 0, 1, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)
#        mainTable.attach(variableIDValueLabel, 1, 2, 0, 1, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)
# 
#        # name of the variable
#        variableNameLabel = NetzobLabel(_("Name : "))
#        variableNameEntry = Gtk.Entry()
#        variableNameEntry.show()
#        mainTable.attach(variableNameLabel, 0, 1, 1, 2, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)
#        mainTable.attach(variableNameEntry, 1, 2, 1, 2, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)
# 
#        # Include current binary values
#        variableWithCurrentBinariesLabel = NetzobLabel(_("Add current binaries : "))
# 
#        variableWithCurrentBinariesButton = Gtk.CheckButton(_("Disjunctive inclusion"))
#        variableWithCurrentBinariesButton.set_active(False)
#        variableWithCurrentBinariesButton.show()
# 
#        mainTable.attach(variableWithCurrentBinariesLabel, 0, 1, 2, 3, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)
#        mainTable.attach(variableWithCurrentBinariesButton, 1, 2, 2, 3, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)
# 
#        dialog.vbox.pack_end(mainTable, True, True, 0)
#        dialog.show_all()
#        result = dialog.run()
# 
#        if result != Gtk.ResponseType.OK:
#            dialog.destroy()
#            return
# 
#        # We retrieve the value of the variable
#        varName = variableNameEntry.get_text()
# 
#        # Disjonctive inclusion ?
#        disjunctive = variableWithCurrentBinariesButton.get_active()
# 
#        if disjunctive:
#            # Create a default value
#            defaultValue = field.getDefaultVariable(symbol)
#        else:
#            defaultValue = None
# 
#        # We close the current dialog
#        dialog.destroy()
#===============================================================================

        # Dedicated view for the creation of a variable
        creationPanel = VariableTreeController(self.netzob, field)
        creationPanel.display()

    def rightClickRemoveVariable(self, widget, field):
        questionMsg = _("Click yes to confirm the removal of the variable {0}").format(field.getVariable().getID())
        md = Gtk.MessageDialog(None, Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT, Gtk.MessageType.QUESTION, Gtk.ButtonsType.YES_NO, questionMsg)
        result = md.run()
        md.destroy()
        if result == Gtk.ResponseType.YES:
            field.setVariable(None)
            self.update()
        else:
            self.log.debug(_("The user didn't confirm the deletion of the variable {0}").format(str(field.getVariable().getID())))

    def rightClickEditVariable(self, widget, field):
        creationPanel = VariableTreeController(self.netzob, field)
        creationPanel.display()

    def doSplitColumn(self, widget, textview, field, dialog):
        if self.split_max_len <= 1:
            dialog.destroy()
            return

        if self.split_align == "right":
            split_index = -self.split_position
        else:
            split_index = self.split_position
        self.vocabularyController.treeSymbolController.selectedSymbol.splitField(field, split_index, self.split_align)
        self.updateDefault()
        dialog.destroy()
        self.update()

    def adjustSplitColumn(self, widget, textview, direction, field):
        if self.split_max_len <= 1:
            return
        messages = self.vocabularyController.treeSymbolController.selectedSymbol.getCellsByField(field)

        # Bounds checking
        if self.split_align == "left":
            if direction == "left":
                self.split_position -= 1
                if self.split_position < 1:
                    self.split_position = 1
            else:
                self.split_position += 1
                if self.split_position > self.split_max_len - 1:
                    self.split_position = self.split_max_len - 1
        else:
            if direction == "left":
                self.split_position += 1
                if self.split_position > self.split_max_len - 1:
                    self.split_position = self.split_max_len - 1
            else:
                self.split_position -= 1
                if self.split_position < 1:
                    self.split_position = 1

        # Colorize text according to position
        textview.get_buffer().set_text("")
        for m in messages:
            # Crate padding in case of right alignment
            if self.split_align == "right":
                padding = ""
                messageLen = len(m)
                for i in range(self.split_max_len - messageLen):
                    padding += " "
                textview.get_buffer().insert_with_tags_by_name(textview.get_buffer().get_end_iter(), padding, "greenTag")
                split_index = -self.split_position
            else:
                split_index = self.split_position
            textview.get_buffer().insert_with_tags_by_name(textview.get_buffer().get_end_iter(), TypeConvertor.encodeNetzobRawToGivenType(m[:split_index], field.getFormat()) + "  ", "redTag")
            textview.get_buffer().insert_with_tags_by_name(textview.get_buffer().get_end_iter(), TypeConvertor.encodeNetzobRawToGivenType(m[split_index:], field.getFormat()) + "\n", "greenTag")

    def doAlignSplit(self, widget, textview, field, button_align):
        if self.split_align == "left":
            self.split_align = "right"
            button_align.set_label(_("Align to left"))
        else:
            self.split_align = "left"
            button_align.set_label(_("Align to right"))

        messages = self.vocabularyController.treeSymbolController.selectedSymbol.getCellsByField(field)

        # Adapt alignment
        textview.get_buffer().set_text("")
        for m in messages:
            # Crate padding in case of right alignment
            if self.split_align == "right":
                padding = ""
                messageLen = len(m)
                for i in range(self.split_max_len - messageLen):
                    padding += " "
                textview.get_buffer().insert_with_tags_by_name(textview.get_buffer().get_end_iter(), padding, "greenTag")
                split_index = -self.split_position
            else:
                split_index = self.split_position
            textview.get_buffer().insert_with_tags_by_name(textview.get_buffer().get_end_iter(), TypeConvertor.encodeNetzobRawToGivenType(m[:split_index], field.getFormat()) + "  ", "redTag")
            textview.get_buffer().insert_with_tags_by_name(textview.get_buffer().get_end_iter(), TypeConvertor.encodeNetzobRawToGivenType(m[split_index:], field.getFormat()) + "\n", "greenTag")

    #+----------------------------------------------
    #| dbClickToChangeFormat_cb:
    #|   Called when user double click on a row
    #|    in order to change the field format
    #+----------------------------------------------
    def dbClickToChangeFormat_cb(self, treeview, path, treeviewColumn):
        # Retrieve the selected column number
        iField = 0
        for col in treeview.get_columns():
            if col == treeviewColumn:
                break
            iField += 1

        selectedField = None
        for field in self.getSymbol().getFields():
            if field.getIndex() == iField:
                selectedField = field

        if selectedField is None:
            self.log.warn(_("Impossible to retrieve the clicked field !"))
            return

        possible_choices = Format.getSupportedFormats()
#        possibleTypes = self.getSymbol().getPossibleTypesForAField(selectedField)
        i = 0
        chosedFormat = selectedField.getFormat()
        for aFormat in possible_choices:
            if aFormat == chosedFormat:
                chosedFormat = possible_choices[(i + 1) % len(possible_choices)]
                break
            i += 1

        # Apply the new choosen format for this field
        selectedField.setFormat(chosedFormat)
        self.vocabularyController.update()

    #+--------------------------------------------------------
    #| moveTo:
    #|   Move selected messages from symbol_src to symbol_dst
    #+--------------------------------------------------------
    def moveTo(self, widget, symbol_dst, symbol_src, listmessages):

        self.log.debug(_("Move messages from {0} to {1} : {2}").format(symbol_src.getName(), symbol_dst.getName(), ",".join(listmessages)))

        if not listmessages:
            return

        for id_message in listmessages:
            message = symbol_src.getMessageByID(id_message)
            symbol_src.removeMessage(message)
            symbol_dst.addMessage(message)

        #TODO do a needleman ?
        # Retrieve default parameters of alignment
        #doInternalSlick = False
        #defaultFormat = Format.HEX
        #global_unitsize = self.netzob.getCurrentProject().getConfiguration().getVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_GLOBAL_UNITSIZE)
        #unitSize = UnitSize.getSizeInBits(global_unitsize)
        #if unitSize is None:
        #    unitSize = 8

        #alignmentProcess = NeedlemanAndWunsch(unitSize, self.loggingNeedlemanStatus)
        #alignmentProcess.alignSymbol(symbol_src, doInternalSlick, defaultFormat)
        #alignmentProcess.alignSymbol(symbol_dst, doInternalSlick, defaultFormat)

        self.update()

    #+----------------------------------------------
    #| fieldPartitioning:
    #|   Make a partitioning at the field level
    #+----------------------------------------------
    def fieldPartitioning(self, widget, field, partitioningType):
        # Create a temporary symbol to store cells
        id = str(uuid.uuid4())
        tmpSymbol = Symbol(id, "", self.netzob.getCurrentProject())
        for cell in self.vocabularyController.treeSymbolController.selectedSymbol.getCellsByField(field):
            idMsg = str(uuid.uuid4())
            msg = RawMessage(idMsg, 0, cell)
            tmpSymbol.addMessage(msg)

        # Retrieve default parameters of alignment
        doInternalSlick = False
        defaultFormat = Format.HEX
        global_unitsize = self.netzob.getCurrentProject().getConfiguration().getVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_GLOBAL_UNITSIZE)
        unitSize = UnitSize.getSizeInBits(global_unitsize)
        if unitSize is None:
            unitSize = 4

        # Process the partitioning
        if partitioningType == "alignment":
            alignmentProcess = NeedlemanAndWunsch(unitSize, self.loggingNeedlemanStatus)
            alignmentProcess.alignSymbol(tmpSymbol, doInternalSlick, defaultFormat)
        elif partitioningType == "force":
            logging.warn("Not yet implemented")
            return
        elif partitioningType == "simple":
            tmpSymbol.simplePartitioning(self.netzob.getCurrentProject().getConfiguration(), unitSize)
        else:
            return

        # Adapt the computated field partitionment to the original symbol
        index = field.getIndex()
        self.vocabularyController.treeSymbolController.selectedSymbol.popField(index)

        i = 0
        for tmpField in tmpSymbol.getFields():
            currentIndex = index + i
            i += 1
            self.vocabularyController.treeSymbolController.selectedSymbol.addField(tmpField, currentIndex)
            tmpField.setName(tmpField.getName() + "-" + str(i))

        # Adapt next fields indexes
        for nextField in self.vocabularyController.treeSymbolController.selectedSymbol.fields:
            if nextField.getIndex() > index:
                nextField.setIndex(index + len(tmpSymbol.getFields()))
        self.update()

    def loggingNeedlemanStatus(self, status, message):
        self.log.debug(_("Status = {0}: {1}").format(str(status), str(message)))

    #+----------------------------------------------
    #| dragFromDND_cb:
    #|   defines the operation executed when a message is
    #|   is dragged out current symbol
    #+----------------------------------------------
    def dragFromDND_cb(self, treeview, contexte, selection, info, dateur):
        ids = []
        treeview.get_selection().selected_foreach(self.foreach_drag_fromDND, ids)
        selection.set_text(";".join(ids), -1)

    def foreach_drag_fromDND(self, model, path, iter, ids):
        texte = str(model.get_value(iter, 0))
        ids.append(texte)
        return

    #+----------------------------------------------
    #| GETTERS:
    #+----------------------------------------------
    def getTreeview(self):
        return self.view.treeview

    def getScrollLib(self):
        return self.view.scroll

    def getSymbol(self):
        return self.symbol

    def getWidget(self):
        return self.view.scroll
