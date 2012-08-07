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
from gettext import gettext as _
import os
import uuid
import logging

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+
from gi.repository import Gtk
import gi
gi.require_version('Gtk', '3.0')

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.UI.Vocabulary.Views.NewVocabularyView import NewVocabularyView
from netzob.Common.ResourcesConfiguration import ResourcesConfiguration
from netzob.Common.Symbol import Symbol
from netzob.UI.Vocabulary.Controllers.NewSequenceAlignmentController import NewSequenceAlignmentController
from netzob.UI.Vocabulary.Controllers.NewForcePartitioningController import NewForcePartitioningController
from netzob.UI.Vocabulary.Controllers.NewSimplePartitioningController import NewSimplePartitioningController
from netzob.UI.Vocabulary.Controllers.NewSmoothPartitioningController import NewSmoothPartitioningController
from netzob.UI.Vocabulary.Controllers.MessagesDistributionController import MessagesDistributionController


class NewVocabularyController(object):

    def __init__(self, netzob):
        self.netzob = netzob
        self._view = NewVocabularyView(self)
        self.log = logging.getLogger(__name__)
        self.view.updateLeftPanel()

    @property
    def view(self):
        return self._view

    def restart(self):
        """Restart the view"""
        logging.debug("Restarting the vocabulary view")
        self.view.removeAllMessageTables()
        self.view.updateLeftPanel()

    ## Symbol List toolbar callbacks
    def selectAllSymbolsButton_clicked_cb(self, toolButton):
        """
        select all the symbol in the symbol list
        @type  widget: boolean
        @param widget: if selected symbol
        """
        for row in self.view.symbolListStore:
            row[self.view.SYMBOLLISTSTORE_SELECTED_COLUMN] = True
        self.view.updateSymbolListToolbar()

    def unselectAllSymbolsButton_clicked_cb(self, toolButton):
        """
        unselect all the symbol in the symbol list
        @type  widget: boolean
        @param widget: if selected symbol
        """
        for row in self.view.symbolListStore:
            row[self.view.SYMBOLLISTSTORE_SELECTED_COLUMN] = False
        self.view.updateSymbolListToolbar()

    def createSymbolButton_clicked_cb(self, toolButton):
        builder2 = Gtk.Builder()
        builder2.add_from_file(os.path.join(
            ResourcesConfiguration.getStaticResources(),
            "ui",
            "dialogbox.glade"))
        dialog = builder2.get_object("createsymbol")
        #button apply
        applybutton = builder2.get_object("button1")
        applybutton.set_sensitive(False)
        dialog.add_action_widget(applybutton, 0)
        #button cancel
        cancelbutton = builder2.get_object("button435")
        dialog.add_action_widget(cancelbutton, 1)
        #disable apply button if no text
        entry = builder2.get_object("entry1")
        entry.connect("changed", self.entry_disableButtonIfEmpty_cb, applybutton)
        #run the dialog window and wait for the result
        result = dialog.run()

        if (result == 0):
            #apply
            newSymbolName = entry.get_text()
            newSymbolId = str(uuid.uuid4())
            self.log.debug("A new symbol will be created with the given name : {0}".format(newSymbolName))
            currentProject = self.netzob.getCurrentProject()
            newSymbol = Symbol(newSymbolId, newSymbolName, currentProject)
            currentProject.getVocabulary().addSymbol(newSymbol)
            self.view.updateLeftPanel()
            dialog.destroy()
        if (result == 1):
            #cancel
            dialog.destroy()

    def entry_disableButtonIfEmpty_cb(self, widget, button):
        if(len(widget.get_text()) > 0):
            button.set_sensitive(True)
        else:
            button.set_sensitive(False)

    def concatSymbolButton_clicked_cb(self, toolButton):
        #concat the message of all selected symbols
        symbols = self.view.getCheckedSymbolList()
        message = []
        for sym in symbols:
            message.extend(sym.getMessages())
        #give the message to the first symbol
        concatSymbol = symbols[0]
        concatSymbol.setMessages(message)
        currentProject = self.netzob.getCurrentProject()
        #delete all selected symbols
        self.view.emptyMessageTableDisplayingSymbols(symbols[1:])
        for sym in symbols:
            currentProject.getVocabulary().removeSymbol(sym)
        #add the concatenate symbol
        currentProject.getVocabulary().addSymbol(concatSymbol)
        #refresh view
        self.view.updateMessageTableDisplayingSymbols([concatSymbol])
        self.view.updateLeftPanel()

    #possible que si on selectionne un unique symbol
    def renameSymbolButton_clicked_cb(self, widget):
        symbol = self.view.getCheckedSymbolList()[0]
        builder2 = Gtk.Builder()
        builder2.add_from_file(os.path.join(
            ResourcesConfiguration.getStaticResources(),
            "ui",
            "dialogbox.glade"))
        dialog = builder2.get_object("renamesymbol")
        dialog.set_title("Rename the symbol " + symbol.getName())

        #button apply
        applybutton = builder2.get_object("button10")
        applybutton.set_sensitive(False)
        dialog.add_action_widget(applybutton, 0)
        #button cancel
        cancelbutton = builder2.get_object("button2")
        dialog.add_action_widget(cancelbutton, 1)
        #disable apply button if no text
        entry = builder2.get_object("entry3")
        entry.connect("changed", self.entry_disableButtonIfEmpty_cb, applybutton)
        #run the dialog window and wait for the result
        result = dialog.run()

        if (result == 0):
            #apply
            newSymbolName = entry.get_text()
            self.log.debug(_("Renamed symbol {0} to {1}").format(symbol.getName(), newSymbolName))
            currentProject = self.netzob.getCurrentProject()
            currentProject.getVocabulary().getSymbolByID(symbol.getID()).setName(newSymbolName)
            self.view.updateLeftPanel()
            self.view.updateMessageTableDisplayingSymbols([symbol])
            dialog.destroy()
        if (result == 1):
            #cancel
            dialog.destroy()

    def deleteSymbolButton_clicked_cb(self, toolButton):
        # Delete symbol
        for sym in self.view.getCheckedSymbolList():
            currentProject = self.netzob.getCurrentProject()
            currentVocabulary = currentProject.getVocabulary()
            for mess in sym.getMessages():
                currentVocabulary.removeMessage(mess)
            currentVocabulary.removeSymbol(sym)
            self.view.emptyMessageTableDisplayingSymbols([sym])
        # Update view
        self.view.updateLeftPanel()

    def newMessageTableButton_clicked_cb(self, toolButton):
        self.view.addMessageTable()

    def toggleCellRenderer_toggled_cb(self, widget, buttonid):
        model = self.view.symbolListStore
        model[buttonid][0] = not model[buttonid][0]
        self.view.updateSymbolListToolbar()

    def symbolListTreeViewSelection_changed_cb(self, selection):
        model, iter = selection.get_selected()
        currentVocabulary = self.netzob.getCurrentProject().getVocabulary()
        if iter is not None:
            symID = model[iter][self.view.SYMBOLLISTSTORE_ID_COLUMN]
            symbol = currentVocabulary.getSymbolByID(symID)
            self.view.setDisplayedSymbolInSelectedMessageTable(symbol)

