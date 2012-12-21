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
from netzob.UI.NetzobWidgets import NetzobInfoMessage
from netzob.Common.Plugins.Exporters.AbstractExporterController import AbstractExporterController
from netzob_plugins.Exporters.PeachExporter.PeachExporter.PeachExportView import PeachExportView
from netzob_plugins.Exporters.PeachExporter.PeachExporter.PeachExport import PeachExport


class PeachExportController(AbstractExporterController):
    """PeachExportController:
            A controller liking the Peach export and its view in the netzob GUI.
    """

    def __init__(self, netzob, plugin):
        """Constructor of PeachExportController:

                @type netzob: netzob.NetzobGUI.NetzobGUI
                @param netzob: the main netzob project.
        """
        self.netzob = netzob
        self.plugin = plugin
        self.model = PeachExport(netzob)
        self.view = PeachExportView()
        self.initCallbacks()
        self.selectedSymbolID = -4

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
        # TODO: Add tooltips to explain each case.
        if self.netzob.getCurrentProject() is not None:
            self.view.symbolTreeview.get_model().append(None, ["-1", _("Randomized state order fuzzer"), '#000000', '#DEEEF0'])
            self.view.symbolTreeview.get_model().append(None, ["-2", _("Randomized transitions stateful fuzzer"), '#000000', '#DEEEF0'])
            #self.view.symbolTreeview.get_model().append(None, ["-3", _("Fully stateful fuzzer"), '#000000', '#DEEEF0'])
            for symbol in self.netzob.getCurrentProject().getVocabulary().getSymbols():
                self.view.symbolTreeview.get_model().append(None, ["{0}".format(symbol.getID()), "One-state fuzzer (symbol \"{0}\")".format(symbol.getName()), '#000000', '#DEEEF0'])

            self.view.symbolTreeview.set_tooltip_text("Randomized state order fuzzer: a fuzzer that have one state per symbol of the Netzob project. It goes to one of this state randomly chosen at each step.\n\n" +
                                                      "Randomized transitions stateful fuzzer: a stateful fuzzer that follows Netzob's states and transitions. It does not take inputs into account and goes from one state to another by choosing randomly one of the transitions allowed by Netzob.\n\n" +
                                                      "Fully stateful fuzzer:a stateful fuzzer that respect as strictly as possible the Netzob grammar in its state model.\n\n")

    def clear(self):
        """clear:
        """
        pass

    def kill(self):
        """kill:
        """
        pass

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
            (model, itr) = treeview.get_selection().get_selected()
            if(itr):
                if(model.iter_is_valid(itr)):
                    symbolID = model.get_value(itr, 0)
                    self.showXMLDefinition(symbolID)
                    logging.debug("Selected treepath : {0}".format(str(model.get_path(itr))))

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
        if self.selectedSymbolID > -4:
            self.showXMLDefinition(self.selectedSymbolID)

    def toggleStaticFieldsMutation(self, check):
        """toggleStaticFieldsMutation:
            Allow or not netzob static fields to be mutated.

            @type check: gtk.ToggleButton
            @param check: the checkButton which toggling causes the call of this function.
        """
        self.model.setMutateStaticFields(check.get_active())
        # If nothing is currently displayed, nothing is updated.
        if self.selectedSymbolID > -4:
            self.showXMLDefinition(self.selectedSymbolID)

    def showXMLDefinition(self, symbolID):
        """showXMLDefinition:
                Show the XML Definition of the given symbol in the main subview of the Peachexportview.

                @type symbolID: integer
                @param symbolID: a number which identifies the symbol which XML Definition is displayed.
        """
        self.selectedSymbolID = symbolID
        xmlDefinition = self.getXmlDefinition()
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
                filePath = chooser.get_current_folder()
            else:
                return
            chooser.destroy()
            peachzobAddonsPath = os.path.join(self.getPlugin().getPluginStaticResourcesPath(), "PeachzobAddons.py.default")
            logging.debug("Path: {0}".format(peachzobAddonsPath))

            # Write down the PeachzobAddons essential for Peach to interprete files exported by Netzob.
            defaultAddonsFile = open(peachzobAddonsPath, 'r')
            addonsFile = open(os.path.join(filePath, "PeachzobAddons.py"), 'w')
            addonsFile.write(defaultAddonsFile.read())
            defaultAddonsFile.close()
            addonsFile.close()

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
                xmlDefinition = self.getXmlDefinition()
                try:
                    fuzzfile = open(fileName, 'w')
                    fuzzfile.write(xmlDefinition)
                    fuzzfile.close()
                except Exception, e:
                    NetzobInfoMessage(_("The following error occurred while exporting the project as a Peach Fuzzer to '{0}': {1}").format(fileName, e))

    def getXmlDefinition(self):
        """getXmlDefinition:
                Return the xml definition corresponding to the selected symbol.
        """
        # Special cases for stateful fuzzer:
        if self.selectedSymbolID == "-1":
            xmlDefinition = self.model.getPeachDefinition(0, 1)
        elif self.selectedSymbolID == "-2":
            xmlDefinition = self.model.getPeachDefinition(0, 2)
        elif self.selectedSymbolID == "-3":
            xmlDefinition = self.model.getPeachDefinition(0, 3)
        # Usual case with usual symbolID
        else:
            xmlDefinition = self.model.getPeachDefinition(self.selectedSymbolID, 0)
        return xmlDefinition

    def getPanel(self):
        """getPanel:

                @rtype: netzob_plugins.PeachExporter.PeachExportView.PeachExportView
                @return: the plugin view.
        """
        return self.view

    def getPlugin(self):
        """getPlugin:
        """
        return self.plugin
