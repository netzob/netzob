# -*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|          01001110 01100101 01110100 01111010 01101111 01100010            |
#|                                                                           |
#|               Netzob : Inferring communication protocols                  |
#+---------------------------------------------------------------------------+
#| Copyright (C) 2011 AMOSSYS                                                |
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
import os

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+
from gi.repository import Gtk

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.UI.NetzobWidgets import NetzobInfoMessage, NetzobErrorMessage
from netzob.Common.Plugins.Exporters.AbstractExporterController import AbstractExporterController
from PeachExportView import PeachExportView
from PeachExport import PeachExport


class PeachExportController(AbstractExporterController):
    """PeachExportController:
            A controller liking the Peach export and its view in the netzob GUI.
    """

    def run(self):
        """run:
            Show the plugin view.
        """
        self.view.dialog.show_all()
        self.view.hideWarning()
        self.update()

    def new(self):
        """new:
                Called when a user select a new trace.
        """
        pass

    def update(self):
        """update:
                Update the view. More precisely, it sets the symbol tree view which is its left part.
        """
        self.view.symbolTreeview.get_model().clear()
        logging.debug("The current project is {0}".format(str(self.netzob.getCurrentProject())))
        if self.netzob.getCurrentProject() is not None:
            # Append an "Entire project" leaf to the tree view.
            iter = self.view.symbolTreeview.get_model().append(None, ["-1", "{0} [{1}, {2}]".format(_("Entire project"), str(len(self.netzob.getCurrentProject().getVocabulary().getSymbols())), str(len(self.netzob.getCurrentProject().getVocabulary().getMessages()))), '#000000', '#DEEEF0'])

            for symbol in self.netzob.getCurrentProject().getVocabulary().getSymbols():
                iter = self.view.symbolTreeview.get_model().append(None, ["{0}".format(symbol.getID()), "{0} [{1}]".format(symbol.getName(), str(len(symbol.getMessages()))), '#000000', '#DEEEF0'])

    def clear(self):
        """clear:
        """
        pass

    def kill(self):
        """kill:
        """
        pass

    def __init__(self, netzob):
        """Constructor of PeachExportController:

                @type netzob: netzob.NetzobGUI.NetzobGUI
                @param netzob: the main netzob project.
        """
        self.netzob = netzob
        self.model = PeachExport(netzob)
        self.view = PeachExportView()
        self.initCallbacks()
        self.selectedSymbolID = -2

    def initCallbacks(self):
        """initCallbacks:
                Link the callbacks.
        """
        self.view.symbolTreeview.connect("cursor-changed", self.symbolSelected_cb)
        self.view.comboFuzzingBase.connect("changed", self.changeFuzzingBase)
        self.view.exportButton.connect("clicked", self.exportFuzzer)
        self.view.checkMutateStaticFields.connect("toggled", self.toggleStaticFieldsMutation)

    def symbolSelected_cb(self, treeview):
        """symbolSelected_cb:
                Called when a symbol is selected in the symbol tree view.

                @type treeview: gtk.TreeView
                @param treeview: the symbol tree view.
        """
        if treeview.get_selection() is not None:
            (model, iter) = treeview.get_selection().get_selected()
            if(iter):
                if(model.iter_is_valid(iter)):
                    symbolID = model.get_value(iter, 0)
                    self.showXMLDefinition(symbolID)

    def changeFuzzingBase(self, combo):
        """changeFuzzingBase:
                Change the fuzzing base between "based on regex" and "based on variable".

                @type combo: netzob.UI.NetzobWidgets.NetzobComboBoxEntry
                @param combo: the combobox which modification causes the call of this functions.
        """
        # Set the format choice as default
        fuzzingBase = combo.get_active_text()
        if fuzzingBase == "Variable":
            self.model.setVariableOverRegex(True)
        elif fuzzingBase == "Regex":
            self.model.setVariableOverRegex(False)

        # If nothing is currently displayed, nothing is updated.
        if self.selectedSymbolID > -2:
            self.showXMLDefinition(self.selectedSymbolID)

    def toggleStaticFieldsMutation(self, check):
        """toggleStaticFieldsMutation:
            Allow or not netzob static fields to be mutated.

            @type check: gtk.ToggleButton
            @param check: the checkButton which toggling causes the call of this function.
        """
        self.model.setMutateStaticFields(check.get_active())
        # If nothing is currently displayed, nothing is updated.
        if self.selectedSymbolID > -2:
            self.showXMLDefinition(self.selectedSymbolID)

    def showXMLDefinition(self, symbolID):
        """showXMLDefinition:
                Show the XML Definition of the given symbol in the main subview of the Peachexportview.

                @type symbolID: integer
                @param symbolID: a number which identifies the symbol which XML Definition is displayed.
        """
        self.selectedSymbolID = symbolID
        # Special case "entire project"
        if symbolID == "-1":
            xmlDefinition = self.model.getPeachDefinition(0, True)
        # Usual case with usual symbolID
        else:
            xmlDefinition = self.model.getPeachDefinition(symbolID, False)

        if xmlDefinition != None:
            self.view.textarea.get_buffer().set_text("")
            self.view.textarea.get_buffer().insert_with_tags_by_name(self.view.textarea.get_buffer().get_start_iter(), xmlDefinition, "normalTag")
        else:
            self.view.textarea.get_buffer().set_text(_("No XML definition found"))

    def exportFuzzer(self, button):
        """exportFuzzer:
                Export one or all netzob symbols in a Peach Fuzzer.

                @type button: gtk.Button
                @param button: the button which was clicked and caused the call of this function.
        """
        if self.selectedSymbolID != "-2":
            chooser = Gtk.FileChooserDialog(title=_("Export as Peach Fuzzer (XML)"), action=Gtk.FileChooserAction.SAVE, buttons=(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
            res = chooser.run()
            fileName = ""
            if res == Gtk.ResponseType.OK:
                fileName = chooser.get_filename()
            chooser.destroy()

            doCreateFile = False
            isFile = os.path.isfile(fileName)
            if not isFile:
                doCreateFile = True
            else:
                md = Gtk.MessageDialog(None, Gtk.DIALOG_DESTROY_WITH_PARENT, Gtk.MESSAGE_QUESTION, Gtk.BUTTONS_OK_CANCEL, _("Are you sure to override the file '{0}'?").format(fileName))
                resp = md.run()
                md.destroy()
                if resp == Gtk.RESPONSE_OK:
                    doCreateFile = True

            if doCreateFile:
                # Special case "entire project"
                if self.selectedSymbolID == "-1":
                    xmlDefinition = self.model.getPeachDefinition(0, True)
                # Usual case with usual symbolID
                else:
                    xmlDefinition = self.model.getPeachDefinition(self.selectedSymbolID, False)
                try:
                    file = open(fileName, 'w')
                    file.write(xmlDefinition)
                    file.close()
                    # TODO: maybe copy the plugin file with shutil
                    NetzobInfoMessage(_("The project has been correctly exported as a Peach Fuzzer to '{0}'.\nDo not forget to copy in the targeted directory our Peach plugin netzob_plugins/Exporters/PeachExporter/PeachzobAddons.py.").format(fileName))
                except Exception, e:
                    NetzobInfoMessage(_("The following error occurred while exporting the project as a Peach Fuzzer to '{0}': {1}").format(fileName, e))

    def getPanel(self):
        """getPanel:

                @rtype: netzob_plugins.PeachExporter.PeachExportView.PeachExportView
                @return: the plugin view.
        """
        return self.view
