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
#| Standard library imports                                                  |
#+---------------------------------------------------------------------------+
from gettext import gettext as _
import logging
import uuid

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+
from gi.repository import Gtk, Gdk

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.ProjectConfiguration import ProjectConfiguration
from netzob.Common.Symbol import Symbol
from netzob.Common.Type.Endianess import Endianess
from netzob.Common.Type.Format import Format
from netzob.Common.Type.Sign import Sign
from netzob.Common.Type.TypeConvertor import TypeConvertor
from netzob.Common.Type.UnitSize import UnitSize
from netzob.Inference.Vocabulary.Alignment.NeedlemanAndWunsch import \
    NeedlemanAndWunsch
from netzob.UI.NetzobWidgets import NetzobErrorMessage, NetzobLabel
from netzob.UI.Vocabulary.Controllers.ForcePartitioningController import \
    ForcePartitioningController
from netzob.UI.Vocabulary.Controllers.ResetPartitioningController import \
    ResetPartitioningController
from netzob.UI.Vocabulary.Controllers.SequenceAlignmentController import \
    SequenceAlignmentController
from netzob.UI.Vocabulary.Controllers.SimplePartitioningController import \
    SimplePartitioningController
from netzob.UI.Vocabulary.Controllers.SmoothPartitioningController import \
    SmoothPartitioningController
from netzob.UI.Vocabulary.Views.TreeSymbolView import TreeSymbolView


#+----------------------------------------------
#| TreeSymbolController:
#+----------------------------------------------
class TreeSymbolController(object):

    #+----------------------------------------------
    #| Constructor:
    #+----------------------------------------------
    def __init__(self, netzob, vocabularyController):
        self.netzob = netzob
        self.vocabularyController = vocabularyController
        self.selectedSymbol = None
        self.log = logging.getLogger('netzob.UI.Vocabulary.Controllers.TreeSymbolController.py')
        self.view = TreeSymbolView(self.netzob)
        self.initCallbacks()

    def initCallbacks(self):
        self.getTreeview().connect("drag-data-received", self.dropFromDND_cb)
        self.getTreeview().connect('button-press-event', self.button_press_on_treeview_symbols)

    #+----------------------------------------------
    #| Update the content of the tree store for symbols
    #+----------------------------------------------
    def update(self):
        # Updates the treestore with a selected message
        if (self.vocabularyController.treeMessageController.selectedMessage is not None):
            self.default(self.selectedSymbol)