################ TO BE FIXED
    def button_newview_cb(self, widget):
        self.focus = self.addSpreadSheet("empty", 0)
        self.focus.idsymbol = None

    def button_closeview_cb(self, widget, spreadsheet):
        spreadsheet.destroy()

        #refresh focus
        if self.focus.get_object("spreadsheet") == spreadsheet:
            self.focus = None

###############

######### MENU / TOOLBAR ENTRIES CONTROLLERS
    def sequenceAlignment_activate_cb(self, action):
        sequence_controller = NewSequenceAlignmentController(self)
        sequence_controller.run()

    def partitioningForce_activate_cb(self, action):
        force_controller = NewForcePartitioningController(self)
        force_controller.run()

    def partitioningSimple_activate_cb(self, action):
        simple_controller = NewSimplePartitioningController(self)
        simple_controller.run()

    def partitioningSmooth_activate_cb(self, action):
        smooth_controller = NewSmoothPartitioningController(self)
        smooth_controller.run()

    def partitioningReset_activate_cb(self, action):
        # ++CODE HERE++
        # RESET THE PARTITIONING OF CHECKED SYMBOL
        # UPDATE VIEW
        pass

    def concatField_activate_cb(self, action):
        pass

    def leftSplit_activate_cb(self, action):
        pass

    def rightSplit_activate_cb(self, action):
        pass

    def createVariable_activate_cb(self, action):
        pass

    def moveMessagesToOtherSymbol_activate_cb(self, action):
        pass

    def deleteMessages_activate_cb(self, action):
        pass

    def searchText_activate_cb(self, action):
        self._view.researchController.show()

    def environmentDep_activate_cb(self, action):
        pass

    def messagesDistribution_activate_cb(self, action):
        distribution = MessagesDistributionController(self._view.getCheckedSymbolList())
        distribution.run()

    def variableTable_activate_cb(self, action):
        builder2 = Gtk.Builder()
        builder2.add_from_file(os.path.join(
            ResourcesConfiguration.getStaticResources(),
            "ui",
            "variable_table.glade"))
        dialog = builder2.get_object("variableDialog")

        #button apply
        okbutton = builder2.get_object("variable_ok")
        dialog.add_action_widget(okbutton, 0)
        #add variable in treeview
        variable_liststore = builder2.get_object("variableListstore")
        # ++CODE HERE++
        # ADD DATA NEEDED ON THE LISTSTORE FOR EVERY VARIABLE CREATE BY USER
        # EXEMPLE TO ADD ONE LINE WITH VALUE : [variable1, symbolToto, re{g0.6]ex, ipv4, initialValue : 192.168.0.6 ]
        # EXEMPLE CODE :
        """i = variable_liststore.append()
        variable_liststore.set(i, 0, "variable1")
        variable_liststore.set(i, 1, "symbolToto")
        variable_liststore.set(i, 2, "re{g0.6]ex")
        variable_liststore.set(i, 3, "ipv4")
        variable_liststore.set(i, 4, "initial value : 192.168.0.6")
        i = variable_liststore.append()
        variable_liststore.set(i, 0, "variable2")
        variable_liststore.set(i, 1, "symbolToto")
        variable_liststore.set(i, 2, "re{g1006.8]ex")
        variable_liststore.set(i, 3, "binary")
        variable_liststore.set(i, 4, "initial value : 0110, min bits : 2, max bits : 8")"""
        ##

        #run the dialog window and wait for the result
        result = dialog.run()

        if (result == 0):
            dialog.destroy()

    def fieldLimits_activate_cb(self, action):
        pass

    def importMessagesFromFile_activate_cb(self, action):
        pass

    def captureMessages_activate_cb(self, action):
        pass

#########
