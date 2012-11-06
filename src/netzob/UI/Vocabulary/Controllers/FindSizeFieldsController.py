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
from gi.repository import Gtk, Gdk
from gi.repository import Pango
import gi
from gi.repository import GObject
gi.require_version('Gtk', '3.0')
import logging

#+----------------------------------------------
#| Local Imports
#+----------------------------------------------
from netzob.UI.NetzobWidgets import NetzobLabel, NetzobButton, NetzobFrame, NetzobComboBoxEntry, \
    NetzobProgressBar, NetzobErrorMessage, NetzobInfoMessage
from netzob.Common.Threads.Tasks.ThreadedTask import ThreadedTask, TaskError
from netzob.Common.Threads.Job import Job
from netzob.Common.Type.TypeConvertor import TypeConvertor
from netzob.Common.Symbol import Symbol
from netzob.Common.ProjectConfiguration import ProjectConfiguration
from netzob.Inference.Vocabulary.SizeFieldIdentifier import SizeFieldIdentifier


#+----------------------------------------------
#| FindSizeFieldsController:
#+----------------------------------------------
class FindSizeFieldsController(object):

    #+----------------------------------------------
    #| Constructor:
    #| @param netzob: the netzob main class
    #+----------------------------------------------
    def __init__(self, netzob, vocabularyController):
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.UI.Vocabulary.Controllers.FindSizeFieldsController.py')
        self.netzob = netzob
        self.vocabularyController = vocabularyController
        self.initCallbacks()

    def initCallbacks(self):
        pass

    #+----------------------------------------------
    #| Called when user wants to find the potential size fields
    #+----------------------------------------------
    def findSizeFields(self):
        # Save the current encapsulation level of each field
        savedEncapsulationLevel = []
        for field in self.vocabularyController.treeSymbolController.selectedSymbol.getExtendedFields():
            savedEncapsulationLevel.append(field.getEncapsulationLevel())

        sizeFieldIdentifier = SizeFieldIdentifier()

        # Show the progression dialog
        dialog = Gtk.Dialog(title=_("Size Fields Identifications"), flags=0, buttons=None)
        panel = Gtk.Table(rows=2, columns=2, homogeneous=False)
        panel.show()

        # Progress bar
        self.progressBarSizeField = NetzobProgressBar()
        panel.attach(self.progressBarSizeField, 0, 2, 0, 1, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)

        # Buttons
        cancelSizeFieldButton = NetzobButton(_("Cancel"))
        startSizeFieldButton = NetzobButton(_("Start"))

        cancelSizeFieldButton.set_sensitive(False)
        cancelSizeFieldButton.connect("clicked", self.cancelfindSizeFields_cb, dialog, startSizeFieldButton, sizeFieldIdentifier)
        startSizeFieldButton.connect("clicked", self.findSizeFields_cb, dialog, sizeFieldIdentifier, [self.vocabularyController.treeSymbolController.selectedSymbol], cancelSizeFieldButton, savedEncapsulationLevel)

        panel.attach(startSizeFieldButton, 0, 1, 1, 2, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)
        panel.attach(cancelSizeFieldButton, 1, 2, 1, 2, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)

        dialog.vbox.pack_start(panel, True, True, 0)
        dialog.show()

    def findSizeFields_cb(self, button, dialog, sizeFieldIdentifier, symbols, cancelButton, savedEncapsulationLevel):
        # first we deactivate the start button
        button.set_sensitive(False)
        # reactivate the cancel button
        cancelButton.set_sensitive(True)

        self.currentExecutionOfFindSizeFieldHasFinished = False
        # Start the progress bar
        GObject.timeout_add(100, self.do_pulse_for_findSizeField)
        # Start the findsize field JOB
        Job(self.startFindSizeField(sizeFieldIdentifier, symbols, dialog, savedEncapsulationLevel))

    def startFindSizeField(self, sizeFieldIdentifier, symbols, dialog, savedEncapsulationLevel):
        results = []
        self.currentExecutionOfFindSizeFieldHasFinished = False
        try:
            (yield ThreadedTask(sizeFieldIdentifier.search, symbols, results))
        except TaskError, e:
            self.log.error("Error while proceeding to the size field identification: {0}".format(str(e)))

        sizeFields = sizeFieldIdentifier.getResults()
        logging.debug(sizeFields)

        self.currentExecutionOfFindSizeFieldHasFinished = True
        dialog.destroy()
        self.findSizeFields_results_cb(results, savedEncapsulationLevel)

    #+----------------------------------------------
    #| do_pulse_for_findSizeField:
    #|   Computes if the progress bar must be updated or not
    #+----------------------------------------------
    def do_pulse_for_findSizeField(self):
        if self.currentExecutionOfFindSizeFieldHasFinished == False:
            self.progressBarSizeField.pulse()
            return True
        return False

    def cancelfindSizeFields_cb(self, button, dialog, startButton, sizeFieldIdentifier):
        # first we deactivate the cancel button
        button.set_sensitive(False)
        # deactivate the start button
        startButton.set_sensitive(True)

        sizeFieldIdentifier.cancel()

        self.currentExecutionOfFindSizeFieldHasFinished = True

    def findSizeFields_results_cb(self, results, savedEncapsulationLevel):
        dialog = Gtk.Dialog(title="Potential size fields and related payload", flags=0, buttons=None)
        ## ListStore format:
        # int: size field column
        # int: size field size
        # int: start column
        # int: substart column
        # int: end column
        # int: subend column
        # str: message rendered in cell
        treeview = Gtk.TreeView(Gtk.ListStore(int, int, int, int, int, int, str))
        cell = Gtk.CellRendererText()
        selection = treeview.get_selection()
        selection.connect("changed", self.sizeField_selected, savedEncapsulationLevel)
        column = Gtk.TreeViewColumn('Size field and related payload')
        column.pack_start(cell, True)
        column.add_attribute(cell, "text", 6)
        treeview.append_column(column)

       # Chose button
        but = NetzobButton("Apply size field")
        but.connect("clicked", self.applySizeField, dialog, savedEncapsulationLevel)
        dialog.action_area.pack_start(but, True, True, 0)

       # Text view containing potential size fields
        treeview.set_size_request(800, 300)

        if len(results) == 0:
            NetzobErrorMessage("No size field found.")
        else:
            for result in results:
                treeview.get_model().append(result)

            treeview.show()
            scroll = Gtk.ScrolledWindow()
            scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
            scroll.show()
            scroll.add(treeview)
            dialog.vbox.pack_start(scroll, True, True, 0)
            dialog.connect("destroy", self.destroyDialogFindSizeFields, savedEncapsulationLevel)
            dialog.show()

    def destroyDialogFindSizeFields(self, dialog, savedEncapsulationLevel):
        # Optionaly restore original encapsulation levels if there were no modification
        i = -1
        for field in self.vocabularyController.treeSymbolController.selectedSymbol.getExtendedFields():
            i += 1
            field.setEncapsulationLevel(savedEncapsulationLevel[i])
        self.update()

    #+----------------------------------------------
    #| Called when user wants to try to apply a size field on a symbol
    #+----------------------------------------------
    def sizeField_selected(self, selection, savedEncapsulationLevel):
        # Optionaly restore original encapsulation levels
        i = -1
        for field in self.vocabularyController.treeSymbolController.selectedSymbol.getExtendedFields():
            i += 1
            field.setEncapsulationLevel(savedEncapsulationLevel[i])

        # Apply new encapsulation levels
        (model, iter) = selection.get_selected()
        if(iter):
            if(model.iter_is_valid(iter)):
                size_field = model.get_value(iter, 0)
                size_field_len = model.get_value(iter, 1)
                start_field = model.get_value(iter, 2)
                start_field_len = model.get_value(iter, 3)
                end_field = model.get_value(iter, 4)
                end_field_len = model.get_value(iter, 5)

                sizeField = self.vocabularyController.treeSymbolController.selectedSymbol.getFieldByIndex(size_field)
                startField = self.vocabularyController.treeSymbolController.selectedSymbol.getFieldByIndex(start_field)
                endField = self.vocabularyController.treeSymbolController.selectedSymbol.getFieldByIndex(end_field)

#                # We check if some values of the size field are longer than the expected size field length
#                cells = self.vocabularyController.treeSymbolController.selectedSymbol.getField().getCellsByField(sizeField)
#                for cell in cells:
#                    if len(cell) > size_field_len:
#                        print "SPLIT"
#                        # Then we split the field
#                        self.vocabularyController.treeSymbolController.selectedSymbol.splitField(sizeField, size_field_len)

                sizeField.setDescription(_("size field"))
                startField.setDescription(_("start of payload"))
                for i in range(start_field, end_field + 1):
                    field = self.vocabularyController.treeSymbolController.selectedSymbol.getFieldByIndex(i)
                    field.setEncapsulationLevel(field.getEncapsulationLevel() + 1)

                self.update()

    #+----------------------------------------------
    #| Called when user wants to apply a size field on a symbol
    #+----------------------------------------------
    def applySizeField(self, button, dialog, savedEncapsulationLevel):
        # Apply the new encapsulation levels on original fields
        del savedEncapsulationLevel[:]
        for field in self.vocabularyController.treeSymbolController.selectedSymbol.getExtendedFields():
            savedEncapsulationLevel.append(field.getEncapsulationLevel())