#            self.vocabularyController.treeMessageController.selectedMessage = None
        else:
            # Default display of the symbols
            self.default(self.selectedSymbol)

    #+----------------------------------------------
    #| clear:
    #|         Clear the class
    #+----------------------------------------------
    def clear(self):
        self.selectedSymbol = None

    #+----------------------------------------------
    #| default:
    #|         Update the treestore in normal mode
    #+----------------------------------------------
    def default(self, selectedSymbol=None):
        self.log.debug(_("Updating the treestore of the symbol in default mode"))
        self.view.treestore.clear()

        # We retrieve the current project
        project = self.netzob.getCurrentProject()

        if project is not None:
            # We retrieve the vocabulary of the project
            vocabulary = project.getVocabulary()

            # Include the name of the project
            self.view.lvcolumn.set_title(project.getName())

            # We retrieve the symbols declared in (symbol = symbol)
            symbols = vocabulary.getSymbols()

            toSelectEntry = None
            for symbol in symbols:
                symbolName = symbol.getName()

                for filter in symbol.getVisualizationFilters():
                    symbolName = filter.apply(symbolName)

                symbolName = symbolName + " (" + str(len(symbol.getMessages())) + ")"
                symbolEntry = [str(symbol.getID()), symbolName, str(symbol.getScore()), '#000000', '#DEEEF0']
                symbolIter = self.view.treestore.append(None, symbolEntry)
                if selectedSymbol is not None and str(symbol.getID()) == str(selectedSymbol.getID()):
                    toSelectEntry = symbolIter

            # if a selection entry has been found, we highlight it
            if toSelectEntry is not None:
                self.view.treeview.get_selection().select_iter(toSelectEntry)

    #+----------------------------------------------
    #| button_press_on_treeview_symbols:
    #|   operation when the user click on the treeview.
    #|   mainly to open a contextual menu
    #+----------------------------------------------
    def button_press_on_treeview_symbols(self, treeview, event):
        # Sanity checks
        project = self.netzob.getCurrentProject()
        if project is None:
            NetzobErrorMessage(_("No project selected."))
            return
        if project.getVocabulary() is None:
            NetzobErrorMessage(_("The current project doesn't have any referenced vocabulary."))
            return

        x = int(event.x)
        y = int(event.y)
        clickedSymbol = self.getSymbolAtPosition(x, y)

        if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 1 and clickedSymbol is not None:
            self.selectedSymbol = clickedSymbol
            self.vocabularyController.update()

        if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 3:
            self.build_context_menu_for_symbols(event, clickedSymbol)

    #+----------------------------------------------
    #| getSymbolAtPosition:
    #|         retrieves the symbol wich is inserted
    #|         in the treeview at the given position
    #| @param x the position in X
    #| @param y the position in Y
    #| @return the symbol if it exists (or None)
    #+----------------------------------------------
    def getSymbolAtPosition(self, x, y):
        self.log.debug(_("Search for the symbol referenced at position {0};{1}").format(str(x), str(y)))
        vocabulary = self.netzob.getCurrentProject().getVocabulary()

        info = self.view.treeview.get_path_at_pos(x, y)
        if info is not None:
            path = info[0]
            iter = self.view.treeview.get_model().get_iter(path)
            idSymbol = str(self.view.treeview.get_model().get_value(iter, 0))
            if idSymbol is not None:
                self.log.debug(_("An entry with the ID {0} has been found.").format(idSymbol))
                for symbol in vocabulary.getSymbols():
                    if (str(symbol.getID()) == idSymbol):
                        self.log.debug(_("The requested symbol with ID {0} has been found").format(symbol.getID()))
                        return symbol
        return None

    #+----------------------------------------------
    #| build_context_menu_for_symbols:
    #|   Create a menu to display available operations
    #|   on the treeview symbols
    #+----------------------------------------------
    def build_context_menu_for_symbols(self, event, symbol):
        # Build the contextual menu
        self.menu = Gtk.Menu()

        if (symbol is not None):
            # Edit the Symbol
            itemEditSymbol = Gtk.MenuItem(_("Edit symbol"))
            itemEditSymbol.show()
            itemEditSymbol.connect("activate", self.displayPopupToEditSymbol, symbol)
            self.menu.append(itemEditSymbol)

            # Search in the Symbol
            itemSearchSymbol = Gtk.MenuItem(_("Search in"))
            itemSearchSymbol.show()
            itemSearchSymbol.connect("activate", self.displayPopupToSearch, "Symbol", symbol)
            self.menu.append(itemSearchSymbol)

            # SubMenu : Alignments
            subMenuAlignment = Gtk.Menu()

            # Sequence alignment
            itemSequenceAlignment = Gtk.MenuItem(_("Sequence Alignment"))
            itemSequenceAlignment.show()
            itemSequenceAlignment.connect("activate", self.sequenceAlignmentOnSpecifiedSymbols, [symbol])
            subMenuAlignment.append(itemSequenceAlignment)

            # Force partitioning
            itemForcePartitioning = Gtk.MenuItem(_("Force Partitioning"))
            itemForcePartitioning.show()
            itemForcePartitioning.connect("activate", self.forcePartitioningOnSpecifiedSymbols, [symbol])
            subMenuAlignment.append(itemForcePartitioning)

            # Simple partitioning
            itemSimplePartitioning = Gtk.MenuItem(_("Simple Partitioning"))
            itemSimplePartitioning.show()
            itemSimplePartitioning.connect("activate", self.simplePartitioningOnSpecifiedSymbols, [symbol])
            subMenuAlignment.append(itemSimplePartitioning)

            # Smooth partitioning
            itemSmoothPartitioning = Gtk.MenuItem(_("Smooth Partitioning"))
            itemSmoothPartitioning.show()
            itemSmoothPartitioning.connect("activate", self.smoothPartitioningOnSpecifiedSymbols, [symbol])
            subMenuAlignment.append(itemSmoothPartitioning)

            # Reset partitioning
            itemResetPartitioning = Gtk.MenuItem(_("Reset Partitioning"))
            itemResetPartitioning.show()
            itemResetPartitioning.connect("activate", self.resetPartitioningOnSpecifiedSymbols, [symbol])
            subMenuAlignment.append(itemResetPartitioning)

            itemMenuAlignment = Gtk.MenuItem(_("Align the symbol"))
            itemMenuAlignment.show()
            itemMenuAlignment.set_submenu(subMenuAlignment)

            self.menu.append(itemMenuAlignment)

            # Add sub-entries to change the type of a specific column
            subMenu = self.build_encoding_submenu(symbol, None)
            item = Gtk.MenuItem(_("Field visualization"))
            item.set_submenu(subMenu)
            item.show()
            self.menu.append(item)

            # Remove a Symbol
            itemRemoveSymbol = Gtk.MenuItem(_("Remove symbol"))
            itemRemoveSymbol.show()
            itemRemoveSymbol.connect("activate", self.displayPopupToRemoveSymbol, symbol)
            self.menu.append(itemRemoveSymbol)
        else:
            # Create a Symbol
            itemCreateSymbol = Gtk.MenuItem(_("Create a symbol"))
            itemCreateSymbol.show()
            itemCreateSymbol.connect("activate", self.displayPopupToCreateSymbol, symbol)
            self.menu.append(itemCreateSymbol)

        self.menu.popup(None, None, None, None, event.button, event.time)

    def sequenceAlignmentOnSpecifiedSymbols(self, widget, symbols):
        # Execute the process of alignment (show the gui...)
        sequenceAlignment = SequenceAlignmentController(self.netzob, self.vocabularyController)
        sequenceAlignment.sequenceAlignment(symbols)

    def forcePartitioningOnSpecifiedSymbols(self, widget, symbols):
        # Execute the process of alignment (show the gui...)
        forcePartitioning = ForcePartitioningController(self.netzob, self.vocabularyController)
        forcePartitioning.forcePartitioning(symbols)

    def simplePartitioningOnSpecifiedSymbols(self, widget, symbols):
        # Sanity checks
        if self.netzob.getCurrentProject() is None:
            NetzobErrorMessage(_("No project selected."))
            return
        # Retrieve all the symbols
        project = self.netzob.getCurrentProject()
        # Execute the process of alignment (show the gui...)
        simplePartitioning = SimplePartitioningController(self.netzob, self.vocabularyController)
        simplePartitioning.simplePartitioning(symbols)

    def smoothPartitioningOnSpecifiedSymbols(self, widget, symbols):
        # Sanity checks
        if self.netzob.getCurrentProject() is None:
            NetzobErrorMessage(_("No project selected."))
            return
        # Execute the process of alignment (show the gui...)
        smoothPartitioning = SmoothPartitioningController(self.netzob, self.vocabularyController)
        smoothPartitioning.smoothPartitioning(symbols)

    def resetPartitioningOnSpecifiedSymbols(self, widget, symbols):
        # Sanity checks
        if self.netzob.getCurrentProject() is None:
            NetzobErrorMessage(_("No project selected."))
            return
        # Execute the process of alignment (show the gui...)
        resetPartitioning = ResetPartitioningController(self.netzob, self.vocabularyController)
        resetPartitioning.resetPartitioning(symbols)

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

    #+----------------------------------------------
    #| rightClickToChangeFormat:
    #|   Callback to change the field/symbol format
    #|   by doing a right click on it.
    #+----------------------------------------------
    def rightClickToChangeFormat(self, event, aObject, aFormat):
        aObject.setFormat(aFormat)
        self.vocabularyController.update()

    #+----------------------------------------------
    #| rightClickToChangeUnitSize:
    #|   Callback to change the field/symbol unitsize
    #|   by doing a right click on it.
    #+----------------------------------------------
    def rightClickToChangeUnitSize(self, event, aObject, unitSize):
        aObject.setUnitSize(unitSize)
        self.vocabularyController.update()

    #+----------------------------------------------
    #| rightClickToChangeSign:
    #|   Callback to change the field/symbol sign
    #|   by doing a right click on it.
    #+----------------------------------------------
    def rightClickToChangeSign(self, event, aObject, sign):
        aObject.setSign(sign)
        self.vocabularyController.update()

    #+----------------------------------------------
    #| rightClickToChangeEndianess:
    #|   Callback to change the field/symbol endianess
    #|   by doing a right click on it.
    #+----------------------------------------------
    def rightClickToChangeEndianess(self, event, aObject, endianess):
        aObject.setEndianess(endianess)
        self.vocabularyController.update()

    def displayPopupToSearch(self, event, typeSearch, searchTarget):
        dialog = Gtk.MessageDialog(None,
                                   Gtk.DialogFlags.MODAL,
                                   Gtk.MessageType.OTHER,
                                   Gtk.ButtonsType.OK,
                                   _("Searching"))
        # Create the main panel
        panel = Gtk.Table(rows=3, columns=2, homogeneous=False)
        panel.show()

        # Create the header (first row) with the search form
        # Search entry
        searchEntry = Gtk.Entry()
        searchEntry.show()

        # Combo to select the type of the input
        typeCombo = Gtk.ComboBoxText.new_with_entry()
        typeCombo.show()
        typeStore = Gtk.ListStore(str)
        typeCombo.set_model(typeStore)
        typeCombo.get_model().append([Format.STRING])
        typeCombo.get_model().append([Format.HEX])
        typeCombo.get_model().append([Format.BINARY])
        typeCombo.get_model().append([Format.OCTAL])
        typeCombo.get_model().append([Format.DECIMAL])
        typeCombo.get_model().append([Format.IP])
        typeCombo.set_active(0)

        panel.attach(searchEntry, 0, 1, 0, 1, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)
        panel.attach(typeCombo, 1, 2, 0, 1, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)

        dialog.vbox.pack_end(panel, True, True, 0)

        dialog.run()
        searchedPattern = searchEntry.get_text()
        typeOfPattern = typeCombo.get_active_text()
        self.prepareSearchInSymbol(searchedPattern, typeOfPattern, searchTarget)

        dialog.destroy()

    def displayPopupToEditSymbol(self, event, symbol):
        dialog = Gtk.MessageDialog(
            None,
            Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
            Gtk.MessageType.QUESTION,
            Gtk.ButtonsType.OK,
            None)
        dialog.set_markup(_("<b>Please enter the name of the symbol :</b>"))
        #create the text input field
        entry = Gtk.Entry()
        entry.set_text(symbol.getName())
        #allow the user to press enter to do ok
        entry.connect("activate", self.responseToDialog, dialog, Gtk.ResponseType.OK)
        #create a horizontal box to pack the entry and a label
        hbox = Gtk.HBox()
        hbox.pack_start(NetzobLabel(_("Name : ")), False, 5, 5)
        hbox.pack_end(entry, True, True, 0)
        dialog.vbox.pack_end(hbox, True, True, 0)
        dialog.show_all()
        #go go go
        dialog.run()
        text = entry.get_text()
        if (len(text) > 0):
            self.selectedSymbol.setName(text)
        dialog.destroy()
        self.update()

    #+----------------------------------------------
    #| responseToDialog:
    #|   pygtk is so good ! arf :(<-- clap clap :D
    #+----------------------------------------------
    def responseToDialog(self, entry, dialog, response):
        dialog.response(response)

    #+----------------------------------------------
    #| displayPopupToCreateSymbol:
    #|   Display a form to create a new symbol.
    #|   Based on the famous dialogs
    #+----------------------------------------------
    def displayPopupToCreateSymbol(self, event, symbol):

        #base this on a message dialog
        dialog = Gtk.MessageDialog(None,
                                   Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
                                   Gtk.MessageType.QUESTION,
                                   Gtk.ButtonsType.OK,
                                   None)
        dialog.set_markup(_("<b>Please enter symbol's name</b> :"))
        #create the text input field
        entry = Gtk.Entry()
        #allow the user to press enter to do ok
        entry.connect("activate", self.responseToDialog, dialog, Gtk.ResponseType.OK)
        #create a horizontal box to pack the entry and a label
        hbox = Gtk.HBox()
        hbox.pack_start(NetzobLabel(_("Name :")), False, 5, 5)
        hbox.pack_end(entry, True, True, 0)
        #add it and show it
        dialog.vbox.pack_end(hbox, True, True, 0)
        dialog.show_all()
        #go go go
        dialog.run()
        newSymbolName = entry.get_text()
        dialog.destroy()

        if (len(newSymbolName) > 0):
            newSymbolId = str(uuid.uuid4())
            self.log.debug(_("a new symbol will be created with the given name : {0}").format(newSymbolName))
            newSymbol = Symbol(newSymbolId, newSymbolName, self.netzob.getCurrentProject())

            self.netzob.getCurrentProject().getVocabulary().addSymbol(newSymbol)

            #Update Left and Right
            self.update()

    #+----------------------------------------------
    #| displayPopupToRemoveSymbol:
    #|   Display a popup to remove a symbol
    #|   the removal of a symbol can only occurs
    #|   if its an empty symbol
    #+----------------------------------------------
    def displayPopupToRemoveSymbol(self, event, symbol):

        self.log.debug(_("Can remove the symbol {0} since it's an empty one.").format(symbol.getName()))
        questionMsg = _("Click yes to confirm the removal of the symbol {0}").format(symbol.getName())
        md = Gtk.MessageDialog(None, Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT, Gtk.MessageType.QUESTION, Gtk.ButtonsType.YES_NO, questionMsg)
        result = md.run()
        md.destroy()
        if result == Gtk.ResponseType.YES:
            while(symbol.getMessages()):
                message = symbol.getMessages()[0]
                symbol.removeMessage(message)
                self.netzob.getCurrentProject().getVocabulary().removeMessage(message)
            self.netzob.getCurrentProject().getVocabulary().removeSymbol(symbol)
            #Update Left and Right
            self.update()
        else:
            self.log.debug(_("The user didn't confirm the deletion of the symbol {0}").format(symbol.getName()))

    #+----------------------------------------------
    #| dropDromDND_cb:
    #|   defines the operation executed when a message is
    #|   is dropped out current symbol to the selected symbol
    #+----------------------------------------------
    def dropFromDND_cb(self, treeview, context, x, y, selection, info, etime):
        ids = selection.get_text()

        modele = treeview.get_model()
        info_depot = treeview.get_dest_row_at_pos(x, y)

        for msg_id in ids.split(";"):

            # First we search for the message to move
            message = None
            message_symbol = self.selectedSymbol
            for msg in message_symbol.getMessages():
                if str(msg.getID()) == msg_id:
                    message = msg

            # Break if the message to move was not found
            if message is None:
                self.log.warning(_("Impossible to retrieve the message to move based on its ID [{0}]".format(msg_id)))
                return

            self.log.debug(_("The message having the ID [{0}] has been found !".format(msg_id)))

            # Now we search for the new symbol of the message
            if info_depot:
                # TODO : check need to position variable
                chemin, position = info_depot
                iter = modele.get_iter(chemin)
                new_symbol_id = str(modele.get_value(iter, 0))

                new_message_symbol = self.netzob.getCurrentProject().getVocabulary().getSymbol(new_symbol_id)

            if new_message_symbol is None:
                self.log.warning(_("Impossible to retrieve the symbol in which the selected message must be moved out."))
                return

            self.log.debug(_("The new symbol of the message is {0}").format(str(new_message_symbol.getID())))
            message_symbol.removeMessage(message)

            # Adding to its new symbol
            new_message_symbol.addMessage(message)

            # Retrieve default parameters of alignment
            doInternalSlick = False
            defaultFormat = Format.HEX
            global_unitsize = self.netzob.getCurrentProject().getConfiguration().getVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_GLOBAL_UNITSIZE)
            unitSize = UnitSize.getSizeInBits(global_unitsize)
            if unitSize is None:
                unitSize = 8

            alignmentProcess = NeedlemanAndWunsch(unitSize, self.loggingNeedlemanStatus)
            alignmentProcess.alignSymbol(new_message_symbol, doInternalSlick, defaultFormat)
            alignmentProcess.alignSymbol(message_symbol, doInternalSlick, defaultFormat)

#            message_symbol.buildRegexAndAlignment(self.netzob.getCurrentProject().getConfiguration())
#            new_message_symbol.buildRegexAndAlignment(self.netzob.getCurrentProject().getConfiguration())

        #Update Left and Right
        self.update()
        return

    #+----------------------------------------------
    #| GETTERS:
    #+----------------------------------------------
    def getTreeview(self):
        return self.view.treeview

    def getScrollLib(self):
        return self.view.scroll

    def getWidget(self):
        return self.view.scroll
